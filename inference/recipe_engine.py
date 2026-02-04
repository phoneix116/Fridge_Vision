"""
Recipe recommendation engine.
Matches detected ingredients against recipe database and ranks results.
"""

import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class RecipeEngine:
    """Match ingredients to recipes and provide recommendations."""
    
    def __init__(self, recipes_path: Optional[str] = None):
        """
        Initialize recipe engine.
        
        Args:
            recipes_path: Path to recipes JSON file
        """
        self.recipes = []
        self._load_recipes(recipes_path)
    
    def _load_recipes(self, recipes_path: Optional[str]):
        """Load recipes from JSON file."""
        if recipes_path and Path(recipes_path).exists():
            try:
                with open(recipes_path, 'r') as f:
                    self.recipes = json.load(f)
                logger.info(f"Loaded {len(self.recipes)} recipes from {recipes_path}")
                return
            except Exception as e:
                logger.warning(f"Could not load recipes from file: {e}")
        
        # Use default recipes if file not found
        self.recipes = self._get_default_recipes()
        logger.info(f"Using {len(self.recipes)} default recipes")
    
    def _get_default_recipes(self) -> List[Dict]:
        """Return default recipe database."""
        return [
            {
                "id": 1,
                "name": "Simple Salad",
                "ingredients": ["lettuce", "tomato", "cucumber", "onion"],
                "difficulty": "easy",
                "prep_time_mins": 10,
                "servings": 2,
                "description": "Fresh green salad with vegetables"
            },
            {
                "id": 2,
                "name": "Vegetable Stir Fry",
                "ingredients": ["broccoli", "carrot", "onion", "bell pepper", "oil"],
                "difficulty": "easy",
                "prep_time_mins": 20,
                "servings": 3,
                "description": "Quick and healthy stir fry"
            },
            {
                "id": 3,
                "name": "Tomato Pasta",
                "ingredients": ["pasta", "tomato", "garlic", "onion", "oil"],
                "difficulty": "easy",
                "prep_time_mins": 25,
                "servings": 4,
                "description": "Classic Italian pasta sauce"
            },
            {
                "id": 4,
                "name": "Vegetable Soup",
                "ingredients": ["carrot", "onion", "potato", "tomato", "celery"],
                "difficulty": "easy",
                "prep_time_mins": 30,
                "servings": 4,
                "description": "Hearty vegetable soup"
            },
            {
                "id": 5,
                "name": "Fruit Smoothie",
                "ingredients": ["banana", "strawberry", "yogurt", "milk"],
                "difficulty": "easy",
                "prep_time_mins": 5,
                "servings": 2,
                "description": "Refreshing fruit smoothie"
            },
            {
                "id": 6,
                "name": "Grilled Vegetables",
                "ingredients": ["bell pepper", "zucchini", "onion", "tomato", "oil"],
                "difficulty": "easy",
                "prep_time_mins": 20,
                "servings": 3,
                "description": "Seasoned grilled vegetables"
            },
            {
                "id": 7,
                "name": "Garlic Bread",
                "ingredients": ["bread", "butter", "garlic"],
                "difficulty": "easy",
                "prep_time_mins": 15,
                "servings": 4,
                "description": "Crispy garlic bread"
            },
            {
                "id": 8,
                "name": "Avocado Toast",
                "ingredients": ["bread", "avocado", "tomato", "salt", "pepper"],
                "difficulty": "easy",
                "prep_time_mins": 5,
                "servings": 1,
                "description": "Trendy avocado toast breakfast"
            },
            {
                "id": 9,
                "name": "Carrot Salad",
                "ingredients": ["carrot", "lettuce", "onion"],
                "difficulty": "easy",
                "prep_time_mins": 10,
                "servings": 2,
                "description": "Crunchy carrot and lettuce salad"
            },
            {
                "id": 10,
                "name": "Lemon Rice",
                "ingredients": ["rice", "lemon", "oil", "onion"],
                "difficulty": "easy",
                "prep_time_mins": 20,
                "servings": 3,
                "description": "Fragrant lemon-flavored rice"
            }
        ]
    
    def recommend_recipes(
        self,
        ingredients: List[str],
        top_k: int = 5,
        min_match: int = 1
    ) -> List[Dict]:
        """
        Recommend recipes based on available ingredients.
        
        Args:
            ingredients: List of available ingredient names
            top_k: Number of top recipes to return
            min_match: Minimum number of ingredients that must match
            
        Returns:
            List of recommended recipes sorted by match score
        """
        if not ingredients:
            logger.warning("No ingredients provided for recommendation")
            return []
        
        # Normalize ingredient names
        available = set(ing.lower() for ing in ingredients)
        
        ranked_recipes = []
        
        for recipe in self.recipes:
            recipe_ingredients = set(ing.lower() for ing in recipe.get("ingredients", []))
            
            # Calculate match metrics
            matches = available.intersection(recipe_ingredients)
            match_count = len(matches)
            
            if match_count < min_match:
                continue
            
            # Calculate match score
            match_percentage = (match_count / len(recipe_ingredients)) * 100 if recipe_ingredients else 0
            missing_count = len(recipe_ingredients) - match_count
            
            ranked_recipes.append({
                "recipe_id": recipe["id"],
                "name": recipe["name"],
                "description": recipe.get("description", ""),
                "ingredients_required": recipe["ingredients"],
                "matched_ingredients": list(matches),
                "missing_ingredients": list(recipe_ingredients - matches),
                "match_count": match_count,
                "missing_count": missing_count,
                "match_percentage": round(match_percentage, 1),
                "difficulty": recipe.get("difficulty", "unknown"),
                "prep_time_mins": recipe.get("prep_time_mins", 0),
                "servings": recipe.get("servings", 0),
                "score": self._calculate_score(match_count, len(recipe_ingredients), missing_count)
            })
        
        # Sort by score (descending)
        ranked_recipes.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"Found {len(ranked_recipes)} recipes matching {len(available)} ingredients")
        
        return ranked_recipes[:top_k]
    
    def _calculate_score(self, matches: int, total: int, missing: int) -> float:
        """
        Calculate recommendation score.
        
        Score considers:
        - Number of matches (higher is better)
        - Match percentage (higher is better)
        - Number of missing ingredients (lower is better)
        
        Args:
            matches: Number of matched ingredients
            total: Total ingredients needed
            missing: Number of missing ingredients
            
        Returns:
            Score between 0 and 100
        """
        if total == 0:
            return 0
        
        # Match percentage (0-50 points)
        match_percentage = (matches / total) * 50
        
        # Missing penalty (0-50 points, inverted)
        missing_penalty = max(0, 50 - (missing * 10))
        
        # Total score
        score = match_percentage + missing_penalty
        
        return max(0, min(100, score))
    
    def find_recipe_by_id(self, recipe_id: int) -> Optional[Dict]:
        """Find a recipe by ID."""
        for recipe in self.recipes:
            if recipe.get("id") == recipe_id:
                return recipe
        return None
    
    def get_all_ingredients(self) -> List[str]:
        """Get all unique ingredients across all recipes."""
        ingredients = set()
        for recipe in self.recipes:
            for ingredient in recipe.get("ingredients", []):
                ingredients.add(ingredient.lower())
        return sorted(list(ingredients))


# Global recipe engine instance
_recipe_engine = None


def get_recipe_engine(recipes_path: Optional[str] = None) -> RecipeEngine:
    """Get or create singleton recipe engine."""
    global _recipe_engine
    
    if _recipe_engine is None:
        _recipe_engine = RecipeEngine(recipes_path=recipes_path)
    
    return _recipe_engine
