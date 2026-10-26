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
st.markdown('<p class="sub-header">Multi-Sheet Roll-up & Robust Index-Safe Engine</p>', unsafe_allow_html=True)
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
# 2. FLEXIBLE COLUMN MAPPING & ROLL-UP
# ==========================================
def clean_sum_by_keywords(df, possible_keywords):
    for col in df.columns:
        c_low = str(col).lower()
        if any(k in c_low for k in possible_keywords):
            selected = df[col]
            if isinstance(selected, pd.DataFrame):
                selected = selected.iloc[:, 0]
            cleaned = (
                selected.astype(str)
                .str.replace(',', '', regex=False)
                .str.replace('%', '', regex=False)
                .str.replace(' ', '', regex=False)
                .str.replace('-', '0', regex=False)
            )
            return float(pd.to_numeric(cleaned, errors='coerce').fillna(0.0).sum())
    return 0.0

summary_rows = []

for idx, (s_key, df) in enumerate(sheets.items()):
    if df is None or df.empty:
        continue
        
    s_june = clean_sum_by_keywords(df, ["june", "jun"])
    s_ytd_plan = clean_sum_by_keywords(df, ["ytd. plan", "ytd plan", "plan"])
    s_ytd_act = clean_sum_by_keywords(df, ["ytd. actual", "ytd actual", "ytd.act", "actual"])
    s_m_plan = clean_sum_by_keywords(df, ["m.plan", "month plan", "m plan", "monthly plan"])
    s_m_act = clean_sum_by_keywords(df, ["m. actual", "m actual", "month actual", "monthly actual"])

    if s_june == 0.0 and s_ytd_plan == 0.0:
        text_headers = ["branch", "code", "name", "district", "location", "particular", "variable", "item", "description"]
        num_cols = [c for c in df.columns if not any(t in str(c).lower() for t in text_headers) and "unnamed" not in str(c).lower()]
        if len(num_cols) > 0: s_june = clean_sum_by_keywords(df, [str(num_cols[0])])
        if len(num_cols) > 1: s_ytd_plan = clean_sum_by_keywords(df, [str(num_cols[1])])
        if len(num_cols) > 2: s_ytd_act = clean_sum_by_keywords(df, [str(num_cols[2])])
        if len(num_cols) > 3: s_m_plan = clean_sum_by_keywords(df, [str(num_cols[3])])
        if len(num_cols) > 4: s_m_act = clean_sum_by_keywords(df, [str(num_cols[4])])

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
    st.markdown("Consolidated variable totals mapped precisely into correct columns:")
    st.data_editor(exec_summary_df, num_rows="dynamic", use_container_width=True, key="bank_standard_matrix")

with tab2:
    st.subheader("📑 Detailed Source Workbooks & Domain Inspector")
    selected_sheet = st.selectbox("Select Variable Sheet to Inspect Details:", list(sheets.keys()))
    if selected_sheet in sheets:
        st.markdown(f"**Showing full branch breakdown and automated Grand Total for `{selected_sheet}`:**")
        
        detail_df = sheets[selected_sheet].copy()
        
        # Build safe positional total row for detail view (avoids duplicate index errors)
        total_list = []
        for i, c in enumerate(detail_df.columns):
            if i == 0:
                total_list.append("GRAND TOTAL")
            else:
                col_sum = clean_sum_by_keywords(detail_df, [str(c).lower()])
                total_list.append(f"{col_sum:,.0f}" if col_sum > 0 else "")
                
        detail_df.loc[len(detail_df)] = total_list
        st.data_editor(detail_df, num_rows="dynamic", use_container_width=True, key=f"insp_{selected_sheet}")

with tab3:
    st.subheader("📄 Executive Narrative Report & Boardroom PPT Outline")
    
    narrative_text = f"""
====================================================================================
COMMERCIAL BANKING PERFORMANCE REPORT | PERIOD: {reporting_period}
====================================================================================

1. EXECUTIVE SUMMARY ROLL-UP MATRIX
   ---------------------------------------------------------------------------------
   • Master summary compiled successfully with flexible keyword column matching.
   • Position As of August 31, 2026 computed precisely as June 30 Position + YTD Actual.

====================================================================================
CERTIFIED BY EXECUTIVE PULSE AI | ENTERPRISE BANKING INTELLIGENCE
====================================================================================
"""

    ppt_outline = f"""
SLIDE 1: INSTITUTIONAL PERFORMANCE ROLL-UP ({reporting_period})
- Multi-variable consolidated summary table.
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
    st.markdown("Download the fully structured Excel workbook containing the summarized master table as the first sheet.")

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
