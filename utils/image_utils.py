"""
Image preprocessing and postprocessing utilities.
Handles image loading, resizing, and results conversion.
"""

import cv2
import numpy as np
import logging
from pathlib import Path
from typing import Tuple, List, Dict, Optional

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Handle image preprocessing for model inference."""
    
    MAX_SIZE = 640  # Standard YOLO input size
    
    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        """
        Load image from file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image as numpy array in BGR format
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        logger.info(f"Loaded image from {image_path}, shape: {image.shape}")
        return image
    
    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
        """
        Load image from bytes.
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Image as numpy array in BGR format
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Failed to decode image from bytes")
        
        logger.info(f"Loaded image from bytes, shape: {image.shape}")
        return image
    
    @staticmethod
    def resize_image(image: np.ndarray, max_size: int = MAX_SIZE) -> np.ndarray:
        """
        Resize image while maintaining aspect ratio.
        
        Args:
            image: Input image
            max_size: Maximum size for longest dimension
            
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        scale = min(max_size / max(height, width), 1.0)
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        logger.info(f"Resized image from {image.shape} to {resized.shape}")
        
        return resized
    
    @staticmethod
    def get_image_info(image: np.ndarray) -> Dict:
        """Get basic image information."""
        height, width = image.shape[:2]
        return {
            "width": width,
            "height": height,
            "channels": image.shape[2] if len(image.shape) > 2 else 1,
            "size_mb": (image.nbytes / (1024 * 1024))
        }


class ResultPostprocessor:
    """Convert model predictions to clean output format."""
    
    @staticmethod
    def process_detections(
        predictions,
        class_names: List[str],
        conf_threshold: float = 0.5
    ) -> List[Dict]:
        """
        Convert YOLO predictions to structured format.
        
        Args:
            predictions: YOLOv5 predictions object
            class_names: List of class names
            conf_threshold: Confidence threshold for filtering
            
        Returns:
            List of detection dictionaries
        """
        detections = []
        
        # Extract predictions
        xyxy = predictions.xyxy[0].cpu().numpy()  # Bounding boxes
        confs = predictions.conf[0].cpu().numpy()  # Confidences
        classes = predictions.cls[0].cpu().numpy().astype(int)  # Class indices
        
        for bbox, conf, cls_idx in zip(xyxy, confs, classes):
            if conf >= conf_threshold:
                x1, y1, x2, y2 = bbox
                
                detection = {
                    "class_id": int(cls_idx),
                    "class_name": class_names[cls_idx] if cls_idx < len(class_names) else "unknown",
                    "confidence": float(conf),
                    "bbox": {
                        "x1": float(x1),
                        "y1": float(y1),
                        "x2": float(x2),
                        "y2": float(y2)
                    },
                    "center": {
                        "x": float((x1 + x2) / 2),
                        "y": float((y1 + y2) / 2)
                    },
                    "width": float(x2 - x1),
                    "height": float(y2 - y1)
                }
                detections.append(detection)
        
        logger.info(f"Processed {len(detections)} detections")
        return detections
    
    @staticmethod
    def merge_overlapping_detections(
        detections: List[Dict],
        iou_threshold: float = 0.5
    ) -> List[Dict]:
        """
        Merge nearby detections of the same class using IoU.
        
        Args:
            detections: List of detection dictionaries
            iou_threshold: IoU threshold for merging
            
        Returns:
            Merged detections
        """
        if not detections:
            return detections
        
        # Sort by confidence (descending)
        sorted_dets = sorted(detections, key=lambda x: x["confidence"], reverse=True)
        merged = []
        used = set()
        
        for i, det in enumerate(sorted_dets):
            if i in used:
                continue
            
            current_class = det["class_name"]
            bbox1 = det["bbox"]
            
            for j, other in enumerate(sorted_dets[i+1:], start=i+1):
                if j in used:
                    continue
                
                # Only merge same class
                if other["class_name"] != current_class:
                    continue
                
                bbox2 = other["bbox"]
                iou = ResultPostprocessor._calculate_iou(bbox1, bbox2)
                
                if iou >= iou_threshold:
                    used.add(j)
            
            merged.append(det)
        
        logger.info(f"Merged overlapping detections: {len(detections)} -> {len(merged)}")
        return merged
    
    @staticmethod
    def _calculate_iou(bbox1: Dict, bbox2: Dict) -> float:
        """Calculate Intersection over Union of two bboxes."""
        x1_min, y1_min = bbox1["x1"], bbox1["y1"]
        x1_max, y1_max = bbox1["x2"], bbox1["y2"]
        
        x2_min, y2_min = bbox2["x1"], bbox2["y1"]
        x2_max, y2_max = bbox2["x2"], bbox2["y2"]
        
        # Intersection area
        xi_min = max(x1_min, x2_min)
        yi_min = max(y1_min, y2_min)
        xi_max = min(x1_max, x2_max)
        yi_max = min(y1_max, y2_max)
        
        if xi_max < xi_min or yi_max < yi_min:
            return 0.0
        
        intersection = (xi_max - xi_min) * (yi_max - yi_min)
        
        # Union area
        area1 = (x1_max - x1_min) * (y1_max - y1_min)
        area2 = (x2_max - x2_min) * (y2_max - y2_min)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
