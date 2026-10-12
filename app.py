
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Page settings
st.set_page_config(
    page_title="Pakistan Flood Intelligence",
    page_icon="🌊",
    layout="wide",
)

# Dashboard colours and styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #07111f;
        color: #e5edf7;
    }

    [data-testid="stMetric"] {
        background-color: #101f32;
        border: 1px solid #203650;
        padding: 18px;
        border-radius: 12px;
    }

    h1, h2, h3, p, label {
        color: #e5edf7;
    }

    div[data-testid="stSidebar"] {
        background-color: #0c1929;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.title("🌊 Pakistan Flood Intelligence")
st.caption("HISTORICAL RAINFALL MONITORING | PAKISTAN")

# Load the downloaded dataset
data_file = Path(__file__).parent / "data" / "pakistan_rainfall.csv"

if not data_file.exists():
    st.error("Rainfall data not found. Run download_data.py first.")
    st.stop()

df = pd.read_csv(data_file)
df["date"] = pd.to_datetime(df["date"])
df["rainfall_mm"] = pd.to_numeric(df["rainfall_mm"], errors="coerce")
df = df.dropna(subset=["date", "rainfall_mm"])

# Sidebar filters
st.sidebar.header("Dashboard Controls")

cities = sorted(df["city"].unique().tolist())
selected_cities = st.sidebar.multiselect(
    "Select cities",
    cities,
    default=cities,
)

start_date = st.sidebar.date_input(
    "Start date",
    value=df["date"].min().date(),
    min_value=df["date"].min().date(),
    max_value=df["date"].max().date(),
)

end_date = st.sidebar.date_input(
    "End date",
    value=df["date"].max().date(),
    min_value=df["date"].min().date(),
    max_value=df["date"].max().date(),
)

if start_date > end_date:
    st.error("Start date must be before the end date.")
    st.stop()

filtered = df[
    df["city"].isin(selected_cities)
    & (df["date"].dt.date >= start_date)
    & (df["date"].dt.date <= end_date)
].copy()

# Summary metrics
st.subheader("Situation Overview")

col1, col2, col3, col4 = st.columns(4)

total_rain = filtered["rainfall_mm"].sum()
wettest_day = (
    filtered.loc[filtered["rainfall_mm"].idxmax()]
    if not filtered.empty
    else None
)

col1.metric("Cities Selected", filtered["city"].nunique())
col2.metric("Rainfall Total", f"{total_rain:,.1f} mm")
col3.metric(
    "Highest Daily Rainfall",
    f"{filtered['rainfall_mm'].max():.1f} mm"
    if not filtered.empty
    else "N/A",
)
col4.metric(
    "Wettest City-Day",
    str(wettest_day["city"]) if wettest_day is not None else "N/A",
)

st.divider()

# Daily rainfall chart
st.subheader("Daily Rainfall Trends")

if not filtered.empty:
    daily_chart = px.line(
        filtered,
        x="date",
        y="rainfall_mm",
        color="city",
        labels={
            "date": "Date",
            "rainfall_mm": "Rainfall (mm)",
            "city": "City",
        },
        template="plotly_dark",
    )
    daily_chart.update_layout(
        paper_bgcolor="#07111f",
        plot_bgcolor="#07111f",
        legend_title_text="City",
    )
    st.plotly_chart(daily_chart, use_container_width=True)
else:
    st.info("Select at least one city to view rainfall trends.")

# Pakistan city monitoring map
st.divider()
st.subheader("📍 Pakistan Monitoring Map")

CITY_COORDINATES = {
    "Karachi": {"latitude": 24.8607, "longitude": 67.0011},
    "Hyderabad": {"latitude": 25.3960, "longitude": 68.3578},
    "Sukkur": {"latitude": 27.7052, "longitude": 68.8574},
    "Larkana": {"latitude": 27.5584, "longitude": 68.2120},
    "Islamabad": {"latitude": 33.6844, "longitude": 73.0479},
}

if not filtered.empty:
    map_data = (
        filtered.groupby("city", as_index=False)["rainfall_mm"]
        .sum()
        .merge(
            pd.DataFrame.from_dict(CITY_COORDINATES, orient="index")
            .rename_axis("city")
            .reset_index(),
            on="city",
            how="left",
        )
    )

    st.map(
        map_data,
        latitude="latitude",
        longitude="longitude",
        size="rainfall_mm",
        color="#00CFE8",
        zoom=4,
    )

    st.caption(
        "Marker size represents cumulative estimated rainfall over the selected "
        "date range. This is a monitoring map, not a flood-inundation map."
    )
else:
    st.info("Select at least one city to display the monitoring map.")

# City monitoring status
st.divider()
st.subheader("🛰️ City Monitoring Status")

if not filtered.empty:
    city_status = (
        filtered.groupby("city", as_index=False)
        .agg(
            total_rainfall_mm=("rainfall_mm", "sum"),
            average_daily_rainfall_mm=("rainfall_mm", "mean"),
            highest_daily_rainfall_mm=("rainfall_mm", "max"),
            days_monitored=("date", "nunique"),
        )
    )

    def monitoring_status(rainfall):
        if rainfall >= 50:
            return "HIGH RAINFALL"
        elif rainfall >= 20:
            return "MODERATE RAINFALL"
        else:
            return "LOW RAINFALL"

    city_status["monitoring_status"] = city_status[
        "highest_daily_rainfall_mm"
    ].apply(monitoring_status)

    city_status = city_status.sort_values(
        "highest_daily_rainfall_mm", ascending=False
    )

    st.dataframe(
        city_status.rename(
            columns={
                "city": "City",
                "total_rainfall_mm": "Total Rainfall (mm)",
                "average_daily_rainfall_mm": "Average Daily Rainfall (mm)",
                "highest_daily_rainfall_mm": "Highest Daily Rainfall (mm)",
                "days_monitored": "Days Monitored",
                "monitoring_status": "Monitoring Status",
            }
        ).round(2),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Status is based on the highest daily rainfall in the selected period. "
        "Thresholds are illustrative and are not official flood-warning criteria."
    )
else:
    st.info("Select at least one city to view monitoring status.")

# Monthly rainfall comparison
st.divider()
st.subheader("📅 Monthly Rainfall Analysis")

if not filtered.empty:
    monthly_data = filtered.copy()
    monthly_data["month"] = monthly_data["date"].dt.to_period("M").astype(str)

    monthly_totals = (
        monthly_data.groupby(["month", "city"], as_index=False)["rainfall_mm"]
        .sum()
    )

    monthly_chart = px.bar(
        monthly_totals,
        x="month",
        y="rainfall_mm",
        color="city",
        barmode="group",
        labels={
            "month": "Month",
            "rainfall_mm": "Total Rainfall (mm)",
            "city": "City",
        },
        template="plotly_dark",
    )

    monthly_chart.update_layout(
        paper_bgcolor="#07111f",
        plot_bgcolor="#07111f",
        legend_title_text="City",
    )

    st.plotly_chart(monthly_chart, use_container_width=True)
else:
    st.info("Select at least one city to view monthly rainfall.")

# City comparison

st.subheader("City Rainfall Comparison")

if not filtered.empty:
    city_totals = (
        filtered.groupby("city", as_index=False)["rainfall_mm"]
        .sum()
        .sort_values("rainfall_mm", ascending=False)
    )

    bar_chart = px.bar(
        city_totals,
        x="city",
        y="rainfall_mm",
        color="rainfall_mm",
        labels={
            "city": "City",
            "rainfall_mm": "Total Rainfall (mm)",
        },
        template="plotly_dark",
        color_continuous_scale=["#164e63", "#06b6d4", "#67e8f9"],
    )
    bar_chart.update_layout(
        paper_bgcolor="#07111f",
        plot_bgcolor="#07111f",
        coloraxis_showscale=False,
    )
    st.plotly_chart(bar_chart, use_container_width=True)

# Data table

# Rainfall monitoring alerts
st.divider()
st.subheader("⚠️ Rainfall Monitoring Alerts")
st.caption(
    "Screening thresholds for this portfolio project only. "
    "These are not official flood-warning thresholds."
)

if not filtered.empty:
    alerts = filtered[filtered["rainfall_mm"] >= 50].copy()

    if alerts.empty:
        st.success("No days reached the 50 mm monitoring threshold in this selection.")
    else:
        st.warning(
            f"{len(alerts)} city-day record(s) reached or exceeded "
            "50 mm of estimated daily rainfall."
        )

        alerts = alerts.sort_values("rainfall_mm", ascending=False)

        st.dataframe(
            alerts[["date", "city", "rainfall_mm"]].rename(
                columns={
                    "date": "Date",
                    "city": "City",
                    "rainfall_mm": "Rainfall (mm)",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
else:
    st.info("Select at least one city to check rainfall monitoring alerts.")

with st.expander("View Rainfall Records"):
    st.dataframe(
        filtered.sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "Source: Open-Meteo Historical Weather API. "
    
    "Rainfall values are gridded weather estimates, not verified flood reports. "
    "This dashboard monitors rainfall; it does not predict floods."
)

# Project information
with st.expander("About this project"):
    st.markdown(
        """
        **Purpose**

        A portfolio project for monitoring historical rainfall across
        five selected cities in Pakistan.

        **Data source**

        Open-Meteo Historical Weather API. The dataset contains daily
        precipitation estimates from June to October 2022.

        **Technology stack**

        - Python for data collection and processing
        - Pandas for data analysis
        - Streamlit for the dashboard
        - Plotly for interactive charts

        **Important limitations**

        Rainfall estimates are not verified flood events, river levels,
        or inundation measurements. Monitoring labels use illustrative
        thresholds and are not official warnings. This project does not
        currently predict floods.
        """
    )

