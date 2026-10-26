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
st.markdown('<p class="sub-header">Standard Bank Reporting Matrix with Exact Column-Wise Detail Summation</p>', unsafe_allow_html=True)
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
# 2. COLUMN-WISE SUMMATION OF DETAIL TABLES
# ==========================================
def clean_val(val):
    if pd.isna(val):
        return 0.0
    val_str = str(val).replace(',', '').replace('%', '').replace(' ', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def calculate_detail_column_sums(sheets_dict, keywords):
    """Sums all numeric data rows column-by-column across matching detail sheets, ignoring text columns."""
    metrics = {"June": 0.0, "YTD_Plan": 0.0, "YTD_Actual": 0.0, "M_Plan": 0.0, "M_Actual": 0.0}
    matching_sheets = {}

    for s_name, df in sheets_dict.items():
        if any(k in s_name.lower() for k in keywords):
            matching_sheets[s_name] = df
            
            # Identify numeric columns (ignoring text columns like Branch Name, District, Location)
            numeric_cols = []
            for col in df.columns:
                col_lower = str(col).lower()
                if any(w in col_lower for w in ["branch", "district", "location", "name", "#", "unnamed"]):
                    continue
                # Test if column holds numbers
                converted = df[col].apply(clean_val)
                if converted.sum() > 0:
                # Exclude columns that look like percentage columns (values mostly <= 2 or containing %)
                    if not all(v <= 3.0 for v in converted[converted > 0]):
                        numeric_cols.append(col)

            # If we successfully isolated the metric columns (June, YTD Plan, YTD Actual, M. Plan, M. Actual)
            if len(numeric_cols) >= 5:
                metrics["June"] += df[numeric_cols[0]].apply(clean_val).sum()
                metrics["YTD_Plan"] += df[numeric_cols[1]].apply(clean_val).sum()
                metrics["YTD_Actual"] += df[numeric_cols[2]].apply(clean_val).sum()
                metrics["M_Plan"] += df[numeric_cols[3]].apply(clean_val).sum()
                metrics["M_Actual"] += df[numeric_cols[4]].apply(clean_val).sum()
            elif len(numeric_cols) > 0:
                # Fallback positional summation of the first 5 numeric columns found
                all_num_cols = [c for c in df.columns if df[c].apply(clean_val).sum() > 0]
                if len(all_num_cols) >= 5:
                    metrics["June"] += df[all_num_cols[0]].apply(clean_val).sum()
                    metrics["YTD_Plan"] += df[all_num_cols[1]].apply(clean_val).sum()
                    metrics["YTD_Actual"] += df[all_num_cols[2]].apply(clean_val).sum()
                    metrics["M_Plan"] += df[all_num_cols[3]].apply(clean_val).sum()
                    metrics["M_Actual"] += df[all_num_cols[4]].apply(clean_val).sum()

    return metrics, matching_sheets

particulars = [
    ("ATM", ["atm"]),
    ("Mobile Bank", ["mobil", "bank", "ussd", "ibmb", "e-birr"]),
    ("POS Merchant", ["pos"]),
    ("QR Merchant", ["qr"]),
    ("Customer Base", ["customer", "cb", "segment"]),
    ("Balance Sheet & Deposits", ["balance", "sheet", "deposit", "portfolio", "liability", "asset"])
]

summary_rows = []
all_detail_sheets_dict = {}

for idx, (part_name, keywords) in enumerate(particulars, 1):
    sums, matched = calculate_detail_column_sums(sheets, keywords)
    all_detail_sheets_dict[part_name] = matched
    
    # Exact Bank Rule: Position As of August 31 = June 30 Position + YTD Actual
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
    st.subheader("2. Card & Digital Banking Users Summary (August 2026)")
    st.markdown("Structured exactly to bank standards with correct column-wise detail summation and Position = June Position + YTD Actual:")
    st.data_editor(exec_summary_df, num_rows="dynamic", use_container_width=True, key="bank_standard_matrix")

with tab2:
    st.subheader("📑 Detailed Source Workbooks & Domain Inspector")
    selected_part = st.selectbox("Select Particulars / Variable to Inspect:", list(all_detail_sheets_dict.keys()))
    
    matched_dict = all_detail_sheets_dict[selected_part]
    if matched_dict:
        for s_name, s_df in matched_dict.items():
            st.markdown(f"**Source Sheet:** `{s_name}` ({len(s_df)} rows total)")
            st.data_editor(s_df, num_rows="dynamic", use_container_width=True, key=f"insp_{selected_part}_{s_name}")
    else:
        st.info(f"Showing all loaded reference sheets for {selected_part}:")
        for s_name, s_df in list(sheets.items())[:2]:
            st.markdown(f"**Reference Sheet:** `{s_name}` ({len(s_df)} rows total)")
            st.data_editor(s_df, num_rows="dynamic", use_container_width=True, key=f"ref_{selected_part}_{s_name}")

with tab3:
    st.subheader("📄 Executive Narrative Report & Boardroom PPT Outline")
    
    narrative_text = f"""
====================================================================================
COMMERCIAL BANKING PERFORMANCE REPORT | PERIOD: {reporting_period}
====================================================================================

1. EXECUTIVE SUMMARY MATRIX
   ---------------------------------------------------------------------------------
   • Summary table successfully calculated via column-wise detail summation.
   • Position As of August 31, 2026 computed precisely as June 30 Position + YTD Actual.

====================================================================================
CERTIFIED BY EXECUTIVE PULSE AI | ENTERPRISE BANKING INTELLIGENCE
====================================================================================
"""

    ppt_outline = f"""
SLIDE 1: INSTITUTIONAL PERFORMANCE MATRIX ({reporting_period})
- Standardized Particulars Breakdown (ATM, Mobile, POS, QR, Customer Base, Balance Sheet).
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
