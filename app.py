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
st.markdown('<p class="sub-header">Multi-Sheet Roll-up & Robust Vectorized Extraction Engine</p>', unsafe_allow_html=True)
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
        if any(k in row_str for k in ["june", "jun", "ytd", "plan", "actual", "branch", "district", "location"]):
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
# 2. VECTORIZED SUM & COLUMN MAPPING ENGINE
# ==========================================
def sum_column(df, col):
    if not col or col not in df.columns:
        return 0.0
    cleaned = (
        df[col]
        .astype(str)
        .str.replace(',', '', regex=False)
        .str.replace('%', '', regex=False)
        .str.replace(' ', '', regex=False)
        .str.replace('-', '0', regex=False)
    )
    return float(pd.to_numeric(cleaned, errors='coerce').fillna(0.0).sum())

summary_rows = []

for idx, (s_key, df) in enumerate(sheets.items()):
    if df is None or df.empty:
        continue
        
    cols = list(df.columns)
    col_map = {str(c).lower().strip(): c for c in cols}
    
    # Identify explicit metric columns by keywords
    june_col = next((col_map[c] for c in col_map if "june" in c or "jun" in c), None)
    ytd_plan_col = next((col_map[c] for c in col_map if "ytd" in c and "plan" in c), None)
    ytd_act_col = next((col_map[c] for c in col_map if "ytd" in c and ("act" in c or "actual" in c)), None)
    m_plan_col = next((col_map[c] for c in col_map if any(m in c for m in ["m.", "month", "monthly"]) and "plan" in c), None)
    m_act_col = next((col_map[c] for c in col_map if any(m in c for m in ["m.", "month", "monthly"]) and ("act" in c or "actual" in c)), None)
    
    # Filter out text/metadata columns
    text_headers = ["branch", "code", "name", "district", "location", "particular", "variable", "item", "description"]
    numeric_cols = [c for c in cols if not any(t in str(c).lower() for t in text_headers) and "unnamed" not in str(c).lower()]

    # Positional fallback if keyword lookup fails
    if not june_col and len(numeric_cols) > 0: june_col = numeric_cols[0]
    if not ytd_plan_col and len(numeric_cols) > 1: ytd_plan_col = numeric_cols[1]
    if not ytd_act_col and len(numeric_cols) > 2: ytd_act_col = numeric_cols[2]
    if not m_plan_col and len(numeric_cols) > 3: m_plan_col = numeric_cols[3]
    if not m_act_col and len(numeric_cols) > 4: m_act_col = numeric_cols[4]

    # Calculate exact sums for each metric column using vectorized parsing
    s_june = sum_column(df, june_col)
    s_ytd_plan = sum_column(df, ytd_plan_col)
    s_ytd_act = sum_column(df, ytd_act_col)
    s_m_plan = sum_column(df, m_plan_col)
    s_m_act = sum_column(df, m_act_col)

    # Mandatory Banking Calculation Rule: Position As of August 31 = June 30 Position + YTD Actual
    position_august = s_june + s_ytd_act
    ytd_pct = (s_ytd_act / s_ytd_plan * 100) if s_ytd_plan > 0 else 0.0
    m_pct = (s_m_act / s_m_plan * 100) if s_m_plan > 0 else 0.0

    var_name = s_key.split(" -> ")[-1].replace(".xlsx", "").replace(".csv", "")

    summary_rows.append({
        "#": idx + 1,
        "Particulars / variables": var_name,
        "As of June 30, 2026": f"{s_june:,.0f}",
        "YTD. Plan": f"{s_ytd_plan:,.0f}",
        "YTD. Actual": f"{s_ytd_act:,.0f}",
        "%age": f"{ytd_pct:.1f}%",
        "M.Plan": f"{s_m_plan:,.0f}",
        "M. Actual": f"{s_m_act:,.0f}",
        "%age.1": f"{m_pct:.1f}%",
        "Position As of August 31, 2026": f"{position_august:,.0f}"
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
    st.subheader(f"Executive Summary Roll-up ({reporting_period})")
    st.markdown("Consolidated variable totals aligned accurately into the standard matrix:")
    st.data_editor(exec_summary_df, num_rows="dynamic", use_container_width=True, key="bank_standard_matrix")

with tab2:
    st.subheader("📑 Detailed Source Workbooks & Domain Inspector")
    selected_sheet = st.selectbox("Select Variable Sheet to Inspect Details:", list(sheets.keys()))
    if selected_sheet in sheets:
        st.markdown(f"**Showing full branch breakdown and automated Grand Total for `{selected_sheet}`:**")
        
        detail_df = sheets[selected_sheet].copy()
        
        # Build automated Grand Total row for the
