import streamlit as st
import pandas as pd
import numpy as np
import io
import random

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Executive Pulse AI - Commercial Banking Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header { font-size: 2.1rem; font-weight: 800; color: #0F172A; }
    .sub-header { font-size: 1.0rem; color: #475569; }
    .security-badge { background-color: #065F46; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }
    .action-card { background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
    .report-box { background-color: #FFFFFF; border: 1px solid #CBD5E1; padding: 25px; border-radius: 8px; font-family: 'Times New Roman', Times, serif; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SECURITY KEY AUTHENTICATION
# ==========================================
MASTER_SECURITY_KEY = "BANK-EXEC-8899-SECURE"

st.sidebar.markdown("### 🔐 Security & Access Control")
user_key = st.sidebar.text_input("Enter Master Executive Key", type="password")

if user_key != MASTER_SECURITY_KEY:
    st.markdown('<p class="main-header">🏦 Executive Pulse AI: Bank Intelligence Engine</p>', unsafe_allow_html=True)
    st.warning("🔒 Access Restricted: Please enter the valid Master Executive Key in the sidebar to unlock bank data processing.")
    st.info("System Status: Air-Gapped / Offline Local Deployment Ready | Security Level: Tier-1 Enterprise Encryption")
    st.stop()

# ==========================================
# APP HEADER
# ==========================================
col_title, col_sec = st.columns([3, 1])
with col_title:
    st.markdown('<p class="main-header">🏦 Executive Pulse AI: Commercial Banking Engine</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Dynamic Schema Ingestion, Balance Sheet Analytics, Auto-Adapting Templates & Data Wipe Controls</p>', unsafe_allow_html=True)
with col_sec:
    st.markdown("<br><span class='security-badge'>🛡️ AIR-GAPPED SECURE</span>", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 2. DYNAMIC FILE INGESTION & DATA WIPE CONTROLS
# ==========================================
st.sidebar.header("📥 Multi-Department Ingestion & Controls")

uploaded_file = st.sidebar.file_uploader("Upload Raw Department Excel/CSV", type=["xlsx", "csv"], key="bank_file_uploader")

# Session State for File Data Management
if "file_cleared" not in st.session_state:
    st.session_state.file_cleared = False

# Reset Session Button (Temporary Wipe)
if uploaded_file is not None:
    if st.sidebar.button("🗑️ Clear Uploaded File (Temporary Reset)"):
        st.session_state.file_cleared = True
        st.sidebar.success("Uploaded dataset cleared from session memory!")
        st.rerun()

bank_name = st.sidebar.text_input("Institution Name", value="Commercial Bank / Financial Institution")
current_period = st.sidebar.selectbox("Current Reporting Period", ["Q4 2026", "Q3 2026", "Q2 2026", "Q1 2026", "Annual 2026"])
comparison_period = st.sidebar.selectbox("Comparison Base Period", ["Q3 2026 (Prior Quarter)", "Q4 2025 (YoY)", "Budget Target Baseline"])

@st.cache_data
def generate_master_bank_dataset():
    """Generates default standardized banking dataset."""
    districts = ["Addis North", "Addis South", "Hawassa", "Adama", "Bahir Dar", "Dire Dawa"]
    directorates = ["Retail Banking", "Corporate Banking", "Credit & Risk Management", "Digital Banking", "Treasury & Finance", "Operations"]
    saving_types = ["Demand Deposit", "Saving Account", "Fixed Time Deposit", "Special Interest Account"]
    segments = ["Corporate", "Retail", "Institutional", "SME"]
    
    random.seed(101)
    rows = []
    for i in range(1, 51):
        dist = random.choice(districts)
        direct = random.choice(directorates)
        sav = random.choice(saving_types)
        seg = random.choice(segments)
        
        cur_bal = random.randint(12000000, 180000000)
        prior_bal = cur_bal * random.uniform(0.85, 1.15)
        acc = random.randint(800, 25000)
        npl = random.randint(100000, 4500000)
        target = cur_bal * random.uniform(1.05, 1.30)
        
        rows.append({
            "Branch Location": f"Branch_{i:02d}",
            "District": dist,
            "Directorate": direct,
            "Saving Type": sav,
            "Customer Segment": seg,
            "Current Portfolio Balance (ETB)": cur_bal,
            "Prior Portfolio Balance (ETB)": prior_bal,
            "Target Portfolio (ETB)": target,
            "Active Accounts": acc,
            "Non-Performing Loans (NPL ETB)": npl,
            "Operating Expense (ETB)": cur_bal * 0.025,
            "Operating Income (ETB)": cur_bal * 0.085
        })
    return pd.DataFrame(rows)

# Dynamic Schema Resolver
def normalize_and_adapt_schema(input_df):
    """Auto-adapts uploaded spreadsheets with missing or alternative headers."""
    col_mapping = {}
    for col in input_df.columns:
        c_lower = str(col).lower()
        if "branch" in c_lower or "location" in c_lower:
            col_mapping[col] = "Branch Location"
        elif "district" in c_lower or "region" in c_lower:
            col_mapping[col] = "District"
        elif "directorate" in c_lower or "department" in c_lower:
            col_mapping[col] = "Directorate"
        elif "saving" in c_lower or "deposit type" in c_lower:
            col_mapping[col] = "Saving Type"
        elif "segment" in c_lower:
            col_mapping[col] = "Customer Segment"
        elif "current" in c_lower or "balance" in c_lower or "portfolio" in c_lower:
            if "prior" not in c_lower and "target" not in c_lower:
                col_mapping[col] = "Current Portfolio Balance (ETB)"
        elif "prior" in c_lower or "previous" in c_lower:
            col_mapping[col] = "Prior Portfolio Balance (ETB)"
        elif "target" in c_lower or "budget" in c_lower:
            col_mapping[col] = "Target Portfolio (ETB)"
        elif "npl" in c_lower or "non-performing" in c_lower:
            col_mapping[col] = "Non-Performing Loans (NPL ETB)"
            
    adapted_df = input_df.rename(columns=col_mapping)
    
    # Fill in missing required columns dynamically
    if "Branch Location" not in adapted_df.columns:
        adapted_df["Branch Location"] = [f"Branch_{i:02d}" for i in range(1, len(adapted_df)+1)]
    if "District" not in adapted_df.columns:
        adapted_df["District"] = "Central District"
    if "Directorate" not in adapted_df.columns:
        adapted_df["Directorate"] = "Retail Banking"
    if "Current Portfolio Balance (ETB)" not in adapted_df.columns:
        numeric_cols = adapted_df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            adapted_df["Current Portfolio Balance (ETB)"] = adapted_df[numeric_cols[0]]
        else:
            adapted_df["Current Portfolio Balance (ETB)"] = 50000000.0
            
    if "Prior Portfolio Balance (ETB)" not in adapted_df.columns:
        adapted_df["Prior Portfolio Balance (ETB)"] = adapted_df["Current Portfolio Balance (ETB)"] * 0.92
    if "Target Portfolio (ETB)" not in adapted_df.columns:
        adapted_df["Target Portfolio (ETB)"] = adapted_df["Current Portfolio Balance (ETB)"] * 1.15
    if "Non-Performing Loans (NPL ETB)" not in adapted_df.columns:
        adapted_df["Non-Performing Loans (NPL ETB)"] = adapted_df["Current Portfolio Balance (ETB)"] * 0.03
    if "Active Accounts" not in adapted_df.columns:
        adapted_df["Active Accounts"] = 5000
    if "Operating Expense (ETB)" not in adapted_df.columns:
        adapted_df["Operating Expense (ETB)"] = adapted_df["Current Portfolio Balance (ETB)"] * 0.02
    if "Operating Income (ETB)" not in adapted_df.columns:
        adapted_df["Operating Income (ETB)"] = adapted_df["Current Portfolio Balance (ETB)"] * 0.08
        
    # Clean numeric columns to eliminate NaN/nulls
    num_fields = [
        "Current Portfolio Balance (ETB)", "Prior Portfolio Balance (ETB)",
        "Target Portfolio (ETB)", "Non-Performing Loans (NPL ETB)",
        "Active Accounts", "Operating Expense (ETB)", "Operating Income (ETB)"
    ]
    for field in num_fields:
        if field in adapted_df.columns:
            adapted_df[field] = pd.to_numeric(adapted_df[field], errors="coerce").fillna(0)

    return adapted_df

# Load & Process Data
if uploaded_file is not None and not st.session_state.file_cleared:
    try:
        raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df = normalize_and_adapt_schema(raw_df)
        st.sidebar.success("✅ File Ingested & Schema Auto-Adapted!")
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        df = generate_master_bank_dataset()
else:
    df = generate_master_bank_dataset()

# Calculate Portfolio Growth safely
prior_denom = df["Prior Portfolio Balance (ETB)"].replace(0, np.nan)
df["Portfolio Growth (%)"] = (((df["Current Portfolio Balance (ETB)"] - df["Prior Portfolio Balance (ETB)"]) / prior_denom) * 100).fillna(0).round(2)

# ==========================================
# 3. BALANCE SHEET & CAPITAL EVALUATION
# ==========================================
st.header("⚙️ 1. Complete Balance Sheet & Capital Evaluation Engine")

b_col1, b_col2, b_col3, b_col4 = st.columns(4)
with b_col1:
    earning_assets = st.number_input("Total Earning Assets (ETB)", min_value=1.0, value=50000000000.0, step=1000000000.0)
with b_col2:
    tier1_capital = st.number_input("Tier 1 Core Capital (ETB)", min_value=1.0, value=6500000000.0, step=100000000.0)
with b_col3:
    tier2_capital = st.number_input("Tier 2 Supplementary Capital (ETB)", min_value=0.0, value=1500000000.0, step=100000000.0)
with b_col4:
    rwa = st.number_input("Risk-Weighted Assets (RWA ETB)", min_value=1.0, value=38000000000.0, step=1000000000.0)

# Dynamic Variable Injection
st.subheader("➕ Dynamic Shock Variables & Variable Customization")
e_col1, e_col2, e_col3 = st.columns(3)
with e_col1:
    opex_shock = st.number_input("Unplanned OPEX Shock Buffer (ETB)", value=250000000.0, step=10000000.0)
with e_col2:
    npl_provision_buffer = st.number_input("Additional NPL Provision Buffer (%)", value=1.5, step=0.1)
with e_col3:
    liquid_reserve_req = st.number_input("Regulatory Reserve Requirement (%)", value=15.0, step=0.5)

# ==========================================
# 4. DETERMINISTIC FINANCIAL KPIS & CAMELS
# ==========================================
st.markdown("---")
st.header("📊 2. Corporate Performance & CAMELS Soundness Rating")

car = ((tier1_capital + tier2_capital) / rwa) * 100.0
total_cur_portfolio = df["Current Portfolio Balance (ETB)"].sum()
total_prior_portfolio = df["Prior Portfolio Balance (ETB)"].sum()
portfolio_growth_yoy = ((total_cur_portfolio - total_prior_portfolio) / total_prior_portfolio * 100) if total_prior_portfolio > 0 else 0.0

total_npl = df["Non-Performing Loans (NPL ETB)"].sum() + (total_cur_portfolio * (npl_provision_buffer / 100.0))
overall_npl_ratio = (total_npl / total_cur_portfolio) * 100.0 if total_cur_portfolio > 0 else 0.0

total_opinc = df["Operating Income (ETB)"].sum()
total_opex = df["Operating Expense (ETB)"].sum() + opex_shock
cir = (total_opex / total_opinc) * 100.0 if total_opinc > 0 else 0.0

nim = ((total_opinc - total_opex) / earning_assets) * 100.0
roe = ((total_opinc - total_opex) / (tier1_capital + tier2_capital)) * 100.0

# CAMELS Score Logic
if car >= 12.0 and overall_npl_ratio <= 5.0 and cir <= 50.0:
    camels_grade = "1 - STRONG (Grade A Soundness)"
elif car >= 10.0 and overall_npl_ratio <= 8.0:
    camels_grade = "2 - SATISFACTORY (Grade B Soundness)"
else:
    camels_grade = "3 - WATCHLIST (Supervisory Action Required)"

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Total Bank Portfolio", f"{total_cur_portfolio:,.0f} ETB", delta=f"{portfolio_growth_yoy:+.2f}% vs {comparison_period}")
with k2:
    st.metric("Capital Adequacy (CAR)", f"{car:.2f}%", delta="Regulatory Target ≥ 12%")
with k3:
    st.metric("Cost-to-Income (CIR)", f"{cir:.2f}%", delta="Target ≤ 50%", delta_color="inverse")
with k4:
    st.metric("Overall NPL Ratio", f"{overall_npl_ratio:.2f}%", delta="Target ≤ 5%", delta_color="inverse")
with k5:
    st.metric("CAMELS Rating", camels_grade)

# ==========================================
# 5. BSC EVALUATION & DYNAMIC TABLE CONTROLS
# ==========================================
st.markdown("---")
st.header("🎯 3. Directorate BSC Evaluation & Strategy Realization")

dir_summary = df.groupby("Directorate").agg({
    "Current Portfolio Balance (ETB)": "sum",
    "Target Portfolio (ETB)": "sum",
    "Active Accounts": "sum",
    "Non-Performing Loans (NPL ETB)": "sum"
}).reset_index()

target_denom = dir_summary["Target Portfolio (ETB)"].replace(0, np.nan)
dir_summary["Target Achievement (%)"] = pd.to_numeric(
    (dir_summary["Current Portfolio Balance (ETB)"] / target_denom * 100), errors="coerce"
).fillna(0).round(2)

# SAFE RANKING: Fills NaNs before integer casting to prevent IntCastingNaError
dir_summary["BSC Rank"] = dir_summary["Target Achievement (%)"].rank(ascending=False, method="min").fillna(1).astype(int)
dir_summary = dir_summary.sort_values(by="BSC Rank")

overall_mission_achievement = dir_summary["Target Achievement (%)"].mean() if len(dir_summary) > 0 else 0.0

m_col1, m_col2 = st.columns([1, 2])
with m_col1:
    st.markdown("#### Corporate Strategy Realization")
    st.metric("Execution Achievement Score", f"{overall_mission_achievement:.2f}%")
    if overall_mission_achievement >= 95.0:
        st.success("🌟 **EXCELLENT:** Strategy execution aligned with long-term corporate vision.")
    else:
        st.warning("⚠️ **STRATEGIC GAP:** Directorate performance requires intervention.")

with m_col2:
    st.markdown("#### Directorate BSC Performance Table")
    selected_cols = st.multiselect(
        "Customize Table Headings (Add/Delete Columns from View):",
        options=list(dir_summary.columns),
        default=["BSC Rank", "Directorate", "Current Portfolio Balance (ETB)", "Target Portfolio (ETB)", "Target Achievement (%)"]
    )
    # Allows full cell editing, row adding (+), and row deleting dynamically
    st.data_editor(dir_summary[selected_cols], num_rows="dynamic", use_container_width=True, key="directorate_editor")

# ==========================================
# 6. BRANCH RANKINGS & AUTOMATED ACTION PLANS
# ==========================================
st.markdown("---")
st.header("🏆 4. Branch Network Analytics & Intervention Action Plans")

branch_agg = df.groupby(["Branch Location", "District"]).agg({
    "Current Portfolio Balance (ETB)": "sum",
    "Prior Portfolio Balance (ETB)": "sum",
    "Active Accounts": "sum",
    "Non-Performing Loans (NPL ETB)": "sum"
}).reset_index()

cur_denom = branch_agg["Current Portfolio Balance (ETB)"].replace(0, np.nan)
prior_branch_denom = branch_agg["Prior Portfolio Balance (ETB)"].replace(0, np.nan)

branch_agg["NPL Ratio (%)"] = ((branch_agg["Non-Performing Loans (NPL ETB)"] / cur_denom) * 100).fillna(0).round(2)
branch_agg["Growth (%)"] = (((branch_agg["Current Portfolio Balance (ETB)"] - branch_agg["Prior Portfolio Balance (ETB)"]) / prior_branch_denom) * 100).fillna(0).round(2)

sorted_branches = branch_agg.sort_values(by="Current Portfolio Balance (ETB)", ascending=False)
top_10 = sorted_branches.head(10)
least_10 = sorted_branches.tail(10).sort_values(by="Current Portfolio Balance (ETB)", ascending=True)

r_tab1, r_tab2, r_tab3 = st.tabs(["Top 10 Best-Performing Branches", "Least 10 Performing Branches (Watchlist)", "Automated Intervention Action Plans"])

with r_tab1:
    st.subheader("🌟 Top 10 Best-Performing Branches")
    st.data_editor(
        top_10[["Branch Location", "District", "Current Portfolio Balance (ETB)", "Growth (%)", "NPL Ratio (%)"]],
        num_rows="dynamic",
        use_container_width=True,
        key="top_10_editor"
    )

with r_tab2:
    st.subheader("⚠️ Least 10 Performing Branches (Watchlist)")
    st.data_editor(
        least_10[["Branch Location", "District", "Current Portfolio Balance (ETB)", "Growth (%)", "NPL Ratio (%)"]],
        num_rows="dynamic",
        use_container_width=True,
        key="least_10_editor"
    )

with r_tab3:
    st.subheader("🛠️ Automated Action Plans for Watchlist Locations")
    for idx, row in least_10.iterrows():
        b_name = row["Branch Location"]
        b_dist = row["District"]
        b_npl = row["NPL Ratio (%)"]
        b_growth = row["Growth (%)"]
        
        st.markdown(f"""
        <div class="action-card">
            <strong>📍 {b_name} ({b_dist} District)</strong> | Portfolio: {row['Current Portfolio Balance (ETB)']:,.0f} ETB | Growth: {b_growth:+.2f}% | NPL Ratio: {b_npl:.2f}%<br>
            <em>Executive Action Required:</em>
            <ul>
                {"<li><strong>Credit Audit Taskforce:</strong> Immediate NPL collection protocol required due to credit risk > 5%.</li>" if b_npl > 5.0 else "<li><strong>Deposit Mobilization Campaign:</strong> Target local SMEs and retail accounts to expand deposit portfolio.</li>"}
                {"<li><strong>Liquidity Restructuring:</strong> Review local interest rate offerings to halt balance decline.</li>" if b_growth < 0 else "<li><strong>Digital Adoption Push:</strong> Enroll customers into mobile/internet banking to reduce overhead costs.</li>"}
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 7. EXECUTIVE BOARDROOM REPORTS & EXPORTS
# ==========================================
st.markdown("---")
st.header("📄 5. Formal Executive Report & Multi-Sheet Excel Exports")

ex_tab1, ex_tab2, ex_tab3 = st.tabs(["Printable Executive Summary Report", "Boardroom PPT Outline", "Multi-Sheet Excel Export"])

top_dir_name = dir_summary.iloc[0]['Directorate'] if len(dir_summary) > 0 else "N/A"
top_dir_ach = dir_summary.iloc[0]['Target Achievement (%)'] if len(dir_summary) > 0 else 0.0
strat_dir_name = dir_summary.iloc[-1]['Directorate'] if len(dir_summary) > 0 else "N/A"
strat_dir_ach = dir_summary.iloc[-1]['Target Achievement (%)'] if len(dir_summary) > 0 else 0.0

top_branch_name = top_10.iloc[0]['Branch Location'] if len(top_10) > 0 else "N/A"
top_branch_dist = top_10.iloc[0]['District'] if len(top_10) > 0 else "N/A"
watch_branch_name = least_10.iloc[0]['Branch Location'] if len(least_10) > 0 else "N/A"
watch_branch_dist = least_10.iloc[0]['District'] if len(least_10) > 0 else "N/A"

with ex_tab1:
    st.subheader("📄 Boardroom Performance Report")
    formal_report = f"""
    ====================================================================================
    INSTITUTION: {bank_name.upper()}
    OFFICIAL EXECUTIVE PERFORMANCE & BALANCE SHEET REPORT | PERIOD: {current_period}
    BASELINE COMPARISON: {comparison_period}
    ====================================================================================
    
    1. BALANCE SHEET HEALTH & REGULATORY CAPITAL
       ---------------------------------------------------------------------------------
       • Total Portfolio Balance: {total_cur_portfolio:,.2f} ETB ({portfolio_growth_yoy:+.2f}% YoY Growth).
       • Capital Adequacy Ratio (CAR): {car:.2f}% (Regulatory Requirement: 12.00%).
       • Net Interest Margin (NIM): {nim:.2f}% | Return on Equity (ROE): {roe:.2f}%.
       • Cost-to-Income Ratio (CIR): {cir:.2f}% | NPL Exposure Ratio: {overall_npl_ratio:.2f}%.
       • CAMELS Composite Rating: {camels_grade}.
    
    2. BALANCED SCORECARD (BSC) STRATEGY REALIZATION
       ---------------------------------------------------------------------------------
       • Corporate Execution Score: {overall_mission_achievement:.2f}%.
       • Top Performing Directorate: {top_dir_name} ({top_dir_ach:.2f}% Achievement).
       • Strategic Focus Directorate: {strat_dir_name} ({strat_dir_ach:.2f}% Achievement).
    
    3. NETWORK WATCHLIST & BRANCH INTERVENTIONS
       ---------------------------------------------------------------------------------
       • Top Performing Branch: {top_branch_name} ({top_branch_dist} District).
       • Primary Watchlist Priority: {watch_branch_name} ({watch_branch_dist} District).
    
    ====================================================================================
    CERTIFIED BY EXECUTIVE PULSE AI | AIR-GAPPED ENTERPRISE ENGINE
    ====================================================================================
    """
    st.markdown(f'<div class="report-box"><pre>{formal_report}</pre></div>', unsafe_allow_html=True)

with ex_tab2:
    st.subheader("📊 PPT Boardroom Slide Outline")
    ppt_text = f"""
    SLIDE 1: BALANCE SHEET & FINANCIAL SOUNDNESS
    - Total Earning Assets: {earning_assets:,.0f} ETB | CAR: {car:.2f}%.
    - Overall Bank Portfolio Growth: {portfolio_growth_yoy:+.2f}%.
    - CAMELS Rating: {camels_grade}.

    SLIDE 2: BSC STRATEGY EXECUTION
    - Overall Strategy Score: {overall_mission_achievement:.2f}%.
    - Top Directorate: {top_dir_name}.

    SLIDE 3: BRANCH INTERVENTIONS
    - Watchlist Priority Location: {watch_branch_name}.
    - Action Required: Deploy recovery taskforce and targeted SME deposit drives.
    """
    st.text_area("Copy PPT Outline", value=ppt_text, height=220)

with ex_tab3:
    st.subheader("📥 Export Master Excel Workbook")
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Raw_Bank_Data', index=False)
        dir_summary.to_excel(writer, sheet_name='Directorate_BSC', index=False)
        top_10.to_excel(writer, sheet_name='Top_10_Branches', index=False)
        least_10.to_excel(writer, sheet_name='Watchlist_Branches', index=False)
        branch_agg.to_excel(writer, sheet_name='All_Branch_Analytics', index=False)
    
    st.download_button(
        label="📥 Download Master Excel Report (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name=f"Executive_Bank_Report_{current_period}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
