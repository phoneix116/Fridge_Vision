"""
Model loading module for food detection.
Loads local model file provided by user.
Supports YOLO (.pt) and TensorFlow (.h5) models.
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
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_model(self, model_path: Optional[str] = None, conf: float = 0.25, iou: float = 0.45):
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
                'models/model.pt',
                'models/best.pt',
                'model.pt',
            ]
            model_path = next((p for p in common_paths if p and os.path.exists(p)), None)
            
            if not model_path:
                raise FileNotFoundError(
                    "❌ Model file not found. Please:\n"
                    "1. Set MODEL_PATH environment variable, OR\n"
                    "2. Place model in models/ directory (model.pt or best.pt)"
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
            
            if model_ext == '.pt':
                # PyTorch/YOLO model
                import torch
                self._model = torch.hub.load(
                    'ultralytics/yolov5',
                    'custom',
                    path=model_path,
                    force_reload=False
                )
                if hasattr(self._model, 'conf'):
                    self._model.conf = conf
                    self._model.iou = iou
                logger.info(f"✅ YOLO model loaded (conf={conf}, iou={iou})")
                
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
        return self._model
    
    def clear_cache(self):
        """Clear cached model (use when switching models)."""
        self._model = None
        self._model_path = None
        logger.info("Model cache cleared")


def get_model_loader() -> ModelLoader:
    """Get singleton ModelLoader instance."""
    return ModelLoader()
