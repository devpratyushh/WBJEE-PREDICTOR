import pandas as pd

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update Metrics to count Institutes instead of branches
old_metrics = """                            safe_count = len(res_df[res_df['Status'] == 'Safe'])
                            match_count = len(res_df[res_df['Status'] == 'Match'])
                            reach_count = len(res_df[res_df['Status'] == 'Reach'])
                            total_count = len(res_df)"""
new_metrics = """                            safe_count = res_df[res_df['Status'] == 'Safe']['Institute'].nunique()
                            match_count = res_df[res_df['Status'] == 'Match']['Institute'].nunique()
                            reach_count = res_df[res_df['Status'] == 'Reach']['Institute'].nunique()
                            total_count = res_df['Institute'].nunique()"""
code = code.replace(old_metrics, new_metrics)

# 2. Update Dark Green for Safe
old_safe_color = '#10B981'
new_safe_color = '#15803D'
code = code.replace('display_category_expanders(safe_df, "#10B981")', f'display_category_expanders(safe_df, "{new_safe_color}")')
code = code.replace(f"<h3 style='color:#10B981;", f"<h3 style='color:{new_safe_color};")
code = code.replace('rgba(16, 185, 129', 'rgba(21, 128, 61')


# 3. Split the R1, R2, R3 columns into prediction and history in display_category_expanders
target_df = """                                        show_df = inst_df[['Program', 'Quota', 'R1', 'R2', 'R3']].copy()
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

replacement_df = """                                        show_df = inst_df[['Program', 'Quota']].copy()
                                        
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
                                        
                                        st.dataframe(styled_df, use_container_width=True, hide_index=True)"""

code = code.replace(target_df, replacement_df)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
