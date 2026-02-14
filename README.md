# Fridge Vision: AI-Powered Food Detection & Recipe Recommendation System

A mobile-first, backend-only AI application that detects food ingredients from fridge images using **YOLOv8m** object detection, extracts text via OCR, estimates quantities, and recommends recipes using **Ollama LLM** (or keyword matching fallback).

## 🎯 Overview

**Fridge Vision** helps users:
- 📸 Upload photos of their fridge
- 🔍 Automatically detect visible food ingredients (30 food classes)
- 📋 Extract text from food labels and expiry dates (OCR)
- 📊 Estimate ingredient quantities based on visual size
- 👨‍🍳 Get **AI-powered recipe recommendations** via Ollama LLM (or keyword fallback)
- ⭐ **Full-flow endpoint** to detect + recommend in a single API call

## 🛠️ Tech Stack

- **Backend**: Python + FastAPI + Uvicorn
- **Detection Model**: YOLOv8l (Ultralytics) - mAP50: 95.2%, 30 food classes (improved from YOLOv8m: 86.6%)
- **LLM Recipes**: Ollama (local) + Mistral-7B (with HuggingFace Inference API fallback for cloud)
- **OCR**: EasyOCR
- **Image Processing**: OpenCV, NumPy, Pillow
- **Testing**: pytest (86 tests, 100% passing)

## 📁 Project Structure

```
Fridge_Vision/
├── api/
│   ├── main.py                      # FastAPI application & all routes
│   └── __init__.py
├── model/
│   └── model_loader.py              # YOLOv8m model loading & management
├── inference/
│   ├── model_inference.py           # YOLOv8m detection inference
│   ├── llm_recipe_recommender.py    # Ollama LLM integration (NEW)
│   ├── ocr_engine.py                # OCR text extraction
│   ├── quantity_estimator.py        # Quantity estimation heuristics
│   ├── recipe_engine.py             # Recipe matching & ranking
│   └── __init__.py
├── utils/
│   ├── image_utils.py               # Image preprocessing & postprocessing
│   └── __init__.py
├── data/
│   ├── classes.txt                  # 30 food class labels
│   ├── recipes.json                 # Recipe database
│   └── __init__.py
├── tests/                           # Comprehensive test suite (86 tests)
│   ├── test_config.py               # Configuration tests (12)
│   ├── test_recipe_engine.py        # Recipe matching tests (21)
│   ├── test_llm_recommender.py      # LLM integration tests (16)
│   ├── test_quantity_estimator.py   # Quantity tests (18)
│   ├── test_api.py                  # API endpoint tests (19)
│   └── __init__.py
├── models/
│   └── weights2_fridge_vision.pt    # YOLOv8m trained model (52.1MB)
├── scripts/
│   └── convert_recipes_csv_to_json.py # Recipe CSV converter (optional)
├── docs/
│   └── OLLAMA_SETUP.md              # LLM installation guide
├── requirements.txt                 # Python dependencies
├── config.py                        # Centralized configuration
├── run_server.py                    # Server startup script
└── README.md                        # This file
```

## 🚀 Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
cd Fridge_Vision
pip install -r requirements.txt
```

### 3. Prepare Your Model

Place your **pre-trained YOLOv8l model file** in the models directory:

```bash
# YOLOv8l Model (Latest - Recommended)
# models/weights3_fridge_vision_yolov8l.pt
# Performance: mAP50=95.2%, mAP50-95=76.1%
# Size: 87.7MB (via Git LFS)

# Or YOLOv8m baseline:
# models/weights2_fridge_vision.pt
# Performance: mAP50=86.6%, mAP50-95=66.3%
# Size: 52.1MB

# Model specs:
# - Architecture: YOLOv8 (Large variant recommended)
# - Classes: 30 food items
# - Preprocessing: Letterboxing with aspect-ratio preservation
# - File: models/weights*.pt (PyTorch format)
```

Supported formats: `.pt` (PyTorch/YOLO), `.h5` (TensorFlow)

### 4. Setup Ollama LLM (Optional, for AI recipe recommendations)

For AI-powered recipe generation using Ollama:

```bash
# 1. Install Ollama (see docs/OLLAMA_SETUP.md for details)
brew install ollama  # macOS

# 2. Start Ollama server (in a separate terminal)
ollama serve

# 3. Pull Mistral model (4.1GB)
ollama pull mistral

# Now /recommend-recipes with use_llm=true will use AI!
```

If Ollama is unavailable, the system automatically falls back to keyword matching.

### 5. Configure (Optional)

Edit `config.py` to customize settings:

```python
MODEL_PATH = "models/weights3_fridge_vision_yolov8l.pt"
CONF_THRESHOLD = 0.3        # Detection confidence threshold (lowered for better sensitivity)
IOU_THRESHOLD = 0.45        # NMS IOU threshold
ENABLE_OCR = True           # Enable text extraction
ENABLE_QUANTITY_ESTIMATION = True
ENABLE_RECIPE_RECOMMENDATIONS = True
```

### 6. Run the Server

```bash
python run_server.py
# or
/path/to/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 7. Health Check

```bash
curl http://localhost:8000/health
# {"status": "healthy", "message": "Fridge Vision API is running"}
```

## 📡 API Endpoints

### 🌟 1. Full Flow: Detect & Recommend (NEW!)
**POST** `/detect-and-recommend`

Single endpoint that detects ingredients AND recommends recipes in one call.

**Parameters**:
- `image` (File, required) - Fridge image (JPEG, PNG)
- `use_llm` (Boolean, default=true) - Use Ollama LLM for AI recipes
- `top_k` (Integer, default=5) - Number of recipes
- `enable_ocr` (Boolean, default=false) - Extract text from labels
- `confidence_threshold` (Float, default=0.5) - Detection confidence

**Example**:
```bash
curl -X POST http://localhost:8000/detect-and-recommend \
  -F "image=@fridge.jpg" \
  -d "use_llm=true&top_k=5"
```

**Response**:
```json
{
  "status": "success",
  "message": "Detected 3 ingredients, generated 5 recipes",
  "detected_ingredients": [
    {
      "class_name": "apple",
      "confidence": 0.92,
      "count": 2,
      "quantity_estimate": "medium portion",
      "estimated_unit": "pcs",
      "source": "detection"
    }
  ],
  "total_items": 3,
  "image_info": {"width": 640, "height": 480},
  "recipes": [
    {
      "recipe_id": 1,
      "name": "Apple Carrot Soup",
      "description": "A healthy soup...",
      "matched_ingredients": ["apple", "carrot"],
      "missing_ingredients": ["salt", "water"],
      "match_percentage": 100.0,
      "difficulty": "easy",
      "prep_time_mins": 30,
      "servings": 4,
      "score": 95.0
    }
  ]
}
```

---

### 2. Detect Ingredients
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

---

### 3. Recommend Recipes
**POST** `/recommend-recipes`

Get recipe recommendations based on ingredients (with optional LLM).

**Parameters**:
- `ingredients` (List[String]) - Available ingredient names
- `use_llm` (Boolean, default=true) - Use Ollama for AI recommendations
- `top_k` (Integer, default=5) - Number of recipes
- `min_match` (Integer, default=1) - Min ingredients to match

**Example**:
```bash
# With LLM (AI-powered)
curl -X POST "http://localhost:8000/recommend-recipes?ingredients=apple&ingredients=carrot&use_llm=true&top_k=5"

# With keyword matching (fallback)
curl -X POST "http://localhost:8000/recommend-recipes?ingredients=apple&ingredients=carrot&use_llm=false"
```

---

### 4. Search Recipes
**GET** `/recipes/search`

Search recipes by name or ingredient.

**Example**:
```bash
curl "http://localhost:8000/recipes/search?query=pasta"
```

---

### 5. List All Recipes
**GET** `/recipes`

Get all available recipes.

**Example**:
```bash
curl "http://localhost:8000/recipes?limit=10"
```

---

### 6. Get Recipe Details
**GET** `/recipes/{recipe_id}`

Get details of a specific recipe.

**Example**:
```bash
curl "http://localhost:8000/recipes/3"
```

---

### 7. API Info
**GET** `/info`

Get API information, available ingredients, and stats.

**Example**:
```bash
curl "http://localhost:8000/info"
```

---

### 8. Health Check
**GET** `/health`

Check if API is running.

**Example**:
```bash
curl "http://localhost:8000/health"
```

## 🧠 AI Components

### 1. Object Detection (`model_inference.py`)
- **Model**: YOLOv8l (Ultralytics) - Improved from YOLOv8m
- **Classes**: 30 food items (apple, banana, carrot, tomato, potato, etc.)
- **Performance**: mAP50=95.2%, mAP50-95=76.1% (improved from YOLOv8m: 86.6% / 66.3%)
- **Confidence Threshold**: 0.3 (lowered for better sensitivity, configurable)
- **Speed**: ~19ms per image (T4 GPU) / ~500ms (CPU)
- **Output**: Bounding boxes, class names, confidence scores
- **Preprocessing**: Letterboxing (aspect-ratio preserving, no distortion)

### 2. LLM Recipe Engine (`llm_recipe_recommender.py`) ⭐ NEW
- **Local Backend**: Ollama (local machine) + Mistral-7B
  - Best for development/testing on your laptop
  - Free, no API keys required
  - Requires: `ollama serve` running
  
- **Cloud Backend**: HuggingFace Inference API (recommended for production)
  - Best for cloud deployment (Railway, Render, Heroku, etc.)
  - Uses same Mistral-7B model
  - Requires: HuggingFace API token (free tier available)
  - Speed: ~5-30 seconds per request (LLM inference)
  
- **Features**: 
  - Creative recipe generation from detected ingredients
  - Dietary restrictions support (vegan, gluten-free, etc.)
  - Recipe refinement and clarification
  - Graceful fallback to keyword matching if both unavailable

### 3. OCR Engine (`ocr_engine.py`)
- **Library**: EasyOCR
- **Supported Languages**: English (extensible)
- **Speed**: ~1-3 seconds per image
- **Output**: Extracted text, bounding boxes, confidence scores
- **Features**: Expiry date detection, ingredient parsing from labels

### 4. Quantity Estimation (`quantity_estimator.py`)
- **Method**: Size-based classification from bounding box area
- **Categories**: Very small, small, medium, large, very large
- **Unit Selection**: Smart unit assignment (ml for liquids, pcs for items, g for bulk)
- **Output**: Quantity labels, units, estimated values
- **Example**: Apple detected at 30% image area → "large portion" → 0.75x qty

### 5. Recipe Engine (`recipe_engine.py`)
- **Database**: 10 default recipes + 1M+ optional recipes (CSV)
- **Matching**: Ingredient overlap with recipes
- **Scoring**: Match percentage (50%) + missing count penalty (50%)
- **Output**: Ranked recipe recommendations sorted by score
- **Features**: Case-insensitive matching, sorting by relevance

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

### Running the Test Suite

Comprehensive test suite with **86 tests** covering all components:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=api --cov=inference --cov=config --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_recipe_engine.py::TestRecipeEngine::test_recommend_single_ingredient -v
```

### Test Coverage

- **Config Tests** (`test_config.py`) - 12 tests
  - Project paths, model configuration, API settings
  - Feature flags, logging configuration
  
- **Recipe Engine Tests** (`test_recipe_engine.py`) - 21 tests
  - Ingredient matching, case-insensitive matching
  - Score calculation, sorting by relevance
  - Singleton pattern verification
  
- **LLM Recommender Tests** (`test_llm_recommender.py`) - 16 tests
  - Ollama API integration, JSON parsing
  - Timeout handling, fallback logic
  - Availability checks, graceful degradation
  
- **Quantity Estimator Tests** (`test_quantity_estimator.py`) - 18 tests
  - Size classification accuracy
  - Unit selection (ml, pcs, g, portions)
  - Batch processing and merging
  
- **API Endpoint Tests** (`test_api.py`) - 19 tests
  - Health checks, detection endpoint
  - Recipe recommendations, searches
  - Response structure validation
  - Error handling scenarios

### Manual Testing with cURL

**Test Full Flow**:
```bash
curl -X POST http://localhost:8000/detect-and-recommend \
  -F "image=@fridge.jpg" \
  -d "use_llm=true&top_k=5"
```

**Test Detection Only**:
```bash
curl -X POST "http://localhost:8000/detect-ingredients" \
  -F "image=@fridge.jpg"
```

**Test Recommendations (Keyword Matching)**:
```bash
curl -X POST "http://localhost:8000/recommend-recipes?ingredients=apple&ingredients=carrot&use_llm=false"
```

**Test Recommendations (LLM)**:
```bash
curl -X POST "http://localhost:8000/recommend-recipes?ingredients=apple&ingredients=carrot&use_llm=true"
```

### Using Python SDK

```python
import requests

# Full flow example
with open("fridge.jpg", "rb") as img:
    response = requests.post(
        "http://localhost:8000/detect-and-recommend",
        files={"image": img},
        params={"use_llm": True, "top_k": 5}
    )
    print(response.json())

# Recommendation with specific ingredients
response = requests.post(
    "http://localhost:8000/recommend-recipes",
    params={
        "ingredients": ["apple", "carrot", "onion"],
        "use_llm": True,
        "top_k": 5
    }
)
print(response.json())
```

### Test Results

```
======= 86 passed in 1.45s =======

✅ All tests passing
✅ 100% API endpoint coverage
✅ Configuration validation
✅ LLM integration tested with mocks
✅ Error handling verified
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

## 🌐 Cloud Deployment

### Deploy to Railway / Render

**Option 1: HuggingFace Inference API (Recommended)** ✅
Best for cloud without running Ollama server.

```bash
# 1. Get HuggingFace API Token
# - Go to https://huggingface.co/settings/tokens
# - Create a new token (read access)

# 2. Deploy to Railway/Render with environment variables:
HF_API_TOKEN="hf_xxxxxxxxxxxx"  # Your HuggingFace token
CONF_THRESHOLD="0.3"
MODEL_PATH="models/weights3_fridge_vision_yolov8l.pt"

# 3. Test the cloud API
curl -X POST https://your-app.railway.app/detect-and-recommend \
  -F "image=@fridge.jpg" \
  -F "use_llm=true"
```

**Option 2: Docker with Local Ollama** (Advanced)
Use docker-compose if you want Ollama running in your cloud:
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      OLLAMA_API_URL: "http://ollama:11434"
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: serve

volumes:
  ollama_data:
```

**Option 3: Fallback Mode** (No LLM)
IF Ollama and HuggingFace are both unavailable, system falls back to keyword-based recipe matching.

### Deployment Checklist
- [ ] Model file (`weights3_fridge_vision_yolov8l.pt`) in `models/`
- [ ] HuggingFace token set (or Ollama available)
- [ ] Environment variables configured
- [ ] Test with `/health` endpoint
- [ ] Try `/detect-and-recommend` with sample image

## 🚀 Future Enhancements

- [x] YOLOv8l model training (mAP50: 95.2% ✓)
- [x] LLM integration with HuggingFace fallback ✓
- [x] Full /detect-and-recommend endpoint ✓
- [ ] Phase 2 training (additional food classes)
- [ ] Add more OCR languages
- [ ] Implement user preference learning
- [ ] Add nutritional information
- [ ] Support batch image processing
- [ ] Implement caching for frequently detected items
- [ ] Add authentication/API keys

## ⚡ Performance Notes

- **Model Loading**: ~2-5 seconds (first run, YOLOv8l is larger than YOLOv8m)
- **Inference**: ~19ms per image (T4 GPU) / ~500ms (CPU) with YOLOv8l
- **OCR**: ~1-3 seconds per image
- **LLM Recipe Generation**: ~5-30 seconds per request (cloud-dependent)
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
