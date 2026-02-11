"""
Convert recipes CSV to JSON with intelligent ingredient normalization.
Uses semantic similarity to normalize ingredient names and improve recipe matching.
"""

import json
import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Set
from difflib import SequenceMatcher

# YOLO food classes from the trained model
YOLO_CLASSES = {
    'apple', 'banana', 'blueberry', 'bread', 'brinjal', 'butter', 'cabbage',
    'capsicum', 'carrot', 'cheese', 'chicken', 'chocolate', 'corn', 'cucumber',
    'egg', 'flour', 'fresh cream', 'ginger', 'green beans', 'green chilly',
    'green leaves', 'lemon', 'meat', 'milk', 'mushroom', 'potato', 'shrimp',
    'strawberry', 'sweet potato', 'tomato'
}

# Ingredient synonym mappings for better matching
INGREDIENT_SYNONYMS = {
    'tomato': ['tomatoes', 'cherry tomato', 'roma tomato', 'beefsteak tomato'],
    'carrot': ['carrots', 'grated carrot'],
    'potato': ['potatoes', 'mashed potato'],
    'onion': ['onions', 'red onion', 'yellow onion', 'white onion'],
    'garlic': ['garlic cloves', 'minced garlic', 'garlic powder'],
    'egg': ['eggs', 'egg yolk', 'egg white'],
    'milk': ['whole milk', 'skim milk', 'evaporated milk'],
    'cheese': ['cheddar', 'mozzarella', 'parmesan', 'cream cheese', 'feta'],
    'chicken': ['chicken breast', 'chicken thigh', 'ground chicken'],
    'meat': ['beef', 'pork', 'lamb', 'ground meat'],
    'bread': ['white bread', 'wheat bread', 'whole grain bread'],
    'butter': ['unsalted butter', 'salted butter'],
    'flour': ['all-purpose flour', 'wheat flour', 'rice flour'],
    'green beans': ['string beans', 'snap beans'],
    'cucumber': ['cucumbers', 'english cucumber'],
    'mushroom': ['mushrooms', 'button mushroom', 'cremini'],
    'lemon': ['lemons', 'lemon juice', 'lemon zest'],
    'corn': ['sweet corn', 'corn kernels'],
    'fresh cream': ['heavy cream', 'whipped cream', 'sour cream'],
}


def normalize_ingredient(ingredient: str) -> str:
    """
    Normalize ingredient name by:
    1. Removing quantities and units
    2. Converting to lowercase
    3. Finding semantic matches with YOLO classes
    """
    # Remove quantities (e.g., "2 cups", "1 tbsp")
    normalized = re.sub(r'^\d+\s*(?:\d+/\d+)?\s*(?:cup|tbsp|tsp|ml|l|oz|lb|g|kg|x)?s?\.?\s*', '', ingredient.strip(), flags=re.IGNORECASE)
    normalized = normalized.lower().strip()
    
    # Remove common words
    remove_words = ['of', 'the', 'a', 'and', 'or', 'finely', 'chopped', 'diced', 'sliced', 
                    'grated', 'minced', 'whole', 'fresh', 'dried', 'ground', 'powder']
    words = normalized.split()
    words = [w for w in words if w not in remove_words and len(w) > 1]
    normalized = ' '.join(words).strip()
    
    # Try exact match first
    if normalized in YOLO_CLASSES:
        return normalized
    
    # Try synonym matching
    for yolo_class, synonyms in INGREDIENT_SYNONYMS.items():
        if normalized in synonyms or any(normalized in syn for syn in synonyms):
            return yolo_class
    
    # Try fuzzy matching
    for yolo_class in YOLO_CLASSES:
        ratio = SequenceMatcher(None, normalized, yolo_class).ratio()
        if ratio > 0.7:  # 70% similarity threshold
            return yolo_class
    
    return normalized


def extract_and_normalize_ingredients(ingredients_str: str) -> List[str]:
    """Extract and normalize ingredients from CSV string."""
    if not ingredients_str or str(ingredients_str).lower() == 'nan':
        return []
    
    # Split by comma
    ingredients = [ing.strip() for ing in str(ingredients_str).split(',')]
    
    # Normalize each ingredient
    normalized = []
    for ing in ingredients:
        norm = normalize_ingredient(ing)
        if norm and len(norm) > 1 and norm not in normalized:  # Avoid duplicates
            normalized.append(norm)
    
    return normalized


def convert_recipes_csv_to_json(csv_path: str, output_path: str, num_recipes: int = 10000):
    """Convert recipes CSV to JSON format."""
    
    print(f"📖 Reading CSV from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Total recipes in CSV: {len(df)}")
    
    # Take subset
    df_subset = df.head(num_recipes)
    print(f"Processing {len(df_subset)} recipes...")
    
    recipes_list = []
    valid_count = 0
    
    for idx, row in df_subset.iterrows():
        try:
            # Extract and normalize ingredients
            ingredients = extract_and_normalize_ingredients(row.get('ingredients', ''))
            
            if ingredients:  # Only include recipes with ingredients
                recipe = {
                    "recipe_id": idx,
                    "name": str(row['title']).strip(),
                    "ingredients": ingredients,
                    "url": str(row['url']).strip() if 'url' in row else "",
                    "difficulty": "medium",
                    "prep_time_mins": 30,
                    "servings": 4,
                    "description": f"Recipe with {len(ingredients)} ingredients"
                }
                recipes_list.append(recipe)
                valid_count += 1
                
                if (idx + 1) % 1000 == 0:
                    print(f"  ✓ Processed {idx + 1} recipes ({valid_count} valid)")
        
        except Exception as e:
            continue
    
    print(f"\n✅ Converted {valid_count} recipes with valid ingredients")
    
    # Save to JSON
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(recipes_list, f, indent=2)
    
    print(f"💾 Saved to {output_path}")
    print(f"\n📊 Sample recipe:")
    print(json.dumps(recipes_list[0], indent=2))
    
    # Stats
    all_ingredients = set()
    for recipe in recipes_list:
        all_ingredients.update(recipe['ingredients'])
    
    print(f"\n📈 Stats:")
    print(f"  - Total recipes: {len(recipes_list)}")
    print(f"  - Unique ingredients: {len(all_ingredients)}")
    print(f"  - Avg ingredients per recipe: {sum(len(r['ingredients']) for r in recipes_list) / len(recipes_list):.1f}")
    
    return recipes_list


if __name__ == "__main__":
    # Paths
    csv_path = Path(__file__).parent.parent / "Recipe" / "recipes_1M_shortened.csv"
    output_path = Path(__file__).parent.parent / "data" / "recipes.json"
    
    # Convert
    convert_recipes_csv_to_json(str(csv_path), str(output_path), num_recipes=10000)
