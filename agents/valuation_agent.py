"""Valuation_agent: multiples + DCF scenarios."""
import json

from agents.base_agent import BaseAgent
from core import config
from core.context import Context
from core.utils import clip_transcript
from tools.evaluation_tools import collect_valuation_metrics


class ValuationAgent(BaseAgent):
    name = "Valuation_agent"
    system_prompt = (
        "You are a valuation analyst. Judge whether the stock is cheap, fair or expensive using "
        "multiples and the DCF scenarios provided. State assumptions and their limits."
    )

    def run(self, ctx: Context) -> dict:
        data = collect_valuation_metrics(ctx)
        prompt = f"""Company: {ctx.company} ({ctx.ticker})
Valuation data:
{json.dumps(data, indent=2)}

Management outlook from the earnings call (use to sanity-check DCF growth assumptions):
{clip_transcript(ctx.transcript, config.MAX_TRANSCRIPT_CHARS // 2)}

Return JSON with keys:
  "valuation_view": "undervalued" | "fairly valued" | "overvalued",
  "fair_value_range": {{"low": number|null, "high": number|null}},
  "key_assumptions_and_caveats": list of strings,
  "multiples_commentary": string,
  "summary": 3-4 sentences,
  "score": integer 1-10 (10 = very attractive valuation)."""
        return {"agent": self.name, "data": data, "analysis": self.llm_json(prompt)}
