"""Risk metrics, valuation (multiples + DCF) and the composite evaluation score."""
from __future__ import annotations

from core.context import Context
from core.utils import num

# (5-yr FCF growth, discount rate, terminal growth). Generic placeholders: tune per company.
DCF_SCENARIOS = {
    "bear": (0.03, 0.11, 0.015),
    "base": (0.07, 0.10, 0.025),
    "bull": (0.11, 0.09, 0.030),
}

# Weights for the composite score
WEIGHTS = {"financial": 0.30, "valuation": 0.30, "risk": 0.20, "sentiment": 0.20}


# ------------------------------- risk ------------------------------------- #
def collect_risk_metrics(ctx: Context) -> dict:
    info = ctx.info
    price = num(info.get("currentPrice"))
    high, low = num(info.get("fiftyTwoWeekHigh")), num(info.get("fiftyTwoWeekLow"))
    return {
        "country": info.get("country"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "beta": num(info.get("beta")),
        "debt_to_equity": num(info.get("debtToEquity")),
        "current_ratio": num(info.get("currentRatio")),
        "price": price,
        "52w_high": high,
        "52w_low": low,
        "drawdown_from_52w_high_pct": round((price / high - 1) * 100, 2) if price and high else None,
        "short_percent_of_float": num(info.get("shortPercentOfFloat")),
        "yahoo_overall_governance_risk": info.get("overallRisk"),
        "yahoo_audit_risk": info.get("auditRisk"),
    }


# ----------------------------- valuation ---------------------------------- #
def run_dcf(ctx: Context) -> dict:
    """Five-year free-cash-flow DCF under bear/base/bull assumptions."""
    info = ctx.info
    fcf = num(info.get("freeCashflow"))
    shares = num(info.get("sharesOutstanding"))
    if not fcf or fcf <= 0 or not shares:
        return {"note": "DCF skipped: free cash flow missing or non-positive."}
    net_debt = (num(info.get("totalDebt"), 0) or 0) - (num(info.get("totalCash"), 0) or 0)
    out = {}
    for name, (g, r, tg) in DCF_SCENARIOS.items():
        pv, cf = 0.0, fcf
        for t in range(1, 6):
            cf *= 1 + g
            pv += cf / (1 + r) ** t
        terminal = cf * (1 + tg) / (r - tg)
        equity = pv + terminal / (1 + r) ** 5 - net_debt
        out[name] = {
            "assumptions": {"fcf_growth": g, "discount_rate": r, "terminal_growth": tg},
            "intrinsic_value_per_share": round(equity / shares, 2),
        }
    return out


def collect_valuation_metrics(ctx: Context) -> dict:
    info = ctx.info
    price = num(info.get("currentPrice"))
    dcf = run_dcf(ctx)
    base = dcf.get("base", {}).get("intrinsic_value_per_share")
    return {
        "price": price,
        "currency": info.get("currency"),
        "market_cap": num(info.get("marketCap")),
        "trailing_pe": num(info.get("trailingPE")),
        "forward_pe": num(info.get("forwardPE")),
        "peg": num(info.get("pegRatio")),
        "price_to_book": num(info.get("priceToBook")),
        "price_to_sales": num(info.get("priceToSalesTrailing12Months")),
        "ev_to_ebitda": num(info.get("enterpriseToEbitda")),
        "analyst_target_mean": num(info.get("targetMeanPrice")),
        "analyst_recommendation": info.get("recommendationKey"),
        "dcf_scenarios": dcf,
        "base_case_upside_pct": round((base / price - 1) * 100, 1) if base and price else None,
    }


# ------------------------- composite evaluation --------------------------- #
def _agent_score(results: dict, agent: str, key: str):
    analysis = (results.get(agent) or {}).get("analysis")
    return num(analysis.get(key)) if isinstance(analysis, dict) else None


def _clamp(v, lo, hi):
    return None if v is None else max(lo, min(hi, v))


def composite_evaluation(results: dict) -> dict:
    """Combine the four agents' scores into one 1-10 score and a suggested rating (computed in code)."""
    sentiment = _clamp(_agent_score(results, "news_sentiment_agent", "sentiment_score"), -1, 1)
    components = {
        "financial": _clamp(_agent_score(results, "Financial_data_agent", "score"), 1, 10),
        "valuation": _clamp(_agent_score(results, "Valuation_agent", "score"), 1, 10),
        "risk": _clamp(_agent_score(results, "Risk_agent", "risk_score"), 1, 10),
        "sentiment": None if sentiment is None else round((sentiment + 1) / 2 * 9 + 1, 2),  # -1..1 -> 1..10
    }
    available = {k: v for k, v in components.items() if v is not None}
    missing = [k for k, v in components.items() if v is None]
    if not available:
        return {"composite_score": None, "suggested_rating": "Insufficient data",
                "components": components, "missing": missing}

    total_w = sum(WEIGHTS[k] for k in available)
    score = sum(WEIGHTS[k] * v for k, v in available.items()) / total_w
    if score >= 8:
        rating = "Strong Buy"
    elif score >= 6.5:
        rating = "Buy"
    elif score >= 5:
        rating = "Hold"
    elif score >= 3.5:
        rating = "Reduce"
    else:
        rating = "Sell"
    return {
        "composite_score": round(score, 2),
        "suggested_rating": rating,
        "components": components,
        "weights": WEIGHTS,
        "missing": missing,
    }
