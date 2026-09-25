# Update Log

## Version 1.1.4

- Removed the bogus `requires-comfyui >=1.0.0` constraint — ComfyUI versions are 0.x, and the mismatch was disabling the node pack in ComfyUI Manager.

## Version 1.1.3

- Removed the unused Meilisearch search method (dead code — search already goes through the official `huggingface_hub` library).
- Replaced a dynamic `__import__('folder_paths')` lookup with a plain import in the open-path safety check; it also fixes `models_dir` always resolving to None.

## Version 1.1.2

- Security: confine download `save_root`, `subdir` and `create_dir` `root` to known model roots (ComfyUI models dir, registered folder_paths, plugin custom roots); reject path-traversal in `model_type`. Addresses the registry `policy-v0.4: path-traversal` flag on 1.1.0.
- Publish workflow: changelog extraction rewritten in plain shell (no embedded Python) to avoid registry scanner false positives on workflow files.

## Version 1.1.0

- Updated registry metadata for Comfy Node Registry (publisher, description, icon, banner).
- HuggingFace model downloader node: browse, search and download models directly into ComfyUI folders, with one-click "open folder" after download.
