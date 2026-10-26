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
st.markdown('<p class="sub-header">Standard Bank Reporting Matrix with True Dynamic Row Extraction</p>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("📥 Enterprise Data Ingestion")
uploaded_files = st.sidebar.file_uploader(
    "Upload Bank Financial Reports & Detail Workbooks", 
    type=["xlsx", "csv"], 
    accept_multiple_files=True
)
reporting_period = st.sidebar.selectbox("Reporting Period", ["August 2026", "Q4 2026", "Q3 2026", "Q2 2026", "Q1 2026", "Annual 2026"])

# Automated header detection parser
def load_clean_table(file, sheet_name=None):
    file.seek(0)
    if file.name.endswith('.csv'):
        df_raw = pd.read_csv(file, header=None)
    else:
        df_raw = pd.read_excel(file, sheet_name=sheet_name, header=None)
        
    df_raw = df_raw.dropna(how='all').dropna(axis=1, how='all')
    
    header_idx = 0
    for idx, row in df_raw.iterrows():
        row_str = " ".join([str(val).lower() for val in row.values if pd.notna(val)])
        if any(k in row_str for k in ["june", "jun", "ytd", "plan", "actual", "particular", "variable", "description", "item"]):
            header_idx = idx
            break
            
    headers = [str(val).strip() for val in df_raw.iloc[header_idx].values]
    df_clean = df_raw.iloc[header_idx + 1:].copy()
    df_clean.columns = headers
    return df_clean.dropna(how='all')

sheets = {}
if uploaded_files:
    try:
        for file in uploaded_files:
            file_prefix = file.name.rsplit('.', 1)[0]
            if file.name.endswith('.csv'):
                sheets[file_prefix] = load_clean_table(file)
            else:
                xls = pd.ExcelFile(file)
                for s_name in xls.sheet_names:
                    sheet_key = f"{file_prefix} -> {s_name}" if len(xls.sheet_names) > 1 else file_prefix
                    sheets[sheet_key] = load_clean_table(file, sheet_name=s_name)
        st.sidebar.success(f"✅ Loaded {len(uploaded_files)} File(s) | {len(sheets)} Active Sheet(s)")
    except Exception as e:
        st.sidebar.error(f"Error loading files: {e}")
        sheets = {}

if not sheets:
    st.info("👆 Please upload your master bank spreadsheets via the sidebar uploader.")
    st.stop()

# ==========================================
# 2. TRUE DYNAMIC ROW-LEVEL EXTRACTION ENGINE
# ==========================================
def clean_val(val):
    if pd.isna(val):
        return 0.0
    val_str = str(val).replace(',', '').replace('%', '').replace(' ', '').replace('-', '0').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

extracted_rows = []
row_counter = 1

for s_key, df in sheets.items():
    if df is None or df.empty:
        continue
        
    cols = list(df.columns)
    col_map = {str(c).lower().strip(): c for c in cols}
    
    # Identify Particulars/Description column
    part_col = next((col_map[c] for c in col_map if any(k in c for k in ["particular", "variable", "item", "description", "product", "service", "name", "type"])), None)
    if not part_col and len(cols) > 0:
        for c in cols:
            if df[c].dtype == object:
                part_col = c
                break
        if not part_col:
            part_col = cols[0]

    # Identify metric columns flexibly
    june_col = next((col_map[c] for c in col_map if "june" in c or "jun" in c), None)
    ytd_plan_col = next((col_map[c] for c in col_map if "ytd" in c and "plan" in c), None)
    ytd_act_col = next((col_map[c] for c in col_map if "ytd" in c and ("act" in c or "actual" in c)), None)
    m_plan_col = next((col_map[c] for c in col_map if any(m in c for m in ["m.", "month", "monthly"]) and "plan" in c), None)
    m_act_col = next((col_map[c] for c in col_map if any(m in c for m in ["m.", "month", "monthly"]) and ("act" in c or "actual" in c)), None)
    
    # Positional fallback for numeric columns
    numeric_cols = [c for c in cols if c != part_col and not any(w in str(c).lower() for w in ["branch", "district", "location", "code", "#", "unnamed"])]
    
    if not june_col and len(numeric_cols) > 0: june_col = numeric_cols[0]
    if not ytd_plan_col and len(numeric_cols) > 1: ytd_plan_col = numeric_cols[1]
    if not ytd_act_col and len(numeric_cols) > 2: ytd_act_col = numeric_cols[2]
    if not m_plan_col and len(numeric_cols) > 3: m_plan_col = numeric_cols[3]
    if not m_act_col and len(numeric_cols) > 4: m_act_col = numeric_cols[4]

    # Extract each individual row as a distinct variable/particular
    for idx, row in df.iterrows():
        p_name = str(row[part_col]).strip() if part_col in df.columns and pd.notna(row[part_col]) else f"Item {row_counter}"
        if not p_name or p_name.lower() in ["nan", "none", "total", "grand total", "sum", "subtotal", "overall"]:
            continue
            
        june_val = clean_val(row[june_col]) if june_col and june_col in df.columns else 0.0
        ytd_plan_val = clean_val(row[ytd_plan_col]) if ytd_plan_col and ytd_plan_col in df.columns else 0.0
        ytd_act_val = clean_val(row[ytd_act_col]) if ytd_act_col and ytd_act_col in df.columns else 0.0
        m_plan_val = clean_val(row[m_plan_col]) if m_plan_col and m_plan_col in df.columns else 0.0
        m_act_val = clean_val(row[m_act_col]) if m_act_col and m_act_col in df.columns else 0.0
        
        # Mandatory Banking Calculation Rule: Position As of August 31 = June 30 Position + YTD Actual
        position_august = june_val + ytd_act_val
        
        ytd_pct = (ytd_act_val / ytd_plan_val * 100) if ytd_plan_val > 0 else 0.0
        m_pct = (m_act_val / m_plan_val * 100) if m_plan_val > 0 else 0.0
        
        extracted_rows.append({
            "#": row_counter,
            "Particulars / variables": p_name,
            "As of June 30, 2026": f"{june_val:,.0f}" if june_val > 0 else "0",
            "YTD. Plan": f"{ytd_plan_val:,.0f}" if ytd_plan_val > 0 else "0",
            "YTD. Actual": f"{ytd_act_val:,.0f}" if ytd_act_val > 0 else "0",
            "%age": f"{ytd_pct:.0f}%" if ytd_pct > 0 else "0%",
            "M.Plan": f"{m_plan_val:,.0f}" if m_plan_val > 0 else "0",
            "M. Actual": f"{m_act_val:,.0f}" if m_act_val > 0 else "0",
            "%age.1": f"{m_pct:.0f}%" if m_pct > 0 else "0%",
            "Position As of August 31, 2026": f"{position_august:,.0f}" if position_august > 0 else "0"
        })
        row_counter += 1

if not extracted_rows:
    extracted_rows.append({
        "#": 1,
        "Particulars / variables": "No data rows found in uploaded files",
        "As of June 30, 2026": "0",
        "YTD. Plan": "0",
        "YTD. Actual": "0",
        "%age": "0%",
        "M.Plan": "0",
        "M. Actual": "0",
        "%age.1": "0%",
        "Position As of August 31, 2026": "0"
    })

exec_summary_df = pd.DataFrame(extracted_rows)
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
    st.markdown("Extracted dynamically from your uploaded file rows with Position = June Position + YTD Actual:")
    st.data_editor(exec_summary_df, num_rows="dynamic", use_container_width=True, key="bank_standard_matrix")

with tab2:
    st.subheader("📑 Detailed Source Workbooks & Domain Inspector")
    selected_sheet = st.selectbox("Select Sheet to Inspect:", list(sheets.keys()))
    if selected_sheet in sheets:
        st.data_editor(sheets[selected_sheet], num_rows="dynamic", use_container_width=True, key=f"insp_{selected_sheet}")

with tab3:
    st.subheader("📄 Executive Narrative Report & Boardroom PPT Outline")
    
    narrative_text = f"""
====================================================================================
COMMERCIAL BANKING PERFORMANCE REPORT | PERIOD: {reporting_period}
====================================================================================

1. EXECUTIVE SUMMARY MATRIX
   ---------------------------------------------------------------------------------
   • Summary table populated exclusively from uploaded source file rows.
   • Position As of August 31, 2026 computed precisely as June 30 Position + YTD Actual.

====================================================================================
CERTIFIED BY EXECUTIVE PULSE AI | ENTERPRISE BANKING INTELLIGENCE
====================================================================================
"""

    ppt_outline = f"""
SLIDE 1: INSTITUTIONAL PERFORMANCE MATRIX ({reporting_period})
- Dynamic breakdown extracted from ingested workbooks.
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
