"""Runs the four specialist agents, computes the composite score, then calls the report writer."""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agents import FinancialDataAgent, NewsSentimentAgent, ReportWriterAgent, RiskAgent, ValuationAgent
from core import config
from core.context import build_context
from core.llm import LLM
from tools.evaluation_tools import composite_evaluation


def analyze(ticker: str, transcript: str, out_dir: str = "reports") -> str:
    llm = LLM()
    print(f"LLM: {llm.provider} / {llm.model}")
    ctx = build_context(ticker, transcript)

    specialists = [FinancialDataAgent(llm), NewsSentimentAgent(llm), RiskAgent(llm), ValuationAgent(llm)]
    print(f"Running {len(specialists)} agents for {ctx.company} (workers={config.MAX_WORKERS}). "
          "Local models can take a few minutes...")

    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as pool:
        futures = {pool.submit(a.run, ctx): a.name for a in specialists}
        for fut, name in futures.items():
            try:
                results[name] = fut.result()
                print(f"  done: {name}")
            except Exception as e:  # one failing agent shouldn't kill the report
                results[name] = {"agent": name, "error": str(e)}
                print(f"  FAILED: {name}: {e}")

    composite = composite_evaluation(results)
    print(f"Composite score: {composite['composite_score']} -> {composite['suggested_rating']}")

    print("Writing report...")
    report = ReportWriterAgent(llm).run(ctx, results, composite)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / f"{ctx.ticker}_report.md"
    report_path.write_text(report, encoding="utf-8")
    (out / f"{ctx.ticker}_agent_outputs.json").write_text(
        json.dumps({"composite": composite, "agents": results}, indent=2, default=str), encoding="utf-8"
    )
    print(f"Saved: {report_path}")
    return report
