import streamlit as st
import pandas as pd
import numpy as np
import io

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Executive Pulse AI - Commercial Banking Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header { font-size: 2.1rem; font-weight: 800; color: #0F172A; }
    .sub-header { font-size: 1.0rem; color: #475569; }
    .security-badge { background-color: #065F46; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }
    .action-card { background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SECURITY & ACCESS CONTROL
# ==========================================
MASTER_SECURITY_KEY = "BANK-EXEC-8899-SECURE"

st.sidebar.markdown("### 🔐 Security & Access Control")
user_key = st.sidebar.text_input("Enter Master Executive Key", type="password")

if user_key != MASTER_SECURITY_KEY:
    st.markdown('<p class="main-header">🏦 Executive Pulse AI: Commercial Banking Engine</p>', unsafe_allow_html=True)
    st.warning("🔒 Access Restricted: Please enter the valid Master Executive Key in the sidebar.")
    st.stop()

# ==========================================
# APP HEADER & INGESTION
# ==========================================
st.markdown('<p class="main-header">🏦 Executive Pulse AI: Commercial Banking Engine</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Comprehensive Branch Network, Deposit Product Breakdown, & Digital Customer Summaries</p>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("📥 Ingestion & Controls")
uploaded_file = st.sidebar.file_uploader("Upload Master Bank Excel/CSV", type=["xlsx", "csv"])

bank_name = st.sidebar.text_input("Institution Name", value="Commercial Bank / Financial Institution")
current_period = st.sidebar.selectbox("Reporting Period", ["Q4 2026", "Q3 2026", "Q2 2026", "Q1 2026", "Annual 2026"])

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        raw_df = raw_df.dropna(how='all').dropna(axis=1, how='all')
        raw_df.columns = [str(c).strip() for c in raw_df.columns]
        st.sidebar.success(f"✅ Successfully Loaded All {len(raw_df)} Rows from Master File!")
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        raw_df = None
else:
    raw_df = None

if raw_df is None:
    st.info("👆 Please upload your master deposit & branch Excel spreadsheet using the sidebar uploader.")
    st.stop()

# ==========================================
# 2. INTELLIGENT COLUMN MAPPING & DATA PREP
# ==========================================
cols = raw_df.columns.tolist()

def find_header(keywords):
    for c in cols:
        if any(k in c.lower() for k in keywords):
            return c
    return None

c_code = find_header(["branch code", "code"])
c_name = find_header(["branch name", "branch", "name"])
c_loc = find_header(["location", "category", "city", "outlying"])
c_dist = find_header(["district", "region", "area"])
c_m_plan = find_header(["monthly plan", "m_plan"])
c_m_actual = find_header(["monthly actual", "m_actual"])
c_q_plan = find_header(["q1 plan", "quarterly plan"])
c_q_actual = find_header(["q1 actual", "quarterly actual"])
c_pos_start = find_header(["30 jun", "jun 2026", "prior position"])
c_pos_end = find_header(["30 sep", "sep 2026", "current position", "position as of"])
c_saving = find_header(["saving", "demand", "fixed", "deposit type", "product"])
c_digital = find_header(["digital", "mobile", "internet", "e-banking"])
c_segment = find_header(["segment", "group", "customer", "crm", "irm", "msme"])

df = raw_df.copy()
df["__BranchCode"] = raw_df[c_code].astype(str) if c_code else [f"BR-{i:03d}" for i in range(len(raw_df))]
df["__BranchName"] = raw_df[c_name].astype(str) if c_name else [f"Branch_{i}" for i in range(len(raw_df))]
df["__Location"] = raw_df[c_loc].astype(str) if c_loc else "City"
df["__District"] = raw_df[c_dist].astype(str) if c_dist else "North"
df["__MonthlyPlan"] = pd.to_numeric(raw_df[c_m_plan], errors="coerce").fillna(10.0) if c_m_plan else 10.0
df["__MonthlyActual"] = pd.to_numeric(raw_df[c_m_actual], errors="coerce").fillna(5.0) if c_m_actual else 5.0
df["__Q1Plan"] = pd.to_numeric(raw_df[c_q_plan], errors="coerce").fillna(30.0) if c_q_plan else 30.0
df["__Q1Actual"] = pd.to_numeric(raw_df[c_q_actual], errors="coerce").fillna(25.0) if c_q_actual else 25.0
df["__PosStart"] = pd.to_numeric(raw_df[c_pos_start], errors="coerce").fillna(100.0) if c_pos_start else 100.0
df["__PosEnd"] = pd.to_numeric(raw_df[c_pos_end], errors="coerce").fillna(120.0) if c_pos_end else 120.0
df["__DepositType"] = raw_df[c_saving].astype(str) if c_saving else "Saving Account"
df["__DigitalCust"] = pd.to_numeric(raw_df[c_digital], errors="coerce").fillna(1500) if c_digital else 1500
df["__Segment"] = raw_df[c_segment].astype(str) if c_segment else "Retail"

# Performance calculations
df["Monthly Ach (%)"] = ((df["__MonthlyActual"] / df["__MonthlyPlan"].replace(0, np.nan)) * 100).fillna(0).round(1)
df["Q1 Ach (%)"] = ((df["__Q1Actual"] / df["__Q1Plan"].replace(0, np.nan)) * 100).fillna(0).round(1)
df["Growth From Jun (%)"] = (((df["__PosEnd"] - df["__PosStart"]) / df["__PosStart"].replace(0, np.nan)) * 100).fillna(0).round(1)

# ==========================================
# 3. EXECUTIVE TABS & STRUCTURED SUMMARIES
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏛️ District & Location Summary", 
    "💰 Deposit by Product Type", 
    "📱 Digital Customer Summary", 
    "👥 Business Segment Summary", 
    "🏆 Top & Watchlist Branches", 
    "📂 Full Master Data View"
])

with tab1:
    st.subheader("1. Deposit Performance by District & Location Category (City vs Outlying)")
    district_summary = df.groupby(["__District", "__Location"]).agg(
        Total_Branches=("__BranchName", "count"),
        Position_Jun=("__PosStart", "sum"),
        Monthly_Plan=("__MonthlyPlan", "sum"),
        Monthly_Actual=("__MonthlyActual", "sum"),
        Q1_Plan=("__Q1Plan", "sum"),
        Q1_Actual=("__Q1Actual", "sum"),
        Position_Sep=("__PosEnd", "sum"),
        Digital_Customers=("__DigitalCust", "sum")
    ).reset_index()

    district_summary["Monthly %"] = (district_summary["Monthly_Actual"] / district_summary["Monthly_Plan"].replace(0, np.nan) * 100).round(1)
    district_summary["Q1 %"] = (district_summary["Q1_Actual"] / district_summary["Q1_Plan"].replace(0, np.nan) * 100).round(1)
    district_summary["Growth (%)"] = ((district_summary["Position_Sep"] - district_summary["Position_Jun"]) / district_summary["Position_Jun"].replace(0, np.nan) * 100).round(1)

    st.data_editor(district_summary, num_rows="dynamic", use_container_width=True, key="dist_summary_t")

with tab2:
    st.subheader("2. Deposit Breakdown by Product Type (Saving, Demand, Fixed Time)")
    product_summary = df.groupby("__DepositType").agg(
        Branch_Count=("__BranchName", "count"),
        Position_Jun=("__PosStart", "sum"),
        Monthly_Actual=("__MonthlyActual", "sum"),
        YTD_Actual=("__Q1Actual", "sum"),
        Position_Sep=("__PosEnd", "sum")
    ).reset_index().rename(columns={"__DepositType": "Deposit Product Type"})
    
    total_dep = product_summary["Position_Sep"].sum()
    product_summary["Share (%)"] = (product_summary["Position_Sep"] / (total_dep if total_dep != 0 else np.nan) * 100).fillna(0).round(1)
    
    st.data_editor(product_summary, num_rows="dynamic", use_container_width=True, key="prod_summary_t")

with tab3:
    st.subheader("3. Digital Customer & E-Banking Adoption by Branch Network")
    digital_summary = df[["__BranchCode", "__BranchName", "__District", "__Location", "__DigitalCust", "__PosEnd"]].copy()
    digital_summary["Digital Share of Balance (%)"] = (digital_summary["__DigitalCust"] / digital_summary["__PosEnd"].replace(0, np.nan) * 100).round(2)
    digital_summary = digital_summary.rename(columns={
        "__BranchCode": "Branch Code",
        "__BranchName": "Branch Name",
        "__District": "District",
        "__Location": "Location",
        "__DigitalCust": "Digital Active Customers",
        "__PosEnd": "Period-End Position"
    })
    st.data_editor(digital_summary, num_rows="dynamic", use_container_width=True, key="digital_summary_t")

with tab4:
    st.subheader("4. Deposit Summary by Customer Business Segment (CRM, IRM, MSME, Retail)")
    segment_summary = df.groupby("__Segment").agg(
        Branch_Count=("__BranchName", "count"),
        Position_Jun=("__PosStart", "sum"),
        YTD_Actual=("__Q1Actual", "sum"),
        Position_Sep=("__PosEnd", "sum"),
        Digital_Cust=("__DigitalCust", "sum")
    ).reset_index().rename(columns={"__Segment": "Business Segment"})
    
    segment_summary["Segment Share (%)"] = (segment_summary["Position_Sep"] / (total_dep if total_dep != 0 else np.nan) * 100).fillna(0).round(1)
    st.data_editor(segment_summary, num_rows="dynamic", use_container_width=True, key="seg_summary_t")

with tab5:
    st.subheader("5. Top 10 & Watchlist Branch Performance Leaderboards")
    sorted_df = df.sort_values(by="Q1 Ach (%)", ascending=False)
    top_10 = sorted_df.head(10)[["__BranchCode", "__BranchName", "__District", "__Location", "__Q1Actual", "Q1 Ach (%)", "__DigitalCust"]]
    least_10 = sorted_df.tail(10)[["__BranchCode", "__BranchName", "__District", "__Location", "__Q1Actual", "Q1 Ach (%)", "__DigitalCust"]]

    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.markdown("##### 🌟 Top 10 Performing Branches")
        st.data_editor(top_10, num_rows="dynamic", use_container_width=True, key="top10_b")
    with col_l2:
        st.markdown("##### ⚠️ Least 10 Watchlist Branches")
        st.data_editor(least_10, num_rows="dynamic", use_container_width=True, key="least10_b")

with tab6:
    st.subheader(f"6. Complete Master Dataset ({len(raw_df)} Total Rows - Zero Truncation)")
    st.data_editor(raw_df, num_rows="dynamic", use_container_width=True, key="master_raw_t")

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        raw_df.to_excel(writer, sheet_name='Master_Data', index=False)
        district_summary.to_excel(writer, sheet_name='District_Summary', index=False)
        product_summary.to_excel(writer, sheet_name='Product_Summary', index=False)
        segment_summary.to_excel(writer, sheet_name='Segment_Summary', index=False)
    
    st.download_button(
        label="📥 Download Complete Executive Excel Report (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name=f"Executive_Bank_Master_Report_{current_period}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
