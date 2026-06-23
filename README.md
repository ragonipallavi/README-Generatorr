# ReadmeAI — Intelligent README Generator

An AI-powered README generator supporting GitHub repos, folder uploads, and individual files.
Uses Groq (cloud) or Ollama (local) for generation.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your GROQ_API_KEY
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Features
- GitHub repo URL parsing
- Folder/file upload with drag & drop
- 6 README tones
- 6 project templates
- Groq & Ollama AI providers
- CSV-based generation history
- Download as .md or .txt

## Env Variables
| Variable | Description |
|---|---|
| GROQ_API_KEY | Groq API key (get free at console.groq.com) |
| GITHUB_TOKEN | Optional: GitHub token for private repos & higher rate limits |
| OLLAMA_BASE_URL | Ollama server URL (default: http://localhost:11434) |
