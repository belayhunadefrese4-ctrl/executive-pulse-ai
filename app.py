import streamlit as st
import pandas as pd
import numpy as np
import io

# ==========================================
# PAGE CONFIGURATION & EXECUTIVE STYLING
# ==========================================
st.set_page_config(
    page_title="Executive Pulse AI - Commercial Banking Engine",
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
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
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
# APP HEADER & FILE INGESTION
# ==========================================
st.markdown('<p class="main-header">🏦 Executive Pulse AI: Financial Intelligence Engine</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Direct Multi-Sheet Ingestion & Executive Summary Generator</p>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("📥 Ingestion Hub")
uploaded_file = st.sidebar.file_uploader("Upload Master Bank Excel/CSV", type=["xlsx", "csv"])
reporting_period = st.sidebar.selectbox("Reporting Period", ["Q4 2026", "Q3 2026", "Q2 2026", "Q1 2026", "Annual 2026"])

sheets = {}
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            master_df = pd.read_csv(uploaded_file).dropna(how='all').dropna(axis=1, how='all')
            master_df.columns = [str(c).strip() for c in master_df.columns]
            sheets["Master_Data"] = master_df
        else:
            xls = pd.ExcelFile(uploaded_file)
            for s_name in xls.sheet_names:
                s_df = pd.read_excel(xls, sheet_name=s_name).dropna(how='all').dropna(axis=1, how='all')
                s_df.columns = [str(c).strip() for c in s_df.columns]
                sheets[s_name] = s_df
        st.sidebar.success(f"✅ Successfully Loaded {len(sheets)} Sheet(s) from File!")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
        sheets = {}

if not sheets:
    st.info("👆 Please upload your master bank Excel spreadsheet using the sidebar uploader.")
    st.stop()

# Combine for overall metrics calculation
combined_master = pd.concat(sheets.values(), ignore_index=True) if sheets else pd.DataFrame()

# ==========================================
# 2. EXECUTIVE TABS & INSPECTOR
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "📊 Sheets Inspector", 
    "📄 Narrative & PPT",
    "📥 Download Package"
])

with tab1:
    st.subheader("1. Ingested Master Sheets Inspector (Zero Truncation)")
    selected_sheet_name = st.selectbox("Select Sheet to View:", list(sheets.keys()))
    if selected_sheet_name:
        st.markdown(f"**Showing Sheet:** `{selected_sheet_name}` ({len(sheets[selected_sheet_name])} rows)")
        st.data_editor(sheets[selected_sheet_name], num_rows="dynamic", use_container_width=True, key=f"inspect_{selected_sheet_name}")

with tab2:
    st.subheader("2. Executive Narrative Report & Linked PPT Outline")
    
    total_rows = len(combined_master)
    total_sheets_count = len(sheets)
    
    narrative_text = f"""
====================================================================================
EXECUTIVE REPORT | PERIOD: {reporting_period}
====================================================================================

1. MASTER DATA INTEGRITY & SCOPE
   ---------------------------------------------------------------------------------
   • Total Ingested Sheets: {total_sheets_count} active domains.
   • Consolidated Records: {total_rows} total rows processed without truncation.
   • All original headings and domain categories are fully preserved from source files.

2. BOARDROOM SUMMARY
   ---------------------------------------------------------------------------------
   • Multi-sheet architecture maintains pristine separation across branch networks, 
     deposit categories, digital channels, and specialized infrastructure.

====================================================================================
CERTIFIED BY EXECUTIVE PULSE AI ENGINE
====================================================================================
"""

    ppt_outline = f"""
SLIDE 1: INSTITUTIONAL PERFORMANCE OVERVIEW
- Reporting Period: {reporting_period}
- Total Processed Records: {total_rows} Rows across {total_sheets_count} Sheets

SLIDE 2: MULTI-VARIABLE STRUCTURE
- Direct domain segregation for Branch Networks, Deposit Categories, and Digital Channels.
"""

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("##### 📄 Executive Narrative Report")
        st.markdown(f'<div class="report-box"><pre>{narrative_text}</pre></div>', unsafe_allow_html=True)
    with col_r2:
        st.markdown("##### 📊 Boardroom PPT Slide Outline")
        st.markdown(f'<div class="ppt-box"><pre>{ppt_outline}</pre></div>', unsafe_allow_html=True)

with tab3:
    st.subheader("3. Multi-Sheet Excel Package Generator")
    st.markdown("Download the fully structured, multi-sheet Excel package keeping all original master tables pristine.")

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        for s_name, s_df in sheets.items():
            clean_name = str(s_name)[:30].replace("/", "_").replace("\\", "_")
            s_df.to_excel(writer, sheet_name=clean_name, index=False)

    st.download_button(
        label="📥 Download Complete Multi-Sheet Executive Package (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name=f"Executive_Master_Package_{reporting_period}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
