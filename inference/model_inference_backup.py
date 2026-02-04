"""
Model inference module for running predictions on images.
"""

import logging
from typing import List, Dict, Optional
from model.model_loader import get_model_loader
from utils.image_utils import ImagePreprocessor, ResultPostprocessor

logger = logging.getLogger(__name__)


class FoodDetectionInference:
    """Run food detection inference on images."""
    
    def __init__(
        self,
        model_path: str = "yolov5s",
        class_names_path: Optional[str] = None,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45
    ):
        """
        Initialize inference engine.
        
        Args:
            model_path: Path to YOLO model or model name
            class_names_path: Path to file with class names
            conf_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
        """
        self.model_loader = get_model_loader(model_path=model_path)
        self.model_loader.set_confidence_threshold(conf_threshold)
        self.model_loader.set_iou_threshold(iou_threshold)
        
        self.class_names = self._load_class_names(class_names_path)
        self.preprocessor = ImagePreprocessor()
        self.postprocessor = ResultPostprocessor()
        self.conf_threshold = conf_threshold
        
        logger.info(f"Inference engine initialized with {len(self.class_names)} classes")
    
    def _load_class_names(self, class_names_path: Optional[str]) -> List[str]:
        """Load class names from file."""
        if class_names_path:
            try:
                with open(class_names_path, 'r') as f:
                    classes = [line.strip() for line in f if line.strip()]
                logger.info(f"Loaded {len(classes)} class names from {class_names_path}")
                return classes
            except Exception as e:
                logger.warning(f"Could not load class names: {e}")
        
        # Default COCO classes if file not provided
        return self._get_default_classes()
    
    def _get_default_classes(self) -> List[str]:
        """Return default food-related class names."""
        # Extended food and kitchen item classes
        return [
            "apple", "banana", "orange", "carrot", "broccoli",
            "potato", "tomato", "onion", "lettuce", "cucumber",
            "bell pepper", "garlic", "ginger", "lemon", "lime",
            "grapes", "strawberry", "blueberry", "watermelon", "pineapple",
            "mango", "avocado", "coconut", "kiwi", "papaya",
            "cheese", "milk", "butter", "eggs", "yogurt",
            "bread", "rice", "pasta", "flour", "sugar",
            "salt", "pepper", "oil", "vinegar", "sauce",
            "can", "bottle", "jar", "package", "container"
        ]
    
    def detect_from_file(self, image_path: str) -> Dict:
        """
        Detect ingredients from image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Detection results dictionary
        """
        logger.info(f"Running detection on {image_path}")
        
        # Load and preprocess image
        image = self.preprocessor.load_image(image_path)
        image_info = self.preprocessor.get_image_info(image)
        
        # Run inference
        predictions = self.model_loader.get_model()(image, size=640)
        
        # Postprocess results
        detections = self.postprocessor.process_detections(
            predictions,
            self.class_names,
            self.conf_threshold
        )
        
        # Merge overlapping detections
        detections = self.postprocessor.merge_overlapping_detections(detections)
        
        return {
            "image_info": image_info,
            "detections": detections,
            "num_detections": len(detections),
            "model_info": {
                "model_path": self.model_loader.model_path,
                "device": self.model_loader.device,
                "confidence_threshold": self.conf_threshold
            }
        }
    
    def detect_from_bytes(self, image_bytes: bytes) -> Dict:
        """
        Detect ingredients from image bytes.
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Detection results dictionary
        """
        logger.info("Running detection on image from bytes")
        
        # Load and preprocess image
        image = self.preprocessor.load_image_from_bytes(image_bytes)
        image_info = self.preprocessor.get_image_info(image)
        
        # Run inference
        predictions = self.model_loader.get_model()(image, size=640)
        
        # Postprocess results
        detections = self.postprocessor.process_detections(
            predictions,
            self.class_names,
            self.conf_threshold
        )
        
        # Merge overlapping detections
        detections = self.postprocessor.merge_overlapping_detections(detections)
        
        return {
            "image_info": image_info,
            "detections": detections,
            "num_detections": len(detections),
            "model_info": {
                "model_path": self.model_loader.model_path,
                "device": self.model_loader.device,
                "confidence_threshold": self.conf_threshold
            }
        }
    
    def get_ingredient_list(self, detections: List[Dict]) -> List[str]:
        """
        Extract unique ingredient names from detections.
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            List of unique ingredient names
        """
        ingredients = set()
        for det in detections:
            ingredients.add(det["class_name"])
        
        return sorted(list(ingredients))


# Global inference instance
_inference_instance = None


def get_inference_engine(
    model_path: str = "yolov5s",
    class_names_path: Optional[str] = None,
    conf_threshold: float = 0.5
) -> FoodDetectionInference:
    """Get or create singleton inference engine."""
    global _inference_instance
    
    if _inference_instance is None:
        _inference_instance = FoodDetectionInference(
            model_path=model_path,
            class_names_path=class_names_path,
            conf_threshold=conf_threshold
        )
    
    return _inference_instance
