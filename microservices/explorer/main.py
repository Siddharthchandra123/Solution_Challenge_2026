import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.data import get_dataset, get_config

app = FastAPI(
    title="Fairness Explorer & Proxy Engine",
    description="Statistical discovery of demographic proxies and correlation heatmaps.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/explorer", summary="Retrieve Correlation and Scatter Plot Data", 
         description="Calculates Cramer's V for categorical proxies and Pearson correlation for numeric features.")
def get_explorer_data():
    df = get_dataset()
    config = get_config()
    target_col = config.get('target_col', 'Income')
    sensitive_col = config.get('sensitive_col', 'Sex')
    
    # Check if Score metric or standard experience proxy is available
    feature1 = "Experience" if "Experience" in df.columns else df.columns[0]
    score_col = "Income_Score" if "Income_Score" in df.columns else df.columns[-1]
    
    # 1. Provide a subset of 100 points for the React Scatter plot
    scatter_subset = df.sample(min(100, len(df)), random_state=42)
    scatter_data = []
    
    # Safe plotting fallbacks
    for _, row in scatter_subset.iterrows():
        try:
            x_val = float(row[feature1])
        except:
            x_val = 0
        try:
            y_val = float(row[score_col])
        except:
            y_val = 0
            
        scatter_data.append({
            "x": x_val,
            "y": round(y_val, 2),
            "group": str(row[sensitive_col])
        })
        
    correlations = []
    
    try:
        # Numeric vs Numeric (Pearson)
        corr_exp_income = df[feature1].corr(df[score_col])
        correlations.append({"feature1": feature1, "feature2": score_col, "correlation": abs(corr_exp_income)})
    except Exception:
        pass
    
    # Categorical vs Categorical (Cramer's V)
    try:
        xtab = pd.crosstab(df[sensitive_col], df[target_col])
        chi2, _, _, _ = chi2_contingency(xtab)
        n = xtab.sum().sum()
        min_dim = min(xtab.shape) - 1
        cramers_v = np.sqrt((chi2 / n) / min_dim) if min_dim > 0 and n > 0 else 0
        
        correlations.append({"feature1": sensitive_col, "feature2": f"{target_col} (Categorical)", "correlation": cramers_v})
    except Exception:
        cramers_v = 0
    
    # Sort
    correlations = sorted(correlations, key=lambda d: d['correlation'], reverse=True)
    
    return {
        "scatter_data": scatter_data,
        "correlations": correlations,
        "insights": [
            {
                "type": "warning",
                "message": f"Proxy Detected: {sensitive_col} and {target_col} have a statistical correlation (Cramer's V: {cramers_v:.2f}). Removing '{sensitive_col}' from the model will not erase bias, as other features may act as proxies."
            }
        ]
    }
