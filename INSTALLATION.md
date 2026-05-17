# Installation Guide

## Prerequisites

- **Python 3.10+** (3.14 tested)
- **Ollama** (for local LLM) -- [Download](https://ollama.ai/)
- **Git** (for cloning)

## Quick Install

```bash
# Clone repository
git clone https://github.com/your-org/nexus.git
cd nexus

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

## Ollama Setup

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Install Ollama (Windows)
# Download from https://ollama.ai/download

# Start Ollama service
ollama serve

# Pull the default model
ollama pull llama3
```

## Optional Dependencies

### Vision Agent
```bash
pip install mss opencv-python easyocr pytesseract pygetwindow Pillow numpy
```

### Notification Agent
```bash
pip install win10toast plyer
```

### Knowledge Agent (Vector Search)
```bash
pip install chromadb sentence-transformers
```

### Terminal UI
```bash
pip install textual rich psutil
```

### OpenAI Provider (Cloud LLM)
```bash
pip install openai
# Set API key in config/settings.json or .env
```

## Configuration

Edit `config/settings.json`:

```json
{
  "llm": {
    "provider": "ollama",
    "ollama": {
      "base_url": "http://localhost:11434",
      "model": "llama3",
      "temperature": 0.7,
      "max_tokens": 2048
    },
    "openai": {
      "api_key": "sk-...",
      "model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 2048
    }
  },
  "logging": {
    "level": "INFO",
    "file": "logs/nexus.log",
    "max_size_mb": 10,
    "backup_count": 5
  }
}
```

## Verify Installation

```bash
# Test Ollama connection
curl http://localhost:11434/api/tags

# Launch NEXUS
python main.py

# Verbose mode (see all logs)
python main.py --verbose

# Debug mode (full stack traces)
python main.py --debug

# Simple CLI mode (no Textual UI)
python main.py --cli
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Cannot connect to Ollama` | Run `ollama serve` |
| `Textual not found` | `pip install textual rich` |
| `ChromaDB error` | `pip install chromadb sentence-transformers` |
| `UnicodeEncodeError` | Set `PYTHONIOENCODING=utf-8` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | (empty) |
| `HF_TOKEN` | HuggingFace token (for embeddings) | (empty) |
| `PYTHONIOENCODING` | Console encoding | `utf-8` |
