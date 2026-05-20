# 📊 Startup KPI Analyzer

> **Automated business intelligence tool that transforms raw startup operational data into consulting-grade KPI analysis and actionable insights.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat-square&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📌 Project Overview

**Startup KPI Analyzer** is a modular Python analytics system that ingests monthly startup operational data and automatically computes the five most critical business KPIs — Churn Rate, CAC, LTV, LTV/CAC Ratio, and Revenue Growth Rate — then generates consulting-style insights and recommendations via an interactive Streamlit dashboard.

The system is designed to simulate the role of a data-driven business analyst embedded in a startup finance or operations team: turning raw numbers into board-ready narrative.

---

## 🎯 Problem Statement

Early-stage startups often have access to raw operational data (customers, revenue, marketing spend) but lack the analytical infrastructure to derive actionable KPIs from it. Leadership ends up making growth, marketing, and retention decisions on intuition rather than metrics.

This project solves that gap by:
- **Automating** KPI computation from any structured CSV
- **Generating** human-readable business insights with thresholds and benchmarks
- **Visualising** trends in an interactive dashboard accessible to non-technical stakeholders
- **Recommending** specific, prioritised actions based on the data

---

## ✨ Features

| Feature | Description |
|---|---|
| 📥 **Data Loader** | Loads, cleans, and validates CSV data with robust error handling |
| ⚙️ **KPI Engine** | Computes 7 KPIs including Churn, CAC, LTV, LTV/CAC, ARPU, Growth Rate |
| 🧠 **Insights Generator** | Produces 6+ consulting-style insights with severity levels and action plans |
| 📊 **Streamlit Dashboard** | Interactive charts, KPI cards, and a business health score (0–100) |
| 📓 **Jupyter Notebook** | Full EDA with correlation analysis and trend visualisations |
| 📈 **Power BI Guide** | Step-by-step instructions for building the executive BI dashboard |

---

## 📐 KPIs Explained

| KPI | Formula | What It Tells You |
|---|---|---|
| **Churn Rate** | Churned ÷ Total Customers | What % of customers left this month? |
| **CAC** | Marketing Spend ÷ New Customers | How much does it cost to acquire one customer? |
| **ARPU** | Revenue ÷ Total Customers | How much does each customer contribute monthly? |
| **LTV** | ARPU × 12 months | How much will a customer generate over their lifetime? |
| **LTV/CAC Ratio** | LTV ÷ CAC | Is marketing spend generating enough return? (<3 = bad, >5 = scale) |
| **Revenue Growth** | (Rev_t − Rev_t-1) ÷ Rev_t-1 | Month-over-month revenue momentum |
| **Net New Customers** | New − Churned | Is the customer base actually growing? |

### Benchmark Reference

```
LTV/CAC < 1.0  → 🚨 Unit economics broken — do not scale
LTV/CAC 1–2    → 🔴 Inefficient — improve or rethink channels
LTV/CAC 2–3    → 🟡 Approaching minimum viable
LTV/CAC 3–5    → ✅ Healthy — controlled growth is safe
LTV/CAC > 5    → 🚀 Scale marketing aggressively

Churn < 3%     → 🏆 Best-in-class
Churn 3–7%     → ✅ Healthy
Churn 7–10%    → 🔶 Watch zone
Churn > 10%    → 🚨 Urgent retention intervention needed
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Data Manipulation | Pandas, NumPy |
| Visualisation | Plotly, Matplotlib |
| Dashboard | Streamlit |
| Notebook | Jupyter |
| BI Tool | Power BI (optional) |

---

## 📁 Project Structure

```
startup-kpi-analyzer/
│
├── data/
│   └── startup_data.csv          # 12-month sample dataset
│
├── src/
│   ├── data_loader.py            # CSV ingestion, cleaning, validation
│   ├── kpi_calculator.py         # All KPI computation logic
│   └── insights_generator.py     # Business insight engine
│
├── app/
│   └── streamlit_app.py          # Interactive dashboard
│
├── notebooks/
│   └── exploratory_analysis.ipynb  # EDA + trend analysis
│
├── dashboard/
│   └── powerbi_dashboard_guide.md  # Power BI build instructions
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 How to Run

### Prerequisites
- Python 3.10 or higher
- pip

### Step 1 — Clone the repository
```bash
git clone https://github.com/oyesubhagi/startup-kpi-analyzer.git
cd startup-kpi-analyzer
```

### Step 2 — Create a virtual environment (recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the Streamlit dashboard
```bash
streamlit run app/streamlit_app.py
```
Opens automatically at `http://localhost:8501`

### Step 5 — Run the insight engine from CLI
```bash
python src/insights_generator.py
```

### Step 6 — Explore the notebook
```bash
jupyter notebook notebooks/exploratory_analysis.ipynb
```

---

## 📸 Dashboard Preview

The interactive dashboard includes:

**Header Row:** Business Health Score (0–100) · Revenue · Churn Rate · CAC · LTV · LTV/CAC

**Charts:**
- Monthly Revenue bar chart with MoM growth overlay
- Churn Rate trend with 3% and 10% threshold markers
- Customer acquisition vs churn waterfall
- CAC vs LTV dual-line chart
- LTV/CAC ratio trend with benchmark lines at 3x and 5x
- ARPU trend

**Insights Panel:** Auto-generated consulting-style recommendations colour-coded by severity (red → amber → blue → green)

**Sidebar:** Theme toggle · Raw data view · Trailing averages

---

## 🔮 Future Improvements

| Improvement | Description |
|---|---|
| 🗄️ Database integration | Replace CSV with PostgreSQL or BigQuery connector |
| 📤 Automated reporting | Weekly email digest of KPI snapshot via SendGrid |
| 🤖 ML forecasting | ARIMA or Prophet model for 3-month revenue forecast |
| 🎯 Cohort analysis | Track KPIs by customer acquisition cohort, not just month |
| 🔔 Alerting system | Slack/email alert when KPI crosses danger threshold |
| 🌍 Multi-company | Support uploading multiple companies for benchmarking |
| 🔐 Auth layer | Streamlit Cloud auth for team access control |

---

## 👩‍💻 Author

**Subhagi Gupta**  
B.Tech Biotechnology (CGPA 8.0) — Banasthali Vidyapith  
Research Intern @ IISc Bengaluru · Ex-Intern @ DRDO New Delhi

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/subhagi-gupta-408817258/)
[![GitHub](https://img.shields.io/badge/GitHub-oyesubhagi-181717?style=flat-square&logo=github)](https://github.com/oyesubhagi)
[![Email](https://img.shields.io/badge/Email-subhagigupta25%40gmail.com-D14836?style=flat-square&logo=gmail)](mailto:subhagigupta25@gmail.com)

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

*Built to demonstrate the intersection of data analytics, business strategy, and software engineering.*
