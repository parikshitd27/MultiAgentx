"""Financial statement tools (Yahoo Finance via yfinance)."""
from __future__ import annotations

from core.context import Context
from core.utils import growth, num, statement_row


def collect_financial_metrics(ctx: Context) -> dict:
    """Revenue/profit trends, margins, returns, leverage and cash-flow figures."""
    s, info = ctx.stock, ctx.info
    income, cash = s.financials, s.cashflow
    revenue = statement_row(income, "Total Revenue", "Operating Revenue")
    net_income = statement_row(income, "Net Income", "Net Income Common Stockholders")
    op_income = statement_row(income, "Operating Income")
    ocf = statement_row(cash, "Operating Cash Flow", "Total Cash From Operating Activities")
    capex = statement_row(cash, "Capital Expenditure")
    return {
        "currency": info.get("financialCurrency"),
        "annual_revenue_latest_first": revenue,
        "revenue_growth_pct": growth(revenue),
        "annual_net_income_latest_first": net_income,
        "net_income_growth_pct": growth(net_income),
        "annual_operating_income_latest_first": op_income,
        "operating_cash_flow": ocf,
        "capex": capex,
        "gross_margin": num(info.get("grossMargins")),
        "operating_margin": num(info.get("operatingMargins")),
        "net_margin": num(info.get("profitMargins")),
        "roe": num(info.get("returnOnEquity")),
        "roa": num(info.get("returnOnAssets")),
        "debt_to_equity": num(info.get("debtToEquity")),
        "current_ratio": num(info.get("currentRatio")),
        "free_cash_flow": num(info.get("freeCashflow")),
        "total_cash": num(info.get("totalCash")),
        "total_debt": num(info.get("totalDebt")),
        "dividend_yield": num(info.get("dividendYield")),
    }
