import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Rapha Google Ads Dashboard", layout="wide")

st.title("🚀 Rapha | Google Ads Campaign Intelligence Dashboard")

# ----------------------------
# LOAD DATA
# ----------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("Rapha_google_ads_campaign_daily.csv", skiprows=3)

    df.columns = df.columns.str.strip()

    num_cols = ["Cost", "Clicks", "Impr.", "Conversions", "Conv. value"]
    for c in num_cols:
        df[c] = df[c].astype(str).str.replace(",", "").astype(float)

    df["Day"] = pd.to_datetime(df["Day"])

    return df

df = load_data()

# ----------------------------
# SIDEBAR FILTERS
# ----------------------------

st.sidebar.header("Dashboard Filters")

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["Day"].min(), df["Day"].max()]
)

campaign_filter = st.sidebar.multiselect(
    "Select Campaign",
    options=df["Campaign"].unique(),
    default=df["Campaign"].unique()
)

filtered = df[
    (df["Campaign"].isin(campaign_filter)) &
    (df["Day"] >= pd.to_datetime(date_range[0])) &
    (df["Day"] <= pd.to_datetime(date_range[1]))
]

# ----------------------------
# KPI CARDS
# ----------------------------

total_cost = filtered["Cost"].sum()
total_revenue = filtered["Conv. value"].sum()
total_conv = filtered["Conversions"].sum()
total_clicks = filtered["Clicks"].sum()
total_impr = filtered["Impr."].sum()

roas = total_revenue / total_cost if total_cost > 0 else 0
ctr = total_clicks / total_impr if total_impr > 0 else 0
cpc = total_cost / total_clicks if total_clicks > 0 else 0

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Spend", f"£{total_cost:,.0f}")
c2.metric("Revenue", f"£{total_revenue:,.0f}")
c3.metric("Conversions", f"{total_conv:,.0f}")
c4.metric("ROAS", f"{roas:.2f}")
c5.metric("CTR", f"{ctr:.2%}")
c6.metric("CPC", f"£{cpc:.2f}")

st.divider()

# ----------------------------
# CAMPAIGN PERFORMANCE
# ----------------------------

st.header("Campaign Performance")

campaign_perf = (
    filtered.groupby("Campaign")
    .agg(
        Spend=("Cost", "sum"),
        Revenue=("Conv. value", "sum"),
        Conversions=("Conversions", "sum"),
        Clicks=("Clicks", "sum"),
        Impressions=("Impr.", "sum")
    )
    .reset_index()
)

campaign_perf["ROAS"] = campaign_perf["Revenue"] / campaign_perf["Spend"]
campaign_perf["CTR"] = campaign_perf["Clicks"] / campaign_perf["Impressions"]
campaign_perf["CPC"] = campaign_perf["Spend"] / campaign_perf["Clicks"]

# Top spend campaigns

top_campaigns = campaign_perf.sort_values("Spend", ascending=False).head(10)

fig = px.bar(
    top_campaigns,
    y="Campaign",
    x="Spend",
    orientation="h",
    title="Top Campaigns by Spend"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Campaign Performance Table")

st.dataframe(
    campaign_perf.sort_values("Revenue", ascending=False),
    use_container_width=True
)

st.divider()

# ----------------------------
# DAILY PERFORMANCE TREND
# ----------------------------

st.header("Daily Spend vs Revenue")

daily = (
    filtered.groupby("Day")
    .agg(
        Spend=("Cost", "sum"),
        Revenue=("Conv. value", "sum"),
        Clicks=("Clicks", "sum"),
        Impressions=("Impr.", "sum")
    )
    .reset_index()
)

daily["ROAS"] = daily["Revenue"] / daily["Spend"]

fig2 = px.line(
    daily,
    x="Day",
    y=["Spend", "Revenue"],
    title="Spend vs Revenue Over Time"
)

st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# ROAS TREND
# ----------------------------

st.header("ROAS Trend")

fig_roas = px.line(
    daily,
    x="Day",
    y="ROAS",
    title="Return on Ad Spend Over Time"
)

st.plotly_chart(fig_roas, use_container_width=True)

# ----------------------------
# SCALING EFFICIENCY METRIC
# ----------------------------

daily["Spend Change"] = daily["Spend"].diff()
daily["Revenue Change"] = daily["Revenue"].diff()

daily["Delta Efficiency"] = daily["Revenue Change"] / daily["Spend Change"]

latest_delta = daily["Delta Efficiency"].iloc[-1]

st.subheader("Scaling Efficiency")

st.metric(
    "Revenue vs Spend Delta",
    f"{latest_delta:.2f}"
)

# ----------------------------
# CAMPAIGN EFFICIENCY MAP
# ----------------------------

st.header("Campaign Efficiency Map")

fig3 = px.scatter(
    campaign_perf,
    x="Spend",
    y="Revenue",
    size="Conversions",
    color="ROAS",
    hover_name="Campaign",
    title="Campaign Efficiency"
)

st.plotly_chart(fig3, use_container_width=True)

# ----------------------------
# BEST & WORST CAMPAIGNS
# ----------------------------

st.header("Performance Diagnostics")

best = campaign_perf.sort_values("ROAS", ascending=False).head(5)
worst = campaign_perf.sort_values("ROAS", ascending=True).head(5)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top ROAS Campaigns")
    st.dataframe(best)

with col2:
    st.subheader("Lowest ROAS Campaigns")
    st.dataframe(worst)
