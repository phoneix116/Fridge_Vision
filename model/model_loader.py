"""
Model loading module for food detection.
Loads local model file provided by user.
Supports Ultralytics YOLO (.pt) and TensorFlow (.h5) models.
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ModelLoader:
    """Singleton loader for local model files."""
    _instance = None
    _model = None
    _model_path = None
    _conf_threshold = 0.25
    _iou_threshold = 0.5
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_model(self, model_path: Optional[str] = None, conf: float = 0.25, iou: float = 0.5):
        """
        Load model from local file.
        
        Args:
            model_path: Path to model file (.pt for YOLO, .h5 for TensorFlow)
            conf: Confidence threshold
            iou: IOU threshold for NMS
            
        Returns:
            Loaded model
            
        Raises:
            FileNotFoundError: If model file not found
            ValueError: If unsupported model format
        """
        if model_path is None:
            # Try common locations and env variable
            common_paths = [
                os.getenv('MODEL_PATH'),
                'models/weight5_multi_yolov11L.pt',
                'models/best.pt',
                'models/weights4_fridge_vision_yolov8l.pt',
                'models/weights3_fridge_vision_yolov8l.pt',
                'models/model.pt',
                'model.pt',
            ]
            model_path = next((p for p in common_paths if p and os.path.exists(p)), None)
            
            if not model_path:
                raise FileNotFoundError(
                    "❌ Model file not found. Please:\n"
                    "1. Set MODEL_PATH environment variable, OR\n"
                    "2. Place model in models/ directory (weight5_multi_yolov11L.pt, best.pt, or model.pt)"
                )
        
        # Return cached model if same path
        if self._model is not None and self._model_path == model_path:
            return self._model
        
        model_path = str(model_path)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        logger.info(f"Loading model from: {model_path}")
        
        try:
            model_ext = Path(model_path).suffix.lower()
            self._conf_threshold = conf
            self._iou_threshold = iou
            
            if model_ext == '.pt':
                # Ultralytics YOLO model (YOLOv8/YOLOv11)
                from ultralytics import YOLO

                self._model = YOLO(model_path)
                if hasattr(self._model, 'overrides') and isinstance(self._model.overrides, dict):
                    self._model.overrides['conf'] = conf
                    self._model.overrides['iou'] = iou
                logger.info(f"✅ Ultralytics YOLO model loaded (conf={conf}, iou={iou})")
                
            elif model_ext == '.h5':
                # TensorFlow/Keras model
                try:
                    import tensorflow as tf
                    self._model = tf.keras.models.load_model(model_path)
                    logger.info("✅ TensorFlow model loaded")
                except ImportError:
                    raise ImportError("TensorFlow required for .h5 models")
                    
            else:
                raise ValueError(f"Unsupported model format: {model_ext}. Use .pt or .h5")
            
            self._model_path = model_path
            return self._model
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            self._model = None
            self._model_path = None
            raise
    
    def get_model(self, model_path: Optional[str] = None):
        """Get loaded model or load it if not already loaded."""
        if self._model is None:
            return self.load_model(model_path)
        if model_path is not None and str(model_path) != self._model_path:
            return self.load_model(model_path, conf=self._conf_threshold, iou=self._iou_threshold)
        return self._model

    @property
    def model_path(self) -> Optional[str]:
        """Return currently loaded model path."""
        return self._model_path

    @property
    def conf_threshold(self) -> float:
        """Return confidence threshold stored in loader."""
        return self._conf_threshold

    @property
    def iou_threshold(self) -> float:
        """Return IOU threshold stored in loader."""
        return self._iou_threshold

    @property
    def device(self) -> str:
        """Best-effort device info for compatibility with old callers."""
        if self._model is None:
            return "unknown"
        model_obj = getattr(self._model, 'model', None)
        if model_obj is not None and hasattr(model_obj, 'device'):
            return str(model_obj.device)
        return "cpu"

    def set_confidence_threshold(self, conf: float):
        """Set default confidence threshold for compatibility with old callers."""
        self._conf_threshold = conf
        if self._model is not None and hasattr(self._model, 'overrides') and isinstance(self._model.overrides, dict):
            self._model.overrides['conf'] = conf

    def set_iou_threshold(self, iou: float):
        """Set default IOU threshold for compatibility with old callers."""
        self._iou_threshold = iou
        if self._model is not None and hasattr(self._model, 'overrides') and isinstance(self._model.overrides, dict):
            self._model.overrides['iou'] = iou
    
    def clear_cache(self):
        """Clear cached model (use when switching models)."""
        self._model = None
        self._model_path = None
        logger.info("Model cache cleared")


def get_model_loader(
    model_path: Optional[str] = None,
    conf: float = 0.25,
    iou: float = 0.5,
) -> ModelLoader:
    """Get singleton ModelLoader instance, optionally preloading a model."""
    loader = ModelLoader()
    if model_path is not None and (loader.model_path != str(model_path) or loader._model is None):
        loader.load_model(model_path=model_path, conf=conf, iou=iou)
    return loader
