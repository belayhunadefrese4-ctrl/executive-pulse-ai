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
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 8px; text-align: center; }
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
    st.markdown('<p class="main-header">🏦 Executive Pulse AI: Cloud Financial Intelligence Engine</p>', unsafe_allow_html=True)
    st.warning("🔒 Access Restricted: Please enter the valid Master Executive Key in the sidebar.")
    st.stop()

# ==========================================
# APP HEADER & CLOUD MULTI-FILE INGESTION HUB
# ==========================================
st.markdown('<p class="main-header">🏦 Executive Pulse AI: Cloud Financial Intelligence Engine</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Online Multi-File Ingestion, Automated Balance Sheet, Deposit & Segment Summaries</p>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("📥 Cloud Ingestion Hub")
uploaded_files = st.sidebar.file_uploader(
    "Upload Bank Files (Balance Sheet, Deposits, Segments, ATM, Mobile)", 
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
                # Ensure unique column names to prevent InvalidIndexError
                df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                sheets[file_prefix] = df_temp
            else:
                xls = pd.ExcelFile(file)
                for s_name in xls.sheet_names:
                    s_df = pd.read_excel(xls, sheet_name=s_name).dropna(how='all').dropna(axis=1, how='all')
                    s_df.columns = [str(c).strip() for c in s_df.columns]
                    s_df = s_df.loc[:, ~s_df.columns.duplicated()]
                    sheet_key = f"{file_prefix} - {s_name}" if len(xls.sheet_names) > 1 else file_prefix
                    sheets[sheet_key] = s_df
        st.sidebar.success(f"✅ Loaded {len(uploaded_files)} File(s) | {len(sheets)} Domain Sheet(s)")
    except Exception as e:
        st.sidebar.error(f"Error reading files: {e}")
        sheets = {}

if not sheets:
    st.info("👆 Please upload your online master bank files using the sidebar uploader.")
    st.stop()

# ==========================================
# 2. SAFE DATA PARSING & CALCULATIONS
# ==========================================
# Safely combine dataframes by aligning columns or extracting totals independently
total_portfolio_volume = 0.0
total_records = 0

for s_name, df in sheets.items():
    total_records += len(df)
    for col in df.select_dtypes(include=[np.number]).columns:
        total_portfolio_volume += df[col].sum()

# ==========================================
# 3. EXECUTIVE DASHBOARD TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Automated Summary",
    "📑 Multi-Sheet Inspector", 
    "📄 Report & PPT Outline",
    "📥 Download Master Package"
])

with tab1:
    st.subheader("1. Automated High-Level Financial Summary")
    st.markdown("Calculated dynamically from your online uploaded detail sheets.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h4>Total Domains</h4><h2>{len(sheets)}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h4>Total Records</h4><h2>{total_records:,}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h4>Aggregated Volume</h4><h2>{total_portfolio_volume:,.0f}</h2></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><h4>Period</h4><h2>{reporting_period}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Domain Sheet Quick Overview")
    summary_overview_df = pd.DataFrame([
        {"Sheet Domain": k, "Row Count": len(v), "Column Count": len(v.columns)} for k, v in sheets.items()
    ])
    st.data_editor(summary_overview_df, num_rows="dynamic", use_container_width=True, key="summary_overview_table")

with tab2:
    st.subheader("2. Ingested Master Sheets Inspector (Multi-Select View)")
    st.markdown("Select multiple sheets below to view and compare them concurrently side-by-side or stacked.")
    
    selected_sheets_to_view = st.multiselect(
        "Select Sheets to Inspect:",
        options=list(sheets.keys()),
        default=list(sheets.keys())[:2] if len(sheets) >= 2 else list(sheets.keys())
    )
    
    if selected_sheets_to_view:
        num_selected = len(selected_sheets_to_view)
        cols_layout = st.columns(min(num_selected, 3)) if num_selected in [2, 3] else None

        for idx, s_key in enumerate(selected_sheets_to_view):
            target_container = cols_layout[idx] if cols_layout is not None and idx < len(cols_layout) else st.container()
            with target_container:
                st.markdown(f"##### 📑 Sheet Domain: `{s_key}`")
                st.caption(f"Total Rows: {len(sheets[s_key])} | Columns: {len(sheets[s_key].columns)}")
                st.data_editor(sheets[s_key], num_rows="dynamic", use_container_width=True, key=f"inspect_{s_key}_{idx}")
                st.markdown("---")
    else:
        st.info("Please select at least one sheet above to display its contents.")

with tab3:
    st.subheader("3. Executive Narrative Report & Boardroom PPT Outline")
    
    sheet_names_sample = ", ".join(list(sheets.keys())[:5]) + ("..." if len(sheets) > 5 else "")

    narrative_text = f"""
====================================================================================
EXECUTIVE FINANCIAL & OPERATIONAL REPORT | PERIOD: {reporting_period}
====================================================================================

1. BALANCE SHEET & DEPOSIT PERFORMANCE SUMMARY
   ---------------------------------------------------------------------------------
   • Total Ingested Domain Sheets: {len(sheets)} ({sheet_names_sample})
   • Consolidated Master Records: {total_records:,} total data points processed.
   • Total Aggregated Portfolio Volume: {total_portfolio_volume:,.2f} calculated dynamically.

2. CUSTOMER BASE & SEGMENT DISTRIBUTION
   ---------------------------------------------------------------------------------
   • Online multi-file ingestion successfully aggregates balance sheets, deposit breakdowns, 
     customer segments, and digital channels into a cohesive view.

====================================================================================
CERTIFIED BY EXECUTIVE PULSE AI ENGINE
====================================================================================
"""

    ppt_outline = f"""
SLIDE 1: INSTITUTIONAL PERFORMANCE OVERVIEW
- Reporting Period: {reporting_period}
- Total Processed Records: {total_records:,} Rows across {len(sheets)} Domains

SLIDE 2: BALANCE SHEET & DEPOSIT STRUCTURE
- Consolidated Volume: {total_portfolio_volume:,.0f}
- Detailed breakdown preserved across Deposit Reports, Customer Segments, and Channels.

SLIDE 3: STRATEGIC ACTION POINTS
- Monitor balance sheet liquidity and digital channel outreach metrics.
"""

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("##### 📄 Executive Narrative Report")
        st.markdown(f'<div class="report-box"><pre>{narrative_text}</pre></div>', unsafe_allow_html=True)
    with col_r2:
        st.markdown("##### 📊 Boardroom PPT Slide Outline")
        st.markdown(f'<div class="ppt-box"><pre>{ppt_outline}</pre></div>', unsafe_allow_html=True)

with tab4:
    st.subheader("4. Automated Multi-Sheet Excel Package Generator")
    st.markdown("Download the fully structured Excel package containing an auto-calculated summary sheet alongside all pristine detail sheets.")

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        summary_export_df = pd.DataFrame([
            {"Metric": "Reporting Period", "Value": reporting_period},
            {"Metric": "Total Ingested Domains", "Value": len(sheets)},
            {"Metric": "Total Consolidated Records", "Value": total_records},
            {"Metric": "Aggregated Portfolio Volume", "Value": total_portfolio_volume}
        ])
        summary_export_df.to_excel(writer, sheet_name="Executive_Summary", index=False)
        
        for s_name, s_df in sheets.items():
            clean_name = str(s_name).replace(" -> ", "_")[:30].replace("/", "_").replace("\\", "_")
            s_df.to_excel(writer, sheet_name=clean_name, index=False)

    st.download_button(
        label="📥 Download Complete Multi-Sheet Executive Package (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name=f"Executive_Master_Package_{reporting_period}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
