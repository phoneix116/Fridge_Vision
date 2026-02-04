"""
Pytest configuration and shared fixtures for all tests.
"""

import pytest
import os
import tempfile
import numpy as np
from PIL import Image
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create and cleanup temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_image_array():
    """Create a sample image as numpy array."""
    return np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)


@pytest.fixture
def sample_image_file(temp_dir):
    """Create a temporary sample image file."""
    img = Image.new('RGB', (640, 480), color=(73, 109, 137))
    img_path = os.path.join(temp_dir, "test_image.jpg")
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_image_bytes():
    """Create sample image as bytes (proper JPEG format)."""
    import io
    img = Image.new('RGB', (640, 480), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()


@pytest.fixture
def mock_model_file(temp_dir):
    """Create a mock model file path."""
    model_path = os.path.join(temp_dir, "mock_model.pt")
    # Create empty file (actual model would be downloaded/provided)
    Path(model_path).touch()
    return model_path


@pytest.fixture
def mock_detection_results():
    """Mock YOLO detection results."""
    return {
        'detections': [
            {
                'bbox': [100, 100, 200, 200],
                'confidence': 0.95,
                'class_id': 0,
                'class_name': 'apple',
                'area': 10000
            },
            {
                'bbox': [300, 150, 400, 250],
                'confidence': 0.87,
                'class_id': 1,
                'class_name': 'banana',
                'area': 10000
            }
        ],
        'raw_detections': [],
        'image_size': (480, 640),
        'count': 2
    }


@pytest.fixture
def mock_recipes():
    """Mock recipe database."""
    return [
        {
            'id': 1,
            'name': 'Fruit Salad',
            'ingredients': ['apple', 'banana', 'orange'],
            'difficulty': 'easy',
            'prep_time_mins': 10,
            'servings': 2,
            'description': 'Fresh fruit salad'
        },
        {
            'id': 2,
            'name': 'Apple Pie',
            'ingredients': ['apple', 'flour', 'sugar'],
            'difficulty': 'medium',
            'prep_time_mins': 45,
            'servings': 4,
            'description': 'Homemade apple pie'
        }
    ]


@pytest.fixture(autouse=True)
def cleanup_model_cache():
    """Clear model cache between tests."""
    yield
    # Cleanup code here if needed
    pass


# Pytest configuration
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
