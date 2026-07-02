import pandas as pd
import numpy as np
from sklearn.svm import SVR
import glob
import os
import streamlit as st
import warnings

# Suppress sklearn warnings for clean UI
warnings.filterwarnings('ignore')

@st.cache_data(show_spinner=False)
def load_and_train_predictor():
    """
    Loads historical CSV data, groups into slots, 
    and trains the SVR models to output a consolidated predictions DataFrame.
    """
    pred_file = 'data/predictions_2026.csv'
    if os.path.exists(pred_file):
        return pd.read_csv(pred_file)
        
    data_files = glob.glob('data/*.csv')
    data_files = [f for f in data_files if 'predictions' not in f]
    df_list = []
    for file in data_files:
        year_str = os.path.basename(file).split('.')[0]
        try:
            year = int(year_str)
            df = pd.read_csv(file)
            df['Year'] = year
            df_list.append(df)
        except:
            pass
            
    if not df_list:
        return pd.DataFrame()
        
    full_df = pd.concat(df_list, ignore_index=True)
    
    if 'Seat Type' not in full_df.columns:
        full_df['Seat Type'] = 'WBJEE Seats'
    else:
        full_df['Seat Type'] = full_df['Seat Type'].fillna('WBJEE Seats')
        
    full_df['Closing Rank Num'] = pd.to_numeric(full_df['Closing Rank'].astype(str).str.extract(r'(\d+)')[0], errors='coerce')
    full_df = full_df.dropna(subset=['Closing Rank Num'])
    
    # Parse round numbers (assuming 'Round 1', 'Round 2', etc.)
    full_df['Round Num'] = pd.to_numeric(full_df['Round'].astype(str).str.extract(r'(\d+)')[0], errors='coerce')
    
    slot_cols = ['Institute', 'Program', 'Quota', 'Category', 'Seat Type']
    results = []
    
    grouped = full_df.groupby(slot_cols)
    target_year = 2026
    
    for name, group in grouped:
        institute, program, quota, category, seat_type = name
        
        # Get Final Round ranks per year (for classification and sorting)
        idx_final = group.groupby('Year')['Round Num'].idxmax()
        final_ranks = group.loc[idx_final].set_index('Year')['Closing Rank Num'].sort_index()
        
        # Get Round 1 ranks per year
        r1_df = group[group['Round Num'] == 1]
        r1_ranks = r1_df.set_index('Year')['Closing Rank Num'].sort_index()
        
        if len(final_ranks) == 0:
            continue
            
        # 1. Year-Trend (SVR on Final Round)
        y_final = final_ranks.values
        X_final = (final_ranks.index.values - 2020).reshape(-1, 1)
        
        if len(y_final) >= 3:
            model_final = SVR(kernel='rbf', C=1000, gamma=0.1, epsilon=10)
            model_final.fit(X_final, y_final)
            pred_final_trend = model_final.predict([[target_year - 2020]])[0]
        else:
            pred_final_trend = np.median(y_final)
            
        # 2. Round-Progression Ratio Blend
        if len(r1_ranks) > 0 and len(r1_ranks) == len(final_ranks):
            y_r1 = r1_ranks.values
            X_r1 = (r1_ranks.index.values - 2020).reshape(-1, 1)
            
            if len(y_r1) >= 3:
                model_r1 = SVR(kernel='rbf', C=1000, gamma=0.1, epsilon=10)
                model_r1.fit(X_r1, y_r1)
                pred_r1_trend = model_r1.predict([[target_year - 2020]])[0]
            else:
                pred_r1_trend = np.median(y_r1)
                
            ratios = final_ranks / r1_ranks
            median_ratio = ratios.median()
            
            if pd.isna(median_ratio) or median_ratio < 1.0:
                median_ratio = 1.0
                
            ratio_based_pred = pred_r1_trend * median_ratio
            final_pred_rank = (pred_final_trend + ratio_based_pred) / 2.0
        else:
            final_pred_rank = pred_final_trend
            
        final_pred_rank = max(1, final_pred_rank)
            
        # 3. Confidence Intervals (MAD)
        median_rank = np.median(y_final)
        mad = np.median(np.abs(y_final - median_rank))
        mad = max(mad, 100) # Minimum buffer of 100 ranks
        
        # 4. Compute display strings for R1, R2, R3
        r_displays = {1: "-", 2: "-", 3: "-"}
        for r_num in [1, 2, 3]:
            r_df_cur = group[group['Round Num'] == r_num]
            if not r_df_cur.empty:
                r_ranks_cur = r_df_cur.set_index('Year')['Closing Rank Num'].sort_index()
                years = r_ranks_cur.index.values
                y_hist = r_ranks_cur.values
                
                if len(y_hist) >= 3:
                    mdl = SVR(kernel='rbf', C=1000, gamma=0.1, epsilon=10)
                    X = (years - 2020).reshape(-1, 1)
                    mdl.fit(X, y_hist)
                    pred_r = int(max(1, mdl.predict([[target_year - 2020]])[0]))
                else:
                    pred_r = int(max(1, np.median(y_hist)))
                    
                hist_parts = []
                for y, v in zip(years[::-1], y_hist[::-1]): 
                    hist_parts.append(f"'{str(y)[-2:]}: {int(v):,}")
                hist_str = ", ".join(hist_parts)
                r_displays[r_num] = f"{pred_r:,} ({hist_str})"
        
        results.append({
            'Institute': institute,
            'Program': program,
            'Quota': quota,
            'Category': category,
            'Seat Type': seat_type,
            'Predicted Rank': int(final_pred_rank),
            'Safe Limit': int(max(1, final_pred_rank - mad)),
            'Match Upper Limit': int(final_pred_rank + mad),
            'Reach Upper Limit': int(final_pred_rank + (1.5 * mad)),
            'R1': r_displays[1],
            'R2': r_displays[2],
            'R3': r_displays[3]
        })
        
    res_df = pd.DataFrame(results)
    res_df.to_csv(pred_file, index=False)
    return res_df

# 2026 category mapping: new unified names → old data names
CATEGORY_2026_MAP = {
    "OBC (OBC-NCL)": ["OBC - A", "OBC - B"],
    "OBC (PwD)": ["OBC - A (PwD)", "OBC - B (PwD)"],
}

def predict_colleges(rank, quota, category, seat_type, pred_df):
    """
    Filters predictions based on student inputs and returns a DataFrame with 'Safe', 'Match', 'Reach' status.
    """
    if pred_df.empty:
        return pd.DataFrame()
    
    # Expand 2026 unified categories to old data names
    data_categories = CATEGORY_2026_MAP.get(category, [category])
        
    if quota == "Home State":
        # Home state students are eligible for Home State seats (with their category) 
        # AND All India seats (which are always Open category)
        df = pred_df[
            ((pred_df['Quota'] == "Home State") & (pred_df['Category'].isin(data_categories)) & (pred_df['Seat Type'] == seat_type)) |
            ((pred_df['Quota'] == "All India") & (pred_df['Category'] == "Open") & (pred_df['Seat Type'] == seat_type))
        ].copy()
    else:
        df = pred_df[(pred_df['Quota'] == quota) & 
                     (pred_df['Category'].isin(data_categories)) & 
                     (pred_df['Seat Type'] == seat_type)].copy()
                 
    if df.empty:
        return df
    
    # ── 2026 Policy Correction: Home State Open seats increased ──
    # OBC reservation dropped from 17% (OBC-A 10% + OBC-B 7%) → 7% (unified OBC-NCL).
    # ~10% of Home State seats shifted to Open/General pool.
    # Only affects Home State quota — All India is a separate fixed ~15% pool, always unreserved.
    OPEN_SEAT_CORRECTION = 1.18
    open_home_mask = df['Category'].isin(['Open', 'Open (PwD)']) & (df['Quota'] == 'Home State')
    if open_home_mask.any():
        for col in ['Predicted Rank', 'Safe Limit', 'Match Upper Limit', 'Reach Upper Limit']:
            if col in df.columns:
                df.loc[open_home_mask, col] = (df.loc[open_home_mask, col] * OPEN_SEAT_CORRECTION).astype(int)
    
    df['Status'] = 'Unlikely'
    
    # Lower rank number means a better rank! 
    # E.g., Rank 1000 is better than 5000.
    
    # Safe: My rank is less than or equal to the Safe Limit (I am well within the cutoff)
    df.loc[rank <= df['Safe Limit'], 'Status'] = 'Safe'
    
    # Match: My rank is between Safe Limit and Match Upper Limit
    df.loc[(rank > df['Safe Limit']) & (rank <= df['Match Upper Limit']), 'Status'] = 'Match'
    
    # Reach: My rank is slightly worse than Match Upper Limit, but within Reach limit
    df.loc[(rank > df['Match Upper Limit']) & (rank <= df['Reach Upper Limit']), 'Status'] = 'Reach'
    
    final_df = df[df['Status'] != 'Unlikely'].copy()
    final_df = final_df.sort_values('Predicted Rank', ascending=True)
    return final_df
