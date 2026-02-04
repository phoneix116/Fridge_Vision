"""
Unit tests for model loading module.
Tests ModelLoader singleton, loading, and caching.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from model.model_loader import ModelLoader, get_model_loader


@pytest.mark.unit
class TestModelLoader:
    """Test cases for ModelLoader class."""
    
    def test_singleton_instance(self):
        """Test that ModelLoader returns same instance."""
        loader1 = get_model_loader()
        loader2 = get_model_loader()
        assert loader1 is loader2
    
    def test_model_not_found_error(self):
        """Test error when model file not found."""
        loader = ModelLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_model(model_path="/nonexistent/model.pt")
    
    def test_invalid_model_format(self, temp_dir):
        """Test error for unsupported model format."""
        # Create a dummy file with unsupported extension
        invalid_model = os.path.join(temp_dir, "model.xyz")
        Path(invalid_model).touch()
        
        loader = ModelLoader()
        loader.clear_cache()
        
        with pytest.raises(ValueError, match="Unsupported model format"):
            loader.load_model(model_path=invalid_model)
    
    @patch('torch.hub.load')
    def test_load_pytorch_model(self, mock_torch_load, temp_dir):
        """Test loading PyTorch YOLO model."""
        # Setup mock
        mock_model = MagicMock()
        mock_torch_load.return_value = mock_model
        
        model_path = os.path.join(temp_dir, "model.pt")
        Path(model_path).touch()
        
        loader = ModelLoader()
        loader.clear_cache()
        
        result = loader.load_model(model_path=model_path)
        
        assert result is mock_model
        mock_torch_load.assert_called_once()
    
    def test_model_caching(self, temp_dir):
        """Test that model is cached after loading."""
        with patch('torch.hub.load') as mock_load:
            mock_model = MagicMock()
            mock_load.return_value = mock_model
            
            model_path = os.path.join(temp_dir, "model.pt")
            Path(model_path).touch()
            
            loader = ModelLoader()
            loader.clear_cache()
            
            # First call
            result1 = loader.load_model(model_path=model_path)
            # Second call
            result2 = loader.load_model(model_path=model_path)
            
            # torch.hub.load should be called only once
            mock_load.assert_called_once()
            assert result1 is result2
    
    def test_clear_cache(self, temp_dir):
        """Test clearing model cache."""
        with patch('torch.hub.load') as mock_load:
            mock_model = MagicMock()
            mock_load.return_value = mock_model
            
            model_path = os.path.join(temp_dir, "model.pt")
            Path(model_path).touch()
            
            loader = ModelLoader()
            loader.clear_cache()
            
            # Load model
            loader.load_model(model_path=model_path)
            assert mock_load.call_count == 1
            
            # Clear and reload
            loader.clear_cache()
            loader.load_model(model_path=model_path)
            assert mock_load.call_count == 2
    
    def test_get_model_returns_cached_model(self, temp_dir):
        """Test get_model returns cached model."""
        with patch('torch.hub.load') as mock_load:
            mock_model = MagicMock()
            mock_load.return_value = mock_model
            
            model_path = os.path.join(temp_dir, "model.pt")
            Path(model_path).touch()
            
            loader = ModelLoader()
            loader.clear_cache()
            
            # Load model
            loaded_model = loader.load_model(model_path=model_path)
            # Get cached model
            cached_model = loader.get_model()
            
            assert loaded_model is cached_model
    
    def test_env_variable_priority(self, temp_dir):
        """Test MODEL_PATH environment variable is checked."""
        model_path = os.path.join(temp_dir, "model.pt")
        Path(model_path).touch()
        
        with patch.dict(os.environ, {'MODEL_PATH': model_path}):
            with patch('torch.hub.load') as mock_load:
                mock_model = MagicMock()
                mock_load.return_value = mock_model
                
                loader = ModelLoader()
                loader.clear_cache()
                
                # Should use env variable
                result = loader.load_model()
                assert result is mock_model
    
    @patch('torch.hub.load')
    def test_confidence_threshold_setting(self, mock_torch_load, temp_dir):
        """Test setting confidence threshold on model."""
        mock_model = MagicMock()
        mock_torch_load.return_value = mock_model
        
        model_path = os.path.join(temp_dir, "model.pt")
        Path(model_path).touch()
        
        loader = ModelLoader()
        loader.clear_cache()
        
        loader.load_model(model_path=model_path, conf=0.75, iou=0.5)
        
        # Verify thresholds were set
        assert mock_model.conf == 0.75
        assert mock_model.iou == 0.5
