# ComfyUI-HuggingFace - Downloader Modelli HuggingFace per ComfyUI

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Compatible-orange.svg)](https://github.com/comfyanonymous/ComfyUI)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Integrated-yellow.svg)](https://huggingface.co)
[![Italian](https://img.shields.io/badge/Language-🇮🇹-Italian-red.svg)](README.md)

ComfyUI-HuggingFace integra perfettamente l'enorme repository di modelli HuggingFace direttamente in ComfyUI, permettendoti di cercare, scaricare e organizzare modelli AI senza lasciare il tuo workflow.

![ComfyUI-HuggingFace](https://github.com/user-attachments/assets/3867b704-1b14-4c02-87d4-fc2a61deeb42)

## ✨ Funzionalità

### 🔍 **Ricerca e Scoperta Avanzata**
- **Integrazione Completa HuggingFace**: Cerca nell'intera libreria HuggingFace direttamente da ComfyUI
- **Filtraggio Intelligente**: Filtra per tipi di modelli (LoRA, Checkpoints, Diffusers, ecc.)
- **Filtraggio Base Model**: Filtra per SD 1.5, SDXL, Pony e altri modelli base
- **Opzioni di Ordinamento**: Ordina per download, like, più recenti o pertinenza
- **Supporto NSFW**: Contenuto NSFW abilitato di default (può essere disabilitato)
- **Risultati in Tempo Reale**: Risultati di ricerca istantanei con anteprime modelli

### 📥 **Sistema Download Intelligente**
- **Modalità Download Duali**: 
  - **File Singoli**: Scarica file specifici con `hf_hub_download`
  - **Repo Complete**: Scarica interi repository con `snapshot_download` (perfetto per Diffusers)
- **Rilevamento Automatico Tipi**: Categorizzazione automatica dei modelli (checkpoints, LoRA, ecc.)
- **Preservazione Metadata**: Download includono schede modelli, descrizioni e statistiche
- **Supporto Resume**: Riprendi download interrotti
- **Download Multi-connessione**: Download più veloci con connessioni parallele

### 🎯 **Gestione Modelli**
- **Organizzazione Automatica**: Modelli salvati nelle directory corrette di ComfyUI
- **Supporto Filename Personalizzati**: Rinomina modelli durante il download
- **Immagini Anteprima**: Scarica e mostra miniature modelli
- **Controllo Versioni**: Traccia versioni e aggiornamenti modelli
- **Cronologia Download**: Visualizza e gestisci cronologia download

### 🛠 **Funzionalità Tecniche**
- **Puro huggingface_hub**: Usa esclusivamente la libreria ufficiale `huggingface_hub`
- **Nessuna Dipendenza REST API**: Elimina chiamate API inaffidabili
- **Gestione Errori Robusta**: Fallback graceful per informazioni mancanti
- **Supporto Repository Privati**: Accedi modelli privati con token API
- **Messaggi Errore Puliti**: Notifiche user-friendly senza errori spaventosi

## 🚀 Installazione

### Installazione Automatica (Raccomandata)
1. Apri ComfyUI Manager
2. Cerca "ComfyUI-HuggingFace"
3. Clicca Installa

### Installazione Manuale
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/huchukato/ComfyUI-HuggingFace.git
```

## 📖 Utilizzo

1. **Avvia ComfyUI** con ComfyUI-HuggingFace installato
2. **Accedi al Pannello**: Clicca il pulsante HuggingFace nell'area in alto a destra
3. **Cerca Modelli**: Usa la barra di ricerca con filtri e opzioni di ordinamento
4. **Anteprima Modelli**: Clicca su qualsiasi modello per vedere dettagli e anteprima
5. **Download**: Clicca il pulsante download per salvare modelli localmente
6. **Usa in ComfyUI**: I modelli appaiono automaticamente nei nodi ComfyUI

## ⚙️ Configurazione

### Token API HuggingFace (Opzionale ma Raccomandato)
- **Variabile Ambiente**: `HUGGINGFACE_API_KEY`
- **Impostazioni App**: Inserisci token nelle impostazioni ComfyUI-HuggingFace
- **Benefici**: Limiti rate più alti, accesso a modelli privati

### Download Root Globale (Opzionale)
- **Impostazione**: Directory download personalizzata
- **Formato**: `<global_root>/<model_type>`
- **Esempio**: `/runpod-volume/ComfyUI/checkpoints`
- **Default**: Usa percorsi standard ComfyUI quando vuoto

## 📁 Tipi Modelli Supportati

| Tipo | Descrizione | Directory |
|-------|-------------|------------|
| **Checkpoints** | File modelli principali (.safetensors, .bin) | `checkpoints/` |
| **LoRAs** | Modelli Low-Rank Adaptation | `loras/` |
| **Diffusers** | Pipeline diffusion complete | `diffusers/` |
| **Text Encoders** | Modelli encoder CLIP e altri | `text_encoders/` |
| **VAEs** | Variational Autoencoders | `vae/` |
| **Embeddings** | Modelli embedding testo | `embeddings/` |
| **ControlNet** | Modelli control | `controlnet/` |
| **IP-Adapters** | Modelli adapter immagine | `ip_adapters/` |
| **Custom** | Qualsiasi tipo modello da HuggingFace | Definito dall'utente |

## 🔧 Implementazione Tecnica

### Tecnologie Core
- **huggingface_hub**: Libreria Python ufficiale HuggingFace
- **snapshot_download**: Per download repository completi
- **hf_hub_download**: Per download file singoli
- **ModelCard**: Per leggere metadata e descrizioni modelli
- **HfApi**: Per cercare e listare modelli

### Endpoint API
- `POST /api/huggingface/search` - Ricerca modelli con filtri
- `POST /api/huggingface/get_model_details` - Informazioni modello
- `POST /api/huggingface/download` - Avvia download
- `GET /api/huggingface/base_models` - Modelli base disponibili
- `POST /api/huggingface/cancel` - Cancella download
- `GET /api/huggingface/download_status` - Progresso download
- `GET /api/huggingface/history` - Cronologia download
- `GET /api/huggingface/model_dirs` - Directory modelli disponibili

### Strategia Gestione Errori
1. **Primario**: Usa funzioni `huggingface_hub` direttamente
2. **Fallback 1**: Prova chiamate API per metadata aggiuntive
3. **Fallback 2**: Restituisce informazioni minime senza errori
4. **UI**: Mostra messaggi user-friendly invece di errori spaventosi

## 🔄 Migrazione da Civicomfy

Questo è una riscrittura completa di Civicomfy con integrazione HuggingFace:

### Cosa È Cambiato
- ✅ **Sostituita API Civitai** con API HuggingFace
- ✅ **Aggiornato parsing URL** per struttura modelli HF
- ✅ **Mantenuta UI/UX pulita** dall'originale
- ✅ **Aggiunte funzionalità HF-specifiche** (download repo, schede modelli)
- ✅ **Migliorata gestione errori** e esperienza utente
- ✅ **Rimosse dipendenze REST API** per affidabilità

### Cosa È Meglio
- 🚀 **Più Affidabile**: Libreria ufficiale `huggingface_hub`
- 🎯 **Più Modelli**: Accesso all'intero repository HuggingFace
- 📁 **Download Intelligenti**: Rilevamento repo vs file singolo
- 🛡️ **Migliore Sicurezza**: Niente più costruzione URL diretta
- 🎨 **UI Più Pulita**: Niente più messaggi errore spaventosi

## 🤝 Contributi

I contributi sono benvenuti! Sentiti libero di inviare una Pull Request.

### Aree di Contributo
- **Tipi Modelli Aggiuntivi**: Supporto per nuovi formati modelli
- **Miglioramenti UI/UX**: Migliore interfaccia utente ed esperienza
- **Ottimizzazioni Performance**: Download e ricerca più veloci
- **Bug Fix**: Test e risoluzione problemi
- **Documentazione**: Miglioramento guide ed esempi

### Setup Sviluppo
```bash
git clone https://github.com/huchukato/ComfyUI-HuggingFace.git
cd ComfyUI-HuggingFace
# Installa dipendenze
pip install -r requirements.txt
# Testa con ComfyUI
```

## 📋 Requisiti

### Requisiti Sistema
- **ComfyUI**: Versione più recente raccomandata
- **Python**: 3.8+ 
- **Memoria**: 4GB+ RAM raccomandata
- **Storage**: Spazio sufficiente per download modelli

### Dipendenze Python
- `huggingface_hub>=0.20.0` - Integrazione HuggingFace
- `requests>=2.25.0` - Richieste HTTP
- `aiohttp` - Server web async (ComfyUI)

### Dipendenze Opzionali
- `HUGGINGFACE_API_KEY` - Per limiti rate più alti
- Directory modelli personalizzate - Per organizzazione

## 📄 Licenza

Questo progetto segue la stessa licenza del progetto originale Civicomfy.

## 🙏 Ringraziamenti

- **[Civicomfy](https://github.com/MoonGoblinDev/Civicomfy)** di MoonGoblinDev - Ispirazione originale e base
- **[HuggingFace](https://huggingface.co)** - Repository modelli e API incredibili
- **[Comunità ComfyUI](https://github.com/comfyanonymous/ComfyUI)** - Feedback, test e supporto
- **[huggingface_hub](https://github.com/huggingface/huggingface_hub)** - Libreria Python ufficiale

## 📞 Supporto

- **Issues**: Riporta bug tramite GitHub Issues
- **Funzionalità**: Richiedi funzionalità tramite GitHub Discussions  
- **Discord**: Unisciti alla comunità ComfyUI
- **Aggiornamenti**: Segui il repository per ultime funzionalità

---

**⭐ Se trovi utile, per favore dai una stella su GitHub!**

**🇬🇧 [English Documentation](README.md)** - Torna alla documentazione in inglese

**Fatto con ❤️ per la comunità ComfyUI**
