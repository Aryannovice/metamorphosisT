# Metamorphosis — AI Optimization Gateway

A privacy-first AI gateway that intelligently routes prompts between local and cloud models, with built-in PII masking, prompt compression, semantic memory, and a real-time analytics dashboard.

## Architecture

```
User Prompt
  → PII Guard (spaCy + regex masking)
  → Memory Layer (ChromaDB vector retrieval)
  → Prompt Builder (system + context + user)
  → Prompt Shrinker (token compression)
  → Routing Engine (STRICT / BALANCED / PERFORMANCE)
  → Inference (Ollama local ↔ OpenAI cloud)
  → Post-Processor (unmask, cost, latency)
  → React Dashboard
```

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Create .env from the example
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux

# Start the API server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

> Run the `uvicorn` command from the **project root** (`metamorphosis/`), not from inside `backend/`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** — the Vite dev server proxies API calls to the backend.

### 3. (Optional) Local Model via Ollama

```bash
ollama serve
ollama pull llama3.2
```

## Configuration (.env)

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required for cloud routing |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `LOCAL_MODEL` | `llama3.2` | Model name for local inference |
| `CLOUD_MODEL` | `gpt-3.5-turbo` | Model name for cloud inference |
| `TOKEN_THRESHOLD` | `500` | Token count below which BALANCED routes locally |
| `MEMORY_TOP_K` | `3` | Number of memory snippets to retrieve |

## Routing Modes

| Mode | Behavior |
|---|---|
| **STRICT** | Always local — zero data leaves the machine |
| **BALANCED** | Short/simple prompts go local; complex ones go to cloud with PII masked |
| **PERFORMANCE** | Always cloud — fastest response, PII still masked |

## API

### `POST /gateway`

```json
{
  "prompt": "Summarize this email from john@example.com about the Q3 report",
  "mode": "BALANCED"
}
```

### Response

```json
{
  "request_id": "uuid",
  "response": "...",
  "route": "CLOUD",
  "model_used": "gpt-3.5-turbo",
  "token_stats": { "original": 120, "compressed": 85, "saved": 35, "compression_ratio": 0.292 },
  "latency": { "pii_ms": 12.3, "memory_ms": 5.1, "compression_ms": 2.8, "inference_ms": 890.0, "total_ms": 910.2 },
  "estimated_cost": 0.000145,
  "redaction": { "count": 1, "types": { "EMAIL": 1 } },
  "privacy_level": "BALANCED"
}
```

## Tech Stack

- **Backend:** FastAPI, spaCy, ChromaDB, tiktoken, OpenAI SDK
- **Frontend:** React 18, Vite, Tailwind CSS, Recharts, Lucide Icons
- **Local LLM:** Ollama
- **Cloud LLM:** OpenAI API
