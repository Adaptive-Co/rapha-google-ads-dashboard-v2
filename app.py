import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Rapha Ads Intelligence", layout="wide")

px.defaults.template = "plotly_white"

st.title("Rapha | Google Ads Product Intelligence Dashboard")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("rapha_campaign_clean.csv")

    numeric_cols = ["cost","clicks","impr","conversions","conv_value"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    possible_dates = ["day","Day","date","Date"]
    date_col = None

    for col in possible_dates:
        if col in df.columns:
            date_col = col
            break

    if date_col:
        df = df.rename(columns={date_col:"day"})
        df["day"] = pd.to_datetime(df["day"], errors="coerce")
    else:
        df["day"] = pd.date_range(
            start="2024-01-01",
            periods=len(df),
            freq="D"
        )

    return df


df = load_data()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Global Filters")

campaign_filter = st.sidebar.multiselect(
    "Campaign",
    options=sorted(df["campaign"].dropna().unique()),
    default=list(df["campaign"].dropna().unique())
)

filtered = df[df["campaign"].isin(campaign_filter)]

# --------------------------------------------------
# PRODUCT DATASET
# --------------------------------------------------

product_perf = (
    filtered
    .groupby("product_title", dropna=False)
    .agg(
        Spend=("cost","sum"),
        Revenue=("conv_value","sum"),
        Conversions=("conversions","sum"),
        Clicks=("clicks","sum"),
        Impressions=("impr","sum")
    )
    .reset_index()
)

product_perf["ROAS"] = product_perf["Revenue"] / product_perf["Spend"]
product_perf["AOV"] = product_perf["Revenue"] / product_perf["Conversions"]

product_perf["Cost Share"] = product_perf["Spend"] / product_perf["Spend"].sum()
product_perf["Revenue Share"] = product_perf["Revenue"] / product_perf["Revenue"].sum()

product_perf["Efficiency Ratio"] = (
    product_perf["Cost Share"] / product_perf["Revenue Share"]
)

product_perf.replace([float("inf"), -float("inf")], 0, inplace=True)
product_perf.fillna(0, inplace=True)

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Product Breakdown",
    "Campaign Analysis",
    "Budget Engine"
])

# --------------------------------------------------
# TAB 1 - OVERVIEW
# --------------------------------------------------

with tab1:

    total_spend = filtered["cost"].sum()
    total_rev = filtered["conv_value"].sum()
    total_conv = filtered["conversions"].sum()
    total_clicks = filtered["clicks"].sum()
    total_impr = filtered["impr"].sum()

    roas = total_rev / total_spend if total_spend else 0
    ctr = total_clicks / total_impr if total_impr else 0
    cpc = total_spend / total_clicks if total_clicks else 0

    c1,c2,c3,c4,c5,c6 = st.columns(6)

    c1.metric("Spend", f"{total_spend:,.0f}")
    c2.metric("Revenue", f"{total_rev:,.0f}")
    c3.metric("Conversions", f"{total_conv:,.0f}")
    c4.metric("ROAS", f"{roas:.2f}")
    c5.metric("CTR", f"{ctr:.2%}")
    c6.metric("CPC", f"{cpc:.2f}")

    st.divider()

    st.subheader("Daily Performance Trends")

    daily = (
        filtered
        .groupby("day")
        .agg(
            Spend=("cost","sum"),
            Revenue=("conv_value","sum")
        )
        .reset_index()
    )

    daily["ROAS"] = daily["Revenue"] / daily["Spend"]

    metric_selector = st.multiselect(
        "Select Metrics",
        ["Spend","Revenue","ROAS"],
        default=["Spend","Revenue"]
    )

    fig = px.line(
        daily,
        x="day",
        y=metric_selector,
        markers=True
    )

    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# TAB 2 - PRODUCT BREAKDOWN
# --------------------------------------------------

with tab2:

    st.subheader("Product Performance Insights")

    top_rev = product_perf.sort_values("Revenue",ascending=False).iloc[0]
    top_spend = product_perf.sort_values("Spend",ascending=False).iloc[0]
    top_roas = product_perf.sort_values("ROAS",ascending=False).iloc[0]

    c1,c2,c3 = st.columns(3)

    c1.metric("Top Revenue Product", f"{top_rev['Revenue']:,.0f}", top_rev["product_title"])
    c2.metric("Highest Spend Product", f"{top_spend['Spend']:,.0f}", top_spend["product_title"])
    c3.metric("Best ROAS Product", f"{top_roas['ROAS']:.2f}x", top_roas["product_title"])

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        product_search = st.text_input("Search Product")

    with col2:
        min_spend = st.number_input("Min Spend", value=0.0)

    with col3:
        min_aov = st.number_input("Min AOV", value=0.0)

    with col4:
        show_all = st.checkbox("Show All Products", value=False)

    metric_selector = st.multiselect(
        "Metrics to Visualize",
        ["Revenue","Spend","ROAS","Conversions"],
        default=["Revenue"]
    )

    filtered_products = product_perf.copy()

    if product_search:
        filtered_products = filtered_products[
            filtered_products["product_title"].str.contains(product_search, case=False, na=False)
        ]

    filtered_products = filtered_products[
        filtered_products["Spend"] >= min_spend
    ]

    filtered_products = filtered_products[
        filtered_products["AOV"] >= min_aov
    ]

    if not show_all:
        filtered_products = filtered_products.sort_values("Spend",ascending=False).head(50)

    fig = px.bar(
        filtered_products.head(10),
        x="product_title",
        y=metric_selector,
        barmode="group"
    )

    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("ROAS vs Spend")

    fig = px.scatter(
        filtered_products,
        x="Spend",
        y="ROAS",
        size="Revenue",
        hover_name="product_title",
        color="Efficiency Ratio"
    )

    fig.add_hline(y=2)
    fig.add_vline(x=filtered_products["Spend"].median())

    fig.update_layout(height=600)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Product Performance Table")

    st.dataframe(filtered_products, use_container_width=True)

# --------------------------------------------------
# TAB 3 - CAMPAIGN ANALYSIS
# --------------------------------------------------

with tab3:

    st.subheader("Campaign Performance")

    campaign_perf = (
        filtered
        .groupby("campaign")
        .agg(
            Spend=("cost","sum"),
            Revenue=("conv_value","sum"),
            Conversions=("conversions","sum")
        )
        .reset_index()
    )

    campaign_perf["ROAS"] = campaign_perf["Revenue"] / campaign_perf["Spend"]

    fig = px.bar(
        campaign_perf.sort_values("Spend", ascending=False),
        x="Spend",
        y="campaign",
        orientation="h"
    )

    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(campaign_perf.sort_values("Revenue", ascending=False), use_container_width=True)

# --------------------------------------------------
# TAB 4 - BUDGET ENGINE
# --------------------------------------------------

with tab4:

    st.subheader("Budget Reallocation Engine")

    col1,col2 = st.columns(2)

    with col1:
        min_roas = st.slider("Minimum ROAS",0.0,10.0,0.0)

    with col2:
        max_ratio = st.slider("Max Efficiency Ratio",0.0,3.0,3.0)

    filtered_budget = product_perf[
        (product_perf["ROAS"] >= min_roas) &
        (product_perf["Efficiency Ratio"] <= max_ratio)
    ]

    def recommendation(row):

        roas = row["ROAS"]
        ratio = row["Efficiency Ratio"]

        if roas > 4 and ratio < 0.8:
            return "Scale"

        if roas > 3 and ratio < 1:
            return "Increase Budget"

        if 1 <= ratio <= 1.2:
            return "Maintain"

        if ratio > 1.2 and roas < 2:
            return "Reduce Budget"

        if roas < 1:
            return "Pause"

        return "Review"

    filtered_budget["Recommendation"] = filtered_budget.apply(recommendation, axis=1)

    st.dataframe(
        filtered_budget[
            [
                "product_title",
                "Spend",
                "Revenue",
                "ROAS",
                "Efficiency Ratio",
                "Recommendation"
            ]
        ].sort_values("Spend", ascending=False),
        use_container_width=True
    )