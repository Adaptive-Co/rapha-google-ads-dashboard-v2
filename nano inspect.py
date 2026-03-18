import pandas as pd
import numpy as np

# =========================
# LOAD RAW DATA
# =========================

df = pd.read_csv(
    "Campaign Spend Efficiency & Conversion Performance – Exploratory Analysis.csv",
    skiprows=2
)

print("\n=== RAW SHAPE ===")
print(df.shape)

print("\n=== ORIGINAL COLUMNS ===")
print(df.columns.tolist())

# =========================
# RENAME COLUMNS (CORRECT)
# =========================

df.columns = [
    "campaign",
    "date",
    "currency",
    "cost",
    "conversions",
    "cpa_original",   # FIXED (was wrongly conversion_value)
    "clicks",
    "cvr",
    "search_lost_rank",
    "display_lost_rank",
    "search_lost_top_budget",
    "lost_impr_budget",
    "impressions",
    "ctr"
]

# =========================
# DROP USELESS COLUMNS
# =========================

df = df.drop(columns=[
    "currency",
    "search_lost_rank",
    "display_lost_rank",
    "search_lost_top_budget",
    "lost_impr_budget"
])

# =========================
# TYPE CLEANING
# =========================

# Date
df["date"] = pd.to_datetime(df["date"])

# Numeric columns
numeric_cols = ["cost", "conversions", "clicks", "impressions", "cpa_original"]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Percentage columns
for col in ["ctr", "cvr"]:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace("%", "", regex=False)
        .replace("--", np.nan)
    )
    df[col] = pd.to_numeric(df[col], errors="coerce") / 100

# =========================
# CLEAN CAMPAIGN NAMES
# =========================

df["campaign"] = (
    df["campaign"]
    .str.replace("🔥", "", regex=False)
    .str.strip()
)

# =========================
# DUPLICATE CHECK
# =========================

dupes = df.duplicated(subset=["campaign", "date"]).sum()
print("\n=== DUPLICATES (campaign + date) ===")
print(dupes)

# =========================
# FINAL AGGREGATION
# =========================

df_clean = df.groupby(["campaign", "date"], as_index=False).agg({
    "cost": "sum",
    "conversions": "sum",
    "clicks": "sum",
    "impressions": "sum",
    "ctr": "mean",   # average rate
    "cvr": "mean"
})

# =========================
# METRICS (CORRECT)
# =========================

# CPA (safe calculation)
df_clean["cpa"] = df_clean["cost"] / df_clean["conversions"]

# Replace inf with NaN (NOT 0)
df_clean["cpa"] = df_clean["cpa"].replace([np.inf, -np.inf], np.nan)

# =========================
# FINAL STRUCTURE
# =========================

df_clean = df_clean[[
    "campaign",
    "date",
    "cost",
    "conversions",
    "clicks",
    "impressions",
    "ctr",
    "cvr",
    "cpa"
]]

# =========================
# FINAL CHECKS
# =========================

print("\n=== CLEAN SHAPE ===")
print(df_clean.shape)

print("\n=== CLEAN SAMPLE ===")
print(df_clean.head())

print("\n=== NULL CHECK ===")
print(df_clean.isnull().sum())

# =========================
# SAVE CLEAN DATA
# =========================

df_clean.to_csv("clean_ads_data.csv", index=False)

print("\n✅ CLEAN DATASET READY: clean_ads_data.csv")
