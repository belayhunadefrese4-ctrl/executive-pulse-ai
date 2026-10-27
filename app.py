import streamlit as st
import pandas as pd
import numpy as np
import io
import altair as alt
import openpyxl
from openpyxl.drawing.image import Image as XLImage
import vl_convert as vlc

# ==========================================
# PAGE CONFIGURATION & EXECUTIVE STYLING
# ==========================================
st.set_page_config(
    page_title="Executive Pulse AI - Commercial Banking Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. SECURITY & ACCESS CONTROL
# ==========================================
MASTER_SECURITY_KEY = "BANK-EXEC-8899-SECURE"

st.sidebar.markdown("### 🔐 Security & Access Control")
user_key = st.sidebar.text_input("Enter Master Executive Key", type="password")

if user_key != MASTER_SECURITY_KEY:
    st.markdown('<p style="font-size: 2.2rem; font-weight: 800; color: #800020;">🏦 Executive Pulse AI: Enterprise Banking Engine</p>', unsafe_allow_html=True)
    st.warning("🔒 Access Restricted: Please enter the valid Master Executive Key in the sidebar.")
    st.stop()

# ==========================================
# APP HEADER & INGESTION HUB
# ==========================================
st.markdown('<p style="font-size: 2.2rem; font-weight: 800; color: #800020;">🏦 Executive Pulse AI: Enterprise Banking Intelligence</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 1.05rem; color: #334155; margin-bottom: 20px;">Multi-Sheet Roll-up, Dynamic Period Headers & Master Package with Embedded Charts</p>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("📥 Enterprise Data Ingestion")
uploaded_files = st.sidebar.file_uploader(
    "Upload Bank Financial Reports & Detail Workbooks", 
    type=["xlsx", "csv"], 
    accept_multiple_files=True
)
reporting_period = st.sidebar.selectbox("Reporting Period", ["August 2026", "September 2026", "Q4 2026", "Q3 2026", "Q2 2026", "Q1 2026", "Annual 2026"])

# Dynamically derive date strings based on selected reporting period
if "August" in reporting_period:
    pos_header = "Position As of August 31, 2026"
elif "September" in reporting_period:
    pos_header = "Position As of September 30, 2026"
else:
    pos_header = f"Position As of {reporting_period}"

# ==========================================
# 🎨 CHART & BRAND COLOR CUSTOMIZER WIDGET
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("🎨 Chart & Brand Color Customizer")
plan_color = st.sidebar.color_picker("Plan Color", "#111827")
actual_color = st.sidebar.color_picker("Actual Color", "#800020")

st.markdown(f"""
    <style>
    .plan-badge {{ background-color: {plan_color}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; display: inline-block; }}
    .actual-badge {{ background-color: {actual_color}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; display: inline-block; }}
    .report-box {{ background-color: #FAFAFA; border: 1px solid #CBD5E1; border-left: 5px solid {actual_color}; padding: 20px; border-radius: 6px; font-family: 'Times New Roman', Times, serif; }}
    .ppt-box {{ background-color: #F8FAFC; border: 1px solid #94A3B8; border-left: 5px solid #475569; padding: 20px; border-radius: 6px; font-family: monospace; }}
    </style>
""", unsafe_allow_html=True)

# Helper to ensure unique column names
def make_unique_cols(cols):
    seen = {}
    new_cols = []
    for c in cols:
        c_str = str(c).strip()
        if c_str in seen:
            seen[c_str] += 1
            new_cols.append(f"{c_str}_{seen[c_str]}")
        else:
            seen[c_str] = 0
            new_cols.append(c_str)
    return new_cols

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
    df_clean.columns = make_unique_cols(headers)
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
# 2. COLUMN MAPPING & ROLL-UP ENGINE
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

    position_total = s_june + s_ytd_act
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
        pos_header: f"{position_total:,.0f}"
    })

exec_summary_df = pd.DataFrame(summary_rows)
exec_summary_df.columns = [
    "#", "Particulars / variables", "As of June 30, 2026", 
    "YTD. Plan", "YTD. Actual", "%age", 
    "M.Plan", "M. Actual", "%age ", 
    pos_header
]

# ==========================================
# 3. EXECUTIVE DASHBOARD TABS
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Summary Table",
    "📑 Linked Detail Sheets", 
    "🏆 Top & Least 10 Rankings & Charts",
    "📄 Boardroom Report & PPT",
    "📥 Download Master Package"
])

with tab1:
    st.subheader(f"Executive Summary Roll-up ({reporting_period})")
    st.markdown("Consolidated variable totals mapped precisely into correct columns:")
    st.data_editor(exec_summary_df, num_rows="dynamic", use_container_width=True, key="bank_standard_matrix")

with tab2:
    st.subheader("📑 Detailed Source Workbooks & Domain Inspector")
    selected_sheet = st.selectbox("Select Variable Sheet to Inspect Details:", list(sheets.keys()), key="det_sheet")
    if selected_sheet in sheets:
        st.markdown(f"**Showing full branch breakdown and automated Grand Total for `{selected_sheet}`:**")
        
        detail_df = sheets[selected_sheet].copy()
        for col in detail_df.columns:
            if "position" in str(col).lower() or "august" in str(col).lower():
                detail_df.rename(columns={col: pos_header}, inplace=True)
                break

        total_list = []
        for i, c in enumerate(detail_df.columns):
            if i == 0:
                total_list.append("GRAND TOTAL")
            else:
                col_sum = clean_sum_by_keywords(detail_df, [str(c).lower()])
                total_list.append(f"{col_sum:,.0f}" if col_sum > 0 else "")
                
        detail_df.loc[len(detail_df)] = total_list
        st.data_editor(detail_df, num_rows="dynamic", use_container_width=True, key=f"insp_{selected_sheet}")

export_rankings_dict = {}
chart_objects = {}

with tab3:
    st.subheader("🏆 Branch Performance Analytics & Branded Visualizations")
    st.markdown(f"Active Legend: <span class='plan-badge'>Plan</span> &nbsp;&nbsp;&nbsp; <span class='actual-badge'>Actual</span>", unsafe_allow_html=True)
    
    rank_sheet = st.selectbox("Select Variable Sheet for Analytics:", list(sheets.keys()), key="rank_sheet")
    if rank_sheet in sheets:
        rank_df = sheets[rank_sheet].copy()
        
        def find_col_by_keywords(df, keywords):
            for col in df.columns:
                c_low = str(col).lower()
                if any(k in c_low for k in keywords):
                    return col
            return None

        ytd_plan_col = find_col_by_keywords(rank_df, ["ytd. plan", "ytd plan"])
        ytd_act_col = find_col_by_keywords(rank_df, ["ytd. actual", "ytd actual", "ytd.act"])
        m_plan_col = find_col_by_keywords(rank_df, ["m.plan", "month plan", "m plan"])
        m_act_col = find_col_by_keywords(rank_df, ["m. actual", "m actual", "month actual"])
        
        pct_cols = [c for c in rank_df.columns if "%age" in str(c) or "percent" in str(c).lower()]
        ytd_pct_col = pct_cols[0] if len(pct_cols) > 0 else None
        m_pct_col = pct_cols[1] if len(pct_cols) > 1 else (pct_cols[0] if len(pct_cols) > 0 else None)

        branch_name_col = None
        for col in rank_df.columns:
            c_low = str(col).lower()
            if any(k in c_low for k in ["branch name", "branch", "name", "district"]):
                branch_name_col = col
                break
        if not branch_name_col and len(rank_df.columns) > 0:
            branch_name_col = rank_df.columns[1] if len(rank_df.columns) > 1 else rank_df.columns[0]

        rank_df["_sort_ytd_act"] = pd.to_numeric(rank_df[ytd_act_col].astype(str).str.replace(',', '').str.replace('-', '0'), errors='coerce').fillna(0) if ytd_act_col else 0.0
        rank_df["_sort_ytd_plan"] = pd.to_numeric(rank_df[ytd_plan_col].astype(str).str.replace(',', '').str.replace('-', '0'), errors='coerce').fillna(0) if ytd_plan_col else 0.0
        rank_df["_sort_m_act"] = pd.to_numeric(rank_df[m_act_col].astype(str).str.replace(',', '').str.replace('-', '0'), errors='coerce').fillna(0) if m_act_col else 0.0
        rank_df["_sort_m_plan"] = pd.to_numeric(rank_df[m_plan_col].astype(str).str.replace(',', '').str.replace('-', '0'), errors='coerce').fillna(0) if m_plan_col else 0.0

        rank_df["_sort_ytd_pct"] = pd.to_numeric(rank_df[ytd_pct_col].astype(str).str.replace('%', '').str.replace(',', '').str.replace('-', '0'), errors='coerce').fillna(0) if ytd_pct_col else rank_df["_sort_ytd_act"]
        rank_df["_sort_m_pct"] = pd.to_numeric(rank_df[m_pct_col].astype(str).str.replace('%', '').str.replace(',', '').str.replace('-', '0'), errors='coerce').fillna(0) if m_pct_col else rank_df["_sort_m_act"]

        sorted_ytd_top = rank_df.sort_values(by="_sort_ytd_act", ascending=False)
        sorted_ytd_least = rank_df.sort_values(by="_sort_ytd_act", ascending=True)
        top_10_ytd = sorted_ytd_top.head(10).drop(columns=[c for c in sorted_ytd_top.columns if c.startswith("_")])
        least_10_ytd = sorted_ytd_least.head(10).drop(columns=[c for c in sorted_ytd_least.columns if c.startswith("_")])

        export_rankings_dict["Top_10_YTD"] = top_10_ytd
        export_rankings_dict["Least_10_YTD"] = least_10_ytd

        def get_altair_chart(df_subset, p_col, a_col, chart_title):
            if branch_name_col not in df_subset.columns:
                return None
            plot_df = df_subset.set_index(branch_name_col)[[p_col, a_col]].reset_index()
            plot_df.columns = ["Branch", "Plan", "Actual"]
            melted = plot_df.melt(id_vars="Branch", value_vars=["Plan", "Actual"], var_name="Metric", value_name="Amount")
            
            chart = alt.Chart(melted).mark_bar().encode(
                x=alt.X('Branch:N', sort=None, title=''),
                y=alt.Y('Amount:Q', title=''),
                color=alt.Color('Metric:N', scale=alt.Scale(domain=['Plan', 'Actual'], range=[plan_color, actual_color]), legend=alt.Legend(title="")),
                xOffset='Metric:N',
                tooltip=['Branch', 'Metric', 'Amount']
            ).properties(title=chart_title, width=600, height=300).configure_view(stroke=None)
            return chart

        c_top_ytd = get_altair_chart(sorted_ytd_top.head(10), "_sort_ytd_plan", "_sort_ytd_act", "Top 10 Branches - YTD Plan vs Actual")
        c_least_ytd = get_altair_chart(sorted_ytd_least.head(10), "_sort_ytd_plan", "_sort_ytd_act", "Least 10 Branches - YTD Plan vs Actual")
        
        if c_top_ytd: chart_objects["Top_10_YTD"] = c_top_ytd
        if c_least_ytd: chart_objects["Least_10_YTD"] = c_least_ytd

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("#### 🥇 YTD Performance Rankings & Charts")
            st.markdown("##### Top 10 Branches (YTD)")
            st.dataframe(top_10_ytd, use_container_width=True)
            if c_top_ytd: st.altair_chart(c_top_ytd, use_container_width=True)

            st.markdown("##### Least 10 Branches (YTD - Ascending)")
            st.dataframe(least_10_ytd, use_container_width=True)
            if c_least_ytd: st.altair_chart(c_least_ytd, use_container_width=True)

        with col_t2:
            st.markdown("#### 📅 Monthly Performance Rankings & Charts")
            sorted_m_top = rank_df.sort_values(by="_sort_m_act", ascending=False)
            sorted_m_least = rank_df.sort_values(by="_sort_m_act", ascending=True)
            top_10_m = sorted_m_top.head(10).drop(columns=[c for c in sorted_m_top.columns if c.startswith("_")])
            least_10_m = sorted_m_least.head(10).drop(columns=[c for c in sorted_m_least.columns if c.startswith("_")])
            
            export_rankings_dict["Top_10_Monthly"] = top_10_m
            export_rankings_dict["Least_10_Monthly"] = least_10_m

            c_top_m = get_altair_chart(sorted_m_top.head(10), "_sort_m_plan", "_sort_m_act", "Top 10 Branches - Monthly Plan vs Actual")
            c_least_m = get_altair_chart(sorted_m_least.head(10), "_sort_m_plan", "_sort_m_act", "Least 10 Branches - Monthly Plan vs Actual")
            
            if c_top_m: chart_objects["Top_10_Monthly"] = c_top_m
            if c_least_m: chart_objects["Least_10_Monthly"] = c_least_m

            st.markdown("##### Top 10 Branches (Monthly)")
            st.dataframe(top_10_m, use_container_width=True)
            if c_top_m: st.altair_chart(c_top_m, use_container_width=True)

            st.markdown("##### Least 10 Branches (Monthly - Ascending)")
            st.dataframe(least_10_m, use_container_width=True)
            if c_least_m: st.altair_chart(c_least_m, use_container_width=True)

with tab4:
    st.subheader("📄 Executive Narrative Report & Boardroom PPT Outline")
    narrative_text = f"""
====================================================================================
COMMERCIAL BANKING PERFORMANCE REPORT | PERIOD: {reporting_period}
====================================================================================
1. EXECUTIVE SUMMARY ROLL-UP MATRIX & VISUAL ANALYTICS
   • Master summary compiled successfully with Top/Least 10 branch rankings and charts.
   • {pos_header} computed precisely as June 30 Position + YTD Actual.
====================================================================================
CERTIFIED BY EXECUTIVE PULSE AI | ENTERPRISE BANKING INTELLIGENCE
====================================================================================
"""
    ppt_outline = f"""
SLIDE 1: INSTITUTIONAL PERFORMANCE ROLL-UP ({reporting_period})
- Multi-variable consolidated summary table & Top/Least 10 branch rankings.
"""
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("##### 📄 Boardroom Executive Report")
        st.markdown(f'<div class="report-box"><pre>{narrative_text}</pre></div>', unsafe_allow_html=True)
    with col_r2:
        st.markdown("##### 📊 Boardroom PPT Slide Outline")
        st.markdown(f'<div class="ppt-box"><pre>{ppt_outline}</pre></div>', unsafe_allow_html=True)

with tab5:
    st.subheader("📥 Download Master Package")
    st.markdown("Download the fully structured Excel workbook containing the summarized master table, top/least rankings, embedded visual charts, and all detailed branch source workbooks.")

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        exec_summary_df.to_excel(writer, sheet_name="Executive_Summary", index=False)
        
        for r_name, r_df in export_rankings_dict.items():
            r_df.to_excel(writer, sheet_name=r_name[:30], index=False)

        for s_name, s_df in sheets.items():
            clean_name = str(s_name).replace(" -> ", "_")[:30].replace("/", "_").replace("\\", "_")
            export_df = s_df.copy()
            for col in export_df.columns:
                if "position" in str(col).lower() or "august" in str(col).lower():
                    export_df.rename(columns={col: pos_header}, inplace=True)
                    break
            total_list = []
            for i, c in enumerate(export_df.columns):
                if i == 0:
                    total_list.append("GRAND TOTAL")
                else:
                    col_sum = clean_sum_by_keywords(export_df, [str(c).lower()])
                    total_list.append(f"{col_sum:,.0f}" if col_sum > 0 else "")
            export_df.loc[len(export_df)] = total_list
            export_df.to_excel(writer, sheet_name=clean_name, index=False)

    # Post-process workbook with openpyxl and vl-convert to embed Altair charts as images onto ranking sheets
    excel_buffer.seek(0)
    wb = openpyxl.load_workbook(excel_buffer)
    
    for chart_name, chart_obj in chart_objects.items():
        if chart_name in wb.sheetnames:
            ws = wb[chart_name]
            # Convert Altair chart to PNG bytes via vl_convert
            img_bytes = vlc.vegalite_to_png(chart_obj.to_dict(), scale=2)
            img_io = io.BytesIO(img_bytes)
