"""Risk_agent: market, financial, geopolitical and FX risk."""
import json

from agents.base_agent import BaseAgent
from core.context import Context
from core.utils import clip_transcript
from tools.evaluation_tools import collect_risk_metrics


class RiskAgent(BaseAgent):
    name = "Risk_agent"
    system_prompt = (
        "You are a risk analyst covering multinational companies: FX, geopolitics, regulation, "
        "supply chain, leverage, concentration, and macro exposure."
    )

    def run(self, ctx: Context) -> dict:
        data = collect_risk_metrics(ctx)
        prompt = f"""Company: {ctx.company} ({ctx.ticker})
Risk metrics:
{json.dumps(data, indent=2)}

Earnings call transcript:
{clip_transcript(ctx.transcript)}

Return JSON with keys:
  "risks": list of objects {{"category": "...", "description": "...", "severity": "low|medium|high", "evidence": "..."}}
           covering FX, geopolitical, regulatory, supply chain, macro, leverage, competition where relevant,
  "mitigants": list of strings,
  "overall_risk_level": "low" | "moderate" | "elevated" | "high",
  "risk_score": integer 1-10 (10 = safest),
  "summary": 3-4 sentences."""
        return {"agent": self.name, "data": data, "analysis": self.llm_json(prompt)}
