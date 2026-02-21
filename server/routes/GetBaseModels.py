# ================================================
# File: server/routes/GetBaseModels.py
# ================================================
from aiohttp import web
import yaml
import re
import server # ComfyUI server instance
from ...config import AVAILABLE_MEILI_BASE_MODELS
from ...api.huggingface import HuggingFaceAPI
from ..utils import resolve_huggingface_api_key

prompt_server = server.PromptServer.instance

@prompt_server.routes.get("/api/huggingface/base_models")
async def route_get_base_models(request):
    """API Endpoint to get the known base model types for filtering."""
    try:
        # Try to get base models from HuggingFace API
        api_key = resolve_huggingface_api_key({})
        api = HuggingFaceAPI(api_key)
        
        # Get popular models and extract their base models
        popular_models = [
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5",
            "stabilityai/stable-diffusion-2-1",
            "CompVis/stable-diffusion-v1-4",
            "black-forest-labs/FLUX.1-dev",
            "black-forest-labs/FLUX.1-schnell"
        ]
        
        base_models = set()
        base_models.update(AVAILABLE_MEILI_BASE_MODELS)  # Keep hardcoded ones as fallback
        
        for model_id in popular_models:
            try:
                model_info = api.get_model_info(model_id)
                if model_info and not isinstance(model_info, dict) or "error" not in model_info:
                    # Add the model itself as a base model
                    base_models.add(model_id)
            except Exception as e:
                print(f"[GetBaseModels] Error getting info for {model_id}: {e}")
                continue
        
        return web.json_response({"base_models": sorted(list(base_models))})
        
    except Exception as e:
        print(f"Error getting base model types: {e}")
        # Fallback to hardcoded list
        return web.json_response({"base_models": AVAILABLE_MEILI_BASE_MODELS})
        return web.json_response({"error": "Internal Server Error", "details": str(e), "status_code": 500}, status=500)