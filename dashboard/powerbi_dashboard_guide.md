# 📊 Power BI Dashboard — Build Guide

> This file explains how to recreate the Startup KPI Analyzer dashboard in Power BI Desktop (free).
> The `.pbix` binary is not version-controlled; follow these steps to build it from the CSV.

---

## 1. Load the Data

1. Open **Power BI Desktop**
2. Home → **Get Data → Text/CSV**
3. Select `data/startup_data.csv`
4. In the Power Query preview, click **Transform Data**

### In Power Query Editor:
- Change `Month` column type → **Date** (format: YYYY-MM)
- Ensure `Revenue`, `Marketing_Spend` are **Decimal Number**
- Ensure `Customers`, `New_Customers`, `Churned_Customers` are **Whole Number**
- Click **Close & Apply**

---

## 2. Create Calculated Columns (DAX)

In the **Data** view, add these calculated columns:

```dax
Churn Rate =
DIVIDE([Churned_Customers], [Customers])

CAC =
DIVIDE([Marketing_Spend], [New_Customers])

ARPU =
DIVIDE([Revenue], [Customers])

LTV =
[ARPU] * 12

LTV_CAC_Ratio =
DIVIDE([LTV], [CAC])

Net_New_Customers =
[New_Customers] - [Churned_Customers]
```

For Revenue Growth Rate (requires a sorted table context):
```dax
Revenue_Growth_Rate =
VAR prev = CALCULATE(
    SUM(startup_data[Revenue]),
    DATEADD(startup_data[Month], -1, MONTH)
)
RETURN
IF(
    ISBLANK(prev),
    BLANK(),
    DIVIDE(SUM(startup_data[Revenue]) - prev, prev) * 100
)
```

---

## 3. Dashboard Layout (4 pages)

---

### Page 1: Executive Summary

**KPI Cards (top row)** — Insert → Card visual:
| Card | Field | Format |
|---|---|---|
| Total Revenue | SUM(Revenue) | £ currency |
| Latest Churn | LASTNONBLANK(Churn Rate) | % |
| LTV/CAC | AVERAGE(LTV_CAC_Ratio) | 2 decimal |
| Net New Customers | SUM(Net_New_Customers) | whole number |

**Health Score Gauge** — Insert → Gauge:
- Value: compute a DAX measure: `Health Score = IF(AVERAGE([LTV_CAC_Ratio]) > 3, 70, 40)`
- Min: 0, Max: 100, Target: 70
- Colour code green/amber/red in Format pane

**Revenue Trend** — Line chart:
- X-axis: Month
- Y-axis: Revenue
- Enable data labels and trend line (Analytics pane → Trend Line)

---

### Page 2: Churn Analysis

**Churn Rate Line Chart:**
- X-axis: Month
- Y-axis: Churn Rate (format as %)
- Add a **Constant Line** at 0.10 (10%) — Analytics pane → Constant Line → value: 0.1
- Add a second constant line at 0.03 (3%) in green

**Stacked Bar — New vs Churned:**
- X-axis: Month
- Values: New_Customers (green), Churned_Customers (red)
- Enable small multiples for per-month comparison

**Churn Rate Card (latest month):**
- Conditional formatting: green if <0.07, amber if 0.07–0.10, red if >0.10

---

### Page 3: Marketing Efficiency

**CAC vs LTV Line Chart:**
- X-axis: Month
- Y-axis: CAC (amber line), LTV (green line)
- The gap between the two lines visually represents profitability per customer

**LTV/CAC Ratio Chart:**
- Line chart with reference lines at 3x (minimum viable) and 5x (scale signal)
- Apply conditional formatting background: red zone <3, green zone >5

**Marketing Spend vs Revenue Scatter:**
- X-axis: Marketing_Spend
- Y-axis: Revenue
- Size: Customers
- Add trend line — positive correlation is expected and confirms spend efficiency

---

### Page 4: Customer Growth

**Net New Customers Waterfall Chart:**
- Category: Month
- Breakdown: New_Customers (positive), Churned_Customers (negative)
- This is the most intuitive way to show growth vs contraction at a glance

**Customer Count Over Time:**
- Line chart: Customers by Month
- Annotate any inflection points

**ARPU Trend:**
- Line chart: ARPU by Month
- Rising ARPU = upsell success or pricing power

---

## 4. Slicers & Interactivity

Add a **Date Range Slicer** (Between style) on each page linked to the Month field.
This lets viewers zoom into specific quarters.

Add a **Churn Threshold Slicer** (numeric range) — using a what-if parameter:
```
Home → New Parameter → Numeric Range
Name: "Churn Threshold"
Min: 0, Max: 0.20, Increment: 0.01, Default: 0.10
```
Then use this in a conditional DAX measure to highlight months above threshold dynamically.

---

## 5. Publish

- File → **Publish to Power BI Service** (free account sufficient)
- Share the link with the team or embed in a web report
- Schedule data refresh if connected to a live database rather than CSV

---

## Tips for a polished report
- Use a **dark theme** (View → Themes → Executive) for a modern consulting look
- Lock all visuals (right-click → Lock) before sharing to prevent accidental moves
- Add the Startup KPI Analyzer logo as a top-left image on each page
- Export as PDF for static sharing: File → Export → PDF
