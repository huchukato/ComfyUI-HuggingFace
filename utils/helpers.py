# ================================================
# File: utils/helpers.py
# ================================================
import os
import urllib.parse
import re 
from pathlib import Path
from typing import Optional, List, Dict, Any

import folder_paths 

# Import config values needed here
from ..config import PLUGIN_ROOT, MODEL_TYPE_DIRS

# Canonical aliases for model type/folder names. Values are preferred folder names.
MODEL_TYPE_ALIASES = {
    "checkpoint": "checkpoints",
    "checkpoints": "checkpoints",
    "diffusionmodel": "diffusion_models",
    "diffusionmodels": "diffusion_models",
    "diffusion_model": "diffusion_models",
    "diffusion_models": "diffusion_models",
    "diffusers": "diffusers",
    "unet": "unet",
    "lora": "loras",
    "loras": "loras",
    "locon": "loras",
    "lycoris": "loras",
    "vae": "vae",
    "embedding": "embeddings",
    "embeddings": "embeddings",
    "textualinversion": "embeddings",
    "hypernetwork": "hypernetworks",
    "hypernetworks": "hypernetworks",
    "controlnet": "controlnet",
    "upscaler": "upscale_models",
    "upscalers": "upscale_models",
    "upscale_model": "upscale_models",
    "upscale_models": "upscale_models",
    "motionmodule": "motion_models",
    "motionmodules": "motion_models",
    "motion_model": "motion_models",
    "motion_models": "motion_models",
}

MODEL_TYPE_ALIASES_COMPACT = {
    re.sub(r'[^a-z0-9]', '', k): v for k, v in MODEL_TYPE_ALIASES.items()
}

def _normalize_model_type(model_type: str) -> str:
    """Normalize model type string to canonical form."""
    if not model_type:
        return "other"
    
    normalized = model_type.lower().strip()
    
    # Try exact match first
    if normalized in MODEL_TYPE_ALIASES:
        return MODEL_TYPE_ALIASES[normalized]
    
    # Try compact match (remove non-alphanumeric chars)
    compact = re.sub(r'[^a-z0-9]', '', normalized)
    if compact in MODEL_TYPE_ALIASES_COMPACT:
        return MODEL_TYPE_ALIASES_COMPACT[compact]
    
    return "other"

def get_model_dir(model_type: str, explicit_save_root: str = "", selected_subdir: str = "") -> Optional[str]:
    """Get the directory path for a given model type."""
    try:
        # Normalize the model type
        normalized_type = _normalize_model_type(model_type)
        
        # Use explicit root if provided
        if explicit_save_root:
            base_path = explicit_save_root
            # If selected_subdir is provided, append it
            if selected_subdir:
                base_path = os.path.join(base_path, selected_subdir)
            return base_path
        
        # Try ComfyUI's folder_paths first
        try:
            if normalized_type in ["checkpoints", "loras", "vae", "embeddings", "hypernetworks", "controlnet", "upscale_models"]:
                return folder_paths.get_folder_paths(normalized_type)[0]
            elif normalized_type in ["diffusion_models", "motion_models", "unet", "diffusers"]:
                # These might not be standard ComfyUI types, try to get them
                try:
                    return folder_paths.get_folder_paths(normalized_type)[0]
                except:
                    # Fallback to custom_nodes directory
                    return os.path.join(folder_paths.base_path, "custom_nodes", normalized_type)
            else:
                # For other types, use custom_nodes
                return os.path.join(folder_paths.base_path, "custom_nodes", normalized_type)
        except:
            # Fallback to base_path + type
            return os.path.join(folder_paths.base_path, normalized_type)
            
    except Exception as e:
        print(f"Error getting model directory for {model_type}: {e}")
        return None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage."""
    if not filename:
        return "unnamed_file"
    
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized.strip()

def parse_huggingface_input(url_or_id: str) -> tuple[str | None, str | None]:
    """
    Parses HuggingFace URL or ID string.
    Returns: (model_id, filename) tuple. Both can be None.
    Handles URLs like:
    - https://huggingface.co/FX-FeiHou/wan2.2-Remix/resolve/main/NSFW/Wan2.2_Remix_NSFW_i2v_14b_high_lighting_fp8_e4m3fn_v2.1.safetensors
    - FX-FeiHou/wan2.2-Remix
    """
    if not url_or_id:
        return None, None

    url_or_id = str(url_or_id).strip()
    model_id: str | None = None
    filename: str | None = None

    # Check if it's a direct download URL
    if "/resolve/main/" in url_or_id:
        try:
            parsed_url = urllib.parse.urlparse(url_or_id)
            
            # Extract model ID from path
            path_parts = parsed_url.path.split('/')
            if len(path_parts) >= 2 and path_parts[1] == "resolve":
                # URL format: /FX-FeiHou/wan2.2-Remix/resolve/main/NSFW/file.safetensors
                model_id = "/".join(path_parts[0:2])  # FX-FeiHou/wan2.2-Remix
                filename = "/".join(path_parts[4:])  # NSFW/file.safetensors
                print(f"Parsed HF download URL - Model: {model_id}, File: {filename}")
                return model_id, filename
        except Exception as e:
            print(f"Warning: Could not parse HF download URL '{url_or_id}': {e}")
            return None, None
    
    # Check if it's a simple model ID (username/repo format)
    if "/" in url_or_id and not url_or_id.startswith("http"):
        parts = url_or_id.split("/")
        if len(parts) >= 2:
            model_id = "/".join(parts[0:2])
            print(f"Parsed HF model ID: {model_id}")
            return model_id, None
    
    # Try parsing as full URL
    try:
        parsed_url = urllib.parse.urlparse(url_or_id)
        
        if "huggingface.co" in parsed_url.netloc.lower():
            path_parts = parsed_url.path.split('/')
            if len(path_parts) >= 3:
                model_id = "/".join(path_parts[1:3])  # Extract username/repo
                print(f"Parsed HF URL - Model: {model_id}")
                return model_id, None
    except Exception as e:
        print(f"Warning: Could not parse HF URL '{url_or_id}': {e}")
    
    print(f"Input '{url_or_id}' is not a recognizable HF model ID or URL.")
    return None, None
