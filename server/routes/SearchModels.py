# ================================================
# File: server/routes/SearchModels.py
# ================================================
import json
import traceback
from aiohttp import web

import server # ComfyUI server instance
from ..utils import get_request_json, resolve_huggingface_api_key
from ...config import HUGGINGFACE_API_TYPE_MAP

prompt_server = server.PromptServer.instance

@prompt_server.routes.post("/api/huggingface/search")
async def route_search_models(request):
    """API Endpoint for searching models using huggingface_hub."""
    try:
        data = await get_request_json(request)

        query = data.get("query", "").strip()
        model_type_keys = data.get("model_types", []) # e.g., ["lora", "checkpoint"]
        base_model_filters = data.get("base_models", []) # e.g., ["SD 1.5", "Pony"]
        sort = data.get("sort", "Most Downloaded")
        limit = int(data.get("limit", 20))
        page = int(data.get("page", 1))
        resolved_api_key = resolve_huggingface_api_key(data)
        nsfw = data.get("nsfw", True)  # Default to True (enabled)

        if not query and not model_type_keys and not base_model_filters:
             raise web.HTTPBadRequest(reason="Search requires a query or at least one filter (type or base model).")

        # Use huggingface_hub for search
        try:
            from huggingface_hub import HfApi
            hf_api = HfApi(token=resolved_api_key)
            
            # Prepare search parameters
            search_params = {
                "limit": limit,
                "sort": sort.lower().replace(" ", "_")  # Convert "Most Downloaded" to "most_downloaded"
            }
            
            if query:
                search_params["search"] = query
            
            # Map model types to tags
            if model_type_keys:
                tags = []
                for key in model_type_keys:
                    api_type = HUGGINGFACE_API_TYPE_MAP.get(key.lower())
                    if api_type:
                        tags.append(api_type.lower())
                if tags:
                    search_params["tags"] = tags
            
            # Add base model filters as part of query if specified
            if base_model_filters:
                base_model_query = " ".join([f'base_model:{bm}' for bm in base_model_filters])
                if query:
                    search_params["search"] = f"{query} {base_model_query}"
                else:
                    search_params["search"] = base_model_query
            
            print(f"[Server Search] huggingface_hub: search='{search_params.get('search', '<none>')}', tags={search_params.get('tags', 'Any')}, sort={sort}, limit={limit}")
            
            # Perform search
            models = hf_api.list_models(**search_params)
            
            # Format results for frontend
            formatted_models = []
            for model in models:
                formatted_model = {
                    "id": model.id,
                    "name": model.id.split('/')[-1],
                    "description": model.tags or "",
                    "creator": {"username": model.author or ""},
                    "modelId": model.id,
                    "downloads": model.downloads or 0,
                    "likes": model.likes or 0,
                    "tags": model.tags or [],
                    "modelType": "Unknown",  # Will be determined by frontend
                    "baseModel": [],  # Will be determined by frontend
                    "stats": {
                        "downloadCount": model.downloads or 0,
                        "thumbsUpCount": model.likes or 0
                    }
                }
                formatted_models.append(formatted_model)
            
            response_data = {
                "items": formatted_models,
                "metadata": {
                    "currentPage": page,
                    "pageSize": limit,
                    "totalItems": len(formatted_models),
                    "totalPages": 1  # huggingface_hub doesn't provide pagination info
                }
            }
            
            return web.json_response(response_data)
            
        except Exception as e:
            print(f"[Server Search] huggingface_hub search failed: {e}")
            return web.json_response({"error": "Search failed", "details": str(e)}, status=500)
            
    except Exception as e:
        print(f"Error in search_models: {e}")
        traceback.print_exc()
        return web.json_response({"error": "Internal Server Error", "details": str(e)}, status=500)
