import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import requests

# Must be first
st.set_page_config(page_title="AutoPricer | Profit Optimiser", page_icon="🏎️", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Premium Look ---
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0E1117;
        color: #E0E6ED;
    }
    
    /* Top padding reduction */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Titles and Headers */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }
    
    /* Premium Metric Cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #1E2530 0%, #151A22 100%);
        border: 1px solid #2B3544;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px rgba(0,195,255,0.15);
        border-color: #3A4A5A;
    }

    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        background: -webkit-linear-gradient(45deg, #00F0FF, #0080FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #A3B8CC !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        margin-bottom: 8px;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #151A22;
        border-right: 1px solid #2B3544;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00F0FF 0%, #0080FF 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        box-shadow: 0 4px 12px rgba(0, 240, 255, 0.4);
        transform: translateY(-1px);
    }
    
    /* Form bounding box */
    div[data-testid="stForm"] {
        background-color: #1A212B;
        border: 1px solid #2B3544;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Custom divider */
    hr {
        border-color: #2B3544;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Common Plotly Layout tweaks
PLOTLY_THEME = {
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#E0E6ED", "family": "sans-serif"},
    "title_font": {"size": 22, "color": "#FFFFFF", "weight": "bold"},
    "margin": dict(l=20, r=20, t=60, b=20),
    "xaxis": dict(showgrid=False, zeroline=False, color="#A3B8CC"),
    "yaxis": dict(showgrid=True, gridcolor="#2B3544", zeroline=False, color="#A3B8CC"),
}

# Helpers
@st.cache_data
def load_reports():
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    drift, perf = {}, {}
    try:
        with open(os.path.join(reports_dir, "drift_report.json")) as f:
            drift = json.load(f)
    except: pass
    try:
        with open(os.path.join(reports_dir, "performance_report.json")) as f:
            perf = json.load(f)
    except: pass
    return drift, perf

# --- Sidebar ---
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="color: #00F0FF !important; margin-bottom: 0px;">AutoPricer <span style="color: white;">OS</span></h1>
    <p style="color:#A3B8CC; font-size: 0.9rem; margin-top: 0px;">Algorithmic Vehicle Pricing</p>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["📊 Commercial Overview", "🚨 Drift Monitor", "⚡ Offer Simulator"])

drift_report, perf_report = load_reports()

if page == "📊 Commercial Overview":
    st.title("Commercial Overview")
    st.markdown("<p style='color:#A3B8CC; font-size:1.1rem;'>Expected Value vs Realised Margin & High-Level KPIs</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Profit (Actual)", f"£{perf_report.get('total_profit_actual', 0):,.0f}")
    with col2:
        st.metric("Profit Lift vs Flat Offer", f"+{perf_report.get('profit_lift_pct', 0)}% 🚀")
    with col3:
        st.metric("Price Model MAE", f"£{perf_report.get('price_mae', 0)}")
    with col4:
        st.metric("Conversion Brier Score", f"{perf_report.get('conversion_brier', 0):.3f}")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.subheader("📈 Profit Attribution Simulator")
    
    # Mock chart for illustration
    dates = pd.date_range("2026-01-01", periods=30)
    profit_data = pd.DataFrame({
        "Date": dates,
        "AutoPricer EV Policy": np.random.uniform(2000, 5000, 30).cumsum(),
        "Legacy Flat 85%": np.random.uniform(1500, 4000, 30).cumsum(),
    })
    
    fig = px.line(profit_data, x="Date", y=["AutoPricer EV Policy", "Legacy Flat 85%"], 
                  color_discrete_sequence=["#00F0FF", "#FF3366"])
    
    fig.update_layout(**PLOTLY_THEME)
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None),
        hovermode="x unified"
    )
    # Fill area under curve for AutoPricer EV Policy
    fig.update_traces(fill='tozeroy', selector=dict(name="AutoPricer EV Policy"), fillcolor="rgba(0, 240, 255, 0.1)")
    
    st.plotly_chart(fig, use_container_width=True)

elif page == "🚨 Drift Monitor":
    st.title("Drift & Performance Monitor")
    st.markdown("<p style='color:#A3B8CC; font-size:1.1rem;'>Tracking Population Stability and Distribution Shifts in Real-Time</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if drift_report.get("features"):
        features = list(drift_report["features"].keys())
        psis = [drift_report["features"][f]["psi"] for f in features]
        colors = ["#FF3366" if p > 0.25 else "#FFB020" if p > 0.1 else "#00E676" for p in psis]
        
        fig = go.Figure(data=[go.Bar(
            x=features,
            y=psis,
            marker_color=colors,
            marker_line_width=0,
            opacity=0.85
        )])
        
        fig.add_hline(y=0.25, line_dash="dash", line_color="#FF3366", annotation_text="Critical Drift Threshold", annotation_position="top right", annotation_font_color="#FF3366")
        fig.add_hline(y=0.10, line_dash="dash", line_color="#FFB020", annotation_text="Warning Threshold", annotation_position="top right", annotation_font_color="#FFB020")
        
        fig.update_layout(**PLOTLY_THEME)
        fig.update_layout(title="Feature Population Stability Index (PSI)", yaxis_title="PSI Score")
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🔍 KS Test Diagnostics")
        df_ks = pd.DataFrame({
            "Feature Indicator": features,
            "PSI Score": [f"{p:.3f}" for p in psis],
            "KS p-value": [f"{drift_report['features'][f]['ks_p_value']:.4f}" for f in features],
            "Status": ["🚨 Drift Detected" if drift_report["features"][f]["drift_detected"] else "✅ Stable" for f in features]
        })
        st.dataframe(df_ks, use_container_width=True, hide_index=True)
    else:
        st.warning("No drift report found. Run pipelines/monitor/drift.py")

elif page == "⚡ Offer Simulator":
    st.title("Live Offer Simulator")
    st.markdown("<p style='color:#A3B8CC; font-size:1.1rem;'>Test the Expected Value (EV) Pricing Engine</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.markdown("### 🚘 Vehicle Input")
        with st.form("quote_form"):
            make = st.selectbox("Make", ["Ford", "VW", "BMW", "Audi", "Tesla", "Toyota"])
            fuel = st.selectbox("Fuel", ["petrol", "diesel", "electric", "hybrid"])
            year = st.slider("Year", 2010, 2025, 2019)
            mileage = st.number_input("Mileage", 0, 200000, 45000, step=1000)
            channel = st.selectbox("Acquisition Channel", ["dealer", "private", "fleet"])
            damage = st.selectbox("Damage Severity", ["none", "scratches", "dents", "mechanical", "structural"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("🚀 Generate Optimised Offer")
            
    with col2:
        st.markdown("### 🎯 Engine Decision")
        if submit:
            payload = {
                "make": make,
                "model": "Generic", 
                "year": year,
                "mileage": mileage,
                "fuel_type": fuel,
                "channel": channel,
                "damage_flag": damage != "none",
                "damage_type": damage
            }
            
            api_url = os.getenv("API_URL", "http://localhost:8000")
            with st.spinner("Calculating Expected Value surfaces..."):
                try:
                    res = requests.post(f"{api_url}/quote", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        offer = data['recommended_offer']
                        ev = data['expected_value']
                        p_win = data['p_win']
                        risk = data['risk_band'].upper()
                        
                        # Decision Header
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #00F0FF20 0%, #0080FF20 100%); padding: 30px; border-radius: 15px; border: 1px solid #00F0FF50; text-align: center; box-shadow: 0 4px 15px rgba(0,240,255,0.1);'>
                            <h4 style='color: #A3B8CC; margin-bottom: 0px;'>Recommended Offer</h4>
                            <h1 style='color: #00F0FF; font-size: 3.5rem; margin-top: 5px; margin-bottom: 5px; font-weight: 800;'>£{offer:,.0f}</h1>
                            <p style='color: #FFFFFF; font-size: 1.2rem; margin: 0;'>Expected Profit Formulation: <b>£{ev:,.0f}</b></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Gauges
                        g1, g2 = st.columns(2)
                        
                        # P(Win) Gauge
                        fig_win = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = p_win * 100,
                            number = {'suffix': "%", 'font': {'color': '#00E676', 'size': 40}},
                            title = {'text': "Win Probability", 'font': {'color': '#A3B8CC', 'size': 18}},
                            gauge = {
                                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                                'bar': {'color': "#00E676"},
                                'bgcolor': "rgba(0,0,0,0)",
                                'borderwidth': 0,
                                'steps': [
                                    {'range': [0, 30], 'color': "rgba(255, 51, 102, 0.2)"},
                                    {'range': [30, 70], 'color': "rgba(255, 176, 32, 0.2)"},
                                    {'range': [70, 100], 'color': "rgba(0, 230, 118, 0.2)"}],
                            }
                        ))
                        fig_win.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#FFFFFF"})
                        with g1:
                            st.plotly_chart(fig_win, use_container_width=True)
                            
                        # Risk Band Gauge (Categorical mapped to continuous for visual)
                        risk_val = 20 if risk == "LOW" else 50 if risk == "MEDIUM" else 80
                        risk_color = "#00E676" if risk == "LOW" else "#FFB020" if risk == "MEDIUM" else "#FF3366"
                        
                        fig_risk = go.Figure(go.Indicator(
                            mode = "gauge",
                            value = risk_val,
                            title = {'text': f"Risk Band: {risk}", 'font': {'color': '#A3B8CC', 'size': 18}},
                            gauge = {
                                'axis': {'range': [0, 100], 'showticklabels': False},
                                'bar': {'color': risk_color},
                                'bgcolor': "rgba(0,0,0,0)",
                                'borderwidth': 0,
                                'steps': [
                                    {'range': [0, 33], 'color': "rgba(0, 230, 118, 0.2)"},
                                    {'range': [33, 66], 'color': "rgba(255, 176, 32, 0.2)"},
                                    {'range': [66, 100], 'color': "rgba(255, 51, 102, 0.2)"}],
                            }
                        ))
                        fig_risk.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#FFFFFF"})
                        with g2:
                            st.plotly_chart(fig_risk, use_container_width=True)

                        # Explainability Expander
                        with st.expander("🔍 Engine Explainability Details"):
                            st.markdown(f"""
                            - **Retail Estimate (E_sale):** £{data['explanation']['e_sale']:,.2f}
                            - **Expected Costs (E_costs):** £{data['explanation']['e_costs']:,.2f}
                            - **Tail Risk Penalty (q10 bound):** £{data['explanation']['tail_penalty']:,.2f}
                            """)
                            
                    else:
                        st.error(f"API Error: {res.text}")
                except Exception as e:
                    st.error(f"Could not connect to API at {api_url}: {str(e)}")
                    st.info("Make sure the FastAPI app is running.")
        else:
            st.info("👈 Enter vehicle attributes and generate an offer.")
