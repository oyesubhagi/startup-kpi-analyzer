"""
insights_generator.py
---------------------
Translates raw KPI numbers into human-readable, consulting-style business
insights and actionable recommendations.

Design philosophy:
  Each insight follows the "Signal → Interpretation → Action" structure used
  in management consulting deliverables:
    1. What is happening? (the number)
    2. What does it mean? (business interpretation)
    3. What should leadership do? (the recommendation)
"""

from dataclasses import dataclass, field
from typing import List
import pandas as pd


# ── Severity levels (used for UI colour-coding in Streamlit) ─────────────────
SEVERITY_INFO    = "info"      # Positive signal / context
SEVERITY_SUCCESS = "success"   # Exceeds benchmarks
SEVERITY_WARNING = "warning"   # Requires attention
SEVERITY_DANGER  = "danger"    # Requires urgent action


@dataclass
class Insight:
    """
    A single business insight with metadata for display and prioritisation.
    """
    category: str           # e.g. "Churn", "Marketing Efficiency", "Revenue"
    severity: str           # One of the SEVERITY_* constants above
    headline: str           # One-line summary (appears in bold)
    detail: str             # 2-3 sentence consulting-style explanation
    action: str             # Specific recommended next step
    metric_value: float = 0.0  # Raw value that triggered this insight


@dataclass
class InsightReport:
    """
    Container for the full set of insights generated for a period.
    """
    period: str                        # e.g. "Jan 2024 – Dec 2024"
    insights: List[Insight] = field(default_factory=list)
    score: int = 0                     # Simple health score 0-100

    def add(self, insight: Insight):
        self.insights.append(insight)

    def to_list(self) -> List[str]:
        """Flat text list — used by the notebook and CLI consumers."""
        lines = []
        for ins in self.insights:
            lines.append(f"[{ins.severity.upper()}] {ins.headline}")
            lines.append(f"  → {ins.detail}")
            lines.append(f"  ✅ Action: {ins.action}")
            lines.append("")
        return lines


# ── Thresholds (centralised so they're easy to tune) ─────────────────────────

CHURN_EXCELLENT  = 0.03   # < 3%  — best-in-class
CHURN_HEALTHY    = 0.07   # < 7%  — acceptable
CHURN_WARNING    = 0.10   # < 10% — concerning
# > 10% → DANGER

LTV_CAC_DANGER   = 1.0    # < 1   — unit economics broken
LTV_CAC_WARNING  = 2.0    # < 2   — inefficient
LTV_CAC_HEALTHY  = 3.0    # < 3   — acceptable minimum
LTV_CAC_GOOD     = 5.0    # < 5   — healthy
# > 5   → SUCCESS (scale signal)

REVENUE_GROWTH_STRONG   = 10.0  # > 10% MoM → strong
REVENUE_GROWTH_HEALTHY  = 5.0   # > 5%  MoM → healthy
REVENUE_GROWTH_WEAK     = 0.0   # > 0%  MoM → at least positive


def generate_insights(df: pd.DataFrame) -> InsightReport:
    """
    Main entry point. Accepts the KPI-enriched DataFrame and returns
    a fully populated InsightReport.

    Parameters
    ----------
    df : pd.DataFrame
        Output of kpi_calculator.calculate_all_kpis().

    Returns
    -------
    InsightReport
        Structured collection of insights with severity and actions.
    """
    period = (
        f"{df['Month'].min().strftime('%b %Y')} – "
        f"{df['Month'].max().strftime('%b %Y')}"
    )
    report = InsightReport(period=period)

    latest = df.iloc[-1]
    avg_churn    = df["Churn_Rate"].mean()
    avg_ltv_cac  = df["LTV_CAC_Ratio"].mean()
    avg_growth   = df["Revenue_Growth_Rate"].dropna().mean()

    # Run each insight module
    _churn_insights(report, latest, avg_churn, df)
    _ltv_cac_insights(report, latest, avg_ltv_cac, df)
    _revenue_growth_insights(report, latest, avg_growth, df)
    _cac_trend_insights(report, df)
    _net_growth_insights(report, df)
    _arpu_insights(report, df)

    # Compute a simple health score (0-100) for the dashboard gauge
    report.score = _compute_health_score(latest, avg_churn, avg_ltv_cac, avg_growth)

    return report


# ── Individual insight modules ────────────────────────────────────────────────

def _churn_insights(report, latest, avg_churn, df):
    churn = latest["Churn_Rate"]
    churn_pct = churn * 100

    if churn > CHURN_WARNING:
        report.add(Insight(
            category="Churn",
            severity=SEVERITY_DANGER,
            headline=f"⚠️ Critical churn rate: {churn_pct:.1f}% this month",
            detail=(
                f"Your current churn rate of {churn_pct:.1f}% significantly exceeds the "
                f"10% danger threshold. At this rate, the business is losing more than "
                f"1 in 10 customers every month. The trailing average of {avg_churn*100:.1f}% "
                f"confirms this is a persistent trend, not a one-off anomaly."
            ),
            action=(
                "Immediately launch exit-interview surveys for churned customers. "
                "Prioritise onboarding improvements, proactive customer success outreach, "
                "and review your product's core value delivery against customer expectations."
            ),
            metric_value=churn,
        ))

    elif churn > CHURN_HEALTHY:
        report.add(Insight(
            category="Churn",
            severity=SEVERITY_WARNING,
            headline=f"🔶 Elevated churn rate: {churn_pct:.1f}% — monitor closely",
            detail=(
                f"Churn at {churn_pct:.1f}% sits in the 7–10% 'watch zone'. "
                f"While not yet critical, this level of attrition will compound into "
                f"meaningful revenue loss if left unaddressed over the next 2–3 quarters."
            ),
            action=(
                "Introduce a customer health score model to identify at-risk accounts before "
                "they churn. Consider a loyalty programme or proactive check-ins at the "
                "60-day usage mark."
            ),
            metric_value=churn,
        ))

    elif churn > CHURN_EXCELLENT:
        report.add(Insight(
            category="Churn",
            severity=SEVERITY_INFO,
            headline=f"✅ Churn under control: {churn_pct:.1f}% — healthy range",
            detail=(
                f"A churn rate of {churn_pct:.1f}% is within the acceptable 3–7% band "
                f"for most SaaS and subscription businesses. The business is retaining "
                f"the majority of its customer base month-on-month."
            ),
            action=(
                "Maintain current customer success initiatives. Begin experimenting with "
                "annual contract incentives to lock in revenue and structurally reduce churn."
            ),
            metric_value=churn,
        ))

    else:
        report.add(Insight(
            category="Churn",
            severity=SEVERITY_SUCCESS,
            headline=f"🏆 Exceptional churn rate: {churn_pct:.1f}% — best-in-class",
            detail=(
                f"A churn rate below 3% places this business in the top tier of subscription "
                f"companies globally. This is a strong signal of genuine product-market fit "
                f"and excellent customer experience."
            ),
            action=(
                "Document and systematise what is driving this retention. Package it as a "
                "competitive moat narrative for investors and use it to justify premium pricing."
            ),
            metric_value=churn,
        ))


def _ltv_cac_insights(report, latest, avg_ltv_cac, df):
    ratio = latest["LTV_CAC_Ratio"]

    if ratio < LTV_CAC_DANGER:
        report.add(Insight(
            category="Marketing Efficiency",
            severity=SEVERITY_DANGER,
            headline=f"🚨 LTV/CAC ratio {ratio:.2f} — unit economics are broken",
            detail=(
                f"An LTV/CAC below 1.0 means you are spending more to acquire a customer "
                f"than that customer will ever return. This is a structurally unsustainable "
                f"model and will accelerate cash burn with every new acquisition."
            ),
            action=(
                "Immediately pause or significantly reduce paid acquisition spend. "
                "Shift focus to organic channels (SEO, referral, partnerships). "
                "Simultaneously work to extend customer lifetime — improve onboarding, "
                "add retention touchpoints, or repackage pricing to increase ARPU."
            ),
            metric_value=ratio,
        ))

    elif ratio < LTV_CAC_WARNING:
        report.add(Insight(
            category="Marketing Efficiency",
            severity=SEVERITY_DANGER,
            headline=f"🔴 LTV/CAC ratio {ratio:.2f} — marketing is inefficient",
            detail=(
                f"With an LTV/CAC of {ratio:.2f}, for every £1 of customer value generated, "
                f"you are spending {1/ratio:.2f}x in acquisition costs. "
                f"The industry minimum for sustainable growth is 3:1. "
                f"Scaling marketing at this ratio will destroy value."
            ),
            action=(
                "Audit your highest-CAC acquisition channels and reallocate budget to lower-CAC "
                "sources. In parallel, identify upsell opportunities to increase LTV without "
                "touching acquisition costs."
            ),
            metric_value=ratio,
        ))

    elif ratio < LTV_CAC_HEALTHY:
        report.add(Insight(
            category="Marketing Efficiency",
            severity=SEVERITY_WARNING,
            headline=f"🟡 LTV/CAC ratio {ratio:.2f} — approaching minimum viability",
            detail=(
                f"At {ratio:.2f}, your marketing efficiency is approaching but not yet at "
                f"the 3:1 benchmark investors and operators use as the minimum threshold "
                f"for scaling. There is meaningful room for improvement before aggressive "
                f"growth spend is warranted."
            ),
            action=(
                "Test channel mix optimisation — identify which acquisition channels deliver "
                "the highest-LTV customers, not just the cheapest clicks. Quality of acquisition "
                "matters more than volume at this stage."
            ),
            metric_value=ratio,
        ))

    elif ratio < LTV_CAC_GOOD:
        report.add(Insight(
            category="Marketing Efficiency",
            severity=SEVERITY_INFO,
            headline=f"✅ LTV/CAC ratio {ratio:.2f} — healthy unit economics",
            detail=(
                f"A ratio of {ratio:.2f} signals sound marketing efficiency. For every £1 spent "
                f"acquiring customers, you are generating {ratio:.2f}x in lifetime value. "
                f"This positions the business well for measured, sustainable growth."
            ),
            action=(
                "Begin modelling incremental marketing budget scenarios. The economics support "
                "a controlled increase in acquisition spend — test 15–20% budget increases "
                "and monitor CAC drift before committing to full scale."
            ),
            metric_value=ratio,
        ))

    else:
        report.add(Insight(
            category="Marketing Efficiency",
            severity=SEVERITY_SUCCESS,
            headline=f"🚀 LTV/CAC ratio {ratio:.2f} — strong signal to scale marketing",
            detail=(
                f"An LTV/CAC above 5.0 is a clear green light for growth investment. "
                f"Your current ratio of {ratio:.2f} means the business is generating "
                f"{ratio:.1f}x return on acquisition spend. This level of efficiency is "
                f"rare and represents a significant competitive advantage."
            ),
            action=(
                "Present this metric to the board as justification for a material increase "
                "in marketing budget. The business is leaving growth on the table. "
                "Model a 2–3x increase in marketing spend and project the customer and revenue "
                "impact over the next 12 months."
            ),
            metric_value=ratio,
        ))


def _revenue_growth_insights(report, latest, avg_growth, df):
    growth = latest["Revenue_Growth_Rate"]
    if pd.isna(growth):
        return  # First month — no prior period to compare

    if growth >= REVENUE_GROWTH_STRONG:
        report.add(Insight(
            category="Revenue",
            severity=SEVERITY_SUCCESS,
            headline=f"📈 Strong revenue growth: +{growth:.1f}% MoM",
            detail=(
                f"Month-over-month revenue growth of {growth:.1f}% exceeds the 10% strong-growth "
                f"threshold. The trailing average of {avg_growth:.1f}% suggests this momentum is "
                f"building consistently, not driven by a one-time event."
            ),
            action=(
                "Identify the exact drivers of this month's outperformance — new segment "
                "penetration, pricing change, or channel breakout? Systematise and double down."
            ),
            metric_value=growth,
        ))

    elif growth >= REVENUE_GROWTH_HEALTHY:
        report.add(Insight(
            category="Revenue",
            severity=SEVERITY_INFO,
            headline=f"📊 Steady revenue growth: +{growth:.1f}% MoM",
            detail=(
                f"Revenue grew {growth:.1f}% versus last month, tracking within the healthy "
                f"5–10% band. The business is expanding at a consistent pace."
            ),
            action=(
                "Protect this trajectory. Ensure the sales pipeline is sufficiently stocked "
                "for the next 60–90 days and that no single customer represents >10% of revenue."
            ),
            metric_value=growth,
        ))

    elif growth >= REVENUE_GROWTH_WEAK:
        report.add(Insight(
            category="Revenue",
            severity=SEVERITY_WARNING,
            headline=f"🔶 Slowing revenue growth: +{growth:.1f}% MoM",
            detail=(
                f"Revenue growth of {growth:.1f}% is positive but sluggish. "
                f"For a startup, sub-5% monthly growth risks falling behind the pace "
                f"needed to reach scale. The trend warrants proactive intervention."
            ),
            action=(
                "Convene a growth review. Evaluate whether the slowdown is demand-side "
                "(acquisition), supply-side (delivery capacity), or churn-related. "
                "Each root cause demands a different response."
            ),
            metric_value=growth,
        ))

    else:
        report.add(Insight(
            category="Revenue",
            severity=SEVERITY_DANGER,
            headline=f"📉 Revenue declined: {growth:.1f}% MoM",
            detail=(
                f"A month-over-month revenue decline of {growth:.1f}% is a critical signal. "
                f"Combined with the trailing average growth of {avg_growth:.1f}%, this "
                f"requires immediate leadership attention."
            ),
            action=(
                "Conduct an emergency revenue review. Isolate whether the decline is driven "
                "by churn, contract non-renewals, or failed new business. "
                "Activate your highest-priority sales pipeline opportunities."
            ),
            metric_value=growth,
        ))


def _cac_trend_insights(report, df):
    """
    Detect rising CAC trend — an early warning of channel saturation.
    Uses linear slope rather than point-in-time to avoid false alarms.
    """
    if len(df) < 3:
        return

    cac_series = df["CAC"].dropna()
    if len(cac_series) < 3:
        return

    # Simple slope: last 3 months
    recent = cac_series.tail(3).values
    slope = (recent[-1] - recent[0]) / 2  # average monthly CAC change

    if slope > 50:  # CAC rising by >£50/month on average
        report.add(Insight(
            category="Customer Acquisition Cost",
            severity=SEVERITY_WARNING,
            headline=f"📈 CAC is rising: +£{slope:.0f}/month trend over last 3 months",
            detail=(
                f"Your cost per acquired customer has been rising steadily. "
                f"This typically signals channel saturation — the easiest-to-reach "
                f"audiences have been exhausted and you are now competing for harder-to-convert prospects."
            ),
            action=(
                "Audit your channel mix. Identify which channels show the steepest CAC "
                "increase and reduce allocation there. Test 2–3 new acquisition channels "
                "this quarter to diversify and reset your blended CAC."
            ),
            metric_value=slope,
        ))
    elif slope < -20:  # CAC falling — a positive signal
        report.add(Insight(
            category="Customer Acquisition Cost",
            severity=SEVERITY_SUCCESS,
            headline=f"📉 CAC improving: −£{abs(slope):.0f}/month trend — efficiency gaining",
            detail=(
                f"Customer acquisition cost is trending downward, indicating that your "
                f"marketing channels are maturing and becoming more efficient. "
                f"This is a strong operational signal."
            ),
            action=(
                "Document which channel optimisations or content investments are driving "
                "this improvement. Scale the highest-performing activities before the "
                "efficiency gains plateau."
            ),
            metric_value=slope,
        ))


def _net_growth_insights(report, df):
    """
    Flag months where churn is outpacing acquisition — a retention crisis signal.
    """
    df_recent = df.tail(3)
    negative_months = df_recent[df_recent["Net_New_Customers"] < 0]

    if len(negative_months) >= 2:
        report.add(Insight(
            category="Customer Growth",
            severity=SEVERITY_DANGER,
            headline="⛔ Customer base contracting — churn exceeding new acquisitions",
            detail=(
                f"In {len(negative_months)} of the last 3 months, churned customers outnumbered "
                f"new customers. This means the customer base is shrinking despite ongoing "
                f"acquisition spend. Revenue growth, if any, is being sustained by price — "
                f"not by volume growth — which is unsustainable."
            ),
            action=(
                "This is a dual crisis: simultaneously reduce churn and accelerate acquisition. "
                "In the short term, focus retention spend on your highest-LTV customers. "
                "Longer term, review whether your ICP (Ideal Customer Profile) is well-defined "
                "and whether acquisition is targeting the right audience."
            ),
            metric_value=len(negative_months),
        ))


def _arpu_insights(report, df):
    """
    Detect ARPU trend — expanding or contracting revenue per user.
    """
    if len(df) < 4:
        return

    arpu_early = df["ARPU"].head(3).mean()
    arpu_late  = df["ARPU"].tail(3).mean()
    arpu_change_pct = ((arpu_late - arpu_early) / arpu_early) * 100

    if arpu_change_pct > 10:
        report.add(Insight(
            category="Revenue Quality",
            severity=SEVERITY_SUCCESS,
            headline=f"💰 ARPU growing: +{arpu_change_pct:.1f}% over the period",
            detail=(
                f"Average revenue per user has increased {arpu_change_pct:.1f}% from £{arpu_early:.0f} "
                f"to £{arpu_late:.0f}. This indicates successful upselling, pricing improvement, "
                f"or a shift toward higher-value customer segments."
            ),
            action=(
                "Identify the cohorts and products driving ARPU expansion. Build a systematic "
                "upsell playbook to replicate this across the full customer base."
            ),
            metric_value=arpu_change_pct,
        ))
    elif arpu_change_pct < -5:
        report.add(Insight(
            category="Revenue Quality",
            severity=SEVERITY_WARNING,
            headline=f"⚠️ ARPU declining: {arpu_change_pct:.1f}% over the period",
            detail=(
                f"Despite customer growth, the revenue generated per customer has fallen "
                f"{abs(arpu_change_pct):.1f}%. This could indicate downgrade pressure, "
                f"heavy discounting to win customers, or a shift toward lower-tier plans."
            ),
            action=(
                "Review your pricing and packaging strategy. If discounting is widespread, "
                "implement discount approval workflows. Consider a value-based pricing audit "
                "to ensure pricing reflects customer ROI."
            ),
            metric_value=arpu_change_pct,
        ))


# ── Health score ──────────────────────────────────────────────────────────────

def _compute_health_score(latest, avg_churn, avg_ltv_cac, avg_growth) -> int:
    """
    Simple 0-100 composite score. Not a replacement for nuanced analysis —
    but useful as a single at-a-glance metric for the dashboard.
    """
    score = 0

    # Churn contribution (0-30 pts)
    churn = avg_churn
    if churn < 0.03:   score += 30
    elif churn < 0.07: score += 20
    elif churn < 0.10: score += 10
    else:              score += 0

    # LTV/CAC contribution (0-40 pts)
    ltv_cac = avg_ltv_cac
    if ltv_cac > 5:    score += 40
    elif ltv_cac > 3:  score += 30
    elif ltv_cac > 2:  score += 15
    elif ltv_cac > 1:  score += 5
    else:              score += 0

    # Revenue growth contribution (0-30 pts)
    growth = avg_growth if not pd.isna(avg_growth) else 0
    if growth > 10:    score += 30
    elif growth > 5:   score += 20
    elif growth > 0:   score += 10
    else:              score += 0

    return min(score, 100)


# ── CLI preview ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.data_loader import load_data
    from src.kpi_calculator import calculate_all_kpis

    df = calculate_all_kpis(load_data())
    report = generate_insights(df)

    print(f"\n{'='*60}")
    print(f"  STARTUP KPI INSIGHT REPORT  |  {report.period}")
    print(f"  Business Health Score: {report.score}/100")
    print(f"{'='*60}\n")
    for line in report.to_list():
        print(line)
