"""
kpi_calculator.py
-----------------
Computes all core startup KPIs from raw operational data.

KPIs covered:
  - Churn Rate       : % of customers lost each month
  - CAC              : Cost to acquire one new customer
  - ARPU             : Average revenue per user
  - LTV              : Predicted revenue from a customer over their lifetime
  - LTV/CAC Ratio    : Marketing efficiency benchmark
  - Revenue Growth   : Month-over-month revenue change (%)
  - Net New Customers: Growth signal (new − churned)

Business context is added as inline comments so this module reads
as both code and a mini-consulting brief.
"""

import pandas as pd
import numpy as np

# ── Constants ─────────────────────────────────────────────────────────────────

# Industry assumption: average SaaS/startup customer stays ~12 months.
# Adjust this for your business model (e.g., 24 for enterprise, 6 for SMB).
ASSUMED_CUSTOMER_LIFETIME_MONTHS = 12


def calculate_all_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Master function — applies every KPI calculation in the correct order
    and returns an enriched DataFrame with all metric columns appended.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame from data_loader.load_data().

    Returns
    -------
    pd.DataFrame
        Original data + all computed KPI columns.
    """
    df = df.copy()  # Never mutate the caller's data

    df = _churn_rate(df)
    df = _cac(df)
    df = _arpu(df)
    df = _ltv(df)
    df = _ltv_cac_ratio(df)
    df = _revenue_growth(df)
    df = _net_new_customers(df)

    print(f"[KPICalculator] Computed {len(df.columns)} columns for {len(df)} months.")
    return df


# ── Individual KPI functions ──────────────────────────────────────────────────

def _churn_rate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Churn Rate = Churned_Customers / Customers

    Business meaning: What fraction of your existing customer base left this month?
    - <3%  → Excellent (best-in-class SaaS)
    - 3-7% → Healthy
    - 7-10%→ Concerning — retention work needed
    - >10% → Urgent — product/market fit or support issues
    """
    df["Churn_Rate"] = (
        df["Churned_Customers"] / df["Customers"]
    ).round(4)  # 4 decimal places → shows as e.g. 0.0563 = 5.63%

    return df


def _cac(df: pd.DataFrame) -> pd.DataFrame:
    """
    CAC (Customer Acquisition Cost) = Marketing_Spend / New_Customers

    Business meaning: How much does it cost to win one new customer?
    A rising CAC over time signals that easy acquisition channels are saturating
    and you're now spending more to reach less-warm audiences.
    """
    # Guard against division by zero in months with no new customers
    df["CAC"] = np.where(
        df["New_Customers"] > 0,
        (df["Marketing_Spend"] / df["New_Customers"]).round(2),
        np.nan,
    )
    return df


def _arpu(df: pd.DataFrame) -> pd.DataFrame:
    """
    ARPU (Average Revenue Per User) = Revenue / Customers

    Business meaning: The monthly contribution of a single average customer.
    Growing ARPU signals successful upsell/cross-sell or pricing power.
    Falling ARPU (with flat revenue) can mask customer quality deterioration.
    """
    df["ARPU"] = (df["Revenue"] / df["Customers"]).round(2)
    return df


def _ltv(df: pd.DataFrame) -> pd.DataFrame:
    """
    LTV (Customer Lifetime Value) = ARPU × Assumed Customer Lifetime (months)

    Business meaning: How much total revenue does a single customer generate
    before churning? This is the ceiling on how much you should ever spend to
    acquire that customer (i.e., CAC must always be below LTV).

    Note: A more rigorous LTV = ARPU / Churn_Rate (continuous model).
    We use the simpler fixed-lifetime model here for clarity.
    """
    df["LTV"] = (df["ARPU"] * ASSUMED_CUSTOMER_LIFETIME_MONTHS).round(2)
    return df


def _ltv_cac_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    LTV/CAC Ratio = LTV / CAC

    The single most important marketing efficiency metric for startups.

    Benchmarks:
    - < 1   → Losing money on every customer acquired (existential risk)
    - 1 – 2 → Barely breaking even — unsustainable at scale
    - 2 – 3 → Industry minimum for venture-backed growth
    - 3 – 5 → Healthy — good unit economics
    - > 5   → Strong signal to aggressively scale marketing spend
    """
    df["LTV_CAC_Ratio"] = np.where(
        df["CAC"].notna() & (df["CAC"] > 0),
        (df["LTV"] / df["CAC"]).round(2),
        np.nan,
    )
    return df


def _revenue_growth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Revenue Growth Rate = (Revenue_t - Revenue_t-1) / Revenue_t-1 × 100

    Business meaning: Month-over-month revenue momentum.
    - Consistent double-digit growth → strong product-market fit
    - Decelerating growth → watch for market saturation or churn impact
    - Negative growth → requires immediate investigation
    """
    df["Revenue_Growth_Rate"] = (
        df["Revenue"].pct_change() * 100
    ).round(2)  # expressed as a % (e.g., 8.5 = 8.5% growth)

    return df


def _net_new_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Net New Customers = New_Customers - Churned_Customers

    Business meaning: True organic growth signal.
    Positive = customer base expanding. Negative = contraction.
    A startup can show revenue growth while contracting its customer base
    (via price increases) — this metric catches that distinction.
    """
    df["Net_New_Customers"] = df["New_Customers"] - df["Churned_Customers"]
    return df


# ── Utility helpers ───────────────────────────────────────────────────────────

def get_latest_kpis(df: pd.DataFrame) -> dict:
    """
    Extract the most recent month's KPIs as a flat dict.
    Useful for dashboard header cards and insight thresholds.
    """
    latest = df.iloc[-1]
    return {
        "month": latest["Month"].strftime("%b %Y"),
        "churn_rate": latest["Churn_Rate"],
        "cac": latest["CAC"],
        "arpu": latest["ARPU"],
        "ltv": latest["LTV"],
        "ltv_cac_ratio": latest["LTV_CAC_Ratio"],
        "revenue_growth": latest["Revenue_Growth_Rate"],
        "net_new_customers": latest["Net_New_Customers"],
        "revenue": latest["Revenue"],
    }


def get_averages(df: pd.DataFrame) -> dict:
    """
    Return trailing-period averages for all KPIs.
    Used in insights to distinguish a single bad month from a trend.
    """
    return {
        "avg_churn_rate": df["Churn_Rate"].mean(),
        "avg_cac": df["CAC"].mean(),
        "avg_ltv_cac": df["LTV_CAC_Ratio"].mean(),
        "avg_revenue_growth": df["Revenue_Growth_Rate"].mean(),
        "avg_arpu": df["ARPU"].mean(),
    }


# ── Quick sanity test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.data_loader import load_data

    raw = load_data()
    enriched = calculate_all_kpis(raw)
    print(enriched[["Month", "Churn_Rate", "CAC", "LTV", "LTV_CAC_Ratio", "Revenue_Growth_Rate"]].to_string())
    print("\nLatest KPIs:", get_latest_kpis(enriched))
