"""
data_loader.py
--------------
Responsible for loading, validating, and cleaning the startup KPI dataset.
Acts as the single source of truth for data ingestion across the project.
"""

import pandas as pd
import os


def load_data(filepath: str = None) -> pd.DataFrame:
    """
    Load startup data from a CSV file, apply basic cleaning,
    and return a validated DataFrame ready for KPI calculations.

    Parameters
    ----------
    filepath : str, optional
        Path to the CSV file. Defaults to the standard data/ location.

    Returns
    -------
    pd.DataFrame
        Cleaned and typed DataFrame.
    """
    if filepath is None:
        # Resolve path relative to this file so the project is portable
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, "data", "startup_data.csv")

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Data file not found at '{filepath}'. "
            "Please ensure startup_data.csv exists in the data/ directory."
        )

    df = pd.read_csv(filepath)

    df = _clean_data(df)

    print(f"[DataLoader] Loaded {len(df)} rows from '{filepath}'")
    return df


def _clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Internal cleaning pipeline:
    - Parse Month as datetime
    - Strip whitespace from column names
    - Fill or drop missing values
    - Enforce numeric types on metric columns
    - Remove rows where core business metrics are zero or negative
    """

    # Normalise column names (strip accidental spaces)
    df.columns = df.columns.str.strip()

    # Parse the Month column into a proper datetime for time-series ordering
    df["Month"] = pd.to_datetime(df["Month"], format="%Y-%m", errors="coerce")

    # Drop rows where Month couldn't be parsed — they would break all time series
    df = df.dropna(subset=["Month"])

    # Define columns that must be numeric for KPI calculations
    numeric_cols = [
        "Customers",
        "New_Customers",
        "Churned_Customers",
        "Revenue",
        "Marketing_Spend",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill missing numeric values with column median (conservative imputation)
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    # Business sanity check: Customers and Revenue must be > 0
    df = df[(df["Customers"] > 0) & (df["Revenue"] > 0)]

    # Sort chronologically so growth rates calculate in the right direction
    df = df.sort_values("Month").reset_index(drop=True)

    return df


def get_summary(df: pd.DataFrame) -> dict:
    """
    Return a quick summary dictionary useful for dashboard header cards.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame (output of load_data).

    Returns
    -------
    dict
        High-level summary statistics.
    """
    return {
        "total_months": len(df),
        "date_range": f"{df['Month'].min().strftime('%b %Y')} – {df['Month'].max().strftime('%b %Y')}",
        "total_revenue": df["Revenue"].sum(),
        "avg_customers": df["Customers"].mean(),
        "total_new_customers": df["New_Customers"].sum(),
        "total_churned": df["Churned_Customers"].sum(),
        "total_marketing_spend": df["Marketing_Spend"].sum(),
    }


# ── Quick sanity test when run directly ──────────────────────────────────────
if __name__ == "__main__":
    data = load_data()
    print(data.head())
    print("\nSummary:", get_summary(data))
