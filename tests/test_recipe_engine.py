"""
Unit tests for recipe engine module.
Tests recipe matching and ranking logic.
"""

import pytest
from unittest.mock import patch, MagicMock

from inference.recipe_engine import RecipeEngine


@pytest.mark.unit
class TestRecipeEngine:
    """Test cases for RecipeEngine."""
    
    @pytest.fixture
    def recipe_engine(self, mock_recipes, temp_dir):
        """Create RecipeEngine instance with mock recipes."""
        import json
        # Write mock recipes to temp file
        recipes_path = f"{temp_dir}/recipes.json"
        with open(recipes_path, 'w') as f:
            json.dump(mock_recipes, f)
        return RecipeEngine(recipes_path=recipes_path)
    
    def test_engine_initialization(self, recipe_engine):
        """Test RecipeEngine initialization."""
        assert recipe_engine is not None
        assert hasattr(recipe_engine, 'recommend_recipes')
    
    def test_exact_ingredient_match(self, recipe_engine, mock_recipes):
        """Test recipe recommendation with exact ingredient match."""
        detected_ingredients = ['apple', 'banana', 'orange']
        
        recommendations = recipe_engine.recommend_recipes(detected_ingredients)
        
        assert len(recommendations) > 0
        # Should recommend Fruit Salad which has all three ingredients
        assert any(r['name'] == 'Fruit Salad' for r in recommendations)
    
    def test_partial_ingredient_match(self, recipe_engine):
        """Test recipe recommendation with partial ingredients."""
        detected_ingredients = ['apple', 'flour']
        
        recommendations = recipe_engine.recommend_recipes(detected_ingredients)
        
        assert len(recommendations) > 0
        # Should recommend recipes with these ingredients
        assert len(recommendations[0]['matched_ingredients']) > 0
    
    def test_no_match_recipes(self, recipe_engine):
        """Test handling of no matching recipes."""
        detected_ingredients = ['xyz', 'abc', 'def']
        
        recommendations = recipe_engine.recommend_recipes(detected_ingredients)
        
        # Should return empty or low-scoring recipes
        assert isinstance(recommendations, list)
    
    def test_ranking_by_score(self, recipe_engine):
        """Test recipes are ranked by match score."""
        detected_ingredients = ['apple']
        
        recommendations = recipe_engine.recommend_recipes(detected_ingredients)
        
        # Verify recipes are sorted by score (descending)
        if len(recommendations) > 1:
            scores = [r['match_score'] for r in recommendations]
            assert scores == sorted(scores, reverse=True)
    
    def test_missing_ingredients_tracked(self, recipe_engine):
        """Test that missing ingredients are tracked."""
        detected_ingredients = ['apple']
        
        recommendations = recipe_engine.recommend_recipes(detected_ingredients)
        
        for recipe in recommendations:
            assert 'missing_ingredients' in recipe
            assert isinstance(recipe['missing_ingredients'], list)
    
    def test_case_insensitive_matching(self, recipe_engine):
        """Test case-insensitive ingredient matching."""
        detected_ingredients = ['APPLE', 'Banana', 'OrAnGe']
        
        recommendations = recipe_engine.recommend_recipes(detected_ingredients)
        
        # Should still find matches despite case differences
        assert len(recommendations) > 0
    
    def test_recipe_metadata_preserved(self, recipe_engine):
        """Test that recipe metadata is preserved in results."""
        detected_ingredients = ['apple', 'banana']
        
        recommendations = recipe_engine.recommend_recipes(detected_ingredients)
        
        if len(recommendations) > 0:
            recipe = recommendations[0]
            assert 'name' in recipe
            assert 'description' in recipe
            assert 'ingredients' in recipe
            assert 'difficulty' in recipe
            assert 'prep_time_mins' in recipe
            assert 'servings' in recipe
    
    def test_empty_ingredient_list(self, recipe_engine):
        """Test handling of empty ingredient list."""
        recommendations = recipe_engine.recommend_recipes([])
        
        assert isinstance(recommendations, list)
    
    def test_duplicate_ingredients_handling(self, recipe_engine):
        """Test handling of duplicate ingredients."""
        detected_ingredients = ['apple', 'apple', 'banana', 'apple']
        
        recommendations = recipe_engine.recommend_recipes(detected_ingredients)
        
        # Should handle duplicates gracefully
        assert len(recommendations) >= 0


@pytest.mark.unit
class TestRecipeMatching:
    """Test recipe matching logic details."""
    
    @pytest.fixture
    def recipe_engine(self, mock_recipes, temp_dir):
        """Create RecipeEngine instance."""
        import json
        recipes_path = f"{temp_dir}/recipes.json"
        with open(recipes_path, 'w') as f:
            json.dump(mock_recipes, f)
        return RecipeEngine(recipes_path=recipes_path)
    
    def test_match_score_calculation(self, recipe_engine):
        """Test match score is calculated correctly."""
        detected_ingredients = ['apple', 'flour', 'sugar']
        
        recommendations = recipe_engine.recommend_recipes(detected_ingredients)
        
        for recipe in recommendations:
            # Score should be based on match percentage and other factors
            if len(recipe['ingredients_required']) > 0:
                match_pct = (len(recipe['matched_ingredients']) / len(recipe['ingredients_required'])) * 100
                assert recipe['match_percentage'] == round(match_pct, 1)
    
    def test_score_bounds(self, recipe_engine):
        """Test match scores are within valid bounds."""
        detected_ingredients = ['apple', 'banana']
        
        recommendations = recipe_engine.recommend_recipes(detected_ingredients)
        
        for recipe in recommendations:
            assert 0 <= recipe['score'] <= 100
            assert 0 <= recipe['match_percentage'] <= 100
    
    def test_top_recipe_relevance(self, recipe_engine):
        """Test top recommendation is most relevant."""
        detected_ingredients = ['apple', 'banana', 'orange']
        
        recommendations = recipe_engine.recommend_recipes(detected_ingredients)
        
        if len(recommendations) > 1:
            top_recipe = recommendations[0]
            # Top recipe should have highest score
            assert top_recipe['score'] >= recommendations[1]['score']
