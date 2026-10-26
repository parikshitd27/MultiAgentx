"""Financial_data_agent: financial health from statements + transcript."""
import json

from agents.base_agent import BaseAgent
from core.context import Context
from core.utils import clip_transcript
from tools.financial_tools import collect_financial_metrics


class FinancialDataAgent(BaseAgent):
    name = "Financial_data_agent"
    system_prompt = (
        "You are a fundamental analyst. Interpret financial metrics and cross-check them "
        "against what management said in the earnings call transcript. Never invent numbers."
    )

    def run(self, ctx: Context) -> dict:
        data = collect_financial_metrics(ctx)
        prompt = f"""Company: {ctx.company} ({ctx.ticker})
Financial metrics (Yahoo Finance):
{json.dumps(data, indent=2)}

Earnings call transcript:
{clip_transcript(ctx.transcript)}

Return JSON with keys:
  "summary": 3-5 sentence view on financial health and trajectory,
  "strengths": list of strings,
  "weaknesses": list of strings,
  "management_guidance": list of forward-looking statements from the transcript,
  "transcript_vs_numbers": where management claims match or contradict the numbers,
  "score": integer 1-10 (financial quality)."""
        return {"agent": self.name, "data": data, "analysis": self.llm_json(prompt)}
