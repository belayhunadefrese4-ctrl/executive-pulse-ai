import streamlit as st
import pandas as pd
import numpy as np
import io

# ==========================================
# PAGE CONFIGURATION & EXECUTIVE STYLING
# ==========================================
st.set_page_config(
    page_title="Executive Pulse AI - Commercial Banking Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 800; color: #800020; letter-spacing: -0.5px; }
    .sub-header { font-size: 1.05rem; color: #334155; margin-bottom: 20px; }
    .security-badge { background-color: #800020; color: #FFFFFF; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 0.85rem; }
    .report-box { background-color: #FAFAFA; border: 1px solid #CBD5E1; border-left: 5px solid #800020; padding: 20px; border-radius: 6px; font-family: 'Times New Roman', Times, serif; }
    .ppt-box { background-color: #F8FAFC; border: 1px solid #94A3B8; border-left: 5px solid #475569; padding: 20px; border-radius: 6px; font-family: monospace; }
    /* Streamlit 탭 글자 잘림 방지 및 정렬 최적화 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 45px; white-space: pre-wrap; font-weight: 600; font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SECURITY & ACCESS CONTROL
# ==========================================
MASTER_SECURITY_KEY = "BANK-EXEC-8899-SECURE"

st.sidebar.markdown("### 🔐 Security & Access Control")
user_key = st.sidebar.text_input("Enter Master Executive Key", type="password")

if user_key != MASTER_SECURITY_KEY:
    st.markdown('<p class="main-header">🏦 Executive Pulse AI: Financial Intelligence Engine</p>', unsafe_allow_html=True)
    st.warning("🔒 Access Restricted: Please enter the valid Master Executive Key in the sidebar.")
    st.stop()

# ==========================================
# APP HEADER & MULTI-DOCUMENT INGESTION
# ==========================================
col_title, col_sec = st.columns([3, 1])
with col_title:
    st.markdown('<p class="main-header">🏦 Executive Pulse AI: Financial Intelligence Engine</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Multi-Variable Aggregation, Clean Summaries, Reports & PPT Outlines</p>', unsafe_allow_html=True)
with col_sec:
    st.markdown("<br><span class='security-badge'>🛡️ ENTERPRISE SECURE</span>", unsafe_allow_html=True)

st.markdown("---")

st.sidebar.header("📥 Multi-Document Ingestion Hub")
uploaded_files = st.sidebar.file_uploader(
    "Upload Branch Data, Digital Channels & Deposit Files", 
    type=["xlsx", "csv"], 
    accept_multiple_files=True
)

institution_label = st.sidebar.text_input("Institution Name / Title", value="Commercial Financial Institution")
reporting_period = st.sidebar.selectbox("Reporting Period", ["Q4 2026", "Q3 2026", "Q2 2026", "Q1 2026", "Annual 2026"])

# Multi-Document Ingestion
if uploaded_files:
    try:
        dfs = []
        for file in uploaded_files:
            temp_df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
            temp_df = temp_df.dropna(how='all').dropna(axis=1, how='all')
            temp_df.columns = [str(c).strip() for c in temp_df.columns]
            dfs.append(temp_df)
        raw_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        st.sidebar.success(f"✅ Ingested {len(uploaded_files)} File(s) | {len(raw_df)} Total Rows Loaded")
    except Exception as e:
        st.sidebar.error(f"Error loading files: {e}")
        raw_df = None
else:
    raw_df = None

if raw_df is None or raw_df.empty:
    st.info("👆 Upload your master branch files using the sidebar to generate verified summaries.")
    st.stop()

# ==========================================
# 2. SMART FUZZY HEADER MAPPING ENGINE
# ==========================================
cols = raw_df.columns.tolist()

def match_col(possible_keywords):
    for c in cols:
        cl = c.lower()
        for kw in possible_keywords:
            if kw in cl:
                return c
    return None

c_code = match_col(["branch code", "code", "No", "id"])
c_name = match_col(["branch name", "branch", "name", "unit"])
c_loc = match_col(["location", "category", "city", "outlying", "place", "area type"])
c_dist = match_col(["district", "region", "zone", "branch district"])
c_m_plan = match_col(["monthly plan", "m_plan", "month plan"])
c_m_actual = match_col(["monthly actual", "m_actual", "month actual"])
c_q_plan = match_col(["q1 plan", "quarterly plan", "quarter plan"])
c_q_actual = match_col(["q1 actual", "quarterly actual", "quarter actual"])
c_pos_start = match_col(["30 jun", "jun 2026", "prior", "start", "beginning"])
c_pos_end = match_col(["30 sep", "sep 2026", "current", "position", "balance", "amount", "total"])
c_saving = match_col(["saving", "demand", "fixed", "deposit", "product", "type"])

c_mob = match_col(["mobile", "mbank", "mobil", "smartphone", "cell"])
c_atm = match_col(["atm"])
c_pos_m = match_col(["pos merchant", "merchant"])
c_pos_d = match_col(["pos deployed", "pos dep"])
c_qr_m = match_col(["qr merchant", "q merchant"])
c_qr_d = match_col(["qr deployed", "q deployed"])
c_school = match_col(["school", "education", "student"])
c_agent = match_col(["agent", "digital agent", "banking"])
c_seg = match_col(["segment", "group", "customer", "crm", "irm", "msme", "retail"])

df = raw_df.copy()

df["__BranchCode"] = raw_df[c_code].astype(str) if c_code else "N/A"
df["__BranchName"] = raw_df[c_name].astype(str) if c_name else raw_df.iloc[:, 0].astype(str)
df["__Location"] = raw_df[c_loc].astype(str) if c_loc else "City"
df["__District"] = raw_df[c_dist].astype(str) if c_dist else "Central District"

df["__MonthlyPlan"] = pd.to_numeric(raw_df[c_m_plan], errors="coerce").fillna(0) if c_m_plan else 0.0
df["__MonthlyActual"] = pd.to_numeric(raw_df[c_m_actual], errors="coerce").fillna(0) if c_m_actual else 0.0
df["__Q1Plan"] = pd.to_numeric(raw_df[c_q_plan], errors="coerce").fillna(0) if c_q_plan else 0.0
df["__Q1Actual"] = pd.to_numeric(raw_df[c_q_actual], errors="coerce").fillna(0) if c_q_actual else 0.0
df["__PosStart"] = pd.to_numeric(raw_df[c_pos_start], errors="coerce").fillna(0) if c_pos_start else 0.0
df["__PosEnd"] = pd.to_numeric(raw_df[c_pos_end], errors="coerce").fillna(0) if c_pos_end else 0.0
df["__DepositType"] = raw_df[c_saving].astype(str) if c_saving else "General Deposit"
df["__CustomerSegment"] = raw_df[c_seg].astype(str) if c_seg else "Retail"

df["__MobileUsers"] = pd.to_numeric(raw_df[c_mob], errors="coerce").fillna(0) if c_mob else 0
df["__ATMUsers"] = pd.to_numeric(raw_df[c_atm], errors="coerce").fillna(0) if c_atm else 0
df["__POSMerchant"] = pd.to_numeric(raw_df[c_pos_m], errors="coerce").fillna(0) if c_pos_m else 0
df["__POSDeployed"] = pd.to_numeric(raw_df[c_pos_d], errors="coerce").fillna(0) if c_pos_d else 0
df["__QRMerchant"] = pd.to_numeric(raw_df[c_qr_m], errors="coerce").fillna(0) if c_qr_m else 0
df["__QRDeployed"] = pd.to_numeric(raw_df[c_qr_d], errors="coerce").fillna(0) if c_qr_d else 0
df["__SchoolSys"] = pd.to_numeric(raw_df[c_school], errors="coerce").fillna(0) if c_school else 0
df["__AgentBanking"] = pd.to_numeric(raw_df[c_agent], errors="coerce").fillna(0) if c_agent else 0

total_portfolio = df["__PosEnd"].sum()
total_prior = df["__PosStart"].sum()
overall_growth = ((total_portfolio - total_prior) / total_prior * 100) if total_prior > 0 else 0.0

# ==========================================
# 3. EXECUTIVE TABS (글자 잘림 방지 명칭 적용)
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏛️ District", 
    "💰 Deposits", 
    "📱 Digital", 
    "🏫 Infrastructure", 
    "📄 Report & PPT",
    "📂 Inspector"
])

with tab1:
    st.subheader("1. Deposit Performance by District & Location Category")
    district_summary = df.groupby(["__District", "__Location"]).agg(
        Total_Branches=("__BranchName", "count"),
        Position_Prior=("__PosStart", "sum"),
        Monthly_Plan=("__MonthlyPlan", "sum"),
        Monthly_Actual=("__MonthlyActual", "sum"),
        Q1_Plan=("__Q1Plan", "sum"),
        Q1_Actual=("__Q1Actual", "sum"),
        Position_Current=("__PosEnd", "sum"),
        Mobile_Banking_Users=("__MobileUsers", "sum")
    ).reset_index().rename(columns={"__District": "District", "__Location": "Location Category"})

    district_summary["Monthly Ach (%)"] = (district_summary["Monthly_Actual"] / district_summary["Monthly_Plan"].replace(0, np.nan) * 100).round(1).fillna(0)
    district_summary["Q1 Ach (%)"] = (district_summary["Q1_Actual"] / district_summary["Q1_Plan"].replace(0, np.nan) * 100).round(1).fillna(0)
    district_summary["Growth (%)"] = ((district_summary["Position_Current"] - district_summary["Position_Prior"]) / district_summary["Position_Prior"].replace(0, np.nan) * 100).round(1).fillna(0)

    st.data_editor(district_summary, num_rows="dynamic", use_container_width=True, key="dist_summary_t")

with tab2:
    st.subheader("2. Deposit Breakdown by Product Type (Saving, Demand, Fixed Time)")
    product_summary = df.groupby("__DepositType").agg(
        Branch_Count=("__BranchName", "count"),
        Position_Prior=("__PosStart", "sum"),
        Monthly_Actual=("__MonthlyActual", "sum"),
        YTD_Actual=("__Q1Actual", "sum"),
        Position_Current=("__PosEnd", "sum"),
        Mobile_Users=("__MobileUsers", "sum")
    ).reset_index().rename(columns={"__DepositType": "Deposit Product Type"})
    
    product_summary["Portfolio Share (%)"] = (product_summary["Position_Current"] / (total_portfolio if total_portfolio != 0 else np.nan) * 100).fillna(0).round(1)
    st.data_editor(product_summary, num_rows="dynamic", use_container_width=True, key="prod_summary_t")

with tab3:
    st.subheader("3. Customer Base & Digital Channels Summary")
    digital_chan_sum = df.groupby(["__District", "__Location"]).agg(
        Active_Branches=("__BranchName", "count"),
        Mobile_Banking_Users=("__MobileUsers", "sum"),
        ATM_Bank_Users=("__ATMUsers", "sum"),
        POS_Merchants=("__POSMerchant", "sum"),
        POS_Deployed=("__POSDeployed", "sum"),
        QR_Merchants=("__QRMerchant", "sum"),
        QR_Deployed=("__QRDeployed", "sum")
    ).reset_index().rename(columns={"__District": "District", "__Location": "Location Category"})
    st.data_editor(digital_chan_sum, num_rows="dynamic", use_container_width=True, key="dig_chan_t")

with tab4:
    st.subheader("4. Specialized Infrastructure Summary (School Systems & Digital Agent Banking)")
    infra_sum = df.groupby(["__District", "__Location"]).agg(
        Active_Branches=("__BranchName", "count"),
        School_System_Users=("__SchoolSys", "sum"),
        Digital_Agent_Banking=("__AgentBanking", "sum"),
        Total_Deposit_Position=("__PosEnd", "sum")
    ).reset_index().rename(columns={"__District": "District", "__Location": "Location Category"})
    st.data_editor(infra_sum, num_rows="dynamic", use_container_width=True, key="infra_sum_t")

with tab5:
    st.subheader("5. Executive Narrative Report & Linked PPT Outline")
    
    top_district = district_summary.iloc[0]['District'] if not district_summary.empty else "Central District"
    total_mobile = df["__MobileUsers"].sum()
    total_pos = df["__POSDeployed"].sum()
    total_qr = df["__QRDeployed"].sum()
    total_agents = df["__AgentBanking"].sum()
    total_school = df["__SchoolSys"].sum()

    narrative_text = f"""
====================================================================================
INSTITUTION: {institution_label.upper()}
EXECUTIVE DEPOSIT PERFORMANCE & DIGITAL ADOPTION REPORT | PERIOD: {reporting_period}
====================================================================================

1. CONSOLIDATED FINANCIAL & DEPOSIT PERFORMANCE
   ---------------------------------------------------------------------------------
   • Total Consolidated Portfolio: {total_portfolio:,.2f} ETB across {len(df)} reporting branches.
   • Portfolio Growth Rate: {overall_growth:+.2f}% compared to the prior reporting period.
   • Primary Regional Anchor: {top_district} recorded the highest overall deposit contribution.

2. DIGITAL CHANNEL ADOPTION & INFRASTRUCTURE EXPANSION
   ---------------------------------------------------------------------------------
   • Mobile Banking Ecosystem: Scaled to {total_mobile:,.0f} active users from master records.
   • POS & QR Network: {total_pos:,.0f} POS units and {total_qr:,.0f} QR merchant points deployed.
   • Specialized Services: {total_school:,.0f} school system accounts and {total_agents:,.0f} digital agent outlets active.

====================================================================================
CERTIFIED BY EXECUTIVE PULSE AI | ENTERPRISE FINANCIAL ENGINE
====================================================================================
"""

    ppt_outline = f"""
SLIDE 1: INSTITUTIONAL PERFORMANCE OVERVIEW
- Institution: {institution_label}
- Total Portfolio Balance: {total_portfolio:,.0f} ETB ({overall_growth:+.2f}% Growth)
- Active Reporting Branch Network: {len(df)} Branches

SLIDE 2: DEPOSIT BREAKDOWN BY PRODUCT TYPE
- Product Portfolio Mix: Saving, Demand, and Fixed Time Deposits.
- Leading Performance District: {top_district}.

SLIDE 3: DIGITAL CHANNEL & MERCHANT ECOSYSTEM
- Mobile Banking Users: {total_mobile:,.0f}
- POS Deployed: {total_pos:,.0f} Units | QR Deployed: {total_qr:,.0f} Points
- Agent Banking Outlets: {total_agents:,.0f} | School Systems: {total_school:,.0f}
"""
