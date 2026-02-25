import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# Gemini can be provided either via GEMINI_API_KEY or (for compatibility/branding)
# via OPENAI_API_KEY without changing env var names.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or OPENAI_API_KEY
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Metamorphosis")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "llama3.2")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
MISTRAL_BASE_URL = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-small")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

TOKEN_THRESHOLD = int(os.getenv("TOKEN_THRESHOLD", "500"))
MEMORY_TOP_K = int(os.getenv("MEMORY_TOP_K", "3"))

COST_PER_1K_INPUT = float(os.getenv("COST_PER_1K_INPUT", "0.0005"))
COST_PER_1K_OUTPUT = float(os.getenv("COST_PER_1K_OUTPUT", "0.0015"))

SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_sm")

# Guardrails & rate limiting
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW_SEC = float(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))
