# ================================================
# File: server/routes/GetModelDetails.py
# ================================================
import os
import json
import traceback
from aiohttp import web

import server # ComfyUI server instance
from ..utils import get_request_json, resolve_huggingface_api_key
from ...api.huggingface import HuggingFaceAPI

prompt_server = server.PromptServer.instance

@prompt_server.routes.post("/api/huggingface/get_model_details")
async def route_get_model_details(request):
    """API Endpoint to fetch model details from HuggingFace model card."""
    try:
        data = await get_request_json(request)
        model_url_or_id = data.get("model_url_or_id")
        resolved_api_key = resolve_huggingface_api_key(data)

        if not model_url_or_id:
            raise web.HTTPBadRequest(reason="Missing 'model_url_or_id'")

        # Parse model ID
        from ...utils.helpers import parse_huggingface_input
        parsed_model_id, parsed_filename = parse_huggingface_input(model_url_or_id)
        
        if not parsed_model_id:
            raise web.HTTPBadRequest(reason=f"Could not parse HuggingFace model ID from: {model_url_or_id}")

        # Get model info using huggingface_hub
        try:
            from huggingface_hub import ModelCard
            model_card = ModelCard.load(parsed_model_id, token=resolved_api_key)
            
            # Extract data from model card
            model_name = model_card.data.get("model_name", parsed_model_id.split('/')[-1])
            creator_username = model_card.data.get("author", "Unknown Creator")
            description = model_card.text
            base_model = model_card.data.get("base_model", [])
            tags = model_card.data.get("tags", [])
            license_info = model_card.data.get("license", "Unknown")
            
            # Get model info from API as fallback for stats
            api = HuggingFaceAPI(resolved_api_key)
            api_info = api.get_model_info(parsed_model_id)
            
            stats = {}
            if api_info and not isinstance(api_info, dict) or "error" not in api_info:
                stats = {
                    "downloads": api_info.get("downloads", 0),
                    "likes": api_info.get("likes", 0),
                    "created_at": api_info.get("created_at", ""),
                    "modified_at": api_info.get("modified_at", "")
                }
            
            response_data = {
                "model_name": model_name,
                "creator_username": creator_username,
                "description": description,
                "base_model": base_model,
                "tags": tags,
                "license": license_info,
                "stats": stats,
                "model_id": parsed_model_id,
                "huggingface_model_name": model_name
            }
            
            return web.json_response(response_data)
            
        except Exception as e:
            print(f"[GetModelDetails] Error loading model card: {e}")
            # Fallback to basic info
            return web.json_response({
                "model_name": parsed_model_id.split('/')[-1],
                "creator_username": "Unknown",
                "description": "No description available",
                "base_model": [],
                "tags": [],
                "license": "Unknown",
                "stats": {},
                "model_id": parsed_model_id,
                "huggingface_model_name": parsed_model_id.split('/')[-1]
            })
            
    except Exception as e:
        print(f"Error in get_model_details: {e}")
        traceback.print_exc()
        return web.json_response({"error": "Internal Server Error", "details": str(e)}, status=500)
