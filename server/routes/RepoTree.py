# ================================================
# File: server/routes/RepoTree.py
# ================================================
import traceback
from aiohttp import web

import server  # ComfyUI server instance
from ..utils import get_request_json, resolve_huggingface_api_key
from ...utils.helpers import parse_huggingface_input

prompt_server = server.PromptServer.instance


@prompt_server.routes.post("/api/huggingface/repo_tree")
async def route_repo_tree(request):
    """API Endpoint to list files/folders in a HuggingFace repo revision."""
    try:
        data = await get_request_json(request)

        repo_id_input = data.get("repo_id", "").strip()
        path = data.get("path", "").strip()
        revision = data.get("revision", "main").strip() or "main"
        resolved_api_key = resolve_huggingface_api_key(data)

        if not repo_id_input:
            raise web.HTTPBadRequest(reason="Missing 'repo_id'")

        parsed_model_id, _ = parse_huggingface_input(repo_id_input)
        repo_id = parsed_model_id or repo_id_input

        try:
            from huggingface_hub import HfApi
            from huggingface_hub.hf_api import RepoFile, RepoFolder
        except Exception as import_err:
            return web.json_response(
                {"error": "huggingface_hub not available", "details": str(import_err)},
                status=500,
            )

        try:
            hf_api = HfApi(token=resolved_api_key)

            # list_repo_tree is the modern way to get a file/folder listing.
            # It is available in recent versions of huggingface_hub; fall back
            # to list_repo_files if it is missing.
            if hasattr(hf_api, "list_repo_tree"):
                items = []
                for item in hf_api.list_repo_tree(repo_id, path_in_repo=path, revision=revision):
                    if isinstance(item, RepoFolder):
                        items.append({
                            "type": "directory",
                            "path": item.path,
                            "size": None,
                        })
                    elif isinstance(item, RepoFile):
                        items.append({
                            "type": "file",
                            "path": item.path,
                            "size": getattr(item, "size", None),
                            "lfs": getattr(item, "lfs", None) is not None,
                        })
                    else:
                        # Future-proof: any item-like object
                        items.append({
                            "type": getattr(item, "type", "file"),
                            "path": getattr(item, "path", ""),
                            "size": getattr(item, "size", None),
                            "lfs": None,
                        })
            else:
                raw_files = hf_api.list_repo_files(repo_id, revision=revision)
                prefix = (path + "/") if path else ""
                items = []
                seen_dirs = set()
                for f in raw_files:
                    if not f.startswith(prefix):
                        continue
                    rest = f[len(prefix):]
                    if "/" in rest:
                        dir_name = rest.split("/")[0]
                        dir_path = (path + "/" + dir_name) if path else dir_name
                        if dir_path not in seen_dirs:
                            seen_dirs.add(dir_path)
                            items.append({"type": "directory", "path": dir_path, "size": None})
                    else:
                        items.append({"type": "file", "path": f, "size": None, "lfs": None})

            return web.json_response({
                "repo_id": repo_id,
                "path": path,
                "revision": revision,
                "items": items,
            })

        except Exception as e:
            print(f"[RepoTree] Error listing repo tree for {repo_id}: {e}")
            traceback.print_exc()
            return web.json_response(
                {"error": "Failed to list repository contents", "details": str(e)},
                status=500,
            )

    except web.HTTPException:
        raise
    except Exception as e:
        print(f"Error in repo_tree: {e}")
        traceback.print_exc()
        return web.json_response(
            {"error": "Internal Server Error", "details": str(e)},
            status=500,
        )
