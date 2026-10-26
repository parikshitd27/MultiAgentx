"""Base class shared by all agents."""
from __future__ import annotations

from core.context import Context
from core.llm import LLM, parse_json


class BaseAgent:
    name = "BaseAgent"
    system_prompt = "You are a careful equity research analyst."

    def __init__(self, llm: LLM):
        self.llm = llm

    def llm_json(self, user_prompt: str) -> dict:
        text = self.llm.chat(self.system_prompt + " Respond with valid JSON only, no extra text.",
                             user_prompt, json_mode=True, temperature=0.2)
        return parse_json(text)

    def llm_text(self, user_prompt: str) -> str:
        return self.llm.chat(self.system_prompt, user_prompt, json_mode=False, temperature=0.3)

    def run(self, ctx: Context) -> dict:
        raise NotImplementedError
