import re

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Inject CSS for expander bold titles and dotted containers
css_injection = """
/* Expander Titles Bold */
div[data-testid="stExpander"] summary p {
    font-weight: 800 !important;
    color: #0F172A !important;
}
/* Dotted Status Containers */
div[data-testid="stVerticalBlock"]:has(> div.element-container > div > span#safe-container) {
    border: 2px dashed rgba(16, 185, 129, 0.5) !important;
    padding: 20px !important;
    border-radius: 12px !important;
    background: rgba(16, 185, 129, 0.03) !important;
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
"""
code = code.replace('div[data-testid="stExpander"] details {', css_injection + '\ndiv[data-testid="stExpander"] details {')


# 2. Modify `display_category_expanders` signature and DataFrame logic
target_func = """                    def display_category_expanders(sub_df):"""
replacement_func = """                    def display_category_expanders(sub_df, status_color):"""
code = code.replace(target_func, replacement_func)

target_df = """                                        show_df = inst_df[['Program', 'Quota', 'R1', 'R2', 'R3']].copy()
                                        st.dataframe(show_df, use_container_width=True, hide_index=True)"""
replacement_df = """                                        show_df = inst_df[['Program', 'Quota', 'R1', 'R2', 'R3']].copy()
                                        show_df = show_df.rename(columns={
                                            'R1': '2026 R1 Predictions (Past year data)',
                                            'R2': '2026 R2 Predictions (Past year data)',
                                            'R3': '2026 R3 Predictions (Past year data)'
                                        })
                                        styled_df = show_df.style.set_properties(
                                            **{'font-weight': 'bold', 'color': status_color}, 
                                            subset=['2026 R1 Predictions (Past year data)', '2026 R2 Predictions (Past year data)', '2026 R3 Predictions (Past year data)']
                                        )
                                        st.dataframe(styled_df, use_container_width=True, hide_index=True)"""
code = code.replace(target_df, replacement_df)


# 3. Encapsulate metrics and filters inside banner
target_metrics = """                    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
                            
                    safe_count = len(res_df[res_df['Status'] == 'Safe'])"""
replacement_metrics = """                    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
                            
                    with st.container():
                        st.markdown("<span class='outer-banner-marker'></span>", unsafe_allow_html=True)
                        with st.container():
                            st.markdown("<span class='inner-card-marker'></span>", unsafe_allow_html=True)
                            
                            safe_count = len(res_df[res_df['Status'] == 'Safe'])"""
code = code.replace(target_metrics, replacement_metrics)


# 4. Wrap Safe/Match/Reach outputs in dashed containers and call display function with color
# Safe
safe_target = """                    # Safe
                    safe_df = display_df[display_df['Status'] == 'Safe']
                    if not safe_df.empty:
                        st.markdown(f"<h3 style='color:#10B981; margin-top:30px; margin-bottom: 5px;'><i class='fa-solid fa-circle'></i> SAFE ({len(safe_df)} options)</h3>", unsafe_allow_html=True)
                        display_category_expanders(safe_df)"""
safe_replace = """                    # Safe
                    safe_df = display_df[display_df['Status'] == 'Safe']
                    if not safe_df.empty:
                        with st.container():
                            st.markdown("<span id='safe-container'></span>", unsafe_allow_html=True)
                            st.markdown(f"<h3 style='color:#10B981; margin-top:0px; margin-bottom: 5px;'><i class='fa-solid fa-circle'></i> SAFE ({len(safe_df)} options)</h3>", unsafe_allow_html=True)
                            display_category_expanders(safe_df, "#10B981")"""
code = code.replace(safe_target, safe_replace)

# Match
match_target = """                    # Match
                    match_df = display_df[display_df['Status'] == 'Match']
                    if not match_df.empty:
                        st.markdown(f"<h3 style='color:#F59E0B; margin-top:30px; margin-bottom: 5px;'><i class='fa-solid fa-circle'></i> MATCH ({len(match_df)} options)</h3>", unsafe_allow_html=True)
                        display_category_expanders(match_df)"""
match_replace = """                    # Match
                    match_df = display_df[display_df['Status'] == 'Match']
                    if not match_df.empty:
                        with st.container():
                            st.markdown("<span id='match-container'></span>", unsafe_allow_html=True)
                            st.markdown(f"<h3 style='color:#F59E0B; margin-top:0px; margin-bottom: 5px;'><i class='fa-solid fa-circle'></i> MATCH ({len(match_df)} options)</h3>", unsafe_allow_html=True)
                            display_category_expanders(match_df, "#F59E0B")"""
code = code.replace(match_target, match_replace)

# Reach
reach_target = """                    # Reach
                    reach_df = display_df[display_df['Status'] == 'Reach']
                    if not reach_df.empty:
                        st.markdown(f"<h3 style='color:#EF4444; margin-top:30px; margin-bottom: 5px;'><i class='fa-solid fa-circle'></i> REACH ({len(reach_df)} options)</h3>", unsafe_allow_html=True)
                        display_category_expanders(reach_df)"""
reach_replace = """                    # Reach
                    reach_df = display_df[display_df['Status'] == 'Reach']
                    if not reach_df.empty:
                        with st.container():
                            st.markdown("<span id='reach-container'></span>", unsafe_allow_html=True)
                            st.markdown(f"<h3 style='color:#EF4444; margin-top:0px; margin-bottom: 5px;'><i class='fa-solid fa-circle'></i> REACH ({len(reach_df)} options)</h3>", unsafe_allow_html=True)
                            display_category_expanders(reach_df, "#EF4444")"""
code = code.replace(reach_target, reach_replace)


with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
