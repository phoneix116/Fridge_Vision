"""
OCR (Optical Character Recognition) module for extracting text from images.
Uses EasyOCR for reliable text detection and recognition.
"""

import logging
from typing import List, Dict, Optional
import easyocr

logger = logging.getLogger(__name__)


class OCREngine:
    """Handle OCR for food labels and expiry dates."""
    
    def __init__(self, languages: List[str] = None, use_gpu: bool = False):
        """
        Initialize OCR engine.
        
        Args:
            languages: List of language codes (e.g., ['en', 'es'])
            use_gpu: Whether to use GPU for OCR
        """
        self.languages = languages or ['en']
        self.use_gpu = use_gpu
        self.reader = None
        self._init_reader()
    
    def _init_reader(self):
        """Initialize EasyOCR reader."""
        try:
            logger.info(f"Initializing OCR reader for languages: {self.languages}")
            self.reader = easyocr.Reader(
                self.languages,
                gpu=self.use_gpu,
                model_storage_directory=None
            )
            logger.info("OCR reader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OCR reader: {e}")
            raise RuntimeError(f"OCR initialization failed: {e}")
    
    def extract_text(self, image_path: str, confidence_threshold: float = 0.3) -> Dict:
        """
        Extract text from image file.
        
        Args:
            image_path: Path to image file
            confidence_threshold: Minimum confidence for text detection
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if self.reader is None:
            raise RuntimeError("OCR reader not initialized")
        
        logger.info(f"Extracting text from {image_path}")
        
        try:
            results = self.reader.readtext(image_path)
            
            extracted_texts = []
            for (bbox, text, confidence) in results:
                if confidence >= confidence_threshold:
                    extracted_texts.append({
                        "text": text.strip(),
                        "confidence": float(confidence),
                        "bbox": {
                            "x": float(bbox[0][0]),
                            "y": float(bbox[0][1]),
                            "width": float(bbox[2][0] - bbox[0][0]),
                            "height": float(bbox[2][1] - bbox[0][1])
                        }
                    })
            
            logger.info(f"Extracted {len(extracted_texts)} text regions")
            
            return {
                "status": "success",
                "texts": extracted_texts,
                "full_text": " ".join([t["text"] for t in extracted_texts]),
                "num_texts": len(extracted_texts)
            }
        
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "texts": [],
                "full_text": ""
            }
    
    def extract_text_from_bytes(
        self,
        image_bytes: bytes,
        confidence_threshold: float = 0.3
    ) -> Dict:
        """
        Extract text from image bytes.
        
        Args:
            image_bytes: Image data as bytes
            confidence_threshold: Minimum confidence for text detection
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if self.reader is None:
            raise RuntimeError("OCR reader not initialized")
        
        import cv2
        import numpy as np
        
        logger.info("Extracting text from image bytes")
        
        try:
            # Convert bytes to image
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            # Convert BGR to RGB for EasyOCR
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            results = self.reader.readtext(image)
            
            extracted_texts = []
            for (bbox, text, confidence) in results:
                if confidence >= confidence_threshold:
                    extracted_texts.append({
                        "text": text.strip(),
                        "confidence": float(confidence),
                        "bbox": {
                            "x": float(bbox[0][0]),
                            "y": float(bbox[0][1]),
                            "width": float(bbox[2][0] - bbox[0][0]),
                            "height": float(bbox[2][1] - bbox[0][1])
                        }
                    })
            
            logger.info(f"Extracted {len(extracted_texts)} text regions from bytes")
            
            return {
                "status": "success",
                "texts": extracted_texts,
                "full_text": " ".join([t["text"] for t in extracted_texts]),
                "num_texts": len(extracted_texts)
            }
        
        except Exception as e:
            logger.error(f"OCR extraction from bytes failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "texts": [],
                "full_text": ""
            }
    
    def parse_ingredients_from_text(self, text: str) -> List[str]:
        """
        Parse ingredient names from extracted text.
        Uses simple heuristics to identify likely ingredient names.
        
        Args:
            text: Extracted text from OCR
            
        Returns:
            List of potential ingredient names
        """
        # Common ingredient keywords
        ingredient_keywords = {
            "contains", "ingredients", "product", "made from",
            "of", "and", "with", "including", "mix"
        }
        
        # Split text and filter potential ingredients
        words = text.lower().split()
        potential_ingredients = []
        
        for word in words:
            # Remove common non-ingredient words and punctuation
            cleaned = word.strip('.,;:!?()[]{}"\'-').strip()
            
            if (len(cleaned) > 2 and
                cleaned not in ingredient_keywords and
                not cleaned.isdigit() and
                '%' not in cleaned):
                potential_ingredients.append(cleaned)
        
        # Remove duplicates and sort
        unique_ingredients = list(set(potential_ingredients))
        
        logger.info(f"Parsed {len(unique_ingredients)} potential ingredients from text")
        return sorted(unique_ingredients)
    
    def detect_expiry_date(self, text: str) -> Optional[str]:
        """
        Attempt to detect expiry date from extracted text.
        Looks for common date patterns.
        
        Args:
            text: Extracted text from OCR
            
        Returns:
            Detected expiry date string or None
        """
        import re
        
        # Common expiry date patterns
        patterns = [
            r'\b(?:exp|expiry|best before|use by)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',  # General date pattern
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b'
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                return match.group(0) if match.lastindex is None else match.group(1)
        
        return None


# Global OCR instance
_ocr_instance = None


def get_ocr_engine(languages: List[str] = None, use_gpu: bool = False) -> OCREngine:
    """Get or create singleton OCR engine."""
    global _ocr_instance
    
    if _ocr_instance is None:
        _ocr_instance = OCREngine(languages=languages, use_gpu=use_gpu)
    
    return _ocr_instance
