import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from fairlearn.metrics import demographic_parity_difference
from shared.data import get_dataset, get_config

app = FastAPI(
    title="Vertex AI Drift Monitor",
    description="Real-time tracking of model accuracy, fairness disparity, and feature attribution skew.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/monitor", summary="Fetch Live Drift Analytics", 
         description="Streams time-series data of model performance and bias metrics over a simulated 24-hour window.")
def get_monitor_data():
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
    
    # Train base mock model 
    X_train, X_live, y_train, y_live, A_train, A_live = train_test_split(X_encoded, y, A, test_size=0.7, random_state=42)
    model = RandomForestClassifier(n_estimators=30, max_depth=8, random_state=42)
    model.fit(X_train, y_train)
    
    batches = 24
    batch_size = max(1, len(X_live) // batches)
    
    timeseries_data = []
    now = datetime.datetime.now()
    
    for i in range(batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(X_live))
        
        X_batch = X_live.iloc[start_idx:end_idx]
        y_batch = y_live[start_idx:end_idx]
        A_batch = A_live.iloc[start_idx:end_idx]
        
        if len(y_batch) == 0:
            continue
            
        y_pred = model.predict(X_batch)
        acc = accuracy_score(y_batch, y_pred)
        
        if len(np.unique(A_batch)) > 1:
            dp_diff = demographic_parity_difference(y_batch, y_pred, sensitive_features=A_batch)
            # Smooth artificial drift over 24h for demonstration
            dp_diff = dp_diff + (i * 0.007)
        else:
            dp_diff = 0.0
        # Simulate Vertex AI Model Monitoring Feature Skew (L-infinity Distance)
        vertex_skew = max(0.01, 0.05 + (i * 0.003) + np.random.normal(0, 0.01))
            
        batch_time = now - datetime.timedelta(hours=(batches - 1 - i))
        
        timeseries_data.append({
            "time": batch_time.strftime("%I:%M %p"),
            "disparity": round(dp_diff, 3),
            "accuracy": round(acc, 3),
            "vertex_skew": round(vertex_skew, 3)
        })
        
    return {
        "status": "healthy",
        "current_disparity": timeseries_data[-1]['disparity'] if timeseries_data else 0.1,
        "current_accuracy": timeseries_data[-1]['accuracy'] if timeseries_data else 0.85,
        "current_skew": timeseries_data[-1]['vertex_skew'] if timeseries_data else 0.05,
        "timeseries": timeseries_data
    }
