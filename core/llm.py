"""LLM wrapper: local Ollama (default) or OpenAI."""
from __future__ import annotations

import json
import re
import sys

from core import config


class LLM:
    def __init__(self):
        self.provider = config.PROVIDER
        if self.provider == "ollama":
            import ollama

            self.client = ollama.Client(host=config.OLLAMA_HOST, timeout=900)
            self.model = config.OLLAMA_MODEL
            self._check_ollama()
        elif self.provider == "openai":
            from openai import OpenAI

            if not config.OPENAI_API_KEY:
                sys.exit("LLM_PROVIDER=openai but OPENAI_API_KEY is not set.")
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            self.model = config.OPENAI_MODEL
        else:
            sys.exit("LLM_PROVIDER must be 'ollama' or 'openai'.")

    def _check_ollama(self):
        try:
            raw = self.client.list()
        except Exception as e:
            sys.exit(f"Cannot reach Ollama at {config.OLLAMA_HOST} ({e}). "
                     "Start it with `ollama serve` (or open the Ollama app) and retry.")
        items = raw["models"] if isinstance(raw, dict) else getattr(raw, "models", [])
        names = []
        for m in items:
            n = getattr(m, "model", None) or (m.get("model") or m.get("name") if isinstance(m, dict) else None)
            if n:
                names.append(n)
        wanted = self.model
        if not any(n == wanted or n == f"{wanted}:latest" or n.split(":")[0] == wanted for n in names):
            sys.exit(f"Ollama model '{wanted}' not found. Installed: {names or 'none'}.\n"
                     "Set OLLAMA_MODEL in .env to one of those names, or run `ollama pull <model>`.")

    def chat(self, system: str, user: str, json_mode: bool = False, temperature: float = 0.2) -> str:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        if self.provider == "ollama":
            resp = self.client.chat(
                model=self.model,
                messages=messages,
                format="json" if json_mode else None,
                options={"temperature": temperature, "num_ctx": config.OLLAMA_NUM_CTX},
            )
            text = resp["message"]["content"]
        else:
            kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
            resp = self.client.chat.completions.create(
                model=self.model, temperature=temperature, messages=messages, **kwargs
            )
            text = resp.choices[0].message.content
        # reasoning models (deepseek-r1, qwen3...) may emit <think> blocks
        return re.sub(r"<think>.*?</think>", "", text or "", flags=re.DOTALL).strip()


def parse_json(text: str) -> dict:
    """Tolerant JSON parsing: handles code fences and text around the object."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    for candidate in (cleaned, cleaned[cleaned.find("{"): cleaned.rfind("}") + 1]):
        try:
            return json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            continue
    return {"error": "model returned invalid JSON", "raw": text}
