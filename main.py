"""Full pipeline: 4 specialist agents -> ReportWriterAgent -> report + evaluation remark.

    python main.py AAPL --transcript transcripts/aapl_q3.txt
    python main.py MSFT                      # no transcript: Yahoo data only
"""
import argparse

from core.utils import read_transcript
from orchestrator import analyze


def main():
    ap = argparse.ArgumentParser(description="Multi-agent fundamental analysis from earnings transcripts")
    ap.add_argument("ticker", help="Yahoo Finance symbol, e.g. AAPL, MSFT, NESN.SW")
    ap.add_argument("--transcript", default=None, help="Path to a .txt earnings call transcript (optional)")
    ap.add_argument("--out", default="reports", help="Output directory")
    args = ap.parse_args()

    print("\n" + analyze(args.ticker, read_transcript(args.transcript), args.out))


if __name__ == "__main__":
    main()
