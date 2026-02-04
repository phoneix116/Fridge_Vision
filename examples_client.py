"""
Example client for Fridge Vision API.
Demonstrates how to use the API from Python.

Usage:
    python examples/client_example.py
"""

import requests
import json
from pathlib import Path
from typing import List, Dict

# API endpoint
API_URL = "http://localhost:8000"


class FridgeVisionClient:
    """Client for Fridge Vision API."""
    
    def __init__(self, base_url: str = API_URL):
        """Initialize client."""
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """Check API health."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def detect_ingredients(
        self,
        image_path: str,
        enable_ocr: bool = True,
        confidence_threshold: float = 0.5
    ) -> Dict:
        """
        Detect ingredients in an image.
        
        Args:
            image_path: Path to image file
            enable_ocr: Enable OCR text extraction
            confidence_threshold: Minimum confidence
            
        Returns:
            Detection results
        """
        with open(image_path, 'rb') as f:
            files = {'image': f}
            params = {
                'enable_ocr': enable_ocr,
                'confidence_threshold': confidence_threshold
            }
            response = self.session.post(
                f"{self.base_url}/detect-ingredients",
                files=files,
                params=params
            )
            return response.json()
    
    def recommend_recipes(
        self,
        ingredients: List[str],
        top_k: int = 5,
        min_match: int = 1
    ) -> Dict:
        """
        Get recipe recommendations.
        
        Args:
            ingredients: List of ingredient names
            top_k: Number of recipes to return
            min_match: Minimum ingredients to match
            
        Returns:
            Recipe recommendations
        """
        params = {
            'ingredients': ingredients,
            'top_k': top_k,
            'min_match': min_match
        }
        response = self.session.post(
            f"{self.base_url}/recommend-recipes",
            params=params
        )
        return response.json()
    
    def list_recipes(self, limit: int = 20) -> Dict:
        """List all recipes."""
        params = {'limit': limit}
        response = self.session.get(
            f"{self.base_url}/recipes",
            params=params
        )
        return response.json()
    
    def search_recipes(self, query: str) -> Dict:
        """Search recipes."""
        params = {'query': query}
        response = self.session.get(
            f"{self.base_url}/recipes/search",
            params=params
        )
        return response.json()
    
    def get_recipe(self, recipe_id: int) -> Dict:
        """Get recipe details."""
        response = self.session.get(
            f"{self.base_url}/recipes/{recipe_id}"
        )
        return response.json()
    
    def get_info(self) -> Dict:
        """Get API info."""
        response = self.session.get(f"{self.base_url}/info")
        return response.json()


def example_workflow():
    """Example workflow: detect ingredients and get recipes."""
    
    # Initialize client
    client = FridgeVisionClient()
    
    # Check health
    print("Checking API health...")
    if not client.health_check():
        print("❌ API is not responding. Make sure the server is running.")
        return
    print("✅ API is healthy\n")
    
    # Get API info
    print("Fetching API info...")
    info = client.get_info()
    print(f"API: {info['api_name']} v{info['version']}")
    print(f"Total recipes: {info['database']['total_recipes']}")
    print(f"Available ingredients: {len(info['database']['available_ingredients'])}\n")
    
    # Example 1: Direct recipe recommendation (no image)
    print("=" * 50)
    print("Example 1: Recipe Recommendation")
    print("=" * 50)
    
    test_ingredients = ["tomato", "pasta", "garlic", "onion"]
    print(f"\nSearching recipes for: {test_ingredients}")
    
    recipes = client.recommend_recipes(
        ingredients=test_ingredients,
        top_k=3
    )
    
    print(f"\nFound {len(recipes['recipes'])} recipes:\n")
    for rec in recipes['recipes']:
        print(f"🍽️  {rec['name']} (Difficulty: {rec['difficulty']})")
        print(f"   Match: {rec['match_percentage']}%")
        print(f"   Matched: {', '.join(rec['matched_ingredients'])}")
        print(f"   Missing: {', '.join(rec['missing_ingredients'])}")
        print(f"   Prep time: {rec['prep_time_mins']} mins, Servings: {rec['servings']}")
        print()
    
    # Example 2: Search recipes
    print("=" * 50)
    print("Example 2: Recipe Search")
    print("=" * 50)
    
    search_results = client.search_recipes("salad")
    print(f"\nFound {search_results['count']} recipes matching 'salad':\n")
    for recipe in search_results['results'][:3]:
        print(f"- {recipe['name']}: {recipe['description']}")
    
    # Example 3: Get specific recipe
    print("\n" + "=" * 50)
    print("Example 3: Recipe Details")
    print("=" * 50)
    
    recipe = client.get_recipe(1)
    if recipe['status'] == 'success':
        r = recipe['recipe']
        print(f"\n📖 {r['name']}")
        print(f"   Description: {r['description']}")
        print(f"   Ingredients: {', '.join(r['ingredients'])}")
        print(f"   Prep time: {r['prep_time_mins']} mins")
        print(f"   Servings: {r['servings']}")
        print(f"   Difficulty: {r['difficulty']}")
    
    print("\n✅ Example workflow completed!")


def example_detection(image_path: str = None):
    """Example: Detect ingredients in an image."""
    
    if not image_path:
        print("Please provide an image path: example_detection('path/to/image.jpg')")
        return
    
    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        return
    
    # Initialize client
    client = FridgeVisionClient()
    
    # Check health
    if not client.health_check():
        print("❌ API is not responding")
        return
    
    print(f"Detecting ingredients in: {image_path}\n")
    
    # Detect ingredients
    results = client.detect_ingredients(image_path, enable_ocr=True)
    
    if results['status'] == 'success':
        print(f"✅ {results['message']}\n")
        
        print("Detected ingredients:")
        for ing in results['detected_ingredients']:
            print(f"  - {ing['class_name']}: {ing['quantity_estimate']} ({ing['estimated_unit']})")
            print(f"    Confidence: {ing['confidence']:.2%}, Count: {ing['count']}")
        
        # Get recipe recommendations
        ingredient_names = [ing['class_name'] for ing in results['detected_ingredients']]
        print(f"\nGetting recipe recommendations for {len(ingredient_names)} ingredients...")
        
        recipes = client.recommend_recipes(ingredient_names, top_k=3)
        print(f"\nTop recipes:\n")
        for rec in recipes['recipes']:
            print(f"🍽️  {rec['name']} ({rec['match_percentage']}% match)")
    else:
        print(f"❌ Error: {results['message']}")


if __name__ == "__main__":
    # Run example workflow
    print("\n" + "=" * 50)
    print("Fridge Vision API - Example Client")
    print("=" * 50 + "\n")
    
    example_workflow()
    
    # Uncomment to test image detection (provide your own image)
    # example_detection("path/to/fridge.jpg")
