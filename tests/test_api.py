"""
Unit tests for FastAPI endpoints.
Tests API routes and responses.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.mark.unit
class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_endpoint(self, client):
        """Test health check returns 200."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
    
    def test_health_response_structure(self, client):
        """Test health endpoint response structure."""
        response = client.get("/health")
        data = response.json()
        
        assert 'status' in data
        assert 'message' in data


@pytest.mark.unit
class TestInfoEndpoint:
    """Test info endpoint."""
    
    def test_info_endpoint(self, client):
        """Test info endpoint returns API information."""
        response = client.get("/info")
        
        assert response.status_code == 200
        data = response.json()
        assert 'name' in data or 'description' in data
    
    def test_info_contains_version(self, client):
        """Test info contains version information."""
        response = client.get("/info")
        data = response.json()
        
        # Should contain some versioning info
        assert any(key in data for key in ['version', 'api_version'])


@pytest.mark.unit
class TestDetectEndpoint:
    """Test ingredient detection endpoint."""
    
    def test_detect_endpoint_missing_file(self, client):
        """Test detect endpoint without file."""
        response = client.post("/detect-ingredients")
        
        assert response.status_code == 422  # Unprocessable Entity (validation error)
    
    @patch('api.main.get_inference')
    def test_detect_endpoint_with_file(self, mock_get_inference, client, sample_image_file):
        """Test detect endpoint with valid file."""
        # Setup mock inference
        mock_inference = MagicMock()
        mock_inference.detect_from_file.return_value = {
            'detections': [
                {'class_name': 'apple', 'confidence': 0.95, 'bbox': [100, 100, 200, 200]},
                {'class_name': 'banana', 'confidence': 0.87, 'bbox': [300, 150, 400, 250]}
            ],
            'count': 2,
            'image_size': (480, 640)
        }
        mock_get_inference.return_value = mock_inference
        
        with open(sample_image_file, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = client.post("/detect-ingredients", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert 'ingredients' in data
        assert isinstance(data['ingredients'], list)
    
    @patch('api.main.get_inference')
    def test_detect_response_structure(self, mock_get_inference, client, sample_image_file):
        """Test detection response has correct structure."""
        mock_inference = MagicMock()
        mock_inference.detect_from_file.return_value = {
            'detections': [
                {'class_name': 'apple', 'confidence': 0.95, 'bbox': [100, 100, 200, 200]}
            ],
            'count': 1
        }
        mock_get_inference.return_value = mock_inference
        
        with open(sample_image_file, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = client.post("/detect-ingredients", files=files)
        
        data = response.json()
        assert 'ingredients' in data
        assert 'count' in data


@pytest.mark.unit
class TestRecipeEndpoint:
    """Test recipe endpoints."""
    
    def test_recipes_list_endpoint(self, client):
        """Test getting all recipes."""
        response = client.get("/recipes")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_recipes_search_endpoint(self, client):
        """Test recipe search endpoint."""
        response = client.get("/recipes/search", params={"query": "salad"})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_recipe_by_id_endpoint(self, client):
        """Test getting recipe by ID."""
        response = client.get("/recipes/1")
        
        # May be 200 (found) or 404 (not found)
        assert response.status_code in [200, 404]


@pytest.mark.unit
class TestRecommendEndpoint:
    """Test recipe recommendation endpoint."""
    
    def test_recommend_endpoint_missing_ingredients(self, client):
        """Test recommend endpoint without ingredients."""
        response = client.post("/recommend-recipes", json={})
        
        assert response.status_code in [200, 422]  # May accept empty list
    
    @patch('api.main.get_recipe_engine')
    def test_recommend_endpoint_with_ingredients(self, mock_get_recipes, client):
        """Test recipe recommendation."""
        mock_recipe_engine = MagicMock()
        mock_recipe_engine.recommend_recipes.return_value = [
            {
                'name': 'Fruit Salad',
                'description': 'Fresh fruit',
                'ingredients': ['apple', 'banana'],
                'difficulty': 'easy',
                'prep_time_mins': 10,
                'servings': 2
            }
        ]
        mock_get_recipes.return_value = mock_recipe_engine
        
        payload = {'ingredients': ['apple', 'banana', 'orange']}
        response = client.post("/recommend-recipes", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert 'recipes' in data or isinstance(data, list)
    
    @patch('api.main.get_recipe_engine')
    def test_recommend_response_structure(self, mock_get_recipes, client):
        """Test recommendation response structure."""
        mock_recipe_engine = MagicMock()
        mock_recipe_engine.recommend_recipes.return_value = [
            {
                'name': 'Apple Pie',
                'description': 'Homemade',
                'ingredients': ['apple', 'flour', 'sugar'],
                'difficulty': 'medium',
                'prep_time_mins': 45,
                'servings': 4
            }
        ]
        mock_get_recipes.return_value = mock_recipe_engine
        
        payload = {'ingredients': ['apple']}
        response = client.post("/recommend-recipes", json=payload)
        
        data = response.json()
        # Should contain recipe data
        assert any('name' in str(item) for item in (data if isinstance(data, list) else [data]))


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in endpoints."""
    
    def test_invalid_image_format(self, client, temp_dir):
        """Test detecting with invalid image format."""
        # Create invalid file
        import os
        invalid_file = os.path.join(temp_dir, "test.txt")
        with open(invalid_file, 'w') as f:
            f.write("not an image")
        
        with open(invalid_file, 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            response = client.post("/detect-ingredients", files=files)
        
        # Should reject invalid format
        assert response.status_code in [400, 422]
    
    @patch('api.main.get_inference')
    def test_inference_error_handling(self, mock_get_inference, client, sample_image_file):
        """Test graceful error handling in inference."""
        mock_inference = MagicMock()
        mock_inference.detect_from_file.side_effect = Exception("Model error")
        mock_get_inference.return_value = mock_inference
        
        with open(sample_image_file, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = client.post("/detect-ingredients", files=files)
        
        # Should return 500 error
        assert response.status_code == 500
