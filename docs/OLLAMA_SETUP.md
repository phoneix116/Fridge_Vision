# Ollama Setup Guide

Ollama allows you to run large language models locally on your Mac/Linux/Windows machine.

## Installation

### macOS
```bash
# Option 1: Download DMG from ollama.ai
# Option 2: Homebrew
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
Download from https://ollama.ai

## Running Ollama

```bash
# Start Ollama server (runs in background)
ollama serve
```

The server will start at `http://localhost:11434`

## Pulling a Model

```bash
# Pull Mistral-7B (recommended for recipes - 4.1GB)
ollama pull mistral

# Or pull other models:
ollama pull neural-chat     # 3.9GB - Good for instructions
ollama pull llama2          # 3.8GB - Balanced
ollama pull dolphin-mixtral # 26GB - Larger, better quality
```

## Verify Installation

```bash
# List installed models
ollama list

# Test with a simple prompt
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Give me a recipe for pasta",
  "stream": false
}'
```

## Using in Your App

Once Ollama is running, the FastAPI app will automatically:
1. Detect Ollama availability
2. Send detected ingredients to Ollama
3. Generate creative recipes using the LLM
4. Return recipes to the client

No additional configuration needed!

## Troubleshooting

**"Connection refused"**
- Make sure Ollama is running: `ollama serve`

**"Model not found"**
- Pull the model: `ollama pull mistral`

**"Out of memory"**
- Use smaller models or close other applications
- Or increase Docker memory if using Docker version

**"Slow response"**
- First response is slower (model loading)
- Subsequent responses are faster
- Consider using a smaller model

## Model Recommendations

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| mistral | 4.1GB | Fast | Good | Recipe generation ✓ |
| neural-chat | 3.9GB | Very Fast | Good | Instructions |
| llama2 | 3.8GB | Medium | Very Good | General purpose |
| dolphin-mixtral | 26GB | Slow | Excellent | Complex recipes |

**Recommended: Mistral** - Best balance of speed and quality for recipes
