"""news_sentiment_agent: headline sentiment + management tone."""
import json

from agents.base_agent import BaseAgent
from core.context import Context
from core.utils import clip_transcript
from tools.news_tools import fetch_news


class NewsSentimentAgent(BaseAgent):
    name = "news_sentiment_agent"
    system_prompt = (
        "You are a market-sentiment analyst. Judge tone from headlines and the earnings call. "
        "Separate noise from information that changes the investment case."
    )

    def run(self, ctx: Context) -> dict:
        news = fetch_news(ctx)
        prompt = f"""Company: {ctx.company} ({ctx.ticker})
Recent news:
{json.dumps(news, indent=2)}

Earnings call transcript (for management tone):
{clip_transcript(ctx.transcript)}

Return JSON with keys:
  "news_sentiment": "positive" | "neutral" | "negative" | "mixed",
  "transcript_tone": description of management confidence/evasiveness (cite topics, not long quotes),
  "key_themes": list of strings,
  "catalysts": list of strings,
  "red_flags": list of strings,
  "sentiment_score": number from -1 (very negative) to 1 (very positive),
  "summary": 3-4 sentences."""
        return {"agent": self.name, "data": {"headlines": news}, "analysis": self.llm_json(prompt)}
