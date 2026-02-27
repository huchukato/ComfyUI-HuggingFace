# ComfyUI-HuggingFace - HuggingFace Model Downloader for ComfyUI

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Compatible-orange.svg)](https://github.com/comfyanonymous/ComfyUI)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Integrated-yellow.svg)](https://huggingface.co)
[![Italian](https://img.shields.io/badge/Italian-🇮🇹-red.svg)](README_IT.md)

[![buy-me-coffees](https://i.imgur.com/3MDbAtw.png)](https://buymeacoffee.com/huchukato)

ComfyUI-HuggingFace integra perfettamente l'enorme repository di modelli HuggingFace direttamente in ComfyUI, permettendoti di cercare, scaricare e organizzare modelli AI senza lasciare il tuo workflow.

![ComfyUI-HuggingFace](https://github.com/user-attachments/assets/3867b704-1b14-4c02-87d4-fc2a61deeb42)

## ✨ Features

### 🔍 **Advanced Search & Discovery**
- **Full HuggingFace Integration**: Search HuggingFace's entire model library directly from ComfyUI
- **Smart Filtering**: Filter by model types (LoRA, Checkpoints, Diffusers, etc.)
- **Base Model Filtering**: Filter by SD 1.5, SDXL, Pony, and other base models
- **Multiple Sort Options**: Sort by downloads, likes, newest, or relevancy
- **NSFW Support**: NSFW content enabled by default (can be disabled)
- **Real-time Results**: Instant search results with model previews

### 📥 **Intelligent Download System**
- **Dual Download Modes**: 
  - **Single Files**: Download specific model files with `hf_hub_download`
  - **Full Repos**: Download entire repositories with `snapshot_download` (perfect for Diffusers)
- **Automatic Type Detection**: Smart categorization of models (checkpoints, LoRAs, etc.)
- **Metadata Preservation**: Downloads include model cards, descriptions, and statistics
- **Resume Support**: Resume interrupted downloads
- **Multi-connection Downloads**: Faster downloads with parallel connections

### 🎯 **Model Management**
- **Automatic Organization**: Models saved to correct ComfyUI directories
- **Custom Filename Support**: Rename models during download
- **Preview Images**: Download and display model thumbnails
- **Version Control**: Track model versions and updates
- **Download History**: View and manage download history

### 🛠 **Technical Features**
- **Pure huggingface_hub**: Uses official `huggingface_hub` library exclusively
- **No REST API Dependencies**: Eliminates unreliable API calls
- **Robust Error Handling**: Graceful fallbacks for missing information
- **Private Repository Support**: Access private models with API tokens
- **Clean Error Messages**: User-friendly notifications without scary errors

## 🚀 Installation

### Automatic Installation (Recommended)
1. Open ComfyUI Manager
2. Search for "ComfyUI-HuggingFace"
3. Click Install

### Manual Installation
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/huchukato/ComfyUI-HuggingFace.git
```

## 📖 Usage

1. **Start ComfyUI** with ComfyUI-HuggingFace installed
2. **Access the Panel**: Click the HuggingFace button in the top-right area
3. **Search Models**: Use the search bar with filters and sorting options
4. **Preview Models**: Click on any model to see details and preview
5. **Download**: Click the download button to save models locally
6. **Use in ComfyUI**: Models appear automatically in ComfyUI nodes

## ⚙️ Configuration

### HuggingFace API Token (Optional but Recommended)
- **Environment Variable**: `HUGGINGFACE_API_KEY`
- **In-App Settings**: Enter token in ComfyUI-HuggingFace settings
- **Benefits**: Higher rate limits, access to private models

### Global Download Root (Optional)
- **Setting**: Custom download directory
- **Format**: `<global_root>/<model_type>`
- **Example**: `/runpod-volume/ComfyUI/checkpoints`
- **Default**: Uses standard ComfyUI paths when empty

## 📁 Supported Model Types

| Type | Description | Directory |
|-------|-------------|------------|
| **Checkpoints** | Main model files (.safetensors, .bin) | `checkpoints/` |
| **LoRAs** | Low-Rank Adaptation models | `loras/` |
| **Diffusers** | Complete diffusion pipelines | `diffusers/` |
| **Text Encoders** | CLIP and encoder models | `text_encoders/` |
| **VAEs** | Variational Autoencoders | `vae/` |
| **Embeddings** | Text embedding models | `embeddings/` |
| **ControlNet** | Control models | `controlnet/` |
| **IP-Adapters** | Image adapter models | `ip_adapters/` |
| **Custom** | Any model type from HuggingFace | User-defined |

## 🔧 Technical Implementation

### Core Technologies
- **huggingface_hub**: Official HuggingFace Python library
- **snapshot_download**: For complete repository downloads
- **hf_hub_download**: For single file downloads
- **ModelCard**: For reading model metadata and descriptions
- **HfApi**: For searching and listing models

### API Endpoints
- `POST /api/huggingface/search` - Model search with filters
- `POST /api/huggingface/get_model_details` - Model information
- `POST /api/huggingface/download` - Initiate downloads
- `GET /api/huggingface/base_models` - Available base models
- `POST /api/huggingface/cancel` - Cancel downloads
- `GET /api/huggingface/download_status` - Download progress
- `GET /api/huggingface/history` - Download history
- `GET /api/huggingface/model_dirs` - Available model directories

### Error Handling Strategy
1. **Primary**: Use `huggingface_hub` functions directly
2. **Fallback 1**: Try API calls for additional metadata
3. **Fallback 2**: Return minimal information without errors
4. **UI**: Show user-friendly messages instead of scary errors

## 🔄 Migration from Civicomfy

This is a complete rewrite of Civicomfy with HuggingFace integration:

### What Changed
- ✅ **Replaced Civitai API** with HuggingFace API
- ✅ **Updated URL parsing** for HF model structure  
- ✅ **Maintained clean UI/UX** from original
- ✅ **Added HF-specific features** (repo downloads, model cards)
- ✅ **Improved error handling** and user experience
- ✅ **Removed REST API dependencies** for reliability

### What's Better
- 🚀 **More Reliable**: Official `huggingface_hub` library
- 🎯 **More Models**: Access to entire HuggingFace repository
- 📁 **Smart Downloads**: Repo vs single file detection
- 🛡️ **Better Security**: No more direct URL construction
- 🎨 **Cleaner UI**: No scary error messages

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Areas for Contribution
- **Additional Model Types**: Support for new model formats
- **UI/UX Improvements**: Better user interface and experience
- **Performance Optimizations**: Faster downloads and search
- **Bug Fixes**: Testing and issue resolution
- **Documentation**: Improving guides and examples

### Development Setup
```bash
git clone https://github.com/huchukato/ComfyUI-HuggingFace.git
cd ComfyUI-HuggingFace
# Install dependencies
pip install -r requirements.txt
# Test with ComfyUI
```

## 📋 Requirements

### System Requirements
- **ComfyUI**: Latest version recommended
- **Python**: 3.8+ 
- **Memory**: 4GB+ RAM recommended
- **Storage**: Sufficient space for model downloads

### Python Dependencies
- `huggingface_hub>=0.20.0` - HuggingFace integration
- `requests>=2.25.0` - HTTP requests
- `aiohttp` - Async web server (ComfyUI)

### Optional Dependencies
- `HUGGINGFACE_API_KEY` - For higher rate limits
- Custom model directories - For organization

## 📄 License

This project follows the same license as the original Civicomfy project.

## 🙏 Acknowledgments

- **[Civicomfy](https://github.com/MoonGoblinDev/Civicomfy)** by MoonGoblinDev - Original inspiration and base
- **[HuggingFace](https://huggingface.co)** - Amazing model repository and API
- **[ComfyUI Community](https://github.com/comfyanonymous/ComfyUI)** - Feedback, testing, and support
- **[huggingface_hub](https://github.com/huggingface/huggingface_hub)** - Official Python library

## 📞 Support

- **Issues**: Report bugs via GitHub Issues
- **Features**: Request features via GitHub Discussions  
- **Discord**: Join the ComfyUI community
- **Updates**: Follow the repository for latest features

---

**⭐ If you find this useful, please give it a star on GitHub!**

**Made with ❤️ for the ComfyUI community**

---

**🇮🇹 [Italian Documentation](README_IT.md)** - Read the docs in Italian
