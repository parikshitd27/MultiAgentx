"""Shared analysis context passed to every agent."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any

import yfinance as yf


@dataclass
class Context:
    ticker: str
    transcript: str
    info: dict = field(default_factory=dict)
    stock: Any = None  # yfinance.Ticker

    @property
    def company(self) -> str:
        return self.info.get("longName") or self.info.get("shortName") or self.ticker


def build_context(ticker: str, transcript: str) -> Context:
    stock = yf.Ticker(ticker)
    info = stock.info or {}
    if not info or not (info.get("longName") or info.get("shortName")):
        sys.exit(f"Yahoo Finance returned no data for '{ticker}'. Check the symbol (e.g. NESN.SW, 7203.T).")
    return Context(ticker=ticker.upper(), transcript=transcript, info=info, stock=stock)
