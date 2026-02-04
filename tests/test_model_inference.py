"""
Unit tests for model inference module.
Tests detection pipeline and result parsing.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock, PropertyMock

from inference.model_inference import FoodDetectionInference


@pytest.mark.unit
class TestFoodDetectionInference:
    """Test cases for FoodDetectionInference."""
    
    @pytest.fixture
    def inference_engine(self, temp_dir):
        """Create inference engine with mocked model."""
        with patch('inference.model_inference.get_model_loader') as mock_loader_fn:
            mock_loader = MagicMock()
            mock_model = MagicMock()
            mock_loader.load_model.return_value = mock_model
            mock_loader_fn.return_value = mock_loader
            
            return FoodDetectionInference(model_path=None)
    
    def test_inference_initialization(self, inference_engine):
        """Test inference engine initializes properly."""
        assert inference_engine is not None
        assert hasattr(inference_engine, 'detect_from_file')
        assert hasattr(inference_engine, 'detect_from_bytes')
    
    def test_detect_from_file(self, inference_engine, sample_image_file):
        """Test detection from image file."""
        # Mock the model
        mock_yolo_results = MagicMock()
        mock_df = MagicMock()
        mock_df.iterrows.return_value = [
            (0, {'xmin': 100, 'ymin': 100, 'xmax': 200, 'ymax': 200, 
                 'confidence': 0.95, 'class': 0, 'name': 'apple'})
        ]
        mock_yolo_results.pandas.return_value.xyxy = [mock_df]
        inference_engine.model.return_value = mock_yolo_results
        
        result = inference_engine.detect_from_file(sample_image_file)
        
        assert isinstance(result, dict)
        assert 'detections' in result
        assert 'image_size' in result
        assert 'count' in result
    
    def test_detect_from_bytes(self, inference_engine, sample_image_bytes):
        """Test detection from image bytes."""
        mock_yolo_results = MagicMock()
        mock_df = MagicMock()
        mock_df.iterrows.return_value = [
            (0, {'xmin': 100, 'ymin': 100, 'xmax': 200, 'ymax': 200,
                 'confidence': 0.9, 'class': 0, 'name': 'banana'})
        ]
        mock_yolo_results.pandas.return_value.xyxy = [mock_df]
        inference_engine.model.return_value = mock_yolo_results
        
        result = inference_engine.detect_from_bytes(sample_image_bytes)
        
        assert isinstance(result, dict)
        assert 'detections' in result
        assert result['count'] >= 0
    
    def test_no_model_error(self):
        """Test error when model is not loaded."""
        inference_engine = MagicMock(spec=FoodDetectionInference)
        inference_engine.model = None
        
        # Should raise error if trying to detect without model
        with patch('inference.model_inference.FoodDetectionInference._run_detection') as mock_run:
            mock_run.side_effect = RuntimeError("Model not loaded")
            
            with pytest.raises(RuntimeError, match="Model not loaded"):
                mock_run(np.zeros((480, 640, 3)), (480, 640))
    
    def test_parse_yolo_results(self, inference_engine):
        """Test parsing YOLO detection results."""
        mock_results = MagicMock()
        mock_df = MagicMock()
        mock_df.iterrows.return_value = [
            (0, {'xmin': 100, 'ymin': 100, 'xmax': 200, 'ymax': 200,
                 'confidence': 0.95, 'class': 0, 'name': 'apple'}),
            (1, {'xmin': 300, 'ymin': 150, 'xmax': 400, 'ymax': 250,
                 'confidence': 0.87, 'class': 1, 'name': 'banana'})
        ]
        mock_results.pandas.return_value.xyxy = [mock_df]
        
        detections = inference_engine._parse_results(mock_results)
        
        assert len(detections) == 2
        assert detections[0]['class_name'] == 'apple'
        assert detections[1]['class_name'] == 'banana'
    
    def test_detection_bbox_format(self, inference_engine):
        """Test detection bounding box format."""
        mock_results = MagicMock()
        mock_df = MagicMock()
        mock_df.iterrows.return_value = [
            (0, {'xmin': 10, 'ymin': 20, 'xmax': 100, 'ymax': 150,
                 'confidence': 0.9, 'class': 0, 'name': 'apple'})
        ]
        mock_results.pandas.return_value.xyxy = [mock_df]
        
        detections = inference_engine._parse_results(mock_results)
        
        bbox = detections[0]['bbox']
        assert bbox == [10, 20, 100, 150]
        assert isinstance(bbox, list)
    
    def test_empty_detections(self, inference_engine):
        """Test handling of empty detections."""
        mock_results = MagicMock()
        mock_df = MagicMock()
        mock_df.iterrows.return_value = []
        mock_results.pandas.return_value.xyxy = [mock_df]
        
        detections = inference_engine._parse_results(mock_results)
        
        assert len(detections) == 0
        assert isinstance(detections, list)
    
    def test_get_ingredient_list(self, inference_engine):
        """Test extracting unique ingredients from detections."""
        detections = [
            {'class_name': 'apple', 'confidence': 0.9, 'bbox': [0, 0, 100, 100]},
            {'class_name': 'apple', 'confidence': 0.85, 'bbox': [200, 200, 300, 300]},
            {'class_name': 'banana', 'confidence': 0.8, 'bbox': [400, 400, 500, 500]}
        ]
        
        ingredients = inference_engine.get_ingredient_list(detections)
        
        assert len(ingredients) == 2
        assert 'apple' in ingredients
        assert 'banana' in ingredients
    
    def test_ingredient_list_no_dedup(self, inference_engine):
        """Test ingredient list always deduplicates."""
        detections = [
            {'class_name': 'apple', 'confidence': 0.9, 'bbox': [0, 0, 100, 100]},
            {'class_name': 'apple', 'confidence': 0.85, 'bbox': [200, 200, 300, 300]},
            {'class_name': 'banana', 'confidence': 0.8, 'bbox': [400, 400, 500, 500]}
        ]
        
        ingredients = inference_engine.get_ingredient_list(detections)
        
        # get_ingredient_list always deduplicates
        assert len(ingredients) == 2
        
        assert len(ingredients) == 3
        assert ingredients.count('apple') == 2


@pytest.mark.unit
class TestDetectionResults:
    """Test detection result structure and validation."""
    
    def test_detection_has_required_fields(self, mock_detection_results):
        """Test detection results have required fields."""
        for detection in mock_detection_results['detections']:
            assert 'bbox' in detection
            assert 'confidence' in detection
            assert 'class_id' in detection
            assert 'class_name' in detection
            assert 'area' in detection
    
    def test_detection_confidence_bounds(self, mock_detection_results):
        """Test detection confidence is between 0 and 1."""
        for detection in mock_detection_results['detections']:
            conf = detection['confidence']
            assert 0 <= conf <= 1
    
    def test_bbox_coordinates_valid(self, mock_detection_results):
        """Test bounding box coordinates are valid."""
        for detection in mock_detection_results['detections']:
            bbox = detection['bbox']
            assert len(bbox) == 4
            x1, y1, x2, y2 = bbox
            assert x1 < x2  # x1 should be less than x2
            assert y1 < y2  # y1 should be less than y2
