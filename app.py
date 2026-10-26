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
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 18px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
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
    st.markdown('<p class="main-header">🏦 Executive Pulse AI: Enterprise Banking Engine</p>', unsafe_allow_html=True)
    st.warning("🔒 Access Restricted: Please enter the valid Master Executive Key in the sidebar.")
    st.stop()

# ==========================================
# APP HEADER & INGESTION HUB
# ==========================================
st.markdown('<p class="main-header">🏦 Executive Pulse AI: Enterprise Banking Intelligence</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Automated Variable Summation | Balance Sheet, Deposits, Customer Base & Digital Channels</p>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("📥 Enterprise Data Ingestion")
uploaded_files = st.sidebar.file_uploader(
    "Upload Bank Financial Reports & Detail Workbooks", 
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
        st.sidebar.success(f"✅ Loaded {len(uploaded_files)} File(s) | {len(sheets)} Active Domain Sheet(s)")
    except Exception as e:
        st.sidebar.error(f"Error loading files: {e}")
        sheets = {}

if not sheets:
    st.info("👆 Please upload your master bank spreadsheets via the sidebar uploader.")
    st.stop()

# ==========================================
# 2. AUTOMATED VARIABLE SUMMATION ENGINE
# ==========================================
def calculate_variable_sum(sheets_dict, keywords):
    total_sum = 0.0
    matching_sheets = 0
    for s_name, df in sheets_dict.items():
        if any(k in s_name.lower() for k in keywords):
            matching_sheets += 1
            for col in df.select_dtypes(include=[np.number]).columns:
                total_sum += df[col].sum()
    return total_sum, matching_sheets

# Calculate exact sums for each required banking variable heading
atm_sum, atm_count = calculate_variable_sum(sheets, ["atm"])
mobile_sum, mobile_count = calculate_variable_sum(sheets, ["mobil", "bank", "ussd", "ibmb", "e-birr"])
pos_sum, pos_count = calculate_variable_sum(sheets, ["pos"])
qr_sum, qr_count = calculate_variable_sum(sheets, ["qr"])
cb_sum, cb_count = calculate_variable_sum(sheets, ["customer", "cb", "segment"])
bs_sum, bs_count = calculate_variable_sum(sheets, ["balance", "sheet", "deposit", "portfolio", "liability", "asset"])

# Build executive summary table with exact variable headings in column 1
executive_summary_data = [
    {"Core Banking Variable Heading": "ATM", "Matched Source Sheets": atm_count, "Calculated Total Sum": f"{atm_sum:,.2f}" if atm_sum > 0 else "0.00"},
    {"Core Banking Variable Heading": "Mobile Bank", "Matched Source Sheets": mobile_count, "Calculated Total Sum": f"{mobile_sum:,.2f}" if mobile_sum > 0 else "0.00"},
    {"Core Banking Variable Heading": "POS Merchant", "Matched Source Sheets": pos_count, "Calculated Total Sum": f"{pos_sum:,.2f}" if pos_sum > 0 else "0.00"},
    {"Core Banking Variable Heading": "QR Merchant", "Matched Source Sheets": qr_count, "Calculated Total Sum": f"{qr_sum:,.2f}" if qr_sum > 0 else "0.00"},
    {"Core Banking Variable Heading": "Customer Base", "Matched Source Sheets": cb_count, "Calculated Total Sum": f"{cb_sum:,.2f}" if cb_sum > 0 else "0.00"},
    {"Core Banking Variable Heading": "Balance Sheet & Deposits", "Matched Source Sheets": bs_count, "Calculated Total Sum": f"{bs_sum:,.2f}" if bs_sum > 0 else "0.00"},
]

exec_summary_df = pd.DataFrame(executive_summary_data)

# ==========================================
# 3. EXECUTIVE DASHBOARD & TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Summary Table",
    "📑 Multi-Domain Inspector", 
    "📄 Boardroom Report & PPT",
    "📥 Download Master Package"
])

with tab1:
    st.subheader("1. Automated Core Banking Variable Summary")
    st.markdown("Each heading matches detail source domains, displaying the exact calculated sum directly below.")
    st.data_editor(exec_summary_df, num_rows="dynamic", use_container_width=True, key="exec_summary_table")

with tab2:
    st.subheader("2. Multi-Select Domain Inspector (Concurrent View)")
    st.markdown("Select multiple domain sheets below to review and cross-examine them side-by-side.")
    
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
                st.markdown(f"##### 📑 Domain: `{s_key}`")
                st.caption(f"Rows: {len(sheets[s_key])} | Columns: {len(sheets[s_key].columns)}")
                st.data_editor(sheets[s_key], num_rows="dynamic", use_container_width=True, key=f"inspect_{s_key}_{idx}")
                st.markdown("---")
    else:
        st.info("Please select at least one sheet above to display its contents.")

with tab3:
    st.subheader("3. Executive Narrative Report & Boardroom PPT Outline")
    
    narrative_text = f"""
====================================================================================
EXECUTIVE COMMERCIAL BANKING REPORT | PERIOD: {reporting_period}
====================================================================================

1. CORE BANKING VARIABLE TOTALS
   ---------------------------------------------------------------------------------
   • ATM Network Total Volume: {atm_sum:,.2f}
   • Mobile Banking Total Volume: {mobile_sum:,.2f}
   • POS Merchant Total Volume: {pos_sum:,.2f}
   • QR Merchant Total Volume: {qr_sum:,.2f}
   • Customer Base Total Count/Volume: {cb_sum:,.2f}
   • Balance Sheet & Deposits Total Volume: {bs_sum:,.2f}

2. OPERATIONAL SUMMARY
   ---------------------------------------------------------------------------------
   • All figures are dynamically aggregated and linked directly from the detail worksheets.

====================================================================================
CERTIFIED BY EXECUTIVE PULSE AI | ENTERPRISE BANKING INTELLIGENCE
====================================================================================
"""

    ppt_outline = f"""
SLIDE 1: INSTITUTIONAL PERFORMANCE OVERVIEW ({reporting_period})
- ATM Volume: {atm_sum:,.0f}
- Mobile Banking Volume: {mobile_sum:,.0f}
- POS Merchant Volume: {pos_sum:,.0f}
- QR Merchant Volume: {qr_sum:,.0f}

SLIDE 2: BALANCE SHEET & CUSTOMER BASE
- Customer Base Aggregate: {cb_sum:,.0f}
- Balance Sheet & Deposits Total: {bs_sum:,.0f}
"""

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("##### 📄 Boardroom Executive Report")
        st.markdown(f'<div class="report-box"><pre>{narrative_text}</pre></div>', unsafe_allow_html=True)
    with col_r2:
        st.markdown("##### 📊 Boardroom PPT Slide Outline")
        st.markdown(f'<div class="ppt-box"><pre>{ppt_outline}</pre></div>', unsafe_allow_html=True)

with tab4:
    st.subheader("4. Automated Multi-Sheet Excel Package Generator")
    st.markdown("Download the enterprise-grade multi-sheet workbook with the auto-calculated summary sheet placed as the first tab.")

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        # Write exact summary table as the first sheet
        exec_summary_df.to_excel(writer, sheet_name="Executive_Summary", index=False)
        
        # Write all detail sheets following it
        for s_name, s_df in sheets.items():
            clean_name = str(s_name).replace(" -> ", "_")[:30].replace("/", "_").replace("\\", "_")
            s_df.to_excel(writer, sheet_name=clean_name, index=False)

    st.download_button(
        label="📥 Download Complete Enterprise Multi-Sheet Package (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name=f"Enterprise_Bank_Package_{reporting_period}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
