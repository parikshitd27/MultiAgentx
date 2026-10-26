"""Run ONE agent on its own and print its JSON output (handy for testing and debugging).

    python run_agent.py financial AAPL --transcript transcripts/aapl_q3.txt
    python run_agent.py news MSFT
    python run_agent.py risk NESN.SW
    python run_agent.py valuation AAPL
"""
import argparse
import json

from agents import FinancialDataAgent, NewsSentimentAgent, RiskAgent, ValuationAgent
from core.context import build_context
from core.llm import LLM
from core.utils import read_transcript

AGENTS = {
    "financial": FinancialDataAgent,
    "news": NewsSentimentAgent,
    "risk": RiskAgent,
    "valuation": ValuationAgent,
}


def main():
    ap = argparse.ArgumentParser(description="Run a single analysis agent")
    ap.add_argument("agent", choices=AGENTS)
    ap.add_argument("ticker", help="Yahoo Finance symbol, e.g. AAPL")
    ap.add_argument("--transcript", default=None, help="Path to a .txt earnings call transcript (optional)")
    args = ap.parse_args()

    llm = LLM()
    ctx = build_context(args.ticker, read_transcript(args.transcript))
    result = AGENTS[args.agent](llm).run(ctx)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
