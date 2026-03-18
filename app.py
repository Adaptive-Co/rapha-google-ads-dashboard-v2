import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Rapha Ads Intelligence", layout="wide")

# --------------------------------------------------
# LOGO + HEADER (ADD THIS HERE)
# --------------------------------------------------
col1, col2 = st.columns([1, 6])

with col1:
    st.image("Logo.png", width=110)   # or "Logo.png"

with col2:
    st.markdown("## Rapha Ads Intelligence")

# --------------------------------------------------
# STYLING
# --------------------------------------------------
st.markdown("""
<style>
.exec-card {
    background: #f8fafc;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 12px;
    border: 1px solid #e2e8f0;
}
.section-title {
    font-size: 18px;
    font-weight: 600;
}
.muted {
    color: #64748b;
}
.highlight {
    background: #013a7a;
    color: white;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("Rapha | Google Ads Product Intelligence Dashboard")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("rapha_campaign_clean.csv")

    num_cols = ["cost","clicks","impr","conversions","conv_value"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    currency = df["currency_code"].iloc[0] if "currency_code" in df.columns else "GBP"
    symbol_map = {"GBP": "£", "EUR": "€", "USD": "$"}
    currency_symbol = symbol_map.get(currency, "£")

    return df, currency_symbol

df, currency_symbol = load_data()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
campaign_filter = st.sidebar.multiselect(
    "Select Campaigns",
    options=sorted(df["campaign"].dropna().unique()),
    default=list(df["campaign"].dropna().unique())
)

filtered = df[df["campaign"].isin(campaign_filter)]

if filtered.empty:
    st.warning("No data selected")
    st.stop()

# --------------------------------------------------
# PRODUCT PERF
# --------------------------------------------------
product_perf = (
    filtered.groupby("product_title")
    .agg(
        Spend=("cost","sum"),
        Revenue=("conv_value","sum"),
        Conversions=("conversions","sum")
    )
    .reset_index()
)

product_perf["ROAS"] = product_perf["Revenue"] / product_perf["Spend"].replace(0, np.nan)
product_perf = product_perf.fillna(0)

# --------------------------------------------------
# GLOBAL METRICS
# --------------------------------------------------
total_spend = filtered["cost"].sum()
total_rev = filtered["conv_value"].sum()
total_conv = filtered["conversions"].sum()
roas = total_rev / total_spend if total_spend else 0

# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview",
    "Performance Snapshot",
    "Products",
    "Campaigns",
    "Budget Engine",
    "Meridian Analysis",
    "Meridian Simulator"
])
# --------------------------------------------------
# TAB 1 — OVERVIEW (UPGRADED UI)
# --------------------------------------------------
with tab1:

    st.markdown("## 🧠 Executive Overview")

    # -----------------------------------
    # KPI ROW (CLEAN + VISUAL)
    # -----------------------------------
    c1, c2, c3 = st.columns(3)

    c1.metric("💰 Revenue", f"{currency_symbol}{total_rev:,.0f}")
    c2.metric("💸 Spend", f"{currency_symbol}{total_spend:,.0f}")
    c3.metric("📈 ROAS", f"{roas:.2f}")

    st.markdown("---")

    # -----------------------------------
    # WHAT THIS DASHBOARD DOES (SIMPLER)
    # -----------------------------------
    st.markdown("### 🎯 What this dashboard answers")

    st.info(f"""
    Where should we scale spend, and where should we cut?

    This dashboard combines:
    • Performance data (Revenue, Spend, ROAS)  
    • Product & campaign breakdowns  
    • Simulation modelling (Meridian-style)

    👉 Goal: Maximise revenue without increasing budget
    """)

    # -----------------------------------
    # KPI EXPLANATION (CLEANER)
    # -----------------------------------
    st.markdown("### 📘 Understanding the numbers")

    c1, c2, c3 = st.columns(3)

    c1.markdown("""
    **Revenue**  
    Total value generated from ads
    """)

    c2.markdown("""
    **Spend**  
    Total advertising cost
    """)

    c3.markdown("""
    **ROAS**  
    Revenue per R1 spent  
    *(ROAS 4 = R4 return per R1)*
    """)

    st.markdown("---")

    # -----------------------------------
    # KEY INSIGHT (MORE PUNCHY)
    # -----------------------------------
    performance_label = (
        "🟢 Strong" if roas >= 3 else
        "🟡 Moderate" if roas >= 2 else
        "🔴 Underperforming"
    )

    st.markdown("### 🚨 Key Insight")

    st.success(f"""
    Performance: **{performance_label} (ROAS {roas:.2f})**

    • Revenue is driven by a small group of high-performing products  
    • Some budget is being wasted on low-efficiency campaigns  

    👉 **Action:** Shift spend from weak performers → top performers to unlock more revenue
    """)

    st.markdown("---")

    # -----------------------------------
    # DATA OVERVIEW (CLEAN TABLE)
    # -----------------------------------
    st.markdown("### 🗂️ Data Overview")

    st.dataframe(pd.DataFrame({
        "Category": ["Source", "Analysis", "Granularity", "Rows"],
        "Details": [
            "Google Ads Data",
            "Performance + Meridian Simulation",
            "Product & Campaign",
            f"{len(df):,}"
        ]
    }), use_container_width=True)


# --------------------------------------------------
# TAB 2 — SNAPSHOT
# --------------------------------------------------
with tab2:

    st.markdown("## Overall Performance Snapshot")

    # -----------------------------------
    # KPI STRIP (WITH CONTEXT)
    # -----------------------------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Spend", f"{currency_symbol}{total_spend:,.0f}")
    c2.metric("Revenue", f"{currency_symbol}{total_rev:,.0f}")
    c3.metric("Conversions", f"{total_conv}")
    c4.metric("ROAS", f"{roas:.2f}")

    st.markdown("")

    # -----------------------------------
    # WHAT THIS VIEW SHOWS (NON-TECHNICAL)
    # -----------------------------------
    st.markdown("""
    <div class="exec-card">

    <div class="section-title">How to read this</div>

    <div class="muted">
    Each dot represents a <b>product</b>.<br><br>

    <b>X-axis (Spend)</b> → how much budget was invested<br>
    <b>Y-axis (Revenue)</b> → how much value that product generated<br><br>

    Top-left = inefficient (high spend, low return) ❌<br>
    Bottom-right = high potential (low spend, strong return) 💡<br>
    Top-right = strong performers (scale candidates) 🚀
    </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # -----------------------------------
    # DATA PREP
    # -----------------------------------
    scatter_df = (
        filtered.groupby("product_title")
        .agg(Spend=("cost","sum"), Revenue=("conv_value","sum"))
        .reset_index()
    )

    # -----------------------------------
    # SCATTER (UPGRADED VISUAL)
    # -----------------------------------
    fig = px.scatter(
        scatter_df,
        x="Spend",
        y="Revenue",
        hover_name="product_title",
        size="Revenue",  # adds visual importance
        size_max=25
    )

    # Clean styling (important)
    fig.update_traces(
        marker=dict(opacity=0.7),
    )

    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Spend",
        yaxis_title="Revenue",
    )

    # Optional: add reference line (very powerful visual cue)
    fig.add_shape(
        type="line",
        x0=scatter_df["Spend"].min(),
        y0=scatter_df["Spend"].min() * roas,
        x1=scatter_df["Spend"].max(),
        y1=scatter_df["Spend"].max() * roas,
        line=dict(dash="dot")
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------
    # EXECUTIVE TAKEAWAY (DYNAMIC)
    # -----------------------------------
    st.markdown(f"""
    <div class="exec-card">

    <div class="section-title">What this means</div>

    <div class="muted">
    Overall efficiency is <b>{"high" if roas >= 3 else "moderate" if roas >= 2 else "low"}</b> 
    with a ROAS of <b>{roas:.2f}</b>.<br><br>

    The distribution shows that performance is not evenly spread — 
    a small number of products are driving the majority of revenue.<br><br>

    <b>Action:</b> Focus on scaling products in the upper-right quadrant 
    while reviewing or reducing spend on underperforming ones.
    </div>

    </div>
    """, unsafe_allow_html=True)
# --------------------------------------------------
# TAB 3 — PRODUCT PERFORMANCE
# --------------------------------------------------
with tab3:

    st.markdown("## Top Performing Products")

    # Top products
    top_products = product_perf.sort_values("Revenue", ascending=False).head(5)

    # Metrics row (quick executive view)
    total_top_rev = top_products["Revenue"].sum()
    total_top_conv = top_products["Conversions"].sum()

    c1, c2 = st.columns(2)
    c1.metric("Top 5 Combined Revenue", f"{currency_symbol}{total_top_rev:,.0f}")
    c2.metric("Top 5 Combined Conversions", f"{int(total_top_conv)}")

    st.markdown("---")

    # Bar chart (visual dominance )
    fig = px.bar(
        top_products,
        x="Revenue",
        y="product_title",
        orientation="h",
        text="Revenue"
    )

    fig.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Table (detail view)
    st.markdown("### Product Breakdown")
    display_df = top_products.copy()

    display_df["Spend"] = display_df["Spend"].map(lambda x: f"{currency_symbol}{x:,.0f}")
    display_df["Revenue"] = display_df["Revenue"].map(lambda x: f"{currency_symbol}{x:,.0f}")
    display_df["Conversions"] = display_df["Conversions"].map(lambda x: f"{int(x)}")
    display_df["ROAS"] = display_df["ROAS"].map(lambda x: f"{x:.1f}")

    st.dataframe(display_df, use_container_width=True)

# --------------------------------------------------
# TAB 4 — CAMPAIGNS (CLEAN UI)
# --------------------------------------------------
with tab4:

    st.markdown("## 📊 Top 5 Campaign Performance")

    st.markdown("""
    Quickly identify where budget is working vs being wasted.

    🟢 High ROAS → scale  
    🔴 Low ROAS → optimise or cut  
    """)

    # -----------------------------------
    # DATA PREP
    # -----------------------------------
    campaign_perf = (
        filtered.groupby("campaign")
        .agg(
            Spend=("cost", "sum"),
            Revenue=("conv_value", "sum")
        )
        .reset_index()
    )

    campaign_perf["ROAS"] = campaign_perf["Revenue"] / campaign_perf["Spend"]

    # Sort best → worst
    campaign_perf = campaign_perf.sort_values(by="ROAS", ascending=False)

    # -----------------------------------
    # FORMAT FOR DISPLAY (CLEAN UI)
    # -----------------------------------
    display_df = campaign_perf.copy()

    display_df["Spend"] = display_df["Spend"].map(lambda x: f"{currency_symbol}{x:,.0f}")
    display_df["Revenue"] = display_df["Revenue"].map(lambda x: f"{currency_symbol}{x:,.0f}")
    display_df["ROAS"] = display_df["ROAS"].map(lambda x: f"{x:.2f}")

    display_df = display_df.rename(columns={
        "campaign": "Campaign"
    })

    st.markdown("### 📋 Campaign Breakdown")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------
    # SMART INSIGHT
    # -----------------------------------
    top_campaign = campaign_perf.iloc[0]
    worst_campaign = campaign_perf.iloc[-1]

    st.success(f"""
    🚀 Top Performer: **{top_campaign['campaign']}** (ROAS {top_campaign['ROAS']:.2f})
    """)

# --------------------------------------------------
# TAB 5 — BUDGET ENGINE (CLEAN + FIXED)
# --------------------------------------------------
with tab5:

    st.markdown("## 💡 Budget Recommendation Engine")

    st.markdown("""
    Automatically identifies where to scale, maintain, or cut spend.

    🟢 Scale → High efficiency  
    🟡 Maintain → Stable  
    🔴 Pause → Wasted spend  
    """)

    # -----------------------------------
    # COPY DATA
    # -----------------------------------
    df_budget = product_perf.copy()

    # -----------------------------------
    # FIX ROAS (handle zero / tiny spend)
    # -----------------------------------
    df_budget["ROAS"] = df_budget.apply(
        lambda row: row["Revenue"] / row["Spend"]
        if row["Spend"] > 1 else 0,  # 👈 KEY FIX
        axis=1
    )

    # -----------------------------------
    # RECOMMENDATION LOGIC (CLEAN)
    # -----------------------------------
    def rec(row):
        if row["ROAS"] >= 3:
            return "🟢 Scale"
        elif row["ROAS"] < 1:
            return "🔴 Pause"
        else:
            return "🟡 Maintain"

    df_budget["Action"] = df_budget.apply(rec, axis=1)

    # -----------------------------------
    # ROUNDING
    # -----------------------------------
    df_budget["ROAS"] = df_budget["ROAS"].round(1)

    if "Conversions" in df_budget.columns:
        df_budget["Conversions"] = df_budget["Conversions"].fillna(0).round(0).astype(int)

    # -----------------------------------
    # SORT BEST → WORST
    # -----------------------------------
    df_budget = df_budget.sort_values(by="ROAS", ascending=False)

    # -----------------------------------
    # CLEAN DISPLAY (NO COLORS)
    # -----------------------------------
    display_df = df_budget.copy()

    display_df["Spend"] = display_df["Spend"].map(lambda x: f"R{x:,.0f}")
    display_df["Revenue"] = display_df["Revenue"].map(lambda x: f"R{x:,.0f}")
    display_df["ROAS"] = display_df["ROAS"].map(lambda x: f"{x:.1f}")

    display_df = display_df.rename(columns={
        "product_title": "Product",
        "Spend": "Spend",
        "Revenue": "Revenue",
        "ROAS": "ROAS",
        "Action": "Action"
    })

    st.markdown("### 📋 Budget Breakdown")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------
    # SMART SUMMARY (ONLY ONCE)
    # -----------------------------------
    scale_count = (df_budget["Action"].str.contains("Scale")).sum()
    pause_count = (df_budget["Action"].str.contains("Pause")).sum()

    st.success(f"""
    🚀 {scale_count} products to SCALE  
    ⚠️ {pause_count} products to PAUSE  

    👉 Shift budget from low performers → top performers to increase revenue without increasing spend.
    """)





# --------------------------------------------------
# TAB 6 — MERIDIAN ANALYSIS
# --------------------------------------------------
with tab6:

    st.markdown("##  Meridian Analysis (Diminishing Returns)")

    st.markdown("""
    This chart simulates how revenue grows as you increase spend on selected campaigns.

    ###  What you're looking at:
    - Each line = a selected campaign  
    - X-axis = Spend (budget invested)  
    - Y-axis = Revenue generated  

    ###  How to use:
    - Select up to **2 campaigns** to compare  
    - Compare curve steepness → shows scaling potential  
    """)

    #  NEW: campaign selector (max 2)
    selected_campaigns = st.multiselect(
        "Select up to 2 campaigns to compare",
        options=filtered["campaign"].unique(),
        default=list(filtered["campaign"].unique())[:2]
    )

    if len(selected_campaigns) == 0:
        st.warning("Please select at least one campaign.")
    elif len(selected_campaigns) > 2:
        st.warning("Select maximum 2 campaigns for a clean comparison.")
    else:

        channel_df = (
            filtered[filtered["campaign"].isin(selected_campaigns)]
            .groupby("campaign")
            .agg(Spend=("cost","sum"), Revenue=("conv_value","sum"))
            .reset_index()
        )

        curves = []

        for _, row in channel_df.iterrows():

            spend = max(row["Spend"],1)
            revenue = max(row["Revenue"],1)

            x = np.linspace(0, spend*2,100)
            y = revenue*(1-np.exp(-x/spend))

            curves.append(pd.DataFrame({
                "Spend":x,
                "Revenue":y,
                "Channel":row["campaign"]
            }))

        curve_df = pd.concat(curves)

        fig = px.line(curve_df, x="Spend", y="Revenue", color="Channel")
        st.plotly_chart(fig, use_container_width=True)

        st.info("Tip: The steeper curve indicates better scaling potential before diminishing returns kick in.")
# --------------------------------------------------
# TAB 7 — MERIDIAN SIMULATOR
# --------------------------------------------------
with tab7:

    st.markdown("##  Spend Simulator (What Happens If You Scale?)")

    st.markdown("""
    This tool lets you simulate increasing budget for a campaign and see the **expected revenue impact**.

    ###  What this does:
    - Uses a diminishing returns model  
    - Predicts how revenue changes as spend increases  

    ###  How to use:
    1. Select a campaign  
    2. Adjust the **Increase Spend %** slider  
    3. Watch how revenue responds  

    ###  Key idea:
    - More spend ≠ proportional revenue  
    - The higher you scale, the less efficient each extra unit becomes  
    """)

    campaign = st.selectbox("Select Campaign", filtered["campaign"].unique())

    data = filtered[filtered["campaign"]==campaign]

    spend = data["cost"].sum()
    revenue = data["conv_value"].sum()

    if spend == 0:
        st.warning("No data available for this campaign.")
    else:

        st.markdown("### ⚙️ Adjust Budget Scenario")

        pct = st.slider("Increase Spend (%)", 0, 100, 20)

        new_spend = spend*(1+pct/100)

        def curve(x):
            return revenue*(1-np.exp(-x/spend))

        current = curve(spend)
        new = curve(new_spend)

        x = np.linspace(0,spend*2,100)
        y = curve(x)

        fig = px.line(x=x,y=y)

        fig.add_scatter(
            x=[spend],
            y=[current],
            mode="markers",
            name="Current Spend"
        )

        fig.add_scatter(
            x=[new_spend],
            y=[new],
            mode="markers",
            name="New Spend Scenario"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📊 Impact Summary")

        c1, c2 = st.columns(2)
        c1.metric("Current Spend", f"{currency_symbol}{spend:,.0f}")
        c2.metric("New Spend", f"{currency_symbol}{new_spend:,.0f}")

        st.success(f" Incremental Revenue: {currency_symbol}{(new-current):,.0f}")

        st.info("Tip: If incremental revenue starts shrinking, you're approaching saturation — scale carefully.")




      