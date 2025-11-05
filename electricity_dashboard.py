import streamlit as st
import pandas as pd
import os
import base64
import plotly.express as px

def load_data(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[-1].lower()
    try:
        if ext == ".csv":
            return pd.read_csv(uploaded_file)
        elif ext in [".xls", ".xlsx"]:
            return pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Upload CSV or XLSX.")
            return None
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

def set_background(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{b64}");
                background-size: cover;
                background-position: center;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

st.set_page_config(page_title="Electricity Dashboard", layout="wide", page_icon="")
set_background("603717e29f2a9.jpg") 

st.markdown(
    """
    <style>
    /* semi-transparent sidebar but keep text clearly visible */
    [data-testid="stSidebar"] {
        background: rgba(0,0,0,0.45) !important;
        color: white !important;
        padding: 1rem;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stSelectbox {
        color: white !important;
    }
    /* main content overlay for readability */
    [data-testid="stAppViewContainer"] > .main {
        background: rgba(0,0,0,0.18);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 style='color: white; text-align:center;'> Pakistan Electricity Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: white; text-align:center;'>Forecasting • Shortage • Optimization • Energy Mix</p>", unsafe_allow_html=True)
st.write("---")

st.sidebar.header("Select Module")
module = st.sidebar.selectbox(
    "Choose a module",
    [
        "Electricity Production Forecasting",
        "Electricity Shortage Forecasting",
        "Demand Optimization Model",
        "Energy Mix & Policy Impact Analysis"
    ],
    index=0
)

if module == "Electricity Production Forecasting":
    st.subheader("Electricity Production Forecasting")
    up = st.file_uploader("Upload generation file (csv/xlsx)", type=["csv","xlsx"], key="prod_upload")
    if up:
        df = load_data(up)
        if df is not None:
            st.dataframe(df.head())
            if 'Year' in df.columns and 'Total Generation' in df.columns:
                fig = px.line(df, x='Year', y='Total Generation', markers=True, title="Total Generation")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("File must include columns: Year, Total Generation")

elif module == "Electricity Shortage Forecasting":
    st.subheader("Electricity Shortage Forecasting")
    up = st.file_uploader("Upload shortage/ supply-demand file (csv/xlsx)", type=["csv","xlsx"], key="short_upload")
    if up:
        df = load_data(up)
        if df is not None:
            st.dataframe(df.head())
            if 'Year' in df.columns and ('Shortage' in df.columns or 'Electricity Shortage' in df.columns):
                short_col = 'Shortage' if 'Shortage' in df.columns else 'Electricity Shortage'
                fig = px.bar(df, x='Year', y=short_col, title="Shortage over Years", color=short_col)
                st.plotly_chart(fig, use_container_width=True)
            elif 'Total_Generation' in df.columns and 'Total_Demand' in df.columns:
                df['Shortage'] = df['Total_Demand'] - df['Total_Generation']
                fig = px.line(df, x='Year', y=['Total_Generation','Total_Demand'], title="Supply vs Demand")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df[['Year','Total_Generation','Total_Demand','Shortage']].tail())
            else:
                st.warning("File must contain Year + (Shortage) OR (Total_Generation and Total_Demand).")

elif module == "Demand Optimization Model":
    st.subheader("Demand Optimization Model")
    up = st.file_uploader("Upload optimized allocation or consumption file (csv/xlsx)", type=["csv","xlsx"], key="opt_upload")
    if up:
        df = load_data(up)
        if df is not None:
            st.dataframe(df.head())
            cols = [c.strip() for c in df.columns]
            df.columns = cols
            required = ['Year','Residential Consumption','Industrial Consumption','Agricultural Consumption']
            if all(c in df.columns for c in required):
                fig = px.line(df, x='Year', y=required[1:], title="Sector Allocations", markers=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"File must contain columns: {required}. Detected columns: {df.columns.tolist()}")

elif module == "Energy Mix & Policy Impact Analysis":
    st.subheader("Energy Mix & Policy Impact Analysis")
    up = st.file_uploader("Upload energy mix file (csv/xlsx)", type=["csv","xlsx"], key="mix_upload")
    if up:
        df = load_data(up)
        if df is not None:
            st.dataframe(df.head())
            expected = ['Year','Hydel','Thermal','Nuclear','Solar','Wind']
            missing = [c for c in expected if c not in df.columns]
            if not missing:
                df_melt = df.melt(id_vars='Year', value_vars=['Hydel','Thermal','Nuclear','Solar','Wind'], var_name='Source', value_name='Generation')
                fig = px.area(df_melt, x='Year', y='Generation', color='Source', title="Energy Mix")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Missing columns: {missing}")

st.write("---")
st.caption("Pakistan Electricity Data Project (Forecasting, Shortage, Optimization, and Policy Analysis.")
