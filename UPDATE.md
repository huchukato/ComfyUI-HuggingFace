# Update Log

## Version 1.1.1

- Security: confine download `save_root`, `subdir` and `create_dir` `root` to known model roots (ComfyUI models dir, registered folder_paths, plugin custom roots); reject path-traversal in `model_type`. Addresses the registry `policy-v0.4: path-traversal` flag on 1.1.0.
- Publish workflow: changelog extraction rewritten in plain shell (no embedded Python) to avoid registry scanner false positives on workflow files.

## Version 1.1.0

- Updated registry metadata for Comfy Node Registry (publisher, description, icon, banner).
- HuggingFace model downloader node: browse, search and download models directly into ComfyUI folders, with one-click "open folder" after download.
