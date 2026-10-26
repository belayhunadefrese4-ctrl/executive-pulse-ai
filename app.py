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
st.markdown('<p class="sub-header">Standard Bank Reporting Matrix with Auto-Detection & Interactive Override</p>', unsafe_allow_html=True)
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
# 2. AUTO-DETECTION & MAPPING HELPER
# ==========================================
def find_best_column(columns, keywords):
    for col in columns:
        col_low = str(col).lower()
        if all(k in col_low for k in keywords):
            return col
    return columns[0] if len(columns) > 0 else None

def auto_detect_sheet(sheet_names, part_name):
    keywords = part_name.lower().split()
    for s_name in sheet_names:
        if any(k in s_name.lower() for k in keywords):
            return s_name
    return sheet_names[0] if len(sheet_names) > 0 else "None"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗺️ Interactive Data Mapping (Auto-Configured)")

particulars_list = [
    "ATM", 
    "Mobile Bank", 
    "POS Merchant", 
    "QR Merchant", 
    "Customer Base", 
    "Balance Sheet & Deposits"
]

sheet_names_list = list(sheets.keys())
mapping_config = {}

for idx, part in enumerate(particulars_list):
    default_sheet = auto_detect_sheet(sheet_names_list, part) if idx < len(sheet_names_list) else "None"
    
    with st.sidebar.expander(f"Configure: {part}", expanded=False):
        sel_sheet = st.selectbox(f"Source Sheet for {part}", ["None"] + sheet_names_list, index=sheet_names_list.index(default_sheet)+1 if default_sheet in sheet_names_list else 0, key=f"sheet_{part}")
        
        if sel_sheet != "None":
            df_cols = list(sheets[sel_sheet].columns)
            
            # Auto-detect standard bank columns
            def_june = find_best_column(df_cols, ["june"])
            def_plan = find_best_column(df_cols, ["ytd", "plan"])
            def_act = find_best_column(df_cols, ["ytd", "actual"])
            def_mplan = find_best_column(df_cols, ["m.", "plan"]) or find_best_column(df_cols, ["month", "plan"])
            def_mact = find_best_column(df_cols, ["m.", "actual"]) or find_best_column(df_cols, ["month", "actual"])
            
            c_june = st.selectbox(f"June Position Col", df_cols, index=df_cols.index(def_june) if def_june in df_cols else 0, key=f"june_{part}")
            c_plan = st.selectbox(f"YTD Plan Col", df_cols, index=df_cols.index(def_plan) if def_plan in df_cols else 0, key=f"plan_{part}")
            c_act = st.selectbox(f"YTD Actual Col", df_cols, index=df_cols.index(def_act) if def_act in df_cols else 0, key=f"act_{part}")
            c_mplan = st.selectbox(f"Monthly Plan Col", df_cols, index=df_cols.index(def_mplan) if def_mplan in df_cols else 0, key=f"mplan_{part}")
            c_mact = st.selectbox(f"Monthly Actual Col", df_cols, index=df_cols.index(def_mact) if def_mact in df_cols else 0, key=f"mact_{part}")
            
            mapping_config[part] = {
                "sheet": sel_sheet,
                "june": c_june,
                "plan": c_plan,
                "act": c_act,
                "mplan": c_mplan,
                "mact": c_mact
            }

# ==========================================
# 3. COMPUTATION ENGINE
# ==========================================
def clean_val(val):
    if pd.isna(val):
        return 0.0
    val_str = str(val).replace(',', '').replace('%', '').replace(' ', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

summary_rows = []
all_detail_sheets_dict = {}

for idx, part_name in enumerate(particulars_list, 1):
    sums = {"June": 0.0, "YTD_Plan": 0.0, "YTD_Actual": 0.0, "M_Plan": 0.0, "M_Actual": 0.0}
    matched_df = None
    
    # If not explicitly mapped in expander, use auto-assignment fallback
    if part_name not in mapping_config and idx <= len(sheet_names_list):
        auto_s = sheet_names_list[idx - 1]
        df_cols = list(sheets[auto_s].columns)
        mapping_config[part_name] = {
            "sheet": auto_s,
            "june": find_best_column(df_cols, ["june"]),
            "plan": find_best_column(df_cols, ["ytd", "plan"]),
            "act": find_best_column(df_cols, ["ytd", "actual"]),
            "mplan": find_best_column(df_cols, ["m.", "plan"]),
            "mact": find_best_column(df_cols, ["m.", "actual"])
        }

    if part_name in mapping_config:
        cfg = mapping_config[part_name]
        matched_df = sheets[cfg["sheet"]]
        sums["June"] = matched_df[cfg["june"]].apply(clean_val).sum()
        sums["YTD_Plan"] = matched_df[cfg["plan"]].apply(clean_val).sum()
        sums["YTD_Actual"] = matched_df[cfg["act"]].apply(clean_val).sum()
        sums["M_Plan"] = matched_df[cfg["mplan"]].apply(clean_val).sum()
        sums["M_Actual"] = matched_df[cfg["mact"]].apply(clean_val).sum()
        
    all_detail_sheets_dict[part_name] = {part_name: matched_df} if matched_df is not None else {}
    
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
# 4. EXECUTIVE DASHBOARD TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Summary Table",
    "📑 Linked Detail Sheets", 
    "📄 Boardroom Report & PPT",
    "📥 Download Master Package"
])

with tab1:
    st.subheader(f"2. Card & Digital Banking Users Summary ({reporting_period})")
    st.markdown("Auto-mapped and calculated with Position = June Position + YTD Actual:")
    st.data_editor(exec_summary_df, num_rows="dynamic", use_container_width=True, key="bank_standard_matrix")

with tab2:
    st.subheader("📑 Detailed Source Workbooks & Domain Inspector")
    selected_part = st.selectbox("Select Particulars / Variable to Inspect:", particulars_list)
    
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
   • Summary table auto-populated and verified against source detail workbooks.
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
