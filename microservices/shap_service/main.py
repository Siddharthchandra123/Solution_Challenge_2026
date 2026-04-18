import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import shap
from shared.data import get_dataset, get_config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/shap")
def compute_shap():
    df = get_dataset()
    config = get_config()
    target_col = config.get('target_col', 'Income')
    sensitive_col = config.get('sensitive_col', 'Sex')
    
    df_clean = df.dropna().copy()
    le_target = LabelEncoder()
    y_encoded = le_target.fit_transform(df_clean[target_col].astype(str))
    if len(np.unique(y_encoded)) > 2:
        y = (y_encoded > np.median(y_encoded)).astype(int)
    else:
        y = (y_encoded == y_encoded.max()).astype(int)
    A = df_clean[sensitive_col].astype(str)
    X = df_clean.drop(columns=[target_col, 'Income_Score'], errors='ignore')
    X_encoded = pd.get_dummies(X, drop_first=True)
    
    # Subsample deeply for rapid API response (max ~150 rows)
    X_sub = X_encoded.sample(n=min(150, len(X_encoded)), random_state=42)
    y_sub = y[X_sub.index]
    
    model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    model.fit(X_sub, y_sub)
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sub)
    
    if isinstance(shap_values, list):
        shap_vals_true = shap_values[1] 
    elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
        shap_vals_true = shap_values[:, :, 1]
    else:
        shap_vals_true = shap_values

    # Force 2D
    if len(shap_vals_true.shape) > 2:
        shap_vals_true = shap_vals_true.reshape(shap_vals_true.shape[0], -1)

    global_shaps = np.abs(shap_vals_true).mean(0)
    mean_direction = np.mean(shap_vals_true, axis=0)
    
    features = list(X_sub.columns)
    global_results = []
    
    for i, feature in enumerate(features):
        direction = "positive" if mean_direction[i] > 0 else "negative"
        val = round(float(global_shaps[i]), 3)
        global_results.append({
            "feature": feature,
            "importance": val if direction == "positive" else -val,
            "direction": direction
        })
        
    global_results = sorted(global_results, key=lambda x: x['importance'], reverse=True)
    
    return {
        "global": global_results
    }
