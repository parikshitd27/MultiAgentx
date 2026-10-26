"""News tools (Yahoo Finance via yfinance)."""
from __future__ import annotations

from core.context import Context


def fetch_news(ctx: Context, limit: int = 12) -> list[dict]:
    """Recent headlines. Handles both the old and new yfinance news schemas."""
    try:
        raw = ctx.stock.news or []
    except Exception:
        raw = []
    items = []
    for n in raw[:limit]:
        c = n.get("content", n)
        items.append(
            {
                "title": c.get("title"),
                "summary": (c.get("summary") or "")[:200],
                "publisher": (c.get("provider") or {}).get("displayName") or c.get("publisher"),
                "published": c.get("pubDate") or c.get("providerPublishTime"),
            }
        )
    return [i for i in items if i["title"]]
