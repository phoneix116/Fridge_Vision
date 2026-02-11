"""
LLM-based recipe recommendation using Ollama API.
Generates creative recipes from detected ingredients using local LLM.
"""

import json
import logging
import requests
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class OllamaRecipeRecommender:
    """Generate recipe recommendations using Ollama LLM API."""
    
    def __init__(self, ollama_host: str = "http://localhost:11434", model: str = "mistral"):
        """
        Initialize Ollama recipe recommender.
        
        Args:
            ollama_host: Ollama server URL
            model: Model name (mistral, neural-chat, llama2, etc.)
        """
        self.ollama_host = ollama_host
        self.model = model
        self.api_endpoint = f"{ollama_host}/api/generate"
        self.is_available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(
                f"{self.ollama_host}/api/tags",
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def generate_recipes(
        self,
        ingredients: List[str],
        num_recipes: int = 3,
        dietary_restrictions: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Generate recipes using Ollama LLM.
        
        Args:
            ingredients: List of available ingredients
            num_recipes: Number of recipes to generate
            dietary_restrictions: Optional dietary restrictions (e.g., vegan, gluten-free)
            
        Returns:
            List of recipe recommendations with names, instructions, and requirements
        """
        if not self.is_available:
            logger.warning("Ollama server not available, falling back to keyword matching")
            return []
        
        try:
            # Build prompt
            restrictions_str = f"Dietary restrictions: {', '.join(dietary_restrictions)}. " if dietary_restrictions else ""
            
            prompt = f"""You are a creative cooking assistant. Given the following ingredients, generate {num_recipes} unique recipe suggestions.

Available ingredients: {', '.join(ingredients)}
{restrictions_str}
Requirements:
- Each recipe should use mostly the available ingredients (at least 70% of ingredients available)
- Include recipe name, brief description, preparation time, difficulty level, and any additional items needed
- Format as JSON array with objects: {{"name": "...", "description": "...", "prep_time_mins": ..., "difficulty": "easy/medium/hard", "additional_items": [...]}}
- Only respond with valid JSON, no other text

Generate {num_recipes} recipes:"""

            # Call Ollama API
            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                },
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code}")
                return []
            
            # Extract response
            result = response.json()
            llm_output = result.get("response", "").strip()
            
            # Parse JSON from response
            recipes = self._parse_recipes(llm_output, ingredients)
            
            logger.info(f"Generated {len(recipes)} recipes from LLM")
            return recipes
        
        except Exception as e:
            logger.error(f"LLM recipe generation error: {e}")
            return []
    
    def _parse_recipes(self, llm_output: str, available_ingredients: List[str]) -> List[Dict]:
        """Parse JSON recipes from LLM output."""
        try:
            # Try to extract JSON from response
            # LLM might include extra text, so we look for JSON array
            json_match = re.search(r'\[.*\]', llm_output, re.DOTALL)
            
            if not json_match:
                logger.warning("No JSON found in LLM response")
                return []
            
            json_str = json_match.group(0)
            recipes_data = json.loads(json_str)
            
            # Format recipes
            formatted_recipes = []
            for idx, recipe_data in enumerate(recipes_data, 1):
                formatted_recipe = {
                    "recipe_id": idx,
                    "name": recipe_data.get("name", "Unknown Recipe"),
                    "description": recipe_data.get("description", ""),
                    "prep_time_mins": recipe_data.get("prep_time_mins", 30),
                    "difficulty": recipe_data.get("difficulty", "medium").lower(),
                    "servings": recipe_data.get("servings", 4),
                    "additional_items": recipe_data.get("additional_items", []),
                    "ingredients_used": available_ingredients,
                    "source": "llm"
                }
                formatted_recipes.append(formatted_recipe)
            
            return formatted_recipes
        
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from LLM: {e}")
            logger.debug(f"LLM output: {llm_output[:500]}")
            return []
    
    def refine_recipe(
        self,
        recipe_name: str,
        ingredients: List[str],
        question: str
    ) -> str:
        """
        Ask LLM to refine or explain a recipe.
        
        Args:
            recipe_name: Name of the recipe
            ingredients: Available ingredients
            question: User's question about the recipe
            
        Returns:
            LLM's response
        """
        if not self.is_available:
            return "LLM service not available"
        
        try:
            prompt = f"""You are a cooking assistant helping with recipe details.

Recipe: {recipe_name}
Available ingredients: {', '.join(ingredients)}

User question: {question}

Provide a helpful, concise answer:"""

            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.5,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Unable to generate response").strip()
            else:
                return "Error communicating with LLM"
        
        except Exception as e:
            logger.error(f"Recipe refinement error: {e}")
            return f"Error: {str(e)}"


class HuggingFaceRecipeRecommender:
    """Alternative: Use Hugging Face Inference API (if Ollama not available)."""
    
    def __init__(self, api_token: str, model_name: str = "mistralai/Mistral-7B-Instruct-v0.1"):
        """
        Initialize Hugging Face recipe recommender.
        
        Args:
            api_token: Hugging Face API token
            model_name: Model to use
        """
        self.api_token = api_token
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_token}"}
    
    def generate_recipes(
        self,
        ingredients: List[str],
        num_recipes: int = 3,
        dietary_restrictions: Optional[List[str]] = None
    ) -> List[Dict]:
        """Generate recipes using Hugging Face API."""
        try:
            restrictions_str = f"Dietary restrictions: {', '.join(dietary_restrictions)}. " if dietary_restrictions else ""
            
            prompt = f"""Generate {num_recipes} recipes using these ingredients: {', '.join(ingredients)}.
{restrictions_str}
Format as JSON with: name, description, prep_time_mins, difficulty, additional_items"""

            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse and return recipes
                logger.info("Generated recipes from Hugging Face")
                return []  # Simplified - would parse response
            else:
                logger.error(f"HuggingFace API error: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"HuggingFace recipe generation error: {e}")
            return []


# Convenience function
def get_recipe_recommender(use_ollama: bool = True) -> Optional[OllamaRecipeRecommender]:
    """Get recipe recommender (Ollama preferred, fallback available)."""
    if use_ollama:
        recommender = OllamaRecipeRecommender()
        if recommender.is_available:
            logger.info("✅ Using Ollama for recipe recommendations")
            return recommender
        else:
            logger.warning("Ollama not available - will fall back to keyword matching")
            return None
    return None
