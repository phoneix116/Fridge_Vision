"""
Food detection inference pipeline (Updated).
Uses local model file provided by user.
Integrates with frudrera's OCR pipeline patterns.
"""

import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from PIL import Image
import io

from model.model_loader import get_model_loader
from utils.image_utils import ImagePreprocessor, ResultPostprocessor

logger = logging.getLogger(__name__)


class FoodDetectionInference:
    """
    Food detection pipeline using local model.
    Supports YOLO (.pt) and TensorFlow (.h5) models.
    """
    
    # Default food categories
    DEFAULT_CLASSES = [
        'apple', 'banana', 'orange', 'carrot', 'broccoli', 'potato', 'tomato',
        'lettuce', 'cucumber', 'onion', 'garlic', 'cheese', 'milk', 'egg',
        'chicken', 'beef', 'salmon', 'bread', 'rice', 'pasta', 'yogurt',
        'apple_juice', 'orange_juice', 'coffee', 'tea', 'water', 'soda',
        'wine', 'beer', 'milk_bottle', 'butter', 'chocolate', 'candy',
        'cookie', 'pizza', 'burger', 'sandwich', 'salad', 'soup', 'rice_bowl',
        'noodles', 'steak', 'pork', 'bacon', 'ham', 'sausage', 'hot_dog'
    ]
    
    def __init__(self, model_path: Optional[str] = None, conf: float = 0.25, iou: float = 0.45):
        """
        Initialize detection pipeline.
        
        Args:
            model_path: Path to local model (.pt or .h5)
            conf: Confidence threshold
            iou: IOU threshold for NMS
        """
        self.preprocessor = ImagePreprocessor()
        self.postprocessor = ResultPostprocessor()
        self.conf = conf
        self.iou = iou
        self.model = None
        
        # Load model
        try:
            self.model_loader = get_model_loader()
            self.model = self.model_loader.load_model(model_path, conf=conf, iou=iou)
            logger.info("✅ Detection pipeline initialized with local model")
        except Exception as e:
            logger.error(f"❌ Failed to initialize detection: {e}")
            raise
    
    def detect_from_file(self, image_path: str) -> Dict:
        """
        Detect ingredients from image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with detections
        """
        image = self.preprocessor.load_image(image_path)
        return self._run_detection(image, original_size=image.shape[:2])
    
    def detect_from_bytes(self, image_bytes: bytes) -> Dict:
        """
        Detect ingredients from image bytes.
        
        Args:
            image_bytes: Image as bytes
            
        Returns:
            Dictionary with detections
        """
        image = self.preprocessor.load_image_from_bytes(image_bytes)
        return self._run_detection(image, original_size=image.shape[:2])
    
    def _run_detection(self, image: np.ndarray, original_size: Tuple[int, int]) -> Dict:
        """
        Run detection inference on image.
        
        Args:
            image: Input image (numpy array)
            original_size: Original image size (h, w)
            
        Returns:
            Detection results
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Check model_path configuration.")
        
        try:
            logger.info(f"Running inference on {original_size} image")
            results = self.model(image)
            
            # Parse results
            detections = self._parse_results(results)
            logger.info(f"Raw detections: {len(detections)}")
            
            # Postprocess (merge overlaps)
            processed = self.postprocessor.process_detections(detections)
            logger.info(f"After postprocessing: {len(processed)}")
            
            return {
                'detections': processed,
                'raw_detections': detections,
                'image_size': original_size,
                'count': len(processed)
            }
            
        except Exception as e:
            logger.error(f"❌ Detection failed: {e}")
            raise
    
    def _parse_results(self, results) -> List[Dict]:
        """
        Parse model results (YOLO or TensorFlow).
        
        Args:
            results: Raw model output
            
        Returns:
            List of detection dictionaries
        """
        detections = []
        
        try:
            # YOLO format
            if hasattr(results, 'xyxy'):
                # YOLOv5 Results object
                df = results.pandas().xyxy[0]
                for _, row in df.iterrows():
                    x1, y1, x2, y2 = row['xmin'], row['ymin'], row['xmax'], row['ymax']
                    conf = row['confidence']
                    cls_id = int(row['class'])
                    cls_name = row['name']
                    
                    detections.append({
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'confidence': float(conf),
                        'class_id': cls_id,
                        'class_name': cls_name,
                        'area': float((x2 - x1) * (y2 - y1))
                    })
            
            # Generic tensor output
            elif isinstance(results, np.ndarray):
                for det in results:
                    if len(det) >= 6:
                        x1, y1, x2, y2, conf, cls_id = det[:6]
                        cls_name = self.DEFAULT_CLASSES[int(cls_id) % len(self.DEFAULT_CLASSES)]
                        
                        detections.append({
                            'bbox': [float(x1), float(y1), float(x2), float(y2)],
                            'confidence': float(conf),
                            'class_id': int(cls_id),
                            'class_name': cls_name,
                            'area': float((x2 - x1) * (y2 - y1))
                        })
            
            logger.info(f"Parsed {len(detections)} detections from model output")
            
        except Exception as e:
            logger.warning(f"Result parsing issue: {e}")
        
        return detections
    
    def get_ingredient_list(self, detections: List[Dict]) -> List[str]:
        """
        Extract unique ingredient names.
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            List of unique ingredient names
        """
        ingredients = []
        seen = set()
        
        for detection in detections:
            name = detection['class_name']
            if name.lower() not in seen:
                ingredients.append(name)
                seen.add(name.lower())
        
        return ingredients
