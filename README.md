# ComfyUI-HuggingFace - HuggingFace Model Downloader for ComfyUI

ComfyUI-HuggingFace seamlessly integrates HuggingFace's vast model repository directly into ComfyUI, allowing you to search, download, and organize AI models without leaving your workflow.

<img width="1016" height="833" alt="comfyhf" src="https://github.com/user-attachments/assets/3867b704-1b14-4c02-87d4-fc2a61deeb42" />

## Features

- **Integrated Model Search**: Search HuggingFace's extensive library directly from ComfyUI
- **One-Click Downloads**: Download models with associated metadata and files
- **Automatic Organization**: Models are automatically saved to their appropriate directories
- **Clean UI**: Clean, intuitive interface that complements ComfyUI's aesthetic
- **HF API Integration**: Full support for HuggingFace API endpoints
- **Model Type Detection**: Automatically categorizes models (checkpoints, loras, etc.)

## Installation

### Git Clone
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/huchukato/ComfyUI-HuggingFace.git
```

## Usage

1. Start ComfyUI with ComfyUI-HuggingFace installed
2. Access the HuggingFace panel from the HuggingFace menu button at the right top area
3. Search for models using HuggingFace's powerful search
4. Click the download button on any model to save it to your local installation
5. Models become immediately available in ComfyUI nodes

## Configuration

- **HuggingFace API Token**: Optional but recommended for higher rate limits
  - Set `HUGGINGFACE_API_KEY` environment variable
  - Or enter token in ComfyUI-HuggingFace settings
- **Global Download Root**: Optional custom download directory
  - When set, saves to `<global_root>/<model_type>` 
  - Example: `/runpod-volume/ComfyUI/checkpoints`
  - When empty, uses default ComfyUI paths

## Supported Model Types

- **Checkpoints**: Main model files (.safetensors, .bin)
- **LoRAs**: Low-Rank Adaptation models
- **Text Encoders**: CLIP and other encoder models
- **VAEs**: Variational Autoencoders
- **Embeddings**: Text embedding models
- **Custom**: Any model type from HuggingFace

## API Endpoints Used

- `/api/models` - Model search
- `/api/models/{id}` - Model information
- `/api/models/{id}/tree` - File listing
- `/api/models/{id}/resolve/main/{filename}` - File downloads

## Development

This is a fork of Civicomfy, adapted for HuggingFace integration:

- Replaced Civitai API with HuggingFace API
- Updated URL parsing for HF model structure
- Maintained the same clean UI/UX
- Added HF-specific features

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Areas for Contribution

- Additional model type support
- UI/UX improvements
- Performance optimizations
- Bug fixes and testing

## Requirements

- ComfyUI
- Python 3.8+
- requests library
- Valid HuggingFace account (optional)

## License

This project follows the same license as the original Civicomfy project.

## Acknowledgments

- Based on [Civicomfy](https://github.com/MoonGoblinDev/Civicomfy) by MoonGoblinDev
- HuggingFace for the amazing model repository
- ComfyUI community for feedback and support
