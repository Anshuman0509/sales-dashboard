import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Superstore Sales Dashboard", page_icon="📊", layout="wide")

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0d0f14; color: #e8eaf0; }
    .metric-card { background: #13161e; border: 1px solid #252a38; border-radius: 16px; padding: 20px; text-align: center; }
    .metric-value { font-size: 28px; font-weight: 800; margin: 0; }
    .metric-label { font-size: 13px; color: #7a8099; margin: 0; }
    h1, h2, h3 { color: #e8eaf0 !important; }
    .stSelectbox label { color: #7a8099 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("train.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)
    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
    df["DayOfWeek"] = df["Order Date"].dt.day_name()
    return df

df = load_data()

# ─── Gemini Client ────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})

# ─── Chart Style ──────────────────────────────────────────────────────────────
def style(fig):
    fig.update_layout(
        paper_bgcolor="#13161e", plot_bgcolor="#13161e",
        font_color="#e8eaf0", margin=dict(l=10, r=10, t=30, b=40),
        xaxis=dict(gridcolor="#252a38"), yaxis=dict(gridcolor="#252a38"),
    )
    return fig

CHART_COLORS = ["#ff6b35","#ffb347","#4ade80","#60a5fa","#c084fc","#f472b6"]

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 📊 Superstore Sales Dashboard")
st.markdown("<p style='color:#7a8099'>Real sales data • 9,800 orders • 4 regions • AI-powered insights</p>", unsafe_allow_html=True)
st.divider()

# ─── Filters ──────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    category = st.selectbox("📦 Category", ["All"] + sorted(df["Category"].unique().tolist()))
with col2:
    region = st.selectbox("🗺️ Region", ["All"] + sorted(df["Region"].unique().tolist()))
with col3:
    segment = st.selectbox("👥 Segment", ["All"] + sorted(df["Segment"].unique().tolist()))

# ─── Filter Data ──────────────────────────────────────────────────────────────
filtered = df.copy()
if category != "All": filtered = filtered[filtered["Category"] == category]
if region != "All": filtered = filtered[filtered["Region"] == region]
if segment != "All": filtered = filtered[filtered["Segment"] == segment]

st.divider()

# ─── KPI Cards ────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total Sales", f"${filtered['Sales'].sum():,.0f}")
k2.metric("🛒 Total Orders", f"{filtered['Order ID'].nunique():,}")
k3.metric("📦 Avg Order Value", f"${filtered.groupby('Order ID')['Sales'].sum().mean():,.0f}")
k4.metric("🏆 Top Category", filtered.groupby("Category")["Sales"].sum().idxmax() if len(filtered) > 0 else "N/A")

st.divider()

# ─── Charts Row 1 ─────────────────────────────────────────────────────────────
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("### 📈 Monthly Sales Trend")
    monthly = filtered.groupby("Month")["Sales"].sum().reset_index().sort_values("Month")
    fig = px.line(monthly, x="Month", y="Sales", markers=True, color_discrete_sequence=["#ff6b35"])
    st.plotly_chart(style(fig), use_container_width=True)

with c2:
    st.markdown("### 🥧 Sales by Category")
    cat_data = filtered.groupby("Category")["Sales"].sum().reset_index()
    fig = px.pie(cat_data, names="Category", values="Sales", color_discrete_sequence=CHART_COLORS, hole=0.4)
    st.plotly_chart(style(fig), use_container_width=True)

# ─── Charts Row 2 ─────────────────────────────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    st.markdown("### 🗺️ Sales by Region")
    region_data = filtered.groupby("Region")["Sales"].sum().reset_index().sort_values("Sales")
    fig = px.bar(region_data, x="Sales", y="Region", orientation="h", color_discrete_sequence=["#ffb347"])
    st.plotly_chart(style(fig), use_container_width=True)

with c4:
    st.markdown("### 📦 Top Sub-Categories")
    subcat = filtered.groupby("Sub-Category")["Sales"].sum().reset_index().sort_values("Sales", ascending=False).head(10)
    fig = px.bar(subcat, x="Sub-Category", y="Sales", color_discrete_sequence=["#60a5fa"])
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(style(fig), use_container_width=True)

# ─── Charts Row 3 ─────────────────────────────────────────────────────────────
c5, c6 = st.columns(2)

with c5:
    st.markdown("### 👥 Sales by Segment")
    seg = filtered.groupby("Segment")["Sales"].sum().reset_index()
    fig = px.bar(seg, x="Segment", y="Sales", color_discrete_sequence=["#c084fc"])
    st.plotly_chart(style(fig), use_container_width=True)

with c6:
    st.markdown("### 📅 Sales by Day of Week")
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    day_data = filtered.groupby("DayOfWeek")["Sales"].sum().reindex(day_order).reset_index()
    fig = px.bar(day_data, x="DayOfWeek", y="Sales", color_discrete_sequence=["#4ade80"])
    st.plotly_chart(style(fig), use_container_width=True)

st.divider()

# ─── AI Insights ──────────────────────────────────────────────────────────────
st.markdown("### 🤖 AI Business Insights")

if st.button("✨ Generate AI Insights", type="primary"):
    with st.spinner("Analyzing data with Gemini AI..."):
        try:
            top_subcat = filtered.groupby("Sub-Category")["Sales"].sum().idxmax()
            top_region = filtered.groupby("Region")["Sales"].sum().idxmax()
            best_day = filtered.groupby("DayOfWeek")["Sales"].sum().idxmax()
            monthly = filtered.groupby("Month")["Sales"].sum().sort_index()
            growth = ((monthly.iloc[-1] - monthly.iloc[0]) / monthly.iloc[0] * 100) if len(monthly) > 1 else 0

            summary = f"""
            Total Sales: ${filtered['Sales'].sum():,.0f}
            Total Orders: {filtered['Order ID'].nunique():,}
            Top Sub-Category: {top_subcat}
            Top Region: {top_region}
            Best Day: {best_day}
            Sales Growth: {growth:.1f}%
            Filters: Category={category}, Region={region}, Segment={segment}
            """

            prompt = f"""You are a senior business data analyst. Analyze this Superstore sales data and provide 5 specific actionable business insights:
{summary}
Format each insight on a new line starting with an emoji. Be specific with numbers. Focus on what actions the business should take."""

            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            st.success(response.text)
        except Exception as e:
            st.error(f"Could not generate insights: {str(e)}")
else:
    st.info("Click the button above to get AI-powered analysis of the sales data.")

st.divider()
st.markdown("<p style='color:#7a8099; text-align:center'>Built with Python • Streamlit • Plotly • Google Gemini • Real Superstore Dataset</p>", unsafe_allow_html=True)
