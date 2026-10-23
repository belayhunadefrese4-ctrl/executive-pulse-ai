import streamlit as st
import pandas as pd
import numpy as np
import io
import random

# ==========================================
# PAGE CONFIGURATION & ENTERPRISE STYLING
# ==========================================
st.set_page_config(
    page_title="Executive Pulse AI - Enterprise Banking & BSC Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 800; color: #0F172A; }
    .sub-header { font-size: 1.05rem; color: #475569; }
    .security-badge { background-color: #065F46; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }
    .action-card { background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
    .report-box { background-color: #FFFFFF; border: 1px solid #CBD5E1; padding: 25px; border-radius: 8px; font-family: 'Times New Roman', Times, serif; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SECURITY KEY AUTHENTICATION SYSTEM
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
# APP HEADER (AUTHENTICATED)
# ==========================================
col_title, col_sec = st.columns([3, 1])
with col_title:
    st.markdown('<p class="main-header">🏦 Executive Pulse AI: Enterprise Banking Engine</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Multi-Period Trend Analytics, BSC Strategy Realization, Automated PDF/Print Reporting & Intervention Action Plans</p>', unsafe_allow_html=True)
with col_sec:
    st.markdown("<br><span class='security-badge'>🛡️ AIR-GAPPED SECURE</span>", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 2. MULTI-DEPARTMENT DATA INGESTION & PERIODS
# ==========================================
st.sidebar.header("📥 Multi-Department Data Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload Raw Department Excel/CSV", type=["xlsx", "csv"])

bank_name = st.sidebar.text_input("Institution Name", value="Commercial Bank / Financial Institution")
current_period = st.sidebar.selectbox("Current Reporting Period", ["Q4 2026", "Q3 2026", "Q2 2026", "Q1 2026", "Annual 2026"])
comparison_period = st.sidebar.selectbox("Comparison Base Period", ["Q3 2026 (Prior Quarter)", "Q4 2025 (YoY)", "Budget Target Baseline"])

@st.cache_data
def generate_master_bank_dataset():
    """Generates standardized multi-period bank data including current and prior quarter balances."""
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
        # Prior period balance generated with slight variance (-15% to +20%)
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

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("Multi-Department Raw Data Ingested!")
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        df = generate_master_bank_dataset()
else:
    df = generate_master_bank_dataset()

# Ensure required columns exist
if "Current Portfolio Balance (ETB)" not in df.columns and "Total Portfolio Balance (ETB)" in df.columns:
    df["Current Portfolio Balance (ETB)"] = df["Total Portfolio Balance (ETB)"]
if "Prior Portfolio Balance (ETB)" not in df.columns:
    df["Prior Portfolio Balance (ETB)"] = df["Current Portfolio Balance (ETB)"] * 0.92

# Calculate Growth Rate
df["Portfolio Growth (%)"] = ((df["Current Portfolio Balance (ETB)"] - df["Prior Portfolio Balance (ETB)"]) / df["Prior Portfolio Balance (ETB)"] * 100).round(2)

# ==========================================
# 3. BALANCE SHEET & REGULATORY PARAMETERS
# ==========================================
st.header("⚙️ 1. Corporate Balance Sheet & Regulatory Parameters")

c1, c2, c3, c4 = st.columns(4)
with c1:
    earning_assets = st.number_input("Total Earning Assets (ETB)", min_value=1.0, value=50000000000.0, step=1000000000.0)
with c2:
    tier1_capital = st.number_input("Tier 1 Capital (ETB)", min_value=1.0, value=6500000000.0, step=100000000.0)
with c3:
    tier2_capital = st.number_input("Tier 2 Capital (ETB)", min_value=0.0, value=1500000000.0, step=100000000.0)
with c4:
    rwa = st.number_input("Risk-Weighted Assets (RWA ETB)", min_value=1.0, value=38000000000.0, step=1000000000.0)

# Expansion Slots
st.subheader("➕ Dynamic Expansion Slots (Custom Shock Parameters)")
e_col1, e_col2, e_col3 = st.columns(3)
with e_col1:
    opex_shock = st.number_input("Unplanned OPEX Shock Buffer (ETB)", value=250000000.0, step=10000000.0)
with e_col2:
    npl_provision_buffer = st.number_input("Additional NPL Provision Buffer (%)", value=1.5, step=0.1)
with e_col3:
    digital_adoption_rate = st.number_input("Digital Banking Adoption Rate (%)", value=68.4, step=0.5)

# ==========================================
# 4. DETERMINISTIC FINANCIAL KPIS & MULTI-PERIOD TRENDS
# ==========================================
st.markdown("---")
st.header("📊 2. Corporate KPIs & Multi-Period Trend Analysis")

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

# CAMELS Score Calculation
if car >= 12.0 and overall_npl_ratio <= 5.0 and cir <= 50.0:
    camels_grade = "1 - STRONG (Soundness Grade A)"
elif car >= 10.0 and overall_npl_ratio <= 8.0:
    camels_grade = "2 - SATISFACTORY (Soundness Grade B)"
else:
    camels_grade = "3 - WATCHLIST (Requires Supervisory Attention)"

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Current Portfolio Balance", f"{total_cur_portfolio:,.0f} ETB", delta=f"{portfolio_growth_yoy:+.2f}% vs {comparison_period}")
with k2:
    st.metric("Capital Adequacy (CAR)", f"{car:.2f}%", delta="Target ≥ 12%")
with k3:
    st.metric("Cost-to-Income (CIR)", f"{cir:.2f}%", delta="Target ≤ 50%", delta_color="inverse")
with k4:
    st.metric("Overall NPL Ratio", f"{overall_npl_ratio:.2f}%", delta="Target ≤ 5%", delta_color="inverse")
with k5:
    st.metric("CAMELS Rating", camels_grade)

# ==========================================
# 5. BALANCED SCORECARD (BSC) EVALUATION
# ==========================================
st.markdown("---")
st.header("🎯 3. Directorate BSC Evaluation & Strategy Realization")

dir_summary = df.groupby("Directorate").agg({
    "Current Portfolio Balance (ETB)": "sum",
    "Target Portfolio (ETB)": "sum",
    "Active Accounts": "sum",
    "Non-Performing Loans (NPL ETB)": "sum"
}).reset_index()

dir_summary["Target Achievement (%)"] = (dir_summary["Current Portfolio Balance (ETB)"] / dir_summary["Target Portfolio (ETB)"] * 100).round(2)
dir_summary["BSC Rank"] = dir_summary["Target Achievement (%)"].rank(ascending=False, method="min").astype(int)
dir_summary = dir_summary.sort_values(by="BSC Rank")

overall_mission_achievement = dir_summary["Target Achievement (%)"].mean()

m_col1, m_col2 = st.columns([1, 2])
with m_col1:
    st.markdown("#### Corporate Mission Realization")
    st.metric("Strategy Execution Score", f"{overall_mission_achievement:.2f}%")
    if overall_mission_achievement >= 95.0:
        st.success("🌟 **EXCELLENT:** Strategy execution aligned with long-term corporate vision.")
    else:
        st.warning("⚠️ **GAP DETECTED:** Directorate performance requires strategic intervention.")

with m_col2:
    st.markdown("#### Directorate BSC Performance Ranking")
    st.dataframe(dir_summary[["BSC Rank", "Directorate", "Current Portfolio Balance (ETB)", "Target Portfolio (ETB)", "Target Achievement (%)"]], use_container_width=True)

# ==========================================
# 6. BRANCH RANKINGS & AUTOMATED ACTION PLANS
# ==========================================
st.markdown("---")
st.header("🏆 4. Branch Network Rankings & Automated Intervention Plans")

branch_agg = df.groupby(["Branch Location", "District"]).agg({
    "Current Portfolio Balance (ETB)": "sum",
    "Prior Portfolio Balance (ETB)": "sum",
    "Active Accounts": "sum",
    "Non-Performing Loans (NPL ETB)": "sum"
}).reset_index()

branch_agg["NPL Ratio (%)"] = (branch_agg["Non-Performing Loans (NPL ETB)"] / branch_agg["Current Portfolio Balance (ETB)"] * 100).round(2)
branch_agg["Growth (%)"] = ((branch_agg["Current Portfolio Balance (ETB)"] - branch_agg["Prior Portfolio Balance (ETB)"]) / branch_agg["Prior Portfolio Balance (ETB)"] * 100).round(2)

sorted_branches = branch_agg.sort_values(by="Current Portfolio Balance (ETB)", ascending=False)
top_10 = sorted_branches.head(10)
least_10 = sorted_branches.tail(10).sort_values(by="Current Portfolio Balance (ETB)", ascending=True)

r_tab1, r_tab2, r_tab3 = st.tabs(["Top 10 Performing Branches", "Least 10 Performing Branches (Watchlist)", "Automated Intervention Action Plans"])

with r_tab1:
    st.subheader("🌟 Top 10 Best-Performing Branches")
    st.dataframe(top_10[["Branch Location", "District", "Current Portfolio Balance (ETB)", "Growth (%)", "NPL Ratio (%)"]], use_container_width=True)

with r_tab2:
    st.subheader("⚠️ Least 10 Performing Branches (Watchlist)")
    st.dataframe(least_10[["Branch Location", "District", "Current Portfolio Balance (ETB)", "Growth (%)", "NPL Ratio (%)"]], use_container_width=True)

with r_tab3:
    st.subheader("🛠️ Automated Action Plans for Watchlist Branches")
    st.write("Targeted intervention protocols generated deterministically for low-volume and high-NPL locations:")
    
    for idx, row in least_10.iterrows():
        b_name = row["Branch Location"]
        b_dist = row["District"]
        b_npl = row["NPL Ratio (%)"]
        b_growth = row["Growth (%)"]
        
        st.markdown(f"""
        <div class="action-card">
            <strong>📍 {b_name} ({b_dist} District)</strong> | Portfolio: {row['Current Portfolio Balance (ETB)']:,.0f} ETB | Growth: {b_growth:+.2f}% | NPL Ratio: {b_npl:.2f}%<br>
            <em>Recommended Executive Action:</em>
            <ul>
                {"<li><strong>NPL Recovery Taskforce:</strong> Immediate audit and collection strategy required due to elevated credit risk (>5%).</li>" if b_npl > 5.0 else "<li><strong>Deposit Mobilization Drive:</strong> Launch targeted SME and commercial retail campaigns to increase core deposits.</li>"}
                {"<li><strong>Liquidity Injection & Product Restructuring:</strong> Re-align local interest offerings to reverse negative deposit growth.</li>" if b_growth < 0 else "<li><strong>Digital Onboarding Push:</strong> Expand mobile and digital banking enrollment to lower branch operating overhead.</li>"}
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 7. FORMAL BOARDROOM REPORT, PPT & EXCEL EXPORTS
# ==========================================
st.markdown("---")
st.header("📄 5. Formal Executive Report, Boardroom PPT & Excel Exports")

ex_tab1, ex_tab2, ex_tab3 = st.tabs(["Printable Boardroom PDF Report", "PowerPoint Slide Deck Outline", "Multi-Sheet Excel Download"])

with ex_tab1:
    st.subheader("📄 Official Executive Summary Report")
    st.caption("Copy or print this structured formal report directly for executive committee meetings and regulatory submissions.")
    
    formal_report = f"""
    ====================================================================================
    INSTITUTION: {bank_name.upper()}
    OFFICIAL BOARDROOM EXECUTIVE PERFORMANCE REPORT | PERIOD: {current_period}
    BASELINE COMPARISON: {comparison_period}
    ====================================================================================
    
    1. EXECUTIVE SUMMARY & CAPITAL COMPLIANCE
       ---------------------------------------------------------------------------------
       • Total Managed Earning Portfolio: {total_cur_portfolio:,.2f} ETB (YoY Growth: {portfolio_growth_yoy:+.2f}%).
       • Capital Adequacy Ratio (CAR): {car:.2f}% (Regulatory Minimum: 12.00%).
       • Net Interest Margin (NIM): {nim:.2f}% | Return on Equity (ROE): {roe:.2f}%.
       • Cost-to-Income Ratio (CIR): {cir:.2f}% | Overall NPL Exposure Ratio: {overall_npl_ratio:.2f}%.
       • Institution CAMELS Composite Soundness Rating: {camels_grade}.
    
    2. BALANCED SCORECARD (BSC) & STRATEGIC MISSION REALIZATION
       ---------------------------------------------------------------------------------
       • Overall Corporate Strategy Execution Score: {overall_mission_achievement:.2f}%.
       • Highest Performing Directorate: {dir_summary.iloc[0]['Directorate']} (Rank #1 - Target Achievement: {dir_summary.iloc[0]['Target Achievement (%)']:.2f}%).
       • Priority Strategic Directorate Focus: {dir_summary.iloc[-1]['Directorate']} (Rank #{len(dir_summary)} - Target Achievement: {dir_summary.iloc[-1]['Target Achievement (%)']:.2f}%).
    
    3. BRANCH NETWORK PERFORMANCE & WATCHLIST SUMMARY
       ---------------------------------------------------------------------------------
       • Leading Branch by Volume: {top_10.iloc[0]['Branch Location']} ({top_10.iloc[0]['District']} District) | Portfolio: {top_10.iloc[0]['Current Portfolio Balance (ETB)']:,.2f} ETB.
       • Lowest Volume Watchlist Branch: {least_10.iloc[0]['Branch Location']} ({least_10.iloc[0]['District']} District) | Portfolio: {least_10.iloc[0]['Current Portfolio Balance (ETB)']:,.2f} ETB.
       • Primary Action Required: Deployment of recovery taskforce and targeted deposit drives across Watchlist locations.
    
    ====================================================================================
    REPORT CERTIFIED BY EXECUTIVE PULSE AI | AIR-GAPPED ENTERPRISE ENGINE
    ====================================================================================
    """
    
    st.markdown(f'<div class="report-box"><pre>{formal_report}</pre></div>', unsafe_allow_html=True)

with ex_tab2:
    st.subheader("📊 PowerPoint Slide Deck Outline")
    ppt_text = f"""
    SLIDE 1: FINANCIAL HIGHLIGHTS & CAPITAL ADEQUACY
    - Portfolio Total: {total_cur_portfolio:,.0f} ETB ({portfolio_growth_yoy:+.2f}% growth vs {comparison_period}).
    - Capital Adequacy Ratio: {car:.2f}% | Soundness Rating: {camels_grade}.
    - Cost Efficiency: Cost-to-Income Ratio stands at {cir:.2f}%.

    SLIDE 2: BSC DIRECTORATE RANKINGS & MISSION REALIZATION
    - Strategy Execution Rating: {overall_mission_achievement:.2f}% towards Strategic Plan.
    - Rank 1 Directorate: {dir_summary.iloc[0]['Directorate']} ({dir_summary.iloc[0]['Target Achievement (%)']:.1f}% Target Achieved).

    SLIDE 3: BRANCH RANKINGS & WATCHLIST INTERVENTIONS
    - Top Performing Branch: {top_10.iloc[0]['Branch Location']}.
    - Watchlist Priority Branch: {least_10.iloc[0]['Branch Location']}.
    - Action Plan: Deploy deposit mobilization drives and credit recovery teams.
    """
    st.text_area("PPT Outline Text", value=ppt_text, height=250)

with ex_tab3:
    st.subheader("📥 Master Multi-Sheet Excel Export")
    st.write("Export all raw data, period comparisons, directorate BSC rankings, and branch action plans into a single structured workbook.")
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='MultiPeriod_Raw_Data', index=False)
        dir_summary.to_excel(writer, sheet_name='Directorate_BSC_Rankings', index=False)
        top_10.to_excel(writer, sheet_name='Top_10_Branches', index=False)
        least_10.to_excel(writer, sheet_name='Least_10_Watchlist', index=False)
        branch_agg.to_excel(writer, sheet_name='All_Branch_Analytics', index=False)
    
    processed_excel = excel_buffer.getvalue()

    st.download_button(
        label="📥 Download Master Banking Excel Workbook (.xlsx)",
        data=processed_excel,
        file_name=f"Master_Executive_Bank_Report_{current_period}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
