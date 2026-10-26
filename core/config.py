"""Central settings, loaded from .env in the project root."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()  # "ollama" or "openai"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))  # context window in tokens
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ~4 characters per token; leave room for data + the model's answer inside the context window
MAX_TRANSCRIPT_CHARS = int(os.getenv("MAX_TRANSCRIPT_CHARS", "12000" if PROVIDER == "ollama" else "60000"))
# Local models are usually best run one request at a time
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "1" if PROVIDER == "ollama" else "4"))
