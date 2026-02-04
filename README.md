# Fridge Vision: AI-Powered Food Detection & Recipe Recommendation System

A mobile-first, backend-only AI application that detects food ingredients from fridge images using YOLO-based object detection, extracts text via OCR, estimates quantities, and recommends recipes based on available ingredients.

## 🎯 Overview

**Fridge Vision** helps users:
- 📸 Upload photos of their fridge
- 🔍 Automatically detect visible food ingredients
- 📋 Extract text from food labels and expiry dates (OCR)
- 📊 Estimate ingredient quantities
- 👨‍🍳 Get recipe recommendations based on available ingredients

## 🛠️ Tech Stack

- **Backend**: Python + FastAPI
- **AI Model**: YOLO-based object detection (YOLOv5)
- **OCR**: EasyOCR
- **Image Processing**: OpenCV, NumPy
- **Server Framework**: Uvicorn

## 📁 Project Structure

```
Fridge_Vision/
├── api/
│   ├── main.py                 # FastAPI application & routes
│   └── __init__.py
├── model/
│   ├── model_loader.py         # YOLO model loading & management
│   └── __init__.py
├── inference/
│   ├── model_inference.py      # Detection inference engine
│   ├── ocr_engine.py           # OCR text extraction
│   ├── quantity_estimator.py   # Quantity estimation heuristics
│   ├── recipe_engine.py        # Recipe matching & ranking
│   └── __init__.py
├── utils/
│   ├── image_utils.py          # Image preprocessing & postprocessing
│   └── __init__.py
├── data/
│   ├── classes.txt             # Food class labels
│   ├── recipes.json            # Recipe database
│   └── __init__.py
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
cd Fridge_Vision
pip install -r requirements.txt
```

### 2. Prepare Your Model

Place your **pre-trained model file** in one of these locations:
- `models/model.pt` (recommended for YOLOv5)
- `models/best.pt` (fine-tuned models)
- Project root: `model.pt`
- Or set `MODEL_PATH` environment variable

**Supported formats:**
- `.pt` - PyTorch/YOLOv5 models
- `.h5` - TensorFlow/Keras models

⚠️ **No model download needed** - bring your own trained model!

### 3. Configure (Optional)

```bash
cp .env.example .env
# Edit .env to customize:
# MODEL_PATH=/path/to/your/model.pt
# CONF_THRESHOLD=0.25
# IOU_THRESHOLD=0.45
```

### 4. Run the Server

```bash
python run_server.py
# or
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
### 4. Health Check

```bash
curl http://localhost:8000/health
```

## 📡 API Endpoints

### 1. Detect Ingredients
**POST** `/detect-ingredients`

Detects food ingredients in an uploaded image.

**Parameters**:
- `image` (File) - Image file (JPEG, PNG, etc.)
- `enable_ocr` (Boolean, optional) - Enable OCR text extraction (default: true)
- `confidence_threshold` (Float, optional) - Minimum confidence (0.0-1.0, default: 0.5)

**Example**:
```bash
curl -X POST "http://localhost:8000/detect-ingredients" \
  -F "image=@fridge.jpg" \
  -F "enable_ocr=true"
```

**Response**:
```json
{
  "status": "success",
  "message": "Successfully detected 12 ingredients",
  "detected_ingredients": [
    {
      "class_name": "tomato",
      "confidence": 0.95,
      "count": 3,
      "quantity_estimate": "medium portion",
      "estimated_unit": "pcs",
      "source": "detection"
    }
  ],
  "total_items": 12,
  "image_info": {
    "width": 640,
    "height": 480,
    "channels": 3
  },
  "ocr_results": {
    "status": "success",
    "texts": [...],
    "full_text": "Best before 2024-12-31"
  }
}
```

### 2. Recommend Recipes
**POST** `/recommend-recipes`

Get recipe recommendations based on available ingredients.

**Parameters**:
- `ingredients` (List[String]) - Available ingredient names
- `top_k` (Integer, optional) - Number of recipes to return (default: 5)
- `min_match` (Integer, optional) - Minimum ingredients to match (default: 1)

**Example**:
```bash
curl -X POST "http://localhost:8000/recommend-recipes?ingredients=tomato&ingredients=pasta&ingredients=garlic&top_k=5"
```

**Response**:
```json
{
  "status": "success",
  "message": "Found 3 matching recipes",
  "ingredients_provided": ["tomato", "pasta", "garlic"],
  "recipes": [
    {
      "recipe_id": 3,
      "name": "Tomato Pasta",
      "description": "Classic Italian pasta sauce",
      "matched_ingredients": ["tomato", "pasta", "garlic"],
      "missing_ingredients": ["onion", "oil"],
      "match_percentage": 60.0,
      "difficulty": "easy",
      "prep_time_mins": 25,
      "servings": 4,
      "score": 85.5
    }
  ]
}
```

### 3. List All Recipes
**GET** `/recipes`

Get all available recipes.

**Parameters**:
- `limit` (Integer, optional) - Max recipes to return (default: 20)

**Example**:
```bash
curl "http://localhost:8000/recipes?limit=10"
```

### 4. Search Recipes
**GET** `/recipes/search`

Search recipes by name or ingredient.

**Parameters**:
- `query` (String) - Recipe name or ingredient to search

**Example**:
```bash
curl "http://localhost:8000/recipes/search?query=pasta"
```

### 5. Get Recipe Details
**GET** `/recipes/{recipe_id}`

Get details of a specific recipe.

**Example**:
```bash
curl "http://localhost:8000/recipes/3"
```

### 6. API Info
**GET** `/info`

Get API information and available ingredients.

```bash
curl "http://localhost:8000/info"
```

## 🧠 AI Components

### 1. Object Detection (`model_inference.py`)
- **Model**: YOLOv5s (pretrained on COCO)
- **Confidence Threshold**: 0.5 (configurable)
- **Output**: Bounding boxes, class names, confidence scores

### 2. OCR Engine (`ocr_engine.py`)
- **Library**: EasyOCR
- **Supported Languages**: English (extensible)
- **Output**: Extracted text, bounding boxes, confidence scores
- **Features**: Expiry date detection, ingredient parsing

### 3. Quantity Estimation (`quantity_estimator.py`)
- **Heuristics**: Size-based classification
- **Categories**: Very small, small, medium, large, very large
- **Output**: Quantity labels, units, estimated values

### 4. Recipe Engine (`recipe_engine.py`)
- **Matching**: Ingredient overlap with recipes
- **Scoring**: Match percentage + missing count penalty
- **Output**: Ranked recipe recommendations

## 🔧 Configuration

### Model Configuration
Edit `api/main.py` to change model settings:
```python
_inference_engine = get_inference_engine(
    model_path="yolov5m",  # Change model size (s, m, l, x)
    conf_threshold=0.6      # Adjust confidence threshold
)
```

### OCR Configuration
Modify OCR language support:
```python
_ocr_engine = get_ocr_engine(
    languages=['en', 'es'],  # Add language codes
    use_gpu=True             # Enable GPU if available
)
```

### Recipe Database
Add custom recipes to `data/recipes.json`:
```json
{
  "id": 16,
  "name": "Custom Recipe",
  "ingredients": ["ingredient1", "ingredient2"],
  "difficulty": "easy",
  "prep_time_mins": 20,
  "servings": 4,
  "description": "Recipe description"
}
```

## 📊 Default Recipe Database

The system includes 15 pre-loaded recipes covering common dishes:
- Simple Salad
- Vegetable Stir Fry
- Tomato Pasta
- Vegetable Soup
- Fruit Smoothie
- And more...

## 🧪 Testing

### Manual Testing with cURL

**Test Detection**:
```bash
curl -X POST "http://localhost:8000/detect-ingredients" \
  -F "image=@test_fridge.jpg"
```

**Test Recommendations**:
```bash
curl "http://localhost:8000/recommend-recipes?ingredients=tomato&ingredients=onion&ingredients=bread"
```

### Using Python

```python
import requests

# Test detection
with open("fridge.jpg", "rb") as img:
    response = requests.post(
        "http://localhost:8000/detect-ingredients",
        files={"image": img},
        params={"enable_ocr": True}
    )
    print(response.json())

# Test recommendations
response = requests.post(
    "http://localhost:8000/recommend-recipes",
    params={
        "ingredients": ["tomato", "pasta", "garlic"],
        "top_k": 5
    }
)
print(response.json())
```

## 📦 Dependencies

Key dependencies (see `requirements.txt` for full list):
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **torch** - PyTorch deep learning
- **torchvision** - Computer vision utilities
- **yolov5** - YOLOv5 model
- **opencv-python** - Image processing
- **easyocr** - OCR engine
- **pillow** - Image library
- **numpy** - Numerical computing

## 📄 License

This project builds upon open-source work from:
- [gzaets/Fridge-Ingredient-Detection-with-AI](https://github.com/gzaets/Fridge-Ingredient-Detection-with-AI) - Object detection logic
- [moscardino1/frudrera](https://github.com/moscardino1/frudrera) - OCR and recipe engine design
- [Iskriyana/deep-food](https://github.com/Iskriyana/deep-food) - Food detection reference

**License**: MIT/Apache 2.0 compatible

## 🚀 Future Enhancements

- [ ] Fine-tune YOLO on custom food dataset
- [ ] Add more OCR languages
- [ ] Implement user preference learning
- [ ] Add nutritional information
- [ ] Support batch image processing
- [ ] Implement caching for frequently detected items
- [ ] Add authentication/API keys
- [ ] Docker containerization

## ⚡ Performance Notes

- **Model Loading**: ~2-5 seconds (first run)
- **Inference**: ~500ms per image (GPU) / ~1.5s (CPU)
- **OCR**: ~1-3 seconds per image
- **Memory**: ~4GB peak (VRAM for GPU models)

## 🐛 Troubleshooting

### Model Download Issues
```bash
# Clear cache and retry
rm -rf ~/.cache/torch/hub
python -m torch.hub load ultralytics/yolov5 yolov5s
```

### OCR Initialization Fails
```bash
# Reinstall EasyOCR
pip install --upgrade easyocr
```

### CUDA/GPU Issues
```bash
# Force CPU mode (edit api/main.py)
device = 'cpu'
```

## 📞 Support

For issues or questions:
1. Check the `/info` endpoint for API details
2. Review logs in API output
3. Consult Swagger UI at `/docs`

---

**Made with ❤️ for food lovers and developers**
