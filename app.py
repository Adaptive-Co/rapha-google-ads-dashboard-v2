import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Rapha Google Ads Dashboard", layout="wide")

st.title("🚀 Rapha | Google Ads Campaign Dashboard")

# ----------------------------
# LOAD DATA
# ----------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("Rapha_google_ads_campaign_daily.csv", skiprows=3)

    df.columns = df.columns.str.strip()

    # Convert numbers with commas
    num_cols = ["Cost", "Clicks", "Impr.", "Conversions", "Conv. value"]
    for c in num_cols:
        df[c] = df[c].astype(str).str.replace(",", "").astype(float)

    df["Day"] = pd.to_datetime(df["Day"])

    return df


df = load_data()

# ----------------------------
# KPI CARDS
# ----------------------------

total_cost = df["Cost"].sum()
total_revenue = df["Conv. value"].sum()
total_conv = df["Conversions"].sum()
roas = total_revenue / total_cost

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Spend", f"£{total_cost:,.0f}")
c2.metric("Revenue", f"£{total_revenue:,.0f}")
c3.metric("Conversions", f"{total_conv:,.0f}")
c4.metric("ROAS", f"{roas:.2f}")

st.divider()

# ----------------------------
# CAMPAIGN PERFORMANCE
# ----------------------------

st.header("Campaign Performance")

campaign_perf = df.groupby("Campaign")[["Cost", "Conv. value", "Conversions"]].sum()

campaign_perf["ROAS"] = campaign_perf["Conv. value"] / campaign_perf["Cost"]

fig = px.bar(
    campaign_perf.sort_values("Cost", ascending=False).head(10),
    y=campaign_perf.sort_values("Cost", ascending=False).head(10).index,
    x="Cost",
    orientation="h",
    title="Top Campaigns by Spend"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Campaign Performance Table")

st.dataframe(
    campaign_perf.sort_values("ROAS", ascending=False)
)

# ----------------------------
# DAILY TREND
# ----------------------------

st.header("Daily Spend vs Revenue")

daily = df.groupby("Day")[["Cost", "Conv. value"]].sum()

fig2 = px.line(
    daily,
    x=daily.index,
    y=["Cost", "Conv. value"],
    title="Spend vs Revenue Over Time"
)

st.plotly_chart(fig2, use_container_width=True)
