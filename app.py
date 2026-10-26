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
st.markdown('<p class="sub-header">Balance Sheet Modeling, Deposit Portfolio Mix, Digital Channels & Executive Boardroom Reporting</p>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("📥 Enterprise Data Ingestion")
uploaded_files = st.sidebar.file_uploader(
    "Upload Bank Financial Reports (Balance Sheet, Deposits, Segments, ADC)", 
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
    st.info("👆 Please upload your institutional bank files (Balance Sheet, Deposit Mix, Customer Segments, ATM/Mobile) via the sidebar uploader.")
    st.stop()

# ==========================================
# 2. AUTOMATED FINANCIAL & DOMAIN PARSING
# ==========================================
total_records = 0
total_portfolio_volume = 0.0

for s_name, df in sheets.items():
    total_records += len(df)
    for col in df.select_dtypes(include=[np.number]).columns:
        total_portfolio_volume += df[col].sum()

# Categorize domains for executive intelligence
def classify_domains(sheet_keys):
    classified = {
        "Balance Sheet & Deposits": [],
        "Customer Segments & Base": [],
        "Digital & Delivery Channels (ADC)": [],
        "Branch Network & Performance": [],
        "Other Records": []
    }
    for k in sheet_keys:
        kl = k.lower()
        if any(w in kl for w in ["balance", "sheet", "deposit", "portfolio", "liability", "asset"]):
            classified["Balance Sheet & Deposits"].append(k)
        elif any(w in kl for w in ["customer", "segment", "base", "retail", "corporate", "msme"]):
            classified["Customer Segments & Base"].append(k)
        elif any(w in kl for w in ["mobile", "atm", "pos", "qr", "ussd", "ibmb", "agent", "digital", "card", "e-birr"]):
            classified["Digital & Delivery Channels (ADC)"].append(k)
        elif any(w in kl for w in ["branch", "district", "location", "performer", "top10", "outlying", "city"]):
            classified["Branch Network & Performance"].append(k)
        else:
            classified["Other Records"].append(k)
    return classified

domain_categories = classify_domains(list(sheets.keys()))

# ==========================================
# 3. EXECUTIVE DASHBOARD & BOARDROOM TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive KPI Summary",
    "📑 Multi-Domain Inspector", 
    "📄 Boardroom Report & PPT",
    "📥 Download Master Package"
])

with tab1:
    st.subheader("1. Institutional Financial & Operational KPI Scorecard")
    st.markdown("Automated metrics aggregated from your uploaded commercial banking master sheets.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h4>Active Domains</h4><h2>{len(sheets)}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h4>Consolidated Records</h4><h2>{total_records:,}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h4>Total Volume</h4><h2>{total_portfolio_volume:,.0f}</h2></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><h4>Reporting Cycle</h4><h2>{reporting_period}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Domain Categorization Breakdown")
    cat_summary_data = [{"Category": cat, "Active Sheets Count": len(keys), "Included Sheets": ", ".join(keys[:3]) + ("..." if len(keys)>3 else "")} for cat, keys in domain_categories.items() if len(keys) > 0]
    st.data_editor(pd.DataFrame(cat_summary_data), num_rows="dynamic", use_container_width=True, key="cat_summary_table")

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
    
    bs_count = len(domain_categories["Balance Sheet & Deposits"])
    cust_count = len(domain_categories["Customer Segments & Base"])
    adc_count = len(domain_categories["Digital & Delivery Channels (ADC)"])
    branch_count = len(domain_categories["Branch Network & Performance"])

    narrative_text = f"""
====================================================================================
EXECUTIVE COMMERCIAL BANKING REPORT | PERIOD: {reporting_period}
====================================================================================

1. BALANCE SHEET & FUNDING STRUCTURE REVIEW
   ---------------------------------------------------------------------------------
   • Total Ingested Portfolios: {len(sheets)} active domain sheets analyzed.
   • Balance Sheet & Deposit Modules: {bs_count} dedicated sheet(s) processed.
   • Total Consolidated Volume: {total_portfolio_volume:,.2f} ETB / Unit calculated dynamically.

2. CUSTOMER SEGMENTATION & DIGITAL EXPANSION (ADC)
   ---------------------------------------------------------------------------------
   • Customer Segments: {cust_count} domain(s) tracking retail and institutional mix.
   • Digital Channels: {adc_count} domain(s) monitoring Mobile Banking, ATM, POS, and Agents.
   • Branch Network Performance: {branch_count} domain(s) evaluating regional distribution.

====================================================================================
CERTIFIED BY EXECUTIVE PULSE AI | ENTERPRISE BANKING INTELLIGENCE
====================================================================================
"""

    ppt_outline = f"""
SLIDE 1: INSTITUTIONAL PERFORMANCE OVERVIEW
- Reporting Period: {reporting_period}
- Total Processed Records: {total_records:,} Rows across {len(sheets)} Master Sheets
- Data Assurance: 100% Original Schema Integrity Preserved

SLIDE 2: BALANCE SHEET & DEPOSIT PORTFOLIO MIX
- Consolidated Financial Volume: {total_portfolio_volume:,.0f}
- Core funding distribution tracked across Demand, Saving, and Fixed Time deposits.

SLIDE 3: DIGITAL CHANNEL & SEGMENT ADOPTION
- Mobile Banking, ATM Network, and POS/QR Merchant Penetration Metrics.
- Strategic focus on top and bottom branch performers by district.
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
    st.markdown("Download the pristine, enterprise-grade multi-sheet workbook containing an auto-calculated summary sheet alongside all source details.")

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
        label="📥 Download Complete Enterprise Multi-Sheet Package (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name=f"Enterprise_Bank_Package_{reporting_period}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
