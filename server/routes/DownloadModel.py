# ================================================
# File: server/routes/DownloadModel.py
# ================================================
import os
import json
import traceback
import re
from aiohttp import web

import server # ComfyUI server instance
from ..utils import get_request_json, resolve_huggingface_api_key
from ...downloader.manager import manager as download_manager
from ...api.huggingface import HuggingFaceAPI
from ...utils.helpers import get_model_dir, parse_huggingface_input, sanitize_filename
from ...config import METADATA_SUFFIX, PREVIEW_SUFFIX

prompt_server = server.PromptServer.instance

@prompt_server.routes.post("/api/huggingface/download")
async def route_download_model(request):
    """API Endpoint to initiate a download."""
    try:
        data = await get_request_json(request)

        model_url_or_id = data.get("model_url_or_id")
        model_type_value = data.get("model_type", "checkpoint")
        explicit_save_root = (data.get("save_root") or "").strip()
        custom_filename_input = data.get("custom_filename", "").strip()
        selected_subdir = (data.get("subdir") or "").strip()
        num_connections = int(data.get("num_connections", 4))
        force_redownload = bool(data.get("force_redownload", False))
        resolved_api_key = resolve_huggingface_api_key(data)

        if not model_url_or_id:
            raise web.HTTPBadRequest(reason="Missing 'model_url_or_id'")

        print(f"[HF Download] Request: {model_url_or_id}, SaveType: {model_type_value}")
        
        # Parse HuggingFace URL/ID
        parsed_model_id, parsed_filename = parse_huggingface_input(model_url_or_id)
        
        if not parsed_model_id:
            raise web.HTTPBadRequest(reason=f"Could not parse HuggingFace model ID from: {model_url_or_id}")
        
        target_model_id = parsed_model_id
        print(f"[HF Download] Parsed Model ID: {target_model_id}")
        
        # Initialize API
        api = HuggingFaceAPI(resolved_api_key)
        
        if parsed_filename:
            # Direct download from URL - skip API calls
            target_filename = parsed_filename
            # Try to get model name from the model_id itself
            model_name = target_model_id.split('/')[-1] if target_model_id else "Unknown Model"
            model_info = {"id": target_model_id, "name": model_name}
            print(f"[HF Download] Direct download file: {target_filename}")
            print(f"[HF Download] Using extracted model name: {model_name}")
        else:
            # Get model info and file list
            api = HuggingFaceAPI(resolved_api_key)
            model_info = api.get_model_info(target_model_id)
            
            if not model_info or "error" in model_info:
                print(f"[HF Download] Model info failed, trying direct download")
                # Fallback: try direct download without file listing
                target_filename = parsed_filename if parsed_filename else "model.safetensors"  # Use parsed or default
                # Try to get model name from the model_id itself
                model_name = target_model_id.split('/')[-1] if target_model_id else "Unknown Model"
                model_info = {"id": target_model_id, "name": model_name}
            else:
                # Get file list
                files_info = api.get_model_files(target_model_id)
                if not files_info or "error" in files_info:
                    print(f"[HF Download] File list failed, trying direct download")
                    # Fallback: try direct download without file listing
                    target_filename = parsed_filename if parsed_filename else "model.safetensors"  # Use parsed or default
                    model_info = {"id": target_model_id, "name": target_model_id}
                else:
                    # Find the best file to download
                    target_filename = None
                    if isinstance(files_info, list):
                        # First try .safetensors files
                        for file_info in files_info:
                            if (file_info.get("type") == "file" and 
                                file_info.get("path", "").endswith(".safetensors")):
                                target_filename = file_info["path"]
                                break
                    
                    # If no .safetensors found, pick the largest file
                    if not target_filename:
                        largest_file = max(files_info, key=lambda x: x.get("size", 0), default=None)
                        if largest_file and largest_file.get("type") == "file":
                            target_filename = largest_file["path"]
        
        if not target_filename:
            raise web.HTTPBadRequest(reason="No suitable file found for download")
        
        print(f"[HF Download] Target file: {target_filename}")

        # Determine save directory
        target_dir = get_model_dir(model_type_value, explicit_save_root, selected_subdir)
        if not target_dir:
            raise web.HTTPBadRequest(reason=f"Invalid model type: {model_type_value}")

        # Determine filename
        if custom_filename_input:
            final_filename = sanitize_filename(custom_filename_input)
        else:
            final_filename = os.path.basename(target_filename)
        
        save_path = os.path.join(target_dir, final_filename)

        # Check if file exists
        if os.path.exists(save_path) and not force_redownload:
            raise web.HTTPBadRequest(reason=f"File already exists: {final_filename}")

        # Start download
        download_url = f"https://huggingface.co/{target_model_id}/resolve/main/{target_filename}"
        
        download_info = {
            "model_url_or_id": model_url_or_id,
            "save_path": save_path,
            "output_path": save_path,  # Add this for ChunkDownloader
            "url": download_url,  # Add this for ChunkDownloader
            "filename": final_filename,
            "model_type": model_type_value,
            "download_url": download_url,
            "huggingface_model_info": model_info,
            "huggingface_filename": target_filename,
            "num_connections": num_connections,
            "force_redownload": force_redownload
        }

        download_id = download_manager.add_to_queue(download_info)
        
        # Extract model name from model_info if available, otherwise from model_id
        print(f"[DEBUG] model_info: {model_info}")
        print(f"[DEBUG] target_model_id: {target_model_id}")
        
        # Try to parse model_info as JSON if it's a string
        parsed_model_info = None
        if isinstance(model_info, str):
            try:
                import json
                parsed_model_info = json.loads(model_info)
                print(f"[DEBUG] Parsed model_info from JSON: {parsed_model_info}")
            except:
                print(f"[DEBUG] Failed to parse model_info as JSON")
                parsed_model_info = None
        else:
            parsed_model_info = model_info
        
        if parsed_model_info and isinstance(parsed_model_info, dict) and parsed_model_info.get('name'):
            model_display_name = parsed_model_info['name']
            print(f"[DEBUG] Using parsed model_info name: {model_display_name}")
        elif model_info and isinstance(model_info, dict) and model_info.get('name'):
            model_display_name = model_info['name']
            print(f"[DEBUG] Using model_info name: {model_display_name}")
        else:
            model_display_name = target_model_id.split('/')[-1] if target_model_id else "Unknown Model"
            print(f"[DEBUG] Using parsed name: {model_display_name}")
        
        print(f"[DEBUG] Final model_display_name: {model_display_name}")
        
        response_data = {
            "download_id": download_id,
            "huggingface_model_id": target_model_id,
            "huggingface_model_name": model_display_name,  # Add model name
            "huggingface_filename": target_filename,
            "huggingface_model_info": model_info,
            "save_path": save_path,
            "filename": final_filename,
            "status": "queued"  # Changed from "started" to "queued" to match frontend expectation
        }
        
        print(f"[DEBUG] Response data huggingface_model_name: {response_data['huggingface_model_name']}")

        return web.json_response(response_data)

    except web.HTTPException:
        raise
    except Exception as e:
        print(f"--- Unhandled Error in /huggingface/download ---")
        traceback.print_exc()
        raise web.HTTPInternalServerError(reason=str(e))
