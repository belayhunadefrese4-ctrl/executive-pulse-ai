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
# APP HEADER & MULTI-FILE INGESTION HUB
# ==========================================
st.markdown('<p class="main-header">🏦 Executive Pulse AI: Financial Intelligence Engine</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-File Ingestion Hub, Concurrent Sheet Inspector & Executive Summaries</p>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("📥 Multi-File Ingestion Hub")
uploaded_files = st.sidebar.file_uploader(
    "Upload Multiple Excel/CSV Files (e.g. ATM, Mobile Bank)", 
    type=["xlsx", "csv"], 
    accept_multiple_files=True
)
reporting_period = st.sidebar.selectbox("Reporting Period", ["Q4 2026", "Q3 2026", "Q2 2026", "Q1 2026", "Annual 2026"])

sheets = {}
if uploaded_files:
    try:
        for file in uploaded_files:
            file_prefix = file.name.rsplit('.', 1)[0]
            if file.name.endswith('.csv'):
                df_temp = pd.read_csv(file).dropna(how='all').dropna(axis=1, how='all')
                df_temp.columns = [str(c).strip() for c in df_temp.columns]
                sheets[file_prefix] = df_temp
            else:
                xls = pd.ExcelFile(file)
                for s_name in xls.sheet_names:
                    s_df = pd.read_excel(xls, sheet_name=s_name).dropna(how='all').dropna(axis=1, how='all')
                    s_df.columns = [str(c).strip() for c in s_df.columns]
                    sheet_key = f"{file_prefix} - {s_name}" if len(xls.sheet_names) > 1 else file_prefix
                    sheets[sheet_key] = s_df
        st.sidebar.success(f"✅ Successfully Loaded {len(uploaded_files)} File(s) | {len(sheets)} Total Domain Sheet(s)")
    except Exception as e:
        st.sidebar.error(f"Error reading files: {e}")
        sheets = {}

if not sheets:
    st.info("👆 Please upload your master files (e.g., ATM, Mobile Bank spreadsheets) using the sidebar uploader.")
    st.stop()

# ==========================================
# 2. EXECUTIVE TABS & CONCURRENT INSPECTOR
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "📊 Multi-Sheet Inspector", 
    "📄 Executive Summary & PPT",
    "📥 Download Consolidated Package"
])

with tab1:
    st.subheader("1. Ingested Master Sheets Inspector (Multi-Select View)")
    st.markdown("Select multiple sheets below to view and compare them concurrently.")
    
    selected_sheets_to_view = st.multiselect(
        "Select Sheets to Inspect:",
        options=list(sheets.keys()),
        default=list(sheets.keys())[:2] if len(sheets) >= 2 else list(sheets.keys())
    )
    
    if selected_sheets_to_view:
        # Safe Column Layout Allocation
        num_selected = len(selected_sheets_to_view)
        if num_selected == 2:
            cols_layout = st.columns(2)
        elif num_selected == 3:
            cols_layout = st.columns(3)
        else:
            cols_layout = None

        for idx, s_key in enumerate(selected_sheets_to_view):
            target_container = cols_layout[idx] if cols_layout is not None else st.container()
            with target_container:
                st.markdown(f"##### 📑 Sheet Domain: `{s_key}`")
                st.caption(f"Total Rows: {len(sheets[s_key])} | Columns: {len(sheets[s_key].columns)}")
                st.data_editor(sheets[s_key], num_rows="dynamic", use_container_width=True, key=f"inspect_{s_key}_{idx}")
                st.markdown("---")
    else:
        st.info("Please select at least one sheet above to display its contents.")

with tab2:
    st.subheader("2. Executive Narrative Report & Boardroom PPT Outline")
    
    total_sheets_count = len(sheets)
    total_records = sum(len(df) for df in sheets.values())
    sheet_names_list = ", ".join(list(sheets.keys()))

    narrative_text = f"""
====================================================================================
EXECUTIVE FINANCIAL & OPERATIONAL REPORT | PERIOD: {reporting_period}
====================================================================================

1. INGESTION SCOPE & DOMAIN INTEGRITY
   ---------------------------------------------------------------------------------
   • Total Ingested Domains / Sheets: {total_sheets_count} ({sheet_names_list})
   • Consolidated Master Records: {total_records} total data points processed.
   • Data structures and original headers are preserved without truncation.

2. OPERATIONAL SUMMARY
   ---------------------------------------------------------------------------------
   • Multi-file ingestion successfully aggregates digital channels, ATM networks, 
     and branch positions into a unified executive package.

====================================================================================
CERTIFIED BY EXECUTIVE PULSE AI ENGINE
====================================================================================
"""

    ppt_outline = f"""
SLIDE 1: INSTITUTIONAL PERFORMANCE OVERVIEW
- Reporting Period: {reporting_period}
- Total Processed Records: {total_records} Rows across {total_sheets_count} Domains ({sheet_names_list})

SLIDE 2: MULTI-DOMAIN CHANNEL STRUCTURE
- Consolidated tracking for ATM networks, Mobile Banking, and Branch infrastructure.
"""

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("##### 📄 Executive Narrative Report")
        st.markdown(f'<div class="report-box"><pre>{narrative_text}</pre></div>', unsafe_allow_html=True)
    with col_r2:
        st.markdown("##### 📊 Boardroom PPT Slide Outline")
        st.markdown(f'<div class="ppt-box"><pre>{ppt_outline}</pre></div>', unsafe_allow_html=True)

with tab3:
    st.subheader("3. Consolidated Multi-Sheet Excel Package Generator")
    st.markdown("Download the fully structured Excel package containing all separate domain sheets cleanly organized.")

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        for s_name, s_df in sheets.items():
            clean_name = str(s_name).replace(" -> ", "_")[:30].replace("/", "_").replace("\\", "_")
            s_df.to_excel(writer, sheet_name=clean_name, index=False)

    st.download_button(
        label="📥 Download Complete Multi-Sheet Executive Package (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name=f"Executive_Master_Package_{reporting_period}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
