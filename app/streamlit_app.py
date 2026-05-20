"""
streamlit_app.py
----------------
Interactive dashboard for the Startup KPI Analyzer.

Run with:  streamlit run app/streamlit_app.py
"""

import sys
import os

# Ensure src/ is importable regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from src.data_loader import load_data, get_summary
from src.kpi_calculator import calculate_all_kpis, get_latest_kpis, get_averages
from src.insights_generator import (
    generate_insights,
    SEVERITY_SUCCESS,
    SEVERITY_WARNING,
    SEVERITY_DANGER,
    SEVERITY_INFO,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Startup KPI Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background: #f9fafb;
        border-left: 4px solid #3b82f6;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
    }
    .insight-danger {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.8rem;
    }
    .insight-warning {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.8rem;
    }
    .insight-success {
        background-color: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.8rem;
    }
    .insight-info {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.8rem;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1f2937;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.4rem;
        margin: 1.5rem 0 1rem 0;
    }
    .health-score {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ── Data loading (cached so it only runs once) ─────────────────────────────
@st.cache_data
def load_all_data():
    raw = load_data()
    enriched = calculate_all_kpis(raw)
    report = generate_insights(enriched)
    summary = get_summary(raw)
    latest = get_latest_kpis(enriched)
    averages = get_averages(enriched)
    return enriched, report, summary, latest, averages


df, report, summary, latest, averages = load_all_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    chart_theme = st.selectbox("Chart theme", ["plotly_white", "plotly", "ggplot2"])
    show_raw = st.checkbox("Show raw dataset", value=False)
    show_averages = st.checkbox("Show trailing averages", value=True)

    st.markdown("---")
    st.markdown("### 📅 Dataset Period")
    st.info(summary["date_range"])
    st.metric("Months of data", summary["total_months"])

    st.markdown("---")
    st.markdown(
        "**Startup KPI Analyzer**\n\nBuilt with Python · Streamlit · Plotly\n\n"
        "[GitHub](https://github.com/oyesubhagi)"
    )


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">📊 Startup KPI Analyzer</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Automated business intelligence & consulting-grade insights '
    'for data-driven startup leadership</p>',
    unsafe_allow_html=True,
)

# ── Health Score + Summary KPIs ──────────────────────────────────────────────
score_col, m1, m2, m3, m4, m5 = st.columns([1.2, 1, 1, 1, 1, 1])

score_color = (
    "#22c55e" if report.score >= 70
    else "#f59e0b" if report.score >= 40
    else "#ef4444"
)
with score_col:
    st.markdown(
        f'<div style="text-align:center; padding:0.5rem;">'
        f'<div style="font-size:0.85rem; color:#6b7280; font-weight:600;">BUSINESS HEALTH</div>'
        f'<div class="health-score" style="color:{score_color};">{report.score}</div>'
        f'<div style="font-size:0.75rem; color:#9ca3af;">out of 100</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

with m1:
    st.metric(
        "Revenue (Latest)",
        f"£{latest['revenue']:,.0f}",
        f"{latest['revenue_growth']:.1f}% MoM" if latest['revenue_growth'] else None,
    )
with m2:
    st.metric(
        "Churn Rate",
        f"{latest['churn_rate']*100:.1f}%",
        delta=None,
        delta_color="inverse",
    )
with m3:
    st.metric("CAC", f"£{latest['cac']:.0f}")
with m4:
    st.metric("LTV", f"£{latest['ltv']:.0f}")
with m5:
    ratio = latest["ltv_cac_ratio"]
    st.metric(
        "LTV/CAC",
        f"{ratio:.2f}x",
        "Good" if ratio >= 3 else "Low",
        delta_color="normal" if ratio >= 3 else "inverse",
    )

st.markdown("---")

# ── Charts ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Revenue & Growth Trends</div>', unsafe_allow_html=True)

chart1_col, chart2_col = st.columns(2)

with chart1_col:
    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(
        x=df["Month"], y=df["Revenue"],
        mode="lines+markers",
        name="Revenue",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(size=6),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.08)",
    ))
    fig_rev.update_layout(
        title="Monthly Revenue",
        template=chart_theme,
        height=320,
        margin=dict(l=0, r=0, t=40, b=0),
        yaxis_tickprefix="£",
        xaxis_title=None,
    )
    st.plotly_chart(fig_rev, use_container_width=True)

with chart2_col:
    fig_growth = go.Figure()
    fig_growth.add_trace(go.Bar(
        x=df["Month"],
        y=df["Revenue_Growth_Rate"],
        name="MoM Growth %",
        marker_color=[
            "#22c55e" if v > 0 else "#ef4444"
            for v in df["Revenue_Growth_Rate"].fillna(0)
        ],
    ))
    fig_growth.update_layout(
        title="Revenue Growth Rate (MoM %)",
        template=chart_theme,
        height=320,
        margin=dict(l=0, r=0, t=40, b=0),
        yaxis_ticksuffix="%",
        xaxis_title=None,
    )
    st.plotly_chart(fig_growth, use_container_width=True)

# ── Churn Chart ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔄 Churn Rate Analysis</div>', unsafe_allow_html=True)

churn_col, netcust_col = st.columns(2)

with churn_col:
    fig_churn = go.Figure()
    fig_churn.add_trace(go.Scatter(
        x=df["Month"], y=df["Churn_Rate"] * 100,
        mode="lines+markers",
        name="Churn Rate %",
        line=dict(color="#ef4444", width=2.5),
        marker=dict(size=6),
    ))
    # Danger threshold line
    fig_churn.add_hline(
        y=10, line_dash="dash", line_color="#f97316",
        annotation_text="10% danger threshold",
        annotation_position="top right",
    )
    fig_churn.add_hline(
        y=3, line_dash="dot", line_color="#22c55e",
        annotation_text="3% excellent",
        annotation_position="bottom right",
    )
    fig_churn.update_layout(
        title="Monthly Churn Rate",
        template=chart_theme,
        height=320,
        yaxis_ticksuffix="%",
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis_title=None,
    )
    st.plotly_chart(fig_churn, use_container_width=True)

with netcust_col:
    fig_cust = go.Figure()
    fig_cust.add_trace(go.Bar(
        x=df["Month"], y=df["New_Customers"],
        name="New Customers",
        marker_color="#3b82f6",
    ))
    fig_cust.add_trace(go.Bar(
        x=df["Month"], y=-df["Churned_Customers"],
        name="Churned Customers",
        marker_color="#ef4444",
    ))
    fig_cust.add_trace(go.Scatter(
        x=df["Month"], y=df["Net_New_Customers"],
        name="Net New",
        mode="lines+markers",
        line=dict(color="#8b5cf6", width=2),
    ))
    fig_cust.update_layout(
        title="Customer Acquisition vs Churn",
        template=chart_theme,
        height=320,
        barmode="relative",
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis_title=None,
    )
    st.plotly_chart(fig_cust, use_container_width=True)

# ── CAC vs LTV ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">💰 CAC vs LTV — Marketing Efficiency</div>', unsafe_allow_html=True)

cac_col, ratio_col = st.columns(2)

with cac_col:
    fig_cac_ltv = go.Figure()
    fig_cac_ltv.add_trace(go.Scatter(
        x=df["Month"], y=df["LTV"],
        name="LTV",
        mode="lines+markers",
        line=dict(color="#22c55e", width=2.5),
        marker=dict(size=6),
    ))
    fig_cac_ltv.add_trace(go.Scatter(
        x=df["Month"], y=df["CAC"],
        name="CAC",
        mode="lines+markers",
        line=dict(color="#f59e0b", width=2.5),
        marker=dict(size=6),
    ))
    fig_cac_ltv.update_layout(
        title="CAC vs LTV Over Time",
        template=chart_theme,
        height=320,
        yaxis_tickprefix="£",
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis_title=None,
    )
    st.plotly_chart(fig_cac_ltv, use_container_width=True)

with ratio_col:
    fig_ratio = go.Figure()
    fig_ratio.add_trace(go.Scatter(
        x=df["Month"], y=df["LTV_CAC_Ratio"],
        mode="lines+markers",
        name="LTV/CAC",
        line=dict(color="#8b5cf6", width=2.5),
        marker=dict(size=6),
        fill="tozeroy",
        fillcolor="rgba(139,92,246,0.08)",
    ))
    fig_ratio.add_hline(y=3, line_dash="dash", line_color="#22c55e",
                        annotation_text="3x minimum", annotation_position="top right")
    fig_ratio.add_hline(y=5, line_dash="dot", line_color="#3b82f6",
                        annotation_text="5x scale signal", annotation_position="top right")
    fig_ratio.update_layout(
        title="LTV/CAC Ratio Trend",
        template=chart_theme,
        height=320,
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis_title=None,
    )
    st.plotly_chart(fig_ratio, use_container_width=True)

# ── ARPU Trend ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">👤 Revenue Per User (ARPU)</div>', unsafe_allow_html=True)
fig_arpu = go.Figure()
fig_arpu.add_trace(go.Scatter(
    x=df["Month"], y=df["ARPU"],
    mode="lines+markers",
    name="ARPU",
    line=dict(color="#06b6d4", width=2.5),
    fill="tozeroy",
    fillcolor="rgba(6,182,212,0.08)",
))
fig_arpu.update_layout(
    title="Average Revenue Per User (Monthly)",
    template=chart_theme,
    height=280,
    yaxis_tickprefix="£",
    margin=dict(l=0, r=0, t=40, b=0),
)
st.plotly_chart(fig_arpu, use_container_width=True)

# ── Insights ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🧠 Automated Business Insights</div>', unsafe_allow_html=True)
st.markdown(
    f"**Period:** {report.period} &nbsp;|&nbsp; "
    f"**Business Health Score:** {report.score}/100 &nbsp;|&nbsp; "
    f"**{len(report.insights)} insights generated**"
)

severity_css = {
    SEVERITY_DANGER:  "insight-danger",
    SEVERITY_WARNING: "insight-warning",
    SEVERITY_SUCCESS: "insight-success",
    SEVERITY_INFO:    "insight-info",
}

# Sort by severity so dangers appear first
order = {SEVERITY_DANGER: 0, SEVERITY_WARNING: 1, SEVERITY_INFO: 2, SEVERITY_SUCCESS: 3}
sorted_insights = sorted(report.insights, key=lambda i: order.get(i.severity, 9))

for ins in sorted_insights:
    css_class = severity_css.get(ins.severity, "insight-info")
    st.markdown(
        f'<div class="{css_class}">'
        f'<strong>{ins.headline}</strong><br>'
        f'<span style="font-size:0.9rem; color:#374151;">{ins.detail}</span><br><br>'
        f'<span style="font-size:0.85rem; color:#1d4ed8;"><strong>✅ Recommended Action:</strong> {ins.action}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Trailing averages ─────────────────────────────────────────────────────────
if show_averages:
    st.markdown('<div class="section-title">📐 Trailing Averages</div>', unsafe_allow_html=True)
    avg_cols = st.columns(5)
    avg_data = [
        ("Avg Churn Rate", f"{averages['avg_churn_rate']*100:.1f}%"),
        ("Avg CAC",        f"£{averages['avg_cac']:.0f}"),
        ("Avg LTV/CAC",    f"{averages['avg_ltv_cac']:.2f}x"),
        ("Avg Rev Growth", f"{averages['avg_revenue_growth']:.1f}%"),
        ("Avg ARPU",       f"£{averages['avg_arpu']:.0f}"),
    ]
    for col, (label, val) in zip(avg_cols, avg_data):
        col.metric(label, val)

# ── Raw dataset ───────────────────────────────────────────────────────────────
if show_raw:
    st.markdown('<div class="section-title">🗃️ Raw Dataset</div>', unsafe_allow_html=True)
    display_df = df.copy()
    display_df["Month"] = display_df["Month"].dt.strftime("%b %Y")
    display_df["Churn_Rate"] = (display_df["Churn_Rate"] * 100).round(1).astype(str) + "%"
    display_df["Revenue_Growth_Rate"] = display_df["Revenue_Growth_Rate"].round(1).astype(str) + "%"
    st.dataframe(display_df, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#9ca3af; font-size:0.8rem;">'
    "Startup KPI Analyzer · Built by Subhagi Gupta · "
    "<a href='https://github.com/oyesubhagi' style='color:#3b82f6;'>GitHub</a>"
    "</p>",
    unsafe_allow_html=True,
)
