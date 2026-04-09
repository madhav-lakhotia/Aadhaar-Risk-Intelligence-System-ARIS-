import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="ARIS Dashboard", layout="wide", page_icon="🛡️")

# --- CUSTOM CSS FOR "RISK" THEME ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # Loading your cleaned dataset
    df = pd.read_csv('aadhaar_final_CLEANED.csv')
    # Adding a Risk Metric: Ratio of updates to total enrollments (Simulation based on your columns)
    df['total_enrolment'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Please ensure 'aadhaar_final_CLEANED.csv' is in the same folder.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.title("🛡️ ARIS Control Panel")
st.sidebar.markdown("Jan 2026 – Feb 2026 Analysis")

# Convert to string and drop any empty/NaN values before sorting
available_states = sorted([str(x) for x in df['state'].dropna().unique()])

state_filter = st.sidebar.multiselect(
    "Select State", 
    options=available_states, 
    default=available_states[:3] if len(available_states) >= 3 else available_states
)
district_filter = st.sidebar.multiselect("Select District", options=sorted(df[df['state'].isin(state_filter)]['district'].unique()))

# Filter Logic
filtered_df = df[df['state'].isin(state_filter)]
if district_filter:
    filtered_df = filtered_df[filtered_df['district'].isin(district_filter)]

# --- HEADER ---
st.title("Aadhaar Risk Intelligence System (ARIS)")
st.subheader("Regional Patterns & Demographic Anomaly Detection")

# --- TOP METRICS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Enrolments", f"{filtered_df['total_enrolment'].sum():,}")
m2.metric("Avg Bio Updates (5-17)", f"{int(filtered_df['bio_age_5_17'].mean())}")
m3.metric("Max Regional Load", f"{filtered_df['total_enrolment'].max():,}")
m4.metric("Active Pincodes", filtered_df['pincode'].nunique())

st.divider()

# --- ANALYSIS ROWS ---
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("### 📊 Enrolment Distribution by State")
    fig_state = px.bar(filtered_df.groupby('state')['total_enrolment'].sum().reset_index(), 
                       x='state', y='total_enrolment', 
                       color='total_enrolment', color_continuous_scale='Reds')
    st.plotly_chart(fig_state, use_container_width=True)

with row1_col2:
    st.markdown("### ⚠️ Biometric vs Demographic Behavior")
    # Comparing age 5-17 behavior as requested in your summary
    fig_compare = go.Figure()
    fig_compare.add_trace(go.Box(y=filtered_df['bio_age_5_17'], name='Biometric Updates', marker_color='#1f77b4'))
    fig_compare.add_trace(go.Box(y=filtered_df['demo_age_5_17'], name='Demographic Updates', marker_color='#ff7f0e'))
    fig_compare.update_layout(title="Outlier Detection in Update Behavior")
    st.plotly_chart(fig_compare, use_container_width=True)

st.divider()

row2_col1, row2_col2 = st.columns([2, 1])

with row2_col1:
    st.markdown("### 📈 Age Group Correlation Heatmap")
    corr = filtered_df[['age_0_5', 'age_5_17', 'age_18_greater', 'bio_age_5_17']].corr()
    fig_corr = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
    st.plotly_chart(fig_corr, use_container_width=True)

with row2_col2:
    st.markdown("### 📋 Risk Data View")
    # Flagging districts with high updates relative to enrollment
    risk_view = filtered_df[['state', 'district', 'total_enrolment', 'bio_age_5_17']].sort_values(by='bio_age_5_17', ascending=False)
    st.dataframe(risk_view.head(10), use_container_width=True)

# --- INSIGHTS FOOTER ---
st.info("**ARIS Insight:** Use the box plots above to identify districts where demographic updates significantly exceed biometric updates—these are primary regions for resource audit.")