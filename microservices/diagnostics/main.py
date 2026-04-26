import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.data import get_dataset, get_config

app = FastAPI(
    title="Data Diagnostics & Quality Profiler",
    description="Mathematical dissection of datasets for completeness and protected attribute coverage.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/diagnostics", summary="Identify Data Symmetries and Gaps", 
         description="Scans all features for missingness, identifies protected attributes, and suggests imputation strategies.")
def get_diagnostics_data():
    df = get_dataset()
    config = get_config()
    target_col = config.get('target_col', 'Income')
    sensitive_col = config.get('sensitive_col', 'Sex')
    
    total_records = len(df)
    features = list(df.columns)
    
    # 1. Feature Distribution (Missing vs Present)
    feature_dist = []
    total_missing = 0
    total_cells = total_records * len(features)
    
    for col in features:
        missing_count = int(df[col].isna().sum())
        total_missing += missing_count
        feature_dist.append({
            "feature": col,
            "count": total_records - missing_count,
            "missing": missing_count
        })
        
    # 2. Data Quality Stats (Donut Chart)
    missing_pct = round((total_missing / total_cells) * 100, 2) if total_cells > 0 else 0
    clean_pct = round(100 - missing_pct, 2)
    
    quality_stats = [
        {"name": "Complete", "value": clean_pct, "color": "oklch(0.70 0.18 160)"},
        {"name": "Missing", "value": missing_pct, "color": "oklch(0.75 0.18 65)"},
        {"name": "Invalid", "value": 0.0, "color": "oklch(0.55 0.22 30)"}
    ]
    
    # 3. Protected Attributes Detection
    KNOWN_PROTECTED_TERMS = [
        "sex", "gender", "race", "ethnicity", "age", "religion", 
        "national origin", "disability", "marital", "zip", "location"
    ]
    
    protected_attrs = []
    
    for col in df.columns:
        col_lower = col.lower()
        # Detect if it's the configured sensitive column OR if it matches common protected keywords
        is_protected = (col == sensitive_col) or any(term in col_lower for term in KNOWN_PROTECTED_TERMS)
        
        if is_protected:
            coverage = round((1 - (df[col].isna().sum() / total_records)) * 100, 1)
            groups = df[col].dropna().unique().tolist()
            if len(groups) > 5:
                # Group numeric attributes into buckets for display
                groups = ["Quartile 1", "Quartile 2", "Quartile 3", "Quartile 4"]
            else:
                groups = [str(g) for g in groups]
                
            protected_attrs.append({
                "attribute": col,
                "groups": groups,
                "coverage": coverage
            })
            
    # 4. Warnings Generation
    warnings = []
    for col in df.columns:
        if df[col].isna().sum() > 0:
            warnings.append(f"Attribute '{col}' has {int(df[col].isna().sum())} missing values. Consider K-Nearest Neighbor imputation.")
        
    return {
        "records": total_records,
        "feature_count": len(features),
        "quality_stats": quality_stats,
        "feature_dist": feature_dist,
        "protected_attributes": protected_attrs,
        "warnings": warnings
    }
