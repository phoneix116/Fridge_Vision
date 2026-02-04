"""
Quantity estimation for detected ingredients.
Uses simple heuristics based on bounding box size and position.
"""

import logging
from typing import List, Dict
import math

logger = logging.getLogger(__name__)


class QuantityEstimator:
    """Estimate ingredient quantities based on detection metadata."""
    
    # Mapping of visual size to approximate quantity
    SIZE_TO_QUANTITY = {
        "very_small": ("pinch", 0.1),  # Very small item
        "small": ("small portion", 0.25),
        "medium": ("medium portion", 0.5),
        "large": ("large portion", 0.75),
        "very_large": ("whole/bulk", 1.0)
    }
    
    def __init__(self, image_width: int = 640, image_height: int = 480):
        """
        Initialize quantity estimator.
        
        Args:
            image_width: Width of image in pixels
            image_height: Height of image in pixels
        """
        self.image_width = image_width
        self.image_height = image_height
        self.image_area = image_width * image_height
    
    def estimate_quantity(
        self,
        detection: Dict,
        count: int = 1
    ) -> Dict:
        """
        Estimate quantity for a single detection.
        
        Args:
            detection: Detection dictionary from model
            count: Number of times this ingredient appears
            
        Returns:
            Dictionary with quantity estimate
        """
        bbox = detection["bbox"]
        width = bbox["x2"] - bbox["x1"]
        height = bbox["y2"] - bbox["y1"]
        bbox_area = width * height
        
        # Calculate size relative to image
        size_ratio = bbox_area / self.image_area
        
        # Classify size
        size_category = self._classify_size(size_ratio)
        quantity_label, quantity_value = self.SIZE_TO_QUANTITY[size_category]
        
        # Adjust based on count
        adjusted_quantity = quantity_value * count
        
        return {
            "ingredient": detection["class_name"],
            "confidence": detection["confidence"],
            "count": count,
            "size_category": size_category,
            "quantity_estimate": quantity_label,
            "quantity_value": adjusted_quantity,
            "estimated_unit": self._get_unit(detection["class_name"]),
            "size_ratio": size_ratio
        }
    
    def _classify_size(self, size_ratio: float) -> str:
        """Classify detection size based on area ratio."""
        if size_ratio < 0.02:
            return "very_small"
        elif size_ratio < 0.08:
            return "small"
        elif size_ratio < 0.20:
            return "medium"
        elif size_ratio < 0.40:
            return "large"
        else:
            return "very_large"
    
    def _get_unit(self, ingredient_name: str) -> str:
        """
        Suggest appropriate unit for ingredient.
        
        Args:
            ingredient_name: Name of ingredient
            
        Returns:
            Suggested unit (pcs, g, ml, etc.)
        """
        ingredient = ingredient_name.lower()
        
        # Liquids
        if any(word in ingredient for word in ['milk', 'oil', 'sauce', 'yogurt', 'juice']):
            return "ml"
        
        # Powders/dry goods
        if any(word in ingredient for word in ['flour', 'sugar', 'salt', 'pepper', 'rice']):
            return "g"
        
        # Individual items
        if any(word in ingredient for word in ['apple', 'banana', 'egg', 'tomato', 'onion', 'orange', 'lemon', 'garlic']):
            return "pcs"
        
        # Bulk items
        if any(word in ingredient for word in ['bread', 'pasta', 'butter', 'cheese']):
            return "g"
        
        # Default
        return "portion"
    
    def estimate_quantities_batch(
        self,
        detections: List[Dict],
        image_width: int = None,
        image_height: int = None
    ) -> Dict:
        """
        Estimate quantities for multiple detections.
        
        Args:
            detections: List of detection dictionaries
            image_width: Width of image
            image_height: Height of image
            
        Returns:
            Dictionary with quantity estimates for each ingredient
        """
        if image_width:
            self.image_width = image_width
        if image_height:
            self.image_height = image_height
        
        self.image_area = self.image_width * self.image_height
        
        # Count occurrences of each ingredient
        ingredient_counts = {}
        ingredient_detections = {}
        
        for det in detections:
            ingredient = det["class_name"]
            if ingredient not in ingredient_counts:
                ingredient_counts[ingredient] = 0
                ingredient_detections[ingredient] = det
            ingredient_counts[ingredient] += 1
        
        # Generate quantity estimates
        quantity_estimates = {}
        
        for ingredient, count in ingredient_counts.items():
            det = ingredient_detections[ingredient]
            quantity_estimates[ingredient] = self.estimate_quantity(det, count=count)
        
        logger.info(f"Estimated quantities for {len(quantity_estimates)} ingredients")
        
        return {
            "ingredients_by_quantity": quantity_estimates,
            "total_unique_ingredients": len(quantity_estimates),
            "total_items_detected": len(detections),
            "image_dimensions": {
                "width": self.image_width,
                "height": self.image_height
            }
        }


def merge_ingredients_with_quantities(
    detections: List[Dict],
    quantities: Dict,
    ocr_results: Dict = None
) -> List[Dict]:
    """
    Merge detection data with quantity estimates and OCR results.
    
    Args:
        detections: List of detections from model
        quantities: Quantity estimates from estimator
        ocr_results: Optional OCR results
        
    Returns:
        Merged ingredient list with all information
    """
    merged_ingredients = []
    
    for ingredient_name, quantity_info in quantities.get("ingredients_by_quantity", {}).items():
        merged = {
            **quantity_info,
            "confidence": quantity_info["confidence"],
            "source": "detection",
            "additional_info": {}
        }
        
        # Add OCR info if available
        if ocr_results and ocr_results.get("status") == "success":
            # Check if ingredient name appears in OCR text
            if ingredient_name.lower() in ocr_results.get("full_text", "").lower():
                merged["source"] = "detection + ocr"
                merged["additional_info"]["found_in_text"] = True
        
        merged_ingredients.append(merged)
    
    # Sort by confidence descending
    merged_ingredients.sort(
        key=lambda x: x.get("confidence", 0),
        reverse=True
    )
    
    logger.info(f"Merged {len(merged_ingredients)} ingredients with metadata")
    
    return merged_ingredients
