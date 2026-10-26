"""Small shared helpers."""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

from core import config


def num(x: Any, default=None):
    """Convert to a clean float (None for NaN / missing / non-numeric)."""
    try:
        v = float(x)
        return default if math.isnan(v) or math.isinf(v) else v
    except (TypeError, ValueError):
        return default


def statement_row(df, *names: str, n: int = 4) -> list[float | None]:
    """Latest n annual values for the first matching row label of a yfinance statement."""
    if df is None or getattr(df, "empty", True):
        return []
    for name in names:
        if name in df.index:
            return [num(v) for v in df.loc[name].iloc[:n].tolist()]
    return []


def growth(series: list[float | None]) -> list[float | None]:
    """YoY growth (%) for a newest-first series."""
    out = []
    for new, old in zip(series, series[1:]):
        out.append(round((new / old - 1) * 100, 2) if new is not None and old not in (None, 0) else None)
    return out


def clip_transcript(text: str, limit: int | None = None) -> str:
    limit = limit or config.MAX_TRANSCRIPT_CHARS
    if not text.strip():
        return "(No transcript provided - base the analysis on the Yahoo Finance data only and say so.)"
    if len(text) <= limit:
        return text
    half = limit // 2  # keep prepared remarks (start) and Q&A (end)
    return text[:half] + "\n...[transcript truncated]...\n" + text[-half:]


def read_transcript(path: str | None) -> str:
    if not path:
        print("No --transcript given: running on Yahoo Finance data only.")
        return ""
    p = Path(path)
    if not p.exists():
        sys.exit(f"Transcript file not found: {p}")
    return p.read_text(encoding="utf-8", errors="ignore")
