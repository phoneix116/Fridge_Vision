"""
FastAPI main application for Fridge Vision backend.
Handles ingredient detection and recipe recommendations.
"""

import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import tempfile
import os

from inference.model_inference import FoodDetectionInference
from inference.ocr_engine import OCREngine
from inference.quantity_estimator import QuantityEstimator, merge_ingredients_with_quantities
from inference.recipe_engine import RecipeEngine
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="Fridge Vision API",
    description="Backend API for food detection and recipe recommendations",
    version="1.0.0"
)

# Initialize AI engines (lazy loading on first request)
_inference_engine = None
_ocr_engine = None
_recipe_engine = None
_quantity_estimator = None


def get_inference():
    """Get or initialize inference engine with local model."""
    global _inference_engine
    if _inference_engine is None:
        try:
            logger.info("🔧 Initializing inference engine with local model...")
            _inference_engine = FoodDetectionInference(
                model_path=settings.MODEL_PATH,
                conf=settings.CONF_THRESHOLD,
                iou=settings.IOU_THRESHOLD
            )
            logger.info("✅ Inference engine initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize inference: {e}")
            raise HTTPException(status_code=500, detail=f"Model loading failed: {e}")
    return _inference_engine


def get_ocr():
    """Get or initialize OCR engine."""
    global _ocr_engine
    if _ocr_engine is None:
        logger.info("Initializing OCR engine")
        _ocr_engine = get_ocr_engine(languages=['en'], use_gpu=False)
    return _ocr_engine


def get_recipes():
    """Get or initialize recipe engine."""
    global _recipe_engine
    if _recipe_engine is None:
        logger.info("Initializing recipe engine")
        _recipe_engine = get_recipe_engine()
    return _recipe_engine


# Response models
class Detection(BaseModel):
    """Single detection result."""
    class_name: str
    confidence: float
    count: int
    quantity_estimate: str
    estimated_unit: str
    source: str


class DetectionResponse(BaseModel):
    """Response model for /detect-ingredients endpoint."""
    status: str = Field("success")
    message: str
    detected_ingredients: List[Detection]
    total_items: int
    image_info: Dict
    ocr_results: Optional[Dict] = None
    timestamp: Optional[str] = None


class RecipeRecommendation(BaseModel):
    """Single recipe recommendation."""
    recipe_id: int
    name: str
    description: str
    matched_ingredients: List[str]
    missing_ingredients: List[str]
    match_percentage: float
    difficulty: str
    prep_time_mins: int
    servings: int
    score: float


class RecipeResponse(BaseModel):
    """Response model for /recommend-recipes endpoint."""
    status: str = Field("success")
    message: str
    ingredients_provided: List[str]
    recipes: List[RecipeRecommendation]
    timestamp: Optional[str] = None


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Fridge Vision API is running"
    }


# Detection endpoint
@app.post("/detect-ingredients")
async def detect_ingredients(
    image: UploadFile = File(...),
    enable_ocr: bool = Query(True, description="Enable OCR for text extraction"),
    confidence_threshold: float = Query(0.5, ge=0.0, le=1.0, description="Confidence threshold for detections")
) -> JSONResponse:
    """
    Detect food ingredients in an image.
    
    Args:
        image: Image file (JPEG, PNG, etc.)
        enable_ocr: Whether to run OCR on the image
        confidence_threshold: Minimum confidence for detections
        
    Returns:
        Detection results with ingredients and quantities
    """
    try:
        logger.info(f"Received image: {image.filename}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            contents = await image.read()
            tmp_file.write(contents)
            tmp_path = tmp_file.name
        
        try:
            # Run inference
            inference_engine = get_inference()
            inference_results = inference_engine.detect_from_file(tmp_path)
            
            detections = inference_results["detections"]
            image_info = inference_results["image_info"]
            
            # Estimate quantities
            quantity_estimator = QuantityEstimator(
                image_width=image_info["width"],
                image_height=image_info["height"]
            )
            quantity_results = quantity_estimator.estimate_quantities_batch(detections)
            
            # Run OCR if enabled
            ocr_results = None
            if enable_ocr:
                logger.info("Running OCR on image")
                ocr_engine = get_ocr()
                ocr_results = ocr_engine.extract_text_from_bytes(contents)
            
            # Merge all results
            merged_ingredients = merge_ingredients_with_quantities(
                detections,
                quantity_results,
                ocr_results
            )
            
            # Format response
            detected_list = [
                Detection(
                    class_name=ing["ingredient"],
                    confidence=ing["confidence"],
                    count=ing["count"],
                    quantity_estimate=ing["quantity_estimate"],
                    estimated_unit=ing["estimated_unit"],
                    source=ing.get("source", "detection")
                )
                for ing in merged_ingredients
            ]
            
            response = DetectionResponse(
                message=f"Successfully detected {len(detected_list)} ingredients",
                detected_ingredients=detected_list,
                total_items=len(detections),
                image_info=image_info,
                ocr_results=ocr_results
            )
            
            logger.info(f"Detection completed: {len(detected_list)} ingredients")
            return JSONResponse(
                status_code=200,
                content=response.dict()
            )
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except Exception as e:
        logger.error(f"Detection error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Detection failed: {str(e)}"
            }
        )


# Recipe recommendation endpoint
@app.post("/recommend-recipes")
async def recommend_recipes(
    ingredients: List[str] = Query(..., description="List of available ingredients"),
    top_k: int = Query(5, ge=1, le=20, description="Number of recipes to return"),
    min_match: int = Query(1, ge=1, description="Minimum ingredients to match")
):
    """
    Recommend recipes based on available ingredients.
    
    Args:
        ingredients: List of ingredient names
        top_k: Number of top recipes to return
        min_match: Minimum ingredients that must match
        
    Returns:
        List of recommended recipes ranked by match score
    """
    try:
        if not ingredients:
            raise ValueError("No ingredients provided")
        
        logger.info(f"Recommending recipes for {len(ingredients)} ingredients")
        
        # Get recipe engine
        recipe_engine = get_recipes()
        
        # Get recommendations
        recommendations = recipe_engine.recommend_recipes(
            ingredients=ingredients,
            top_k=top_k,
            min_match=min_match
        )
        
        # Format response
        recipe_list = [
            RecipeRecommendation(
                recipe_id=rec["recipe_id"],
                name=rec["name"],
                description=rec["description"],
                matched_ingredients=rec["matched_ingredients"],
                missing_ingredients=rec["missing_ingredients"],
                match_percentage=rec["match_percentage"],
                difficulty=rec["difficulty"],
                prep_time_mins=rec["prep_time_mins"],
                servings=rec["servings"],
                score=rec["score"]
            )
            for rec in recommendations
        ]
        
        response = RecipeResponse(
            message=f"Found {len(recipe_list)} matching recipes",
            ingredients_provided=ingredients,
            recipes=recipe_list
        )
        
        logger.info(f"Recommended {len(recipe_list)} recipes")
        return JSONResponse(
            status_code=200,
            content=response.dict()
        )
    
    except Exception as e:
        logger.error(f"Recipe recommendation error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Recipe recommendation failed: {str(e)}"
            }
        )


# Search recipes endpoint
@app.get("/recipes/search")
async def search_recipes(
    query: str = Query(..., description="Recipe name or ingredient to search")
):
    """
    Search recipes by name or ingredient.
    
    Args:
        query: Search query (recipe name or ingredient)
        
    Returns:
        List of matching recipes
    """
    try:
        recipe_engine = get_recipes()
        query_lower = query.lower()
        
        results = []
        for recipe in recipe_engine.recipes:
            # Search in name
            if query_lower in recipe.get("name", "").lower():
                results.append(recipe)
            # Search in ingredients
            elif any(query_lower in ing.lower() for ing in recipe.get("ingredients", [])):
                results.append(recipe)
        
        logger.info(f"Recipe search returned {len(results)} results")
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "query": query,
                "results": results,
                "count": len(results)
            }
        )
    
    except Exception as e:
        logger.error(f"Recipe search error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Recipe search failed: {str(e)}"
            }
        )


# List all available recipes endpoint
@app.get("/recipes")
async def list_recipes(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of recipes to return")
):
    """
    List all available recipes.
    
    Args:
        limit: Maximum number of recipes to return
        
    Returns:
        List of recipes
    """
    try:
        recipe_engine = get_recipes()
        recipes = recipe_engine.recipes[:limit]
        
        logger.info(f"Listed {len(recipes)} recipes")
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "recipes": recipes,
                "total": len(recipes)
            }
        )
    
    except Exception as e:
        logger.error(f"List recipes error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Could not list recipes: {str(e)}"
            }
        )


# Get recipe by ID endpoint
@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int):
    """
    Get a specific recipe by ID.
    
    Args:
        recipe_id: Recipe ID
        
    Returns:
        Recipe details
    """
    try:
        recipe_engine = get_recipes()
        recipe = recipe_engine.find_recipe_by_id(recipe_id)
        
        if not recipe:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"Recipe {recipe_id} not found"
                }
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "recipe": recipe
            }
        )
    
    except Exception as e:
        logger.error(f"Get recipe error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Could not retrieve recipe: {str(e)}"
            }
        )


# Info endpoint
@app.get("/info")
async def api_info():
    """Get API information."""
    recipe_engine = get_recipes()
    all_ingredients = recipe_engine.get_all_ingredients()
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "api_name": "Fridge Vision API",
            "version": "1.0.0",
            "description": "Food detection and recipe recommendation API",
            "endpoints": {
                "detect": "/detect-ingredients (POST) - Detect ingredients in image",
                "recommend": "/recommend-recipes (GET) - Get recipe recommendations",
                "search": "/recipes/search (GET) - Search recipes",
                "list": "/recipes (GET) - List all recipes",
                "get": "/recipes/{id} (GET) - Get recipe by ID",
                "health": "/health (GET) - Health check"
            },
            "database": {
                "total_recipes": len(recipe_engine.recipes),
                "total_unique_ingredients": len(all_ingredients),
                "available_ingredients": all_ingredients
            }
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Fridge Vision API",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
