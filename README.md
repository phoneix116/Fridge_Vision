---
title: Fridge Vision
emoji: 🥗
colorFrom: green
colorTo: blue
sdk: docker
app_port: 8000
pinned: false
---

# Fridge Vision: AI-Powered Food Detection & Recipe Recommendation System
# Fridge Vision API

Fridge Vision is a FastAPI backend that detects food ingredients from fridge images and recommends recipes.

## What it does

- Detects ingredients using a YOLO model (`.pt` weights)
- Estimates simple ingredient quantities from bounding boxes
- Optionally runs OCR on labels/text in the image
- Recommends recipes via:
  - local keyword matching, or
  - optional LLM generation (Ollama)

## Current default model

The backend currently defaults to:

- `models/weights4_fridge_vision_yolov8l.pt`

You can override this with `MODEL_PATH` in environment variables.

## Tech stack

- FastAPI + Uvicorn
- Ultralytics YOLO (PyTorch)
- OpenCV + NumPy
- EasyOCR (optional)

## Quick start

### 1) Clone and enter project

```bash
git clone https://github.com/phoneix116/Fridge_Vision.git
cd Fridge_Vision
```

### 2) Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Ensure model file exists

Place your model at:

- `models/weights4_fridge_vision_yolov8l.pt`

or set custom path:

```bash
export MODEL_PATH="/absolute/path/to/model.pt"
```

### 5) Run API

```bash
python run_server.py
```

API docs:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Frontend (React + Vite)

The project also includes a frontend in [frontend/](frontend) built with React, Vite, and Tailwind CSS.

### Frontend stack

- React 18
- Vite 5
- Tailwind CSS 3

### Run frontend locally

From the project root:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on:

- `http://localhost:5173`

### Backend + frontend together

Use two terminals:

- Terminal 1 (backend):

```bash
python run_server.py
```

- Terminal 2 (frontend):

```bash
cd frontend
npm run dev
```

### API integration

Frontend calls `POST /api/detect-and-recommend` from [frontend/src/hooks/useDetect.js](frontend/src/hooks/useDetect.js).

Vite proxy config in [frontend/vite.config.js](frontend/vite.config.js) rewrites:

- `/api/*` → `http://localhost:8000/*`

This avoids CORS issues during local development.

### Frontend flow

- [frontend/src/Landing.jsx](frontend/src/Landing.jsx): marketing/entry screen
- [frontend/src/AppPage.jsx](frontend/src/AppPage.jsx): upload + analysis experience
- [frontend/src/components/IngredientGrid.jsx](frontend/src/components/IngredientGrid.jsx): detected ingredient display
- [frontend/src/components/RecipeList.jsx](frontend/src/components/RecipeList.jsx): recipe results grouped by match tier

### Production build

```bash
cd frontend
npm run build
npm run preview
```

## Main endpoints

- `GET /health` — health check
- `POST /detect-ingredients` — detect ingredients from image
- `POST /recommend-recipes` — recommend recipes from ingredient list
- `POST /detect-and-recommend` — full pipeline in one call
- `GET /recipes` — list recipes
- `GET /recipes/{recipe_id}` — get one recipe
- `GET /recipes/search?query=...` — search recipes
- `GET /info` — API metadata

## Example requests

### Detect ingredients

```bash
curl -X POST "http://localhost:8000/detect-ingredients" \
  -F "image=@test_images/fridge1.jpg"
```

### Full flow (detect + recommend)

```bash
curl -X POST "http://localhost:8000/detect-and-recommend?use_llm=false&top_k=5" \
  -F "image=@test_images/fridge1.jpg"
```

### Recommend from ingredient list

```bash
curl -X POST "http://localhost:8000/recommend-recipes?ingredients=tomato&ingredients=egg&ingredients=cheese&use_llm=false"
```

## Configuration

Use environment variables (or a `.env` file) for key settings:

- `MODEL_PATH` (default: `models/weights4_fridge_vision_yolov8l.pt`)
- `CONF_THRESHOLD` (default: `0.25`)
- `IOU_THRESHOLD` (default: `0.45`)
- `API_HOST` (default: `0.0.0.0`)
- `API_PORT` (default: `8000`)
- `ENABLE_OCR` (default: `true`)
- `ENABLE_RECIPE_RECOMMENDATIONS` (default: `true`)

See `config.py` for full configuration.

## Project layout (core)

```text
api/                    # FastAPI routes
inference/              # Detection, OCR, quantity, recipe logic
model/                  # Model loading
data/                   # classes.txt, recipes.json
models/                 # local model weights
config.py               # central configuration
run_server.py           # server entrypoint
```

## Notes

- `.pt` model files are ignored by default in git, except explicitly allowed files.
- If using LLM recipe generation, ensure your Ollama setup is available.
- Large model files may use Git LFS when pushed.

## License

MIT (see `LICENSE`).
