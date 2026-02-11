"""
Configuration module for Fridge Vision API.
Centralized settings management.
"""

import os
from pathlib import Path
from typing import Optional

# Project root
PROJECT_ROOT = Path(__file__).parent

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
CLASSES_FILE = DATA_DIR / "classes.txt"
RECIPES_FILE = DATA_DIR / "recipes.json"

# Model configuration
MODEL_PATH = os.getenv("MODEL_PATH", str(PROJECT_ROOT / "models" / "weights2_fridge_vision.pt"))
MODEL_CONFIG = {
    "model_path": MODEL_PATH,
    "conf_threshold": float(os.getenv("CONF_THRESHOLD", "0.5")),
    "iou_threshold": float(os.getenv("IOU_THRESHOLD", "0.45")),
}

# OCR configuration
OCR_CONFIG = {
    "languages": os.getenv("OCR_LANGUAGES", "en").split(","),
    "use_gpu": os.getenv("OCR_USE_GPU", "false").lower() == "true",
    "confidence_threshold": float(os.getenv("OCR_CONF_THRESHOLD", "0.3")),
}

# API configuration
API_CONFIG = {
    "host": os.getenv("API_HOST", "0.0.0.0"),
    "port": int(os.getenv("API_PORT", "8000")),
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "reload": os.getenv("RELOAD", "false").lower() == "true",
    "workers": int(os.getenv("WORKERS", "1")),
}

# Recipe configuration
RECIPE_CONFIG = {
    "recipes_file": RECIPES_FILE,
    "default_top_k": int(os.getenv("DEFAULT_TOP_K", "5")),
    "min_match": int(os.getenv("MIN_MATCH", "1")),
}

# Image processing
IMAGE_CONFIG = {
    "max_size": int(os.getenv("IMAGE_MAX_SIZE", "640")),
    "allowed_formats": ["jpg", "jpeg", "png", "bmp", "gif"],
    "max_file_size_mb": int(os.getenv("MAX_FILE_SIZE_MB", "50")),
}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Feature flags
FEATURES = {
    "enable_ocr": os.getenv("ENABLE_OCR", "true").lower() == "true",
    "enable_quantity_estimation": os.getenv("ENABLE_QUANTITY_ESTIMATION", "true").lower() == "true",
    "enable_recipe_recommendations": os.getenv("ENABLE_RECIPE_RECOMMENDATIONS", "true").lower() == "true",
}


def get_config():
    """Get full configuration dictionary."""
    return {
        "model": MODEL_CONFIG,
        "ocr": OCR_CONFIG,
        "api": API_CONFIG,
        "recipe": RECIPE_CONFIG,
        "image": IMAGE_CONFIG,
        "features": FEATURES,
        "log_level": LOG_LEVEL,
    }


class Settings:
    """Settings class for easy access to config in FastAPI."""
    
    def __init__(self):
        self.MODEL_PATH = MODEL_PATH
        self.CONF_THRESHOLD = MODEL_CONFIG["conf_threshold"]
        self.IOU_THRESHOLD = MODEL_CONFIG["iou_threshold"]
        self.ENABLE_OCR = FEATURES["enable_ocr"]
        self.ENABLE_QUANTITY_ESTIMATION = FEATURES["enable_quantity_estimation"]
        self.ENABLE_RECIPE_RECOMMENDATIONS = FEATURES["enable_recipe_recommendations"]


def get_settings() -> Settings:
    """Get FastAPI settings."""
    return Settings()


def print_config():
    """Print configuration (for debugging)."""
    config = get_config()
    print("\n=== Fridge Vision Configuration ===")
    for section, values in config.items():
        print(f"\n[{section.upper()}]")
        if isinstance(values, dict):
            for key, val in values.items():
                print(f"  {key}: {val}")
        else:
            print(f"  {values}")
    print("\n====================================\n")
