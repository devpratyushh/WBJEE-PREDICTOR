import streamlit as st
import pandas as pd
import os
import glob
import numpy as np
import streamlit.components.v1 as components
import plotly.express as px

# Page Config
st.set_page_config(page_title="WBJEE College Directory", page_icon="🏫", layout="wide", initial_sidebar_state="collapsed")

import io
from xhtml2pdf import pisa

# ── Font Awesome CDN ──
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">', unsafe_allow_html=True)

# ── Master CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Reset & Global ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #F8FAFC; }

/* Hide default Streamlit elements */
#MainMenu, footer, header[data-testid="stHeader"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }

/* ── Fix Streamlit White Space ── */
.stApp { margin-top: -10px !important; }
div.stMainBlockContainer, .block-container {
    padding-top: 0px !important; 
    margin-top: -20px !important;
    max-width: 1400px !important;
}

div[data-testid="stElementContainer"]:has(#top-nav-marker) {
    position: sticky !important;
    top: 50px !important;
    z-index: 999999 !important;
}

/* ── Modern Floating Top Nav Bar (In Document Flow) ── */
.top-nav {
    width: 100%; max-width: 1350px; margin: 0 auto;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    padding: 12px 32px;
    border-radius: 60px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 10px 40px -10px rgba(59, 130, 246, 0.2), 
                0 0 20px rgba(21, 128, 61, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.8);
    margin-bottom: 24px;
}
.top-nav-left { display: flex; align-items: center; gap: 14px; }
.top-nav-title { color: #0F172A; font-size: 16px; font-weight: 800; letter-spacing: 0.5px;}
.nav-item {
    color: #334155; text-decoration: none; font-size: 14px; font-weight: 500;
    transition: all 0.2s; cursor: pointer; display: flex; align-items: center; gap: 8px;
}
.nav-item:hover { color: #0F172A; font-weight: 600; }
.nav-item.active { font-weight: 700; color: #4F46E5; }

/* Style Native Labels */
div[data-testid="stSelectbox"] label p {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #374151 !important;
    display: flex;
    align-items: center;
}

/* ── Results Header ── */
.results-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 20px; flex-wrap: wrap; gap: 16px;
}
.results-left { display: flex; align-items: center; gap: 16px; }
.results-icon {
    width: 54px;
    height: 54px;
    background: linear-gradient(135deg, #f1f3ff 0%, #e0e7ff 100%);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.7rem;
    color: #4338ca;
    box-shadow: 0 4px 10px rgba(67, 56, 202, 0.1);
}
.results-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #1a1a2e;
    margin: 0;
    line-height: 1.2;
}

/* ── Metric Cards ── */
.metrics-row { display: flex; gap: 16px; justify-content: flex-end; align-items: center; height: 100%; }
.m-card {
    background: #FFFFFF; border: 1px solid #F3F4F6; border-radius: 12px;
    padding: 10px 18px; display: flex; align-items: center; gap: 12px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.m-text { display: flex; flex-direction: column; }
.m-text span { font-size: 11px; color: #6B7280; font-weight: 500; white-space: nowrap; }
.m-text strong { font-size: 20px; color: #111827; font-weight: 700; white-space: nowrap; }
.m-icon {
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center; font-size: 16px;
}
</style>
""", unsafe_allow_html=True)


# ── Load Data ──
@st.cache_data
def load_data():
    data_dir = "data"
    all_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not all_files:
        return pd.DataFrame()
    df_list = []
    for file in all_files:
        try:
            temp_df = pd.read_csv(file)
            year_str = os.path.splitext(os.path.basename(file))[0]
            temp_df['Year'] = year_str
            df_list.append(temp_df)
        except Exception:
            pass
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("No data found in `data/` directory.")
    st.stop()

# Prepare Data
quotas = df['Quota'].dropna().unique() if 'Quota' in df.columns else []
ordered_quotas = [q for q in ["All India", "Home State"] if q in quotas] + [q for q in quotas if q not in ["All India", "Home State"]]
all_categories = sorted(list(df['Category'].dropna().unique()))
years = ["All Years"] + sorted(list(df['Year'].dropna().unique()), reverse=True)

@st.cache_data(show_spinner=False)
def generate_pdf(institute, df_to_print, sel_prog="--- All Programs ---", sel_cat="--- All Categories ---"):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import base64
    import io
    import pandas as pd
    import numpy as np

    html_content = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Helvetica, sans-serif; font-size: 10px; }}
        h1 {{ color: #1E3A8A; text-align: center; }}
        h2 {{ color: #4338CA; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th {{ background-color: #F3F4F6; color: #111827; font-weight: bold; padding: 6px; border: 1px solid #D1D5DB; text-align: left; }}
        td {{ padding: 6px; border: 1px solid #D1D5DB; color: #374151; }}
        .opening {{ color: #065F46; font-weight: bold; }}
        .closing {{ color: #991B1B; font-weight: bold; }}
    </style>
    </head>
    <body>
    <h1>{institute}</h1>
    """
    
    # Generate Graph for PDF
    idx_trend = df_to_print.groupby(['Year', 'Program', 'Category', 'Quota', 'Seat Type'])['Round'].idxmax()
    trend_df = df_to_print.loc[idx_trend].copy()
    
    if sel_prog != "--- All Programs ---":
        trend_df = trend_df[trend_df['Program'] == sel_prog]
        
    trend_df['Closing Rank Num'] = pd.to_numeric(trend_df['Closing Rank'].astype(str).str.extract(r'(\d+)')[0], errors='coerce')
    trend_df = trend_df.dropna(subset=['Closing Rank Num'])
    
    if not trend_df.empty:
        if sel_prog != "--- All Programs ---":
            trend_df['Line Label'] = trend_df['Category']
        else:
            if sel_cat == "--- All Categories ---":
                trend_df['Line Label'] = trend_df['Program'].str[:30] + " - " + trend_df['Category']
            else:
                trend_df['Line Label'] = trend_df['Program'].str[:40]
                
        trend_df = trend_df.sort_values('Year')
        
        fig, ax = plt.subplots(figsize=(7, 3.5))
        groups = trend_df.groupby('Line Label')
        count = 0
        for label, grp in groups:
            ax.plot(grp['Year'].astype(str), grp['Closing Rank Num'], marker='o', label=label)
            count += 1
            if count > 10:
                break
                
        ax.set_title('Cutoff Trends (Last Round)')
        ax.set_xlabel('Year')
        ax.set_ylabel('Closing Rank')
        
        if count <= 6:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
            
        plt.tight_layout()
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        img_b64 = base64.b64encode(img_buf.getvalue()).decode()
        html_content += f'<div style="text-align: center; margin-top: 20px; margin-bottom: 20px;"><img src="data:image/png;base64,{img_b64}" width="500"></div>'

    
    yrs = sorted(df_to_print['Year'].astype(str).unique(), reverse=True)
    for y in yrs:
        year_df = df_to_print[df_to_print['Year'] == str(y)]
        if year_df.empty:
            continue
            
        idx = year_df.groupby(['Program', 'Category', 'Quota', 'Seat Type'])['Round'].idxmax()
        year_df = year_df.loc[idx].copy()
        
        year_df['_sort'] = pd.to_numeric(year_df['Closing Rank'].astype(str).str.extract(r'(\d+)')[0], errors='coerce').fillna(float('inf'))
        year_df = year_df.sort_values('_sort', ascending=True)
        
        html_content += f"<h2>{y} Final Cutoffs</h2>"
        html_content += "<table><thead><tr><th>Program</th><th>Category</th><th>Opening Rank</th><th>Closing Rank</th><th>Quota</th><th>Seat Type</th></tr></thead><tbody>"
        for _, row in year_df.iterrows():
            html_content += f"<tr><td>{row['Program']}</td><td>{row['Category']}</td><td class='opening'>{row['Opening Rank']}</td><td class='closing'>{row['Closing Rank']}</td><td>{row['Quota']}</td><td>{row['Seat Type']}</td></tr>"
        html_content += "</tbody></table>"
        
    html_content += "</body></html>"
    
    pdf_buffer = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html_content), dest=pdf_buffer)
    return pdf_buffer.getvalue()

# ── Custom College Categorization & Popularity ──
popularity_dict = {}
try:
    # Determine popularity by the lowest closing rank achieved by the college
    pop_df = df.copy()
    pop_df['Closing Rank Num'] = pd.to_numeric(pop_df['Closing Rank'].astype(str).str.replace(r'[^0-9]', '', regex=True), errors='coerce')
    popularity_dict = pop_df.groupby('Institute')['Closing Rank Num'].min().to_dict()
except Exception:
    pass

def get_institute_category(name):
    if name == "--- Select a College ---": return 0, name
    name_upper = name.upper()
    if "JADAVPUR" in name_upper or "UNIVERSITY OF CALCUTTA" in name_upper:
        return 1, "Elite State Univ"
    if "KALYANI GOVER" in name_upper or "JALPAIGURI GOVER" in name_upper:
        return 2, "Top Govt Engg"
    if "GOVERNMENT" in name_upper or "GOVERMENT" in name_upper or "GOVT" in name_upper:
        return 3, "State Govt Engg"
    if "MAULANA ABUL KALAM" in name_upper or "ALIAH" in name_upper or "KAJI NAZRUL" in name_upper or "KALYANI UNIVERSITY" in name_upper or "BIDHAN CHANDRA" in name_upper or "ANIMAL AND FISHERY" in name_upper:
        return 4, "State University"
    
    # Private colleges now above private universities
    if "PHARMACY" in name_upper or "PHARMACEUTICAL" in name_upper:
        return 7, "Pharmacy College"
    if "UNIVERSITY" in name_upper:
        return 6, "Private University"
    return 5, "Private College"

def institute_sort_key(name):
    cat_id, _ = get_institute_category(name)
    pop = popularity_dict.get(name, 999999)
    if pd.isna(pop): pop = 999999
    return (cat_id, pop, name)

# ── Floating Modern Nav Bar ──
st.markdown("<span id='top-nav-marker'></span>", unsafe_allow_html=True)

c1, c2 = st.columns([1.5, 3], vertical_alignment="center")
with c1:
    st.markdown("""
    <span id='nav-container'></span>
    <div style="display: flex; align-items: center; gap: 14px; padding-left: 10px;">
        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/4/46/West_Bengal_Joint_Entrance_Examinations_Board_Logo.svg/500px-West_Bengal_Joint_Entrance_Examinations_Board_Logo.svg.png" style="height: 34px; margin-bottom: 6px;" />
        <span style="color: #0F172A; font-size: 16px; font-weight: 800; letter-spacing: 0.5px; white-space: nowrap;">WBJEE Predictions</span>
    </div>
    """, unsafe_allow_html=True)
with c2:
    app_mode = st.segmented_control(
        "Nav", 
        ["College Directory", "Rank Predictor", "Guide"], 
        default="Rank Predictor", 
        label_visibility="collapsed"
    )

st.markdown("""
<style>
/* Hide Streamlit Default Elements */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Custom Global Font & Background */
div[data-testid="stHorizontalBlock"]:has(#nav-container) {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    padding: 12px 32px !important;
    border-radius: 60px;
    box-shadow: 0 10px 40px -10px rgba(59, 130, 246, 0.2), 0 0 20px rgba(21, 128, 61, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.8);
    position: sticky !important;
    top: 50px !important;
    z-index: 999999 !important;
    margin: 0 auto 24px auto !important;
    max-width: 1350px !important;
}

div[data-testid="stSegmentedControl"] {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-top: 4px;
}
/* Aggressively strip backgrounds and borders from all internal components */
div[data-testid="stSegmentedControl"] * {
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}
/* Style the text elements */
div[data-testid="stSegmentedControl"] p {
    color: #64748B !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    margin: 0 !important;
    padding: 0 8px !important;
    transition: color 0.2s ease;
}
/* Hover state */
div[data-testid="stSegmentedControl"] *:hover > p,
div[data-testid="stSegmentedControl"] *:hover > div > p {
    color: #0F172A !important;
}
/* Selected state */
div[data-testid="stSegmentedControl"] [data-selected="true"] p,
div[data-testid="stSegmentedControl"] [data-selected="true"] * p,
div[data-testid="stSegmentedControl"] [aria-checked="true"] p,
div[data-testid="stSegmentedControl"] [aria-selected="true"] p {
    color: #4338CA !important;
}
/* Ensure all expanders have a solid white background in Predictions */

/* Expander Titles Bold */
div[data-testid="stExpander"] summary p {
    font-weight: 800 !important;
    color: #0F172A !important;
}
/* Dotted Status Containers */
div[data-testid="stVerticalBlock"]:has(> div.element-container > div > span#safe-container) {
    border: 2px dashed rgba(21, 128, 61, 0.5) !important;
    padding: 20px !important;
    border-radius: 12px !important;
    background: rgba(21, 128, 61, 0.03) !important;
    margin-bottom: 24px !important;
}
div[data-testid="stVerticalBlock"]:has(> div.element-container > div > span#match-container) {
    border: 2px dashed rgba(245, 158, 11, 0.5) !important;
    padding: 20px !important;
    border-radius: 12px !important;
    background: rgba(245, 158, 11, 0.03) !important;
    margin-bottom: 24px !important;
}
div[data-testid="stVerticalBlock"]:has(> div.element-container > div > span#reach-container) {
    border: 2px dashed rgba(239, 68, 68, 0.5) !important;
    padding: 20px !important;
    border-radius: 12px !important;
    background: rgba(239, 68, 68, 0.03) !important;
    margin-bottom: 24px !important;
}

div[data-testid="stExpander"] details {
    background-color: #FFFFFF !important;
    border-radius: 8px !important;
    border: 1px solid #E2E8F0 !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DYNAMIC CSS FOR ICONS (Based on Column Count)
# ══════════════════════════════════════════════════════════════
css_icons_5 = """
<style>
div[data-testid="column"]:nth-child(1) label p::before { content: "\\f0ac"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; color: #10B981; font-size: 16px; background: #ECFDF5; padding: 6px; border-radius: 50%; }
div[data-testid="column"]:nth-child(2) label p::before { content: "\\f02b"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; color: #F59E0B; font-size: 16px; background: #FEF3C7; padding: 6px; border-radius: 50%; }
div[data-testid="column"]:nth-child(3) label p::before { content: "\\f133"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; color: #3B82F6; font-size: 16px; background: #EFF6FF; padding: 6px; border-radius: 50%; }
div[data-testid="column"]:nth-child(4) label p::before { content: "\\f19c"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; color: #4F46E5; font-size: 16px; background: #EEF2FF; padding: 6px; border-radius: 50%; }
div[data-testid="column"]:nth-child(5) label p::before { content: "\\f5fd"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; color: #8B5CF6; font-size: 16px; background: #F5F3FF; padding: 6px; border-radius: 50%; }
</style>
"""

css_icons_4 = """
<style>
div[data-testid="column"]:nth-child(1) label p::before { content: "\\f0ac"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; color: #10B981; font-size: 16px; background: #ECFDF5; padding: 6px; border-radius: 50%; }
div[data-testid="column"]:nth-child(2) label p::before { content: "\\f133"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; color: #3B82F6; font-size: 16px; background: #EFF6FF; padding: 6px; border-radius: 50%; }
div[data-testid="column"]:nth-child(3) label p::before { content: "\\f19c"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; color: #4F46E5; font-size: 16px; background: #EEF2FF; padding: 6px; border-radius: 50%; }
div[data-testid="column"]:nth-child(4) label p::before { content: "\\f5fd"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; color: #8B5CF6; font-size: 16px; background: #F5F3FF; padding: 6px; border-radius: 50%; }
</style>
"""

if app_mode == "Rank Predictor":
    import model
    
    with st.container():
        st.markdown("<span class='outer-banner-marker'></span>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0;">
            <div>
                <h1 style="font-size: 32px; font-weight: 800; color: #0F172A; margin: 0 0 6px 0; padding: 0; letter-spacing: -0.5px;">WBJEE Rank Predictor</h1>
                <p style="font-size: 14px; color: #64748B; margin: 0; padding: 0; font-weight: 500;">Predict safe, match, and reach colleges based on your rank using SVR models.</p>
            </div>
            <span style="display: inline-flex; align-items: center; gap: 8px; background: #4338CA; color: #FFF; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; box-shadow: 0 4px 12px rgba(67, 56, 202, 0.2);"><i class="fa-solid fa-robot" style="color: #A5B4FC;"></i> ML Prediction</span>
        </div>
        """, unsafe_allow_html=True)
    
        with st.container():
            st.markdown("<span class='inner-card-marker'></span>", unsafe_allow_html=True)
            cols = st.columns([1.5, 1.2, 1.2, 1.2])
            c_rank, c_quota, c_cat, c_seat = cols
            
            student_rank = c_rank.number_input("Your Rank (e.g. GMR)", min_value=1, max_value=200000, value=5000, step=100)
            selected_quota = c_quota.selectbox("Domicile / Quota", options=ordered_quotas, key="pred_quota")
            if selected_quota == "Home State":
                selected_category = c_cat.selectbox("Category", options=all_categories, key="pred_cat")
            else:
                selected_category = "Open"
                c_cat.selectbox("Category", options=["Open"], disabled=True, key="pred_cat")
                
            selected_seat_type = c_seat.selectbox("Seat Type", options=["WBJEE Seats", "JEE(Main) Seats"], key="pred_seat")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Predict Colleges", use_container_width=True, type="primary"):
                with st.spinner("Running SVR Pipeline..."):
                    pred_df = model.load_and_train_predictor()
                    if not pred_df.empty:
                        res_df = model.predict_colleges(student_rank, selected_quota, selected_category, selected_seat_type, pred_df)
                        st.session_state.res_df = res_df
                        st.session_state.show_predictions = True
            
    if st.session_state.get('show_predictions', False):
        res_df = st.session_state.res_df
        if res_df is not None:
                
                if res_df.empty:
                    st.warning("No colleges found for this combination or rank is too high.")
                else:
                    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
                            
                    with st.container():
                        st.markdown("<span class='outer-banner-marker'></span>", unsafe_allow_html=True)
                        with st.container():
                            st.markdown("<span class='inner-card-marker'></span>", unsafe_allow_html=True)
                            
                            safe_count = res_df[res_df['Status'] == 'Safe']['Institute'].nunique()
                            match_count = res_df[res_df['Status'] == 'Match']['Institute'].nunique()
                            reach_count = res_df[res_df['Status'] == 'Reach']['Institute'].nunique()
                            total_count = res_df['Institute'].nunique()
                            
                            m1, m2, m3, m4 = st.columns(4)
                            m1.markdown(f"""
                            <a href="#safe-section" target="_self" style="text-decoration: none; color: inherit; display: block; border-right: 1px solid #E2E8F0; padding-right: 16px;">
                                <div style="font-size: 14px; color: #64748B; margin-bottom: 4px;">Safe</div>
                                <div style="font-size: 36px; color: #15803D; font-weight: 700; line-height: 1;">{safe_count}</div>
                            </a>
                            """, unsafe_allow_html=True)
                            
                            m2.markdown(f"""
                            <a href="#match-section" target="_self" style="text-decoration: none; color: inherit; display: block; border-right: 1px solid #E2E8F0; padding-right: 16px;">
                                <div style="font-size: 14px; color: #64748B; margin-bottom: 4px;">Match</div>
                                <div style="font-size: 36px; color: #F59E0B; font-weight: 700; line-height: 1;">{match_count}</div>
                            </a>
                            """, unsafe_allow_html=True)
                            
                            m3.markdown(f"""
                            <a href="#reach-section" target="_self" style="text-decoration: none; color: inherit; display: block; border-right: 1px solid #E2E8F0; padding-right: 16px;">
                                <div style="font-size: 14px; color: #64748B; margin-bottom: 4px;">Reach</div>
                                <div style="font-size: 36px; color: #EF4444; font-weight: 700; line-height: 1;">{reach_count}</div>
                            </a>
                            """, unsafe_allow_html=True)
                            
                            m4.markdown(f"""
                            <div style="display: block; padding-right: 16px;">
                                <div style="font-size: 14px; color: #64748B; margin-bottom: 4px;">Total</div>
                                <div style="font-size: 36px; color: #0F172A; font-weight: 700; line-height: 1;">{total_count}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)
                            
                            f1, f2 = st.columns(2)
                            search_branch = f1.text_input("Filter by branch", placeholder="e.g. CSE, Mechanical, Data Science, AI")
                            search_inst = f2.text_input("Filter by institute", placeholder="e.g. Jadavpur, Kalyani, Heritage")
                            
                    # Apply local filters
                    display_df = res_df.copy()
                    if search_branch:
                        display_df = display_df[display_df['Program'].str.contains(search_branch, case=False, na=False)]
                    if search_inst:
                        display_df = display_df[display_df['Institute'].str.contains(search_inst, case=False, na=False)]
                            
                    # Apply Categories
                    display_df['Cat_ID'] = display_df['Institute'].apply(lambda x: get_institute_category(x)[0])
                    display_df['Cat_Name'] = display_df['Institute'].apply(lambda x: get_institute_category(x)[1])
                            
                    # Filter out Pharmacy (Cat_ID = 7)
                    display_df = display_df[display_df['Cat_ID'] != 7]
                            
                    def display_category_expanders(sub_df, status_color):
                        cats = sorted(sub_df['Cat_ID'].unique())
                        for cat in cats:
                            cat_df = sub_df[sub_df['Cat_ID'] == cat]
                            cat_name = cat_df['Cat_Name'].iloc[0]
                                    
                            def render_insts(df_subset):
                                insts = sorted(df_subset['Institute'].unique(), key=institute_sort_key)
                                for inst in insts:
                                    inst_df = df_subset[df_subset['Institute'] == inst]
                                    with st.expander(f"{inst} ({len(inst_df)} branches)"):
                                        st.markdown(f"**{inst}**")
                                        show_df = inst_df[['Program', 'Quota']].copy()
                                        
                                        for r in ['R1', 'R2', 'R3']:
                                            show_df[f'{r} Pred'] = inst_df[r].apply(lambda x: x.split(' (')[0] if pd.notnull(x) and isinstance(x, str) else x)
                                            show_df[f'{r} Hist'] = inst_df[r].apply(lambda x: '(' + x.split(' (')[1] if pd.notnull(x) and isinstance(x, str) and ' (' in x else '')
                                            
                                        # Only display columns that actually have predictions
                                        display_cols = ['Program', 'Quota']
                                        style_subset = []
                                        for r in ['R1', 'R2', 'R3']:
                                            if show_df[f'{r} Pred'].astype(str).str.contains(r'\d').any():
                                                display_cols.extend([f'{r} Pred', f'{r} Hist'])
                                                style_subset.append(f'{r} Pred')
                                                
                                        final_df = show_df[display_cols]
                                        
                                        styled_df = final_df.style.set_properties(
                                            **{'font-weight': 'bold', 'color': status_color}, 
                                            subset=style_subset
                                        ).set_properties(
                                            **{'color': '#94A3B8', 'font-size': '12px'},
                                            subset=[c for c in display_cols if 'Hist' in c]
                                        )
                                        
                                        st.dataframe(styled_df, use_container_width=True, hide_index=True)
                                                
                            if cat == 5: # Private College
                                top_pvt_keywords = ["HERITAGE", "TECHNO MAIN", "CALCUTTA INSTITUTE OF ENGINEERING", "HALDIA", "ST. THOMAS", "NSHM", "NETAJI SUBHAS"]
                                        
                                def is_top(name):
                                    return any(kw in name.upper() for kw in top_pvt_keywords)
                                            
                                is_top_mask = cat_df['Institute'].apply(is_top)
                                top_df = cat_df[is_top_mask]
                                other_df = cat_df[~is_top_mask]
                                        
                                if not top_df.empty:
                                    st.markdown(f"<h4 style='color: #64748B; margin-top: 15px;'>Top Private Colleges ({top_df['Institute'].nunique()} options)</h4>", unsafe_allow_html=True)
                                    render_insts(top_df)
                                            
                                if not other_df.empty:
                                    st.markdown("<br>", unsafe_allow_html=True)
                                    with st.expander(f"Explore More Private Colleges ({other_df['Institute'].nunique()} options)"):
                                        render_insts(other_df)
                            else:
                                st.markdown(f"<h4 style='color: #64748B; margin-top: 15px;'>{cat_name} ({cat_df['Institute'].nunique()} options)</h4>", unsafe_allow_html=True)
                                render_insts(cat_df)
                            
                    # Safe
                    safe_df = display_df[display_df['Status'] == 'Safe']
                    if not safe_df.empty:
                        with st.container():
                            st.markdown("<span id='safe-container'></span>", unsafe_allow_html=True)
                            st.markdown(f"<h3 id='safe-section' style='color:#15803D; margin-top:0px; margin-bottom: 5px;'><i class='fa-solid fa-circle'></i> SAFE ({len(safe_df)} options)</h3>", unsafe_allow_html=True)
                            display_category_expanders(safe_df, "#15803D")
                                
                    # Match
                    match_df = display_df[display_df['Status'] == 'Match']
                    if not match_df.empty:
                        with st.container():
                            st.markdown("<span id='match-container'></span>", unsafe_allow_html=True)
                            st.markdown(f"<h3 id='match-section' style='color:#F59E0B; margin-top:0px; margin-bottom: 5px;'><i class='fa-solid fa-circle'></i> MATCH ({len(match_df)} options)</h3>", unsafe_allow_html=True)
                            display_category_expanders(match_df, "#F59E0B")
                                
                    # Reach
                    reach_df = display_df[display_df['Status'] == 'Reach']
                    if not reach_df.empty:
                        with st.container():
                            st.markdown("<span id='reach-container'></span>", unsafe_allow_html=True)
                            st.markdown(f"<h3 id='reach-section' style='color:#EF4444; margin-top:0px; margin-bottom: 5px;'><i class='fa-solid fa-circle'></i> REACH ({len(reach_df)} options)</h3>", unsafe_allow_html=True)
                            display_category_expanders(reach_df, "#EF4444")

elif app_mode == "Guide":
    with st.container():
        st.markdown("<span class='outer-banner-marker'></span>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0;">
            <div>
                <h1 style="font-size: 32px; font-weight: 800; color: #0F172A; margin: 0 0 6px 0; padding: 0; letter-spacing: -0.5px;">User Guide</h1>
                <p style="font-size: 14px; color: #64748B; margin: 0; padding: 0; font-weight: 500;">How to use the WBJEE Predictions features.</p>
            </div>
            <span style="display: inline-flex; align-items: center; gap: 8px; background: #0EA5E9; color: #FFF; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);"><i class="fa-solid fa-book-open" style="color: #E0F2FE;"></i> Documentation</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<span class='inner-card-marker'></span>", unsafe_allow_html=True)
            st.markdown("""
            ### 📖 College Directory
            The **College Directory** allows you to browse historical opening and closing ranks for all participating institutes in WBJEE. 
            - Select your **Domicile / Quota** (Home State vs All India).
            - Choose a specific **Year** or leave it as "All Years" to see trend data.
            - Filter by **Category** (e.g. Open, OBC, SC) and **Seat Type**.
            - Click any column header in the table to sort!
            - You can **Generate a PDF Report** for any selected institute.

            ### 🔮 Rank Predictor
            The **Rank Predictor** uses an SVR (Support Vector Regression) machine learning model, trained on previous years' cutoff data, to predict your chances of admission.
            - Enter your **GMR Rank** and categories.
            - The model calculates a **Safe**, **Match**, and **Reach** margin based on Mean Absolute Deviation (MAD) of historical fluctuations.
            - **🟢 Safe:** Your rank comfortably clears the predicted cutoffs.
            - **🟡 Match:** Your rank is borderline; admission depends on this year's demand.
            - **🔴 Reach:** Admission is unlikely, but possible if cutoffs drop significantly.
            
            **Understanding the Results:**
            The results show predictions for Round 1 (R1), Round 2 (R2), and Round 3 (R3). The format `10,500 ('25: 12,000, '24: 11,000)` means the model predicts a cutoff of 10,500 for the upcoming year, and in parenthesis you can see the actual closing ranks from 2025 and 2024.
            """)

# ══════════════════════════════════════════════════════════════
#  NESTED HERO & FILTER SECTION
# ══════════════════════════════════════════════════════════════
# Use session state to determine layout BEFORE creating widgets
elif app_mode == "College Directory":
    current_quota = st.session_state.get("quota_select", ordered_quotas[0] if ordered_quotas else "All India")
    current_year = st.session_state.get("year_select", years[0] if years else "")

    if current_quota == "All India":
        st.markdown(css_icons_4, unsafe_allow_html=True)
    else:
        st.markdown(css_icons_5, unsafe_allow_html=True)

    with st.container():
        st.markdown("<span class='outer-banner-marker'></span>", unsafe_allow_html=True)
        # 1. Hero Content
        badge_text = f"{current_year} Cutoff Data &middot; {current_quota} Seats"
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0;">
            <div>
                <h1 style="font-size: 32px; font-weight: 800; color: #0F172A; margin: 0 0 6px 0; padding: 0; letter-spacing: -0.5px;">WBJEE College Directory</h1>
                <p style="font-size: 14px; color: #64748B; margin: 0; padding: 0; font-weight: 500;">Filter cutoffs by domicile, year, institute, program and more to find exact ranks easily!</p>
            </div>
            <span style="display: inline-flex; align-items: center; gap: 8px; background: #1E293B; color: #FFF; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"><i class="fa-solid fa-crown" style="color: #FBBF24;"></i> {badge_text}</span>
        </div>
        """, unsafe_allow_html=True)

        # 2. Nested Filter Card
        with st.container():
            st.markdown("<span class='inner-card-marker'></span>", unsafe_allow_html=True)
            if current_quota == "All India":
                cols = st.columns([1.2, 1, 2.5, 2])
                c_quota, c_year, c_inst, c_prog = cols
                c_cat = None
            else:
                cols = st.columns([1.2, 1.2, 1, 2.5, 2])
                c_quota, c_cat, c_year, c_inst, c_prog = cols
        
            # Dropdowns
            selected_quota = c_quota.selectbox("Domicile / Quota", options=ordered_quotas, key="quota_select")
        
            if c_cat:
                selected_category = c_cat.selectbox("Category", options=["--- All Categories ---"] + all_categories, key="cat_select")
            else:
                selected_category = "--- All Categories ---"
            
            selected_year = c_year.selectbox("Year", options=years, key="year_select")
        
            # Filter Logic
            if selected_year == "All Years":
                base_df = df[(df['Quota'] == selected_quota)]
                year_df = df
            else:
                base_df = df[(df['Quota'] == selected_quota) & (df['Year'] == str(selected_year))]
                year_df = df[df['Year'] == str(selected_year)]
            
            if selected_category != "--- All Categories ---":
                base_df = base_df[base_df['Category'] == selected_category]
        
            # Get all available institutes for the year, regardless of quota
            all_year_insts = sorted(list(year_df['Institute'].dropna().unique()), key=institute_sort_key)
        
            # Institutes valid for the specific selected quota and category
            valid_insts = set(base_df['Institute'].dropna().unique())
        
            # Insert category headers and dynamic "grey out" labels
            grouped_institutes = []
            inst_map = {}
            current_cat = -1
            for inst in all_year_insts:
                cat_id, cat_name = get_institute_category(inst)
                if cat_id != current_cat:
                    header = f"── {cat_name} ──"
                    grouped_institutes.append(header)
                    inst_map[header] = header
                    current_cat = cat_id
            
                display_str = inst
                if inst not in valid_insts:
                    if selected_quota == "All India":
                        display_str = f"🔒 {inst} (Home State Only)"
                    else:
                        display_str = f"🔒 {inst} (Not Available)"
            
                grouped_institutes.append(display_str)
                inst_map[display_str] = inst
            
            selected_display = c_inst.selectbox("Select Institute", options=["--- Select a College ---"] + grouped_institutes)
            selected_institute = inst_map.get(display_str := selected_display, "--- Select a College ---")
        
            college_df = pd.DataFrame()
            rounds = []
            if selected_institute != "--- Select a College ---" and not selected_institute.startswith("── ") and selected_institute in valid_insts:
                college_df = base_df[base_df['Institute'] == selected_institute]
                rounds = sorted(list(college_df['Round'].dropna().unique()))
        
            programs = sorted(list(college_df['Program'].dropna().unique())) if not college_df.empty else []
            selected_program = c_prog.selectbox("Program", options=["--- All Programs ---"] + programs)
        
            # Display the red warning if restricted
            if selected_institute != "--- Select a College ---" and not selected_institute.startswith("── "):
                if selected_institute not in valid_insts:
                    if selected_quota == "All India":
                        st.markdown("<p style='color: #DC2626; font-size: 13px; font-weight: 700; margin-top: 12px; margin-bottom: 0; text-align: right;'><i class='fa-solid fa-lock' style='margin-right: 6px;'></i>Only Available for Home state Students</p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='color: #DC2626; font-size: 13px; font-weight: 700; margin-top: 12px; margin-bottom: 0; text-align: right;'><i class='fa-solid fa-lock' style='margin-right: 6px;'></i>No seats available for this combination</p>", unsafe_allow_html=True)
            elif selected_institute.startswith("── "):
                st.markdown("<p style='color: #64748B; font-size: 13px; font-weight: 600; margin-top: 12px; margin-bottom: 0; text-align: right;'><i class='fa-solid fa-circle-info' style='margin-right: 6px;'></i>This is a category header. Select a college below it.</p>", unsafe_allow_html=True)


    # ══════════════════════════════════════════════════════════════
    #  SPACE BEFORE RESULTS
    # ══════════════════════════════════════════════════════════════
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    #  RESULTS SECTION
    # ══════════════════════════════════════════════════════════════
    if selected_institute != "--- Select a College ---" and not selected_institute.startswith("── ") and selected_institute in valid_insts and rounds:
    
        # 1. Single Row Layout: Title + Metrics
        col_title, col_metrics = st.columns([2.5, 1.5], gap="large", vertical_alignment="center")
    
        with col_title:
            title_col1, title_col2 = st.columns([3, 1], vertical_alignment="center")
            with title_col1:
                st.markdown(f"""
                <div class="results-left" style="margin-bottom: 0;">
                    <div class="results-icon"><i class="fa-solid fa-building-columns"></i></div>
                    <p class="results-title">{selected_institute}</p>
                </div>
                """, unsafe_allow_html=True)
            with title_col2:
                import re
                import base64
            
                with st.popover("📄 Export PDF", use_container_width=True):
                    with st.spinner("Generating..."):
                        pdf_bytes = generate_pdf(selected_institute, college_df, selected_program, selected_category)
                        safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', selected_institute[:30].strip())
                        b64 = base64.b64encode(pdf_bytes).decode()
                    
                        href = f'''
                        <a href="data:application/pdf;base64,{b64}" download="{safe_name}_Cutoffs.pdf" 
                           style="display: block; width: 100%; padding: 8px 0px; background-color: #10B981; 
                                  color: white; text-decoration: none; border-radius: 8px; font-weight: 600; text-align: center;
                                  box-shadow: 0 4px 6px rgba(21, 128, 61, 0.2); font-family: sans-serif;">
                            📥 Click Here to Save
                        </a>
                        '''
                        st.markdown(href, unsafe_allow_html=True)
        
        with col_metrics:
            # Calculate stats based on last available round for each program
            idx = college_df.groupby(['Year', 'Program', 'Category', 'Quota', 'Seat Type'])['Round'].idxmax()
            stat_df = college_df.loc[idx]
            
            clean_closing = stat_df['Closing Rank'].astype(str).str.extract(r'(\d+)')[0]
            closing_nums = pd.to_numeric(clean_closing, errors='coerce').dropna()
            avg_closing = f"{int(closing_nums.mean()):,}" if not closing_nums.empty else "N/A"
    
            st.markdown(f"""
            <div class="metrics-row" style="justify-content: flex-end;">
                <div class="m-card">
                    <div class="m-icon" style="background:#edf2ff; color:#4c6ef5;"><i class="fa-solid fa-users"></i></div>
                    <div class="m-text"><span>Total Programs</span><strong>{len(programs)}</strong></div>
                </div>
                <div class="m-card">
                    <div class="m-icon" style="background:#e8fdf5; color:#12b886;"><i class="fa-solid fa-chart-simple"></i></div>
                    <div class="m-text"><span>Avg. Closing Rank</span><strong>{avg_closing}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        
        if selected_year == "All Years" and not college_df.empty:
            st.markdown("<h4 style='color: #4338CA; margin-top: 16px; margin-bottom: 16px; font-size: 18px;'><i class='fa-solid fa-chart-line' style='margin-right: 8px;'></i>Cutoff Trends (Last Round)</h4>", unsafe_allow_html=True)
        
            # Get last round for each year-program-category-quota combination
            idx_trend = college_df.groupby(['Year', 'Program', 'Category', 'Quota', 'Seat Type'])['Round'].idxmax()
            trend_df = college_df.loc[idx_trend].copy()
        
            # Filter by selected program if any
            if selected_program != "--- All Programs ---":
                trend_df = trend_df[trend_df['Program'] == selected_program]
            
            # Clean Closing Rank to numeric
            trend_df['Closing Rank Num'] = pd.to_numeric(trend_df['Closing Rank'].astype(str).str.extract(r'(\d+)')[0], errors='coerce')
            trend_df = trend_df.dropna(subset=['Closing Rank Num'])
        
            if not trend_df.empty:
                # Create a label for each line
                if selected_program != "--- All Programs ---":
                    trend_df['Line Label'] = trend_df['Category']
                else:
                    if selected_category == "--- All Categories ---":
                        trend_df['Line Label'] = trend_df['Program'].str[:30] + " - " + trend_df['Category']
                    else:
                        trend_df['Line Label'] = trend_df['Program'].str[:40]
            
                # Create Plotly line chart
                trend_df = trend_df.sort_values('Year')
                fig = px.line(
                    trend_df,
                    x='Year',
                    y='Closing Rank Num',
                    color='Line Label',
                    markers=True,
                    labels={'Closing Rank Num': 'Closing Rank', 'Year': 'Year', 'Line Label': 'Category / Program'}
                )
                fig.update_layout(
                    yaxis=dict(autorange=True),
                    xaxis=dict(type='category'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""),
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=450
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

        cols_config = {
            "Program": st.column_config.TextColumn("Program", width="large"),
            "Category": st.column_config.TextColumn("Category", width="medium"),
            "Opening Rank": st.column_config.NumberColumn("Opening Rank", width="small", format="%,d"),
            "Closing Rank": st.column_config.NumberColumn("↑ Closing Rank", width="small", format="%,d"),
            "Quota": st.column_config.TextColumn("Quota", width="medium"),
            "Seat Type": st.column_config.TextColumn("Seat Type", width="medium"),
        }

        # Render each year
        available_years = sorted(college_df['Year'].astype(str).unique(), reverse=True) if selected_year == "All Years" else [str(selected_year)]
    
        if not available_years:
            st.info("No data available for this combination.")
        else:
            for y in available_years:
                year_df = college_df[college_df['Year'] == y].copy()
                if year_df.empty:
                    continue
                
                # Year Header and Round Selector side-by-side
                yh_col1, yh_col2 = st.columns([1, 1], vertical_alignment="center")
                with yh_col1:
                    st.markdown(f"<h4 style='color: #4338CA; margin-top: 8px; margin-bottom: 8px; font-size: 18px;'><i class='fa-regular fa-calendar-days' style='margin-right: 8px;'></i>{y} Cutoffs</h4>", unsafe_allow_html=True)
                
                with yh_col2:
                    # Dynamic round buttons for THIS year
                    y_rounds = sorted(list(year_df['Round'].dropna().unique()))
                    y_default_round = y_rounds[-1] if y_rounds else None
                    y_selected_round = st.segmented_control("Select Round", options=y_rounds, default=y_default_round, label_visibility="collapsed", key=f"round_select_{y}")
                
                if y_selected_round:
                    year_df = year_df[year_df['Round'] == y_selected_round]
                
                if selected_program != "--- All Programs ---":
                    year_df = year_df[year_df['Program'] == selected_program]
                
                if year_df.empty:
                    st.info(f"No data available for this combination in {y}.")
                    continue
                
                # Sort by Closing Rank ascending
                year_df['_sort'] = pd.to_numeric(year_df['Closing Rank'].astype(str).str.extract(r'(\d+)')[0], errors='coerce').fillna(np.inf)
                year_df = year_df.sort_values('_sort', ascending=True).drop(columns=['_sort'])
            
                display_cols = ['Program', 'Category', 'Opening Rank', 'Closing Rank', 'Quota', 'Seat Type']
                display_df = year_df[display_cols].copy()
            
                # Keep as numeric
                display_df['Opening Rank'] = pd.to_numeric(display_df['Opening Rank'], errors='coerce')
                display_df['Closing Rank'] = pd.to_numeric(display_df['Closing Rank'], errors='coerce')
            
                styled_df = display_df.style\
                    .format({"Opening Rank": "{:,.0f}", "Closing Rank": "{:,.0f}"}, na_rep="-")\
                    .set_properties(**{'font-weight': '600', 'color': '#0F172A'}, subset=['Program'])\
                    .set_properties(**{'font-family': 'monospace', 'font-size': '14px', 'color': '#065F46', 'font-weight': 'bold'}, subset=['Opening Rank'])\
                    .set_properties(**{'font-family': 'monospace', 'font-size': '14px', 'color': '#991B1B', 'font-weight': 'bold'}, subset=['Closing Rank'])
            
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=cols_config
                )
                st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)


    # ══════════════════════════════════════════════════════════════
#  JAVASCRIPT STYLING INJECTION (Guarantees Container Styles)
# ══════════════════════════════════════════════════════════════
components.html("""
<script>
    const nav = window.parent.document.getElementById('top-nav-marker');
    if (nav) {
        const navContainer = nav.closest('div[data-testid="stElementContainer"]');
        if (navContainer) {
            navContainer.style.position = 'sticky';
            navContainer.style.top = '50px';
            navContainer.style.zIndex = '999999';
        }
    }
    const outers = window.parent.document.querySelectorAll('.outer-banner-marker');
    outers.forEach(outer => {
        const container = outer.closest('div[data-testid="stVerticalBlock"]');
        if (container) {
            container.style.background = 'linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 40%, #ECFDF5 100%)';
            container.style.borderRadius = '24px';
            container.style.padding = '32px 40px';
            container.style.boxShadow = '0 4px 12px rgba(0,0,0,0.05)';
            container.style.gap = '0px';
        }
    });
    
    const inners = window.parent.document.querySelectorAll('.inner-card-marker');
    inners.forEach(inner => {
        const container = inner.closest('div[data-testid="stVerticalBlock"]');
        if (container) {
            container.style.backgroundColor = '#FFFFFF';
            container.style.borderRadius = '16px';
            container.style.padding = '20px 28px';
            container.style.boxShadow = '0 8px 32px rgba(0,0,0,0.05)';
            container.style.border = '1px solid rgba(226, 232, 240, 0.8)';
            container.style.marginTop = '28px';
        }
    });
    
    // MutationObserver to forcefully disable click events on dropdown category headers
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1 && node.tagName === "DIV") {
                    const listboxes = node.querySelectorAll('ul[role="listbox"]');
                    listboxes.forEach(ul => {
                        const items = ul.querySelectorAll('li[role="option"]');
                        items.forEach(li => {
                            if (li.innerText && li.innerText.includes('── ')) {
                                li.style.pointerEvents = 'none';
                                li.style.cursor = 'default';
                                li.style.background = '#F8FAFC';
                                li.style.color = '#64748B';
                                li.style.fontWeight = '800';
                                li.style.fontSize = '12px';
                                li.style.letterSpacing = '0.5px';
                                li.style.borderBottom = '1px solid #E2E8F0';
                                li.style.paddingTop = '12px';
                                li.style.paddingBottom = '8px';
                            }
                        });
                    });
                }
            });
        });
    });
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
</script>
""", height=0)