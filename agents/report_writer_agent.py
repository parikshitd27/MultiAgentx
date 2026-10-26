"""ReportWriterAgent: merges all agent outputs into the final report + evaluation remark."""
import json

from agents.base_agent import BaseAgent
from core.context import Context


class ReportWriterAgent(BaseAgent):
    name = "ReportWriterAgent"
    system_prompt = (
        "You are a senior equity research writer. Combine specialist analyses into a clear, "
        "balanced, decision-ready report. Flag disagreements between agents. Use only the "
        "supplied data; if something is missing, say so."
    )

    def run(self, ctx: Context, results: dict[str, dict], composite: dict) -> str:
        # Compact payload so it fits a local model's context window
        slim = {
            name: {"data": r.get("data"), "analysis": r.get("analysis"), "error": r.get("error")}
            for name, r in results.items()
        }
        payload = json.dumps(slim, default=str, separators=(",", ":"))
        prompt = f"""Write a fundamental analysis report in Markdown for {ctx.company} ({ctx.ticker}).

Specialist agent outputs:
{payload}

Quantitative composite computed by code from the agents' scores (weights: financial 30%, valuation 30%, risk 20%, sentiment 20%):
{json.dumps(composite, default=str)}

Structure:
# {ctx.company} ({ctx.ticker}) - Fundamental Analysis
## 1. Executive Summary
## 2. Financial Health
## 3. News & Management Sentiment
## 4. Risk Assessment
## 5. Valuation
## 6. Bull vs Bear Case
## 7. Evaluation Remark
   - Rating: one of Strong Buy / Buy / Hold / Reduce / Sell. Align with the composite's suggested rating
     unless the evidence clearly justifies a different one; if you deviate, say why.
   - Conviction: Low / Medium / High (lower it when agents failed or data is missing)
   - 3-5 sentence rationale tying together the four agents' scores
   - Key things to monitor next quarter
End with a one-line disclaimer that this is automated analysis, not investment advice."""
        return self.llm_text(prompt)
