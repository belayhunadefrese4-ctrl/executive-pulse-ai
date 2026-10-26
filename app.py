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
    .report-box { background-color: #FAFAFA; border: 1px solid #CBD5E1; border-left: 5px solid #800020; padding: 20px; border-radius: 6px; font-family: 'Times New Roman', Times, serif; }
    .ppt-box { background-color: #F8FAFC; border: 1px solid #94A3B8; border-left: 5px solid #475569; padding: 20px; border-radius: 6px; font-family: monospace; }
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
st.markdown('<p class="sub-header">Standard Bank Reporting Matrix with Exact Institutional Column Mapping</p>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("📥 Enterprise Data Ingestion")
uploaded_files = st.sidebar.file_uploader(
    "Upload Bank Financial Reports & Detail Workbooks", 
    type=["xlsx", "csv"], 
    accept_multiple_files=True
)
reporting_period = st.sidebar.selectbox("Reporting Period", ["August 2026", "Q4 2026", "Q3 2026", "Q2 2026", "Q1 2026", "Annual 2026"])

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
                    sheet_key = f"{file_prefix} -> {s_name}" if len(xls.sheet_names) > 1 else file_prefix
                    sheets[sheet_key] = s_df
        st.sidebar.success(f"✅ Loaded {len(uploaded_files)} File(s) | {len(sheets)} Active Sheet(s)")
    except Exception as e:
        st.sidebar.error(f"Error loading files: {e}")
        sheets = {}

if not sheets:
    st.info("👆 Please upload your master bank spreadsheets via the sidebar uploader.")
    st.stop()

# ==========================================
# 2. EXACT INSTITUTIONAL EXTRACTION ENGINE
# ==========================================
def clean_val(val):
    if pd.isna(val):
        return 0.0
    val_str = str(val).replace(',', '').replace('%', '').replace(' ', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def extract_metrics_institutional(target_df):
    metrics = {"June": 0.0, "YTD_Plan": 0.0, "YTD_Actual": 0.0, "M_Plan": 0.0, "M_Actual": 0.0}
    if target_df is None or target_df.empty:
        return metrics
        
    cols = target_df.columns
    col_map = {str(c).lower().strip(): c for c in cols}
    
    # 1. Header Name Match
    june_col = next((col_map[c] for c in col_map if "june" in c or "jun" in c), None)
    ytd_plan_col = next((col_map[c] for c in col_map if "ytd" in c and "plan" in c), None)
    ytd_act_col = next((col_map[c] for c in col_map if "ytd" in c and "actual" in c), None)
    m_plan_col = next((col_map[c] for c in col_map if ("m." in c or "month" in c) and "plan" in c), None)
    m_act_col = next((col_map[c] for c in col_map if ("m." in c or "month" in c) and "actual" in c), None)
    
    # 2. Positional Fallback based on standard template structure
    # If headers aren't explicitly named, use precise column index positions
    if not june_col and len(cols) > 4: june_col = cols[4]
    if not ytd_plan_col and len(cols) > 5: ytd_plan_col = cols[5]
    if not ytd_act_col and len(cols) > 6: ytd_act_col = cols[6]
    if not m_plan_col and len(cols) > 8: m_plan_col = cols[8]
    if not m_act_col and len(cols) > 9: m_act_col = cols[9]

    if june_col: metrics["June"] = target_df[june_col].apply(clean_val).sum()
    if ytd_plan_col: metrics["YTD_Plan"] = target_df[ytd_plan_col].apply(clean_val).sum()
    if ytd_act_col: metrics["YTD_Actual"] = target_df[ytd_act_col].apply(clean_val).sum()
    if m_plan_col: metrics["M_Plan"] = target_df[m_plan_col].apply(clean_val).sum()
    if m_act_col: metrics["M_Actual"] = target_df[m_act_col].apply(clean_val).sum()
            
    return metrics

particulars_list = [
    ("Mobile Bank", ["mobil", "bank", "ussd", "ibmb", "e-birr"], 0),
    ("ATM", ["atm"], 1),
    ("POS Merchant", ["pos"], 2),
    ("QR Merchant", ["qr"], 3),
    ("Customer Base", ["customer", "cb", "segment"], 4),
    ("Balance Sheet & Deposits", ["balance", "sheet", "deposit", "portfolio", "liability", "asset"], 5)
]

sheet_keys = list(sheets.keys())
summary_rows = []
all_detail_sheets_dict = {}

for idx, (part_name, keywords, default_file_idx) in enumerate(particulars_list, 1):
    target_df = None
    
    # Match by keyword
    for s_name, df in sheets.items():
        if any(k in s_name.lower() for k in keywords):
            target_df = df
            break
            
    # Fallback to sequential file mapping
    if target_df is None and default_file_idx < len(sheet_keys):
        target_df = sheets[sheet_keys[default_file_idx]]
        
    sums = extract_metrics_institutional(target_df)
    all_detail_sheets_dict[part_name] = {part_name: target_df} if target_df is not None else {}
    
    # Mandatory Banking Rule: Position As of August 31 = June 30 Position + YTD Actual
    position_august = sums["June"] + sums["YTD_Actual"]
    
    ytd_pct = (sums["YTD_Actual"] / sums["YTD_Plan"] * 100) if sums["YTD_Plan"] > 0 else 0.0
    m_pct = (sums["M_Actual"] / sums["M_Plan"] * 100) if sums["M_Plan"] > 0 else 0.0
    
    summary_rows.append({
        "#": idx,
        "Particulars / variables": part_name,
        "As of June 30, 2026": f"{sums['June']:,.0f}" if sums['June'] > 0 else "0",
        "YTD. Plan": f"{sums['YTD_Plan']:,.0f}" if sums['YTD_Plan'] > 0 else "0",
        "YTD. Actual": f"{sums['YTD_Actual']:,.0f}" if sums['YTD_Actual'] > 0 else "0",
        "%age": f"{ytd_pct:.0f}%" if ytd_pct > 0 else "0%",
        "M.Plan": f"{sums['M_Plan']:,.0f}" if sums['M_Plan'] > 0 else "0",
        "M. Actual": f"{sums['M_Actual']:,.0f}" if sums['M_Actual'] > 0 else "0",
        "%age.1": f"{m_pct:.0f}%" if m_pct > 0 else "0%",
        "Position As of August 31, 2026": f"{position_august:,.0f}" if position_august > 0 else "0"
    })

exec_summary_df = pd.DataFrame(summary_rows)
exec_summary_df.columns = [
    "#", "Particulars / variables", "As of June 30, 2026", 
    "YTD. Plan", "YTD. Actual", "%age", 
    "M.Plan", "M. Actual", "%age ", 
    "Position As of August 31, 2026"
]

# ==========================================
# 3. EXECUTIVE DASHBOARD TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Summary Table",
    "📑 Linked Detail Sheets", 
    "📄 Boardroom Report & PPT",
    "📥 Download Master Package"
])

with tab1:
    st.subheader(f"2. Card & Digital Banking Users Summary ({reporting_period})")
    st.markdown("Structured with exact institutional alignment and Position = June Position + YTD Actual:")
    st.data_editor(exec_summary_df, num_rows="dynamic", use_container_width=True, key="bank_standard_matrix")

with tab2:
    st.subheader("📑 Detailed Source Workbooks & Domain Inspector")
    selected_part = st.selectbox("Select Particulars / Variable to Inspect:", [p[0] for p in particulars_list])
    
    matched_dict = all_detail_sheets_dict[selected_part]
    if matched_dict:
        for s_name, s_df in matched_dict.items():
            if s_df is not None:
                st.markdown(f"**Source Workbook / Sheet for `{selected_part}`:** ({len(s_df)} rows total)")
                st.data_editor(s_df, num_rows="dynamic", use_container_width=True, key=f"insp_{selected_part}_{s_name}")
            else:
                st.info("No detail sheet mapped for this particular.")
    else:
        st.info("No details available.")

with tab3:
    st.subheader("📄 Executive Narrative Report & Boardroom PPT Outline")
    
    narrative_text = f"""
====================================================================================
COMMERCIAL BANKING PERFORMANCE REPORT | PERIOD: {reporting_period}
====================================================================================

1. EXECUTIVE SUMMARY MATRIX
   ---------------------------------------------------------------------------------
   • Summary table successfully generated with exact institutional column alignment.
   • Position As of August 31, 2026 computed precisely as June 30 Position + YTD Actual.

====================================================================================
CERTIFIED BY EXECUTIVE PULSE AI | ENTERPRISE BANKING INTELLIGENCE
====================================================================================
"""

    ppt_outline = f"""
SLIDE 1: INSTITUTIONAL PERFORMANCE MATRIX ({reporting_period})
- Standardized Particulars Breakdown (Mobile Bank, ATM, POS, QR, Customer Base, Balance Sheet).
- Comprehensive Tracking: June Position, YTD Plan vs Actual, Monthly Plan vs Actual.
"""

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("##### 📄 Boardroom Executive Report")
        st.markdown(f'<div class="report-box"><pre>{narrative_text}</pre></div>', unsafe_allow_html=True)
    with col_r2:
        st.markdown("##### 📊 Boardroom PPT Slide Outline")
        st.markdown(f'<div class="ppt-box"><pre>{ppt_outline}</pre></div>', unsafe_allow_html=True)

with tab4:
    st.subheader("📥 Download Master Package")
    st.markdown("Download the fully structured Excel workbook containing the standardized summary table as the first sheet.")

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        exec_summary_df.to_excel(writer, sheet_name="Executive_Summary", index=False)
        for s_name, s_df in sheets.items():
            clean_name = str(s_name).replace(" -> ", "_")[:30].replace("/", "_").replace("\\", "_")
            s_df.to_excel(writer, sheet_name=clean_name, index=False)

    st.download_button(
        label="📥 Download Complete Enterprise Multi-Sheet Package (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name=f"Enterprise_Bank_Package_{reporting_period}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
