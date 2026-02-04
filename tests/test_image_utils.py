"""
Unit tests for image utilities module.
Tests image preprocessing and postprocessing.
"""

import pytest
import numpy as np
from PIL import Image
import cv2
from unittest.mock import patch, MagicMock

from utils.image_utils import ImagePreprocessor, ResultPostprocessor


@pytest.mark.unit
class TestImagePreprocessor:
    """Test cases for ImagePreprocessor."""
    
    def test_load_image_from_file(self, sample_image_file):
        """Test loading image from file."""
        preprocessor = ImagePreprocessor()
        image = preprocessor.load_image(sample_image_file)
        
        assert isinstance(image, np.ndarray)
        assert image.shape[2] == 3  # RGB
        assert image.shape[0] > 0 and image.shape[1] > 0
    
    def test_load_image_invalid_file(self, preprocessor=None):
        """Test error on invalid image file."""
        if preprocessor is None:
            preprocessor = ImagePreprocessor()
        
        with pytest.raises(Exception):  # Could be FileNotFoundError or cv2 error
            preprocessor.load_image("/nonexistent/image.jpg")
    
    def test_load_image_from_bytes(self, sample_image_file):
        """Test loading image from bytes."""
        preprocessor = ImagePreprocessor()
        
        # Read image as bytes
        with open(sample_image_file, 'rb') as f:
            image_bytes = f.read()
        
        image = preprocessor.load_image_from_bytes(image_bytes)
        
        assert isinstance(image, np.ndarray)
        assert image.shape[2] == 3
    
    def test_resize_image(self, sample_image_array):
        """Test image resizing."""
        preprocessor = ImagePreprocessor()
        original_shape = sample_image_array.shape
        
        resized = preprocessor.resize_image(sample_image_array, (416, 416))
        
        assert resized.shape == (416, 416, 3)
        assert resized.dtype == np.uint8
    
    def test_get_image_info(self, sample_image_file):
        """Test getting image information."""
        preprocessor = ImagePreprocessor()
        image = preprocessor.load_image(sample_image_file)
        info = preprocessor.get_image_info(image)
        
        assert 'width' in info
        assert 'height' in info
        assert 'channels' in info
        assert info['channels'] == 3
    
    def test_preprocess_maintains_dtype(self, sample_image_array):
        """Test that preprocessing maintains correct dtype."""
        preprocessor = ImagePreprocessor()
        resized = preprocessor.resize_image(sample_image_array, max_size=224)
        
        assert resized.dtype == np.uint8
        assert np.all(resized >= 0) and np.all(resized <= 255)
    
    def test_preprocess_different_sizes(self, sample_image_array):
        """Test preprocessing with various image sizes."""
        preprocessor = ImagePreprocessor()
        
        max_sizes = [224, 416, 640]
        for max_size in max_sizes:
            resized = preprocessor.resize_image(sample_image_array, max_size=max_size)
            # Check longest dimension is at most max_size
            assert max(resized.shape[:2]) <= max_size
            assert resized.shape[2] == 3  # RGB preserved


@pytest.mark.unit
class TestResultPostprocessor:
    """Test cases for ResultPostprocessor."""
    
    def test_merge_overlapping_detections(self):
        """Test merging of overlapping detections."""
        from unittest.mock import MagicMock
        postprocessor = ResultPostprocessor()
        
        # Mock YOLO predictions object
        mock_preds = MagicMock()
        mock_preds.xyxy = [np.array([[100, 100, 200, 200], [110, 110, 210, 210]])]
        mock_preds.conf = [np.array([0.9, 0.85])]
        mock_preds.cls = [np.array([0, 0])]
        
        class_names = ['apple']
        
        processed = postprocessor.process_detections(mock_preds, class_names)
        
        # Should return detections
        assert len(processed) >= 1
        assert processed[0]['confidence'] >= 0.85
    
    def test_iou_calculation(self):
        """Test IOU calculation for bounding boxes."""
        postprocessor = ResultPostprocessor()
        
        box1 = [100, 100, 200, 200]  # Area 10000
        box2 = [150, 150, 250, 250]  # Area 10000, overlap 2500
        
        iou = postprocessor._calculate_iou(box1, box2)
        
        assert 0 <= iou <= 1
        # Intersection = 2500, Union = 17500, IOU = 2500/17500 ≈ 0.143
        assert 0.14 <= iou <= 0.15
    
    def test_process_empty_detections(self):
        """Test processing empty detections."""
        from unittest.mock import MagicMock
        postprocessor = ResultPostprocessor()
        
        # Mock empty predictions
        mock_preds = MagicMock()
        mock_preds.xyxy = [np.array([]).reshape(0, 4)]
        mock_preds.conf = [np.array([])]
        mock_preds.cls = [np.array([])]
        
        processed = postprocessor.process_detections(mock_preds, [])
        
        assert isinstance(processed, list)
        assert len(processed) == 0
    
    def test_filter_low_confidence(self):
        """Test filtering low confidence detections."""
        from unittest.mock import MagicMock
        postprocessor = ResultPostprocessor()
        
        # Mock predictions with different confidence levels
        mock_preds = MagicMock()
        mock_preds.xyxy = [np.array([[100, 100, 200, 200], [300, 300, 400, 400]])]
        mock_preds.conf = [np.array([0.9, 0.1])]
        mock_preds.cls = [np.array([0, 1])]
        
        processed = postprocessor.process_detections(mock_preds, ['apple', 'banana'], conf_threshold=0.5)
        
        # Low confidence should be filtered
        assert len(processed) == 1
        assert processed[0]['class_name'] == 'apple'
    
    def test_non_max_suppression(self):
        """Test non-maximum suppression."""
        from unittest.mock import MagicMock
        postprocessor = ResultPostprocessor()
        
        # Mock overlapping predictions
        mock_preds = MagicMock()
        mock_preds.xyxy = [np.array([[0, 0, 100, 100], [10, 10, 110, 110], [500, 500, 600, 600]])]
        mock_preds.conf = [np.array([0.95, 0.85, 0.8])]
        mock_preds.cls = [np.array([0, 0, 1])]
        
        result = postprocessor.process_detections(mock_preds, ['apple', 'banana'])
        
        # Should return detections
        assert len(result) >= 2
        assert all(d['confidence'] >= 0.5 for d in result)
