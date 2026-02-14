"""
Food detection inference pipeline (Updated for YOLOv8l).
Uses local YOLOv8 model (.pt) with explicit preprocessing.
Supports single and batch inference.
"""

import logging
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional, Union

from ultralytics import YOLO

logger = logging.getLogger(__name__)


class FoodDetectionInference:
    """
    Food detection pipeline using YOLOv8 model (YOLOv8m/YOLOv8l).
    Matches Roboflow preprocessing: Auto-orient, Resize to 640x640.
    """
    
    # Fridge-specific food classes (30 classes from training)
    DEFAULT_CLASSES = [
        'apple', 'banana', 'blueberry', 'bread', 'brinjal', 'butter', 'cabbage',
        'capsicum', 'carrot', 'cheese', 'chicken', 'chocolate', 'corn', 'cucumber',
        'egg', 'flour', 'fresh cream', 'ginger', 'green beans', 'green chilly',
        'green leaves', 'lemon', 'meat', 'milk', 'mushroom', 'potato', 'shrimp',
        'strawberry', 'sweet potato', 'tomato'
    ]
    
    # Preprocessing constants (matches Roboflow training)
    IMG_SIZE = 640
    CONF_THRESHOLD = 0.25
    IOU_THRESHOLD = 0.7
    
    def __init__(self, model_path: Optional[str] = None, conf: float = 0.25, iou: float = 0.7):
        """
        Initialize detection pipeline with YOLOv8 model.
        
        Args:
            model_path: Path to .pt model file (e.g., models/weights3_fridge_vision_yolov8l.pt)
            conf: Confidence threshold (default 0.25)
            iou: IOU threshold for NMS (default 0.7, matches training)
        """
        self.conf = conf
        self.iou = iou
        self.model = None
        
        # Load YOLOv8 model directly from ultralytics
        try:
            if model_path is None:
                model_path = "models/weights3_fridge_vision_yolov8l.pt"
            
            self.model = YOLO(model_path)
            logger.info(f"✅ Detection pipeline initialized with YOLOv8 model: {model_path}")
            logger.info(f"   Inference size: {self.IMG_SIZE}x{self.IMG_SIZE}")
            logger.info(f"   Confidence threshold: {self.conf}")
            logger.info(f"   IOU threshold: {self.iou}")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image matching Roboflow training:
        1. Auto-orient (handled by cv2.imread automatically)
        2. Resize: Stretch to 640x640
        
        Args:
            image: Input image (numpy array in BGR format)
            
        Returns:
            Preprocessed image (640x640)
        """
        # Resize to 640x640 (match training size)
        resized = cv2.resize(image, (self.IMG_SIZE, self.IMG_SIZE))
        return resized
    
    def detect_from_file(self, image_path: str) -> Dict:
        """
        Detect ingredients from image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with detections
        """
        # Read image (auto-orient via cv2.imread)
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Store original size before preprocessing
        original_h, original_w = image.shape[:2]
        
        # Preprocess
        processed = self.preprocess(image)
        
        return self._run_detection(processed, original_size=(original_h, original_w))
    
    def detect_from_bytes(self, image_bytes: bytes) -> Dict:
        """
        Detect ingredients from image bytes.
        
        Args:
            image_bytes: Image as bytes
            
        Returns:
            Dictionary with detections
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Failed to decode image from bytes")
        
        # Store original size before preprocessing
        original_h, original_w = image.shape[:2]
        
        # Preprocess
        processed = self.preprocess(image)
        
        return self._run_detection(processed, original_size=(original_h, original_w))
    
    def detect_batch(self, image_paths: List[str]) -> List[Dict]:
        """
        Batch detection for multiple images (optimized for GPU).
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of detection results
        """
        results = []
        
        try:
            for image_path in image_paths:
                result = self.detect_from_file(image_path)
                results.append(result)
                logger.info(f"Processed {image_path}: {result['count']} detections")
        except Exception as e:
            logger.error(f"❌ Batch detection failed: {e}")
            raise
        
        return results
    
    def _run_detection(self, image: np.ndarray, original_size: Tuple[int, int]) -> Dict:
        """
        Run detection inference on preprocessed image.
        
        Args:
            image: Preprocessed image (640x640)
            original_size: Original image size (h, w)
            
        Returns:
            Detection results dictionary
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Check model_path configuration.")
        
        try:
            logger.info(f"Running YOLOv8 inference on {self.IMG_SIZE}x{self.IMG_SIZE} image")
            
            # Run inference
            results = self.model(
                image,
                conf=self.conf,
                iou=self.iou,
                imgsz=self.IMG_SIZE,
                verbose=False
            )
            
            # Parse results (YOLOv8 format)
            detections = self._parse_results(results[0])
            logger.info(f"Detections found: {len(detections)}")
            
            return {
                'detections': detections,
                'raw_detections': detections,
                'image_size': original_size,
                'inference_size': (self.IMG_SIZE, self.IMG_SIZE),
                'count': len(detections)
            }
            
        except Exception as e:
            logger.error(f"❌ Detection failed: {e}")
            raise
    
    def _parse_results(self, results) -> List[Dict]:
        """
        Parse YOLOv8l Results object.
        
        Args:
            results: YOLOv8 Results object (from model.predict)
            
        Returns:
            List of detection dictionaries
        """
        detections = []
        
        try:
            # YOLOv8 format: results.boxes contains detection info
            if hasattr(results, 'boxes') and results.boxes is not None:
                boxes = results.boxes
                
                for i, box in enumerate(boxes):
                    # Extract coordinates (xyxy format: x1, y1, x2, y2)
                    xyxy = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = xyxy.tolist()
                    
                    # Extract confidence
                    conf = float(box.conf[0])
                    
                    # Extract class
                    cls_id = int(box.cls[0])
                    cls_name = results.names[cls_id] if hasattr(results, 'names') else \
                               self.DEFAULT_CLASSES[cls_id % len(self.DEFAULT_CLASSES)]
                    
                    detections.append({
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'confidence': conf,
                        'class_id': cls_id,
                        'class_name': cls_name,
                        'area': float((x2 - x1) * (y2 - y1))
                    })
                
                logger.info(f"Parsed {len(detections)} detections from YOLOv8 results")
            
            else:
                logger.warning("No boxes found in YOLOv8 results")
            
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
