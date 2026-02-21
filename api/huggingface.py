# ================================================
# File: api/huggingface.py
# ================================================
import requests
import json
from typing import List, Optional, Dict, Any, Union

# Try to import huggingface_hub for better downloads
try:
    from huggingface_hub import hf_hub_download, snapshot_download
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False
    print("[HuggingFace API] huggingface_hub not available, falling back to manual downloads")

# Try to use huggingface_hub CLI as fallback
import subprocess
import sys

class HuggingFaceAPI:
    """Simple wrapper for interacting with the HuggingFace API."""
    BASE_URL = "https://huggingface.co/api"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_headers = {'Content-Type': 'application/json'}
        if api_key:
            self.base_headers["Authorization"] = f"Bearer {api_key}"
            print("[HuggingFace API] Using HF token for private repositories.")
        else:
            print("[HuggingFace API] No HF token provided. Only public repositories accessible.")

    def _get_request_headers(self, method: str, has_json_data: bool) -> Dict[str, str]:
        """Returns headers for a specific request."""
        headers = self.base_headers.copy()
        # Don't send content-type for GET/HEAD if no json_data
        if method.upper() in ["GET", "HEAD"] and not has_json_data:
            headers.pop('Content-Type', None)
        return headers

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                 json_data: Optional[Dict] = None, stream: bool = False,
                 allow_redirects: bool = True, timeout: int = 30) -> Union[Dict[str, Any], requests.Response, None]:
        """Makes a request to the HuggingFace API and handles basic errors."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        request_headers = self._get_request_headers(method, json_data is not None)

        try:
            response = requests.request(
                method,
                url,
                headers=request_headers,
                params=params,
                json=json_data,
                stream=stream,
                allow_redirects=allow_redirects,
                timeout=timeout
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            if stream:
                return response  # Return the response object for streaming

            # Handle No Content response (e.g., 204)
            if response.status_code == 204 or not response.content:
                return None

            return response.json()

        except requests.exceptions.HTTPError as http_err:
            error_detail = None
            status_code = http_err.response.status_code
            try:
                error_detail = http_err.response.json()
            except json.JSONDecodeError:
                error_detail = http_err.response.text[:200] # First 200 chars
            print(f"HuggingFace API HTTP Error ({method} {url}): Status {status_code}, Response: {error_detail}")
            # Return a structured error dictionary
            return {"error": f"HTTP Error: {status_code}", "details": error_detail, "status_code": status_code}

        except requests.exceptions.RequestException as req_err:
            print(f"HuggingFace API Request Error ({method} {url}): {req_err}")
            return {"error": str(req_err), "details": None, "status_code": None}

        except json.JSONDecodeError as json_err:
            print(f"HuggingFace API Error: Failed to decode JSON response from {url}: {json_err}")
            # Include response text if possible and not streaming
            response_text = response.text[:200] if not stream and hasattr(response, 'text') else "N/A"
            return {"error": "Invalid JSON response", "details": response_text, "status_code": response.status_code if hasattr(response, 'status_code') else None}

    def search_models(self, query: str, limit: int = 20) -> Optional[Dict[str, Any]]:
        """Searches for models on HuggingFace. (GET /models)"""
        endpoint = "/models"
        params = {
            "search": query,
            "limit": limit
        }
        result = self._request("GET", endpoint, params=params)
        if isinstance(result, dict) and "error" in result:
            return result
        return result

    def search_models_meili(self, query: str = None, types: Optional[List[str]] = None,
                            base_models: Optional[List[str]] = None,
                            sort: str = 'Most Downloaded', limit: int = 20, page: int = 1,
                            nsfw: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        """Searches models using HuggingFace's Meilisearch endpoint."""
        meili_url = "https://huggingface.co/multi-search"
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        # Build search query
        search_query = {
            "q": query or "",
            "limit": limit,
            "offset": (page - 1) * limit
        }
        
        # Add filters
        filters = []
        
        # Type filters
        if types:
            type_filter = {"type": types}
            filters.append(type_filter)
        
        # Base model filters  
        if base_models:
            base_filter = {"base_model": base_models}
            filters.append(base_filter)
        
        # NSFW filter
        if nsfw is not None:
            nsfw_filter = {"nsfw": nsfw}
            filters.append(nsfw_filter)
        
        if filters:
            search_query["filters"] = filters
        
        # Add sorting
        sort_mapping = {
            "Relevancy": "id:desc",
            "Most Downloaded": "metrics.downloadCount:desc",
            "Highest Rated": "metrics.thumbsUpCount:desc", 
            "Most Liked": "metrics.favoriteCount:desc", 
            "Most Discussed": "metrics.commentCount:desc", 
            "Most Collected": "metrics.collectedCount:desc", 
            "Most Buzz": "metrics.tippedAmountCount:desc", 
            "Newest": "createdAt:desc", 
        }
        
        if sort in sort_mapping:
            search_query["sort"] = [sort_mapping[sort]]
        
        try:
            response = requests.post(meili_url, json=search_query, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"HuggingFace Meili API Error: {e}")
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None}

    def get_model_files(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Gets files for a specific HuggingFace model. (GET /models/{id}/tree)"""
        endpoint = f"/models/{model_id}/tree"
        result = self._request("GET", endpoint)
        if isinstance(result, dict) and "error" in result:
            return result
        return result

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Gets information about a model by its ID. (GET /models/{id})"""
        endpoint = f"/models/{model_id}"
        result = self._request("GET", endpoint)
        if isinstance(result, dict) and "error" in result:
            return result
        return result

    def get_model_version_info(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Gets version information - not applicable for HuggingFace, returns empty dict"""
        # HuggingFace doesn't have version IDs like Civitai
        # This method is kept for compatibility but returns empty
        return {}

    def download_file(self, model_id: str, filename: str, local_dir: str = None) -> Optional[Union[requests.Response, str]]:
        """Downloads a specific file from HuggingFace. Uses huggingface_hub if available."""
        if HF_HUB_AVAILABLE and local_dir:
            try:
                # Use official huggingface_hub library
                print(f"[HuggingFace API] Using huggingface_hub for download: {model_id}/{filename}")
                result = hf_hub_download(
                    repo_id=model_id,
                    filename=filename,
                    local_dir=local_dir,
                    local_dir_use_symlinks=False,
                    resume_download=True,
                    token=self.api_key
                )
                return result  # Returns the local file path
            except Exception as e:
                print(f"[HuggingFace API] huggingface_hub download failed: {e}")
                print("[HuggingFace API] Trying CLI fallback...")
        
        # Try CLI fallback
        if local_dir:
            try:
                print(f"[HuggingFace API] Using CLI fallback for download: {model_id}/{filename}")
                cmd = [
                    sys.executable, "-m", "huggingface_hub", "download",
                    model_id, filename,
                    "--local-dir", local_dir
                ]
                if self.api_key:
                    cmd.extend(["--token", self.api_key])
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    file_path = os.path.join(local_dir, filename)
                    return file_path
                else:
                    print(f"[HuggingFace API] CLI download failed: {result.stderr}")
                    print("[HuggingFace API] Falling back to manual download")
            except Exception as e:
                print(f"[HuggingFace API] CLI fallback failed: {e}")
                print("[HuggingFace API] Falling back to manual download")
        
        # Final fallback to manual download
        endpoint = f"/models/{model_id}/resolve/main/{filename}"
        result = self._request("GET", endpoint, stream=True)
        if isinstance(result, dict) and "error" in result:
            return result
        return result
