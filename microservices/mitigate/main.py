import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from fairlearn.metrics import MetricFrame, demographic_parity_difference, selection_rate
from fairlearn.postprocessing import ThresholdOptimizer
from fairlearn.reductions import ExponentiatedGradient, DemographicParity
from shared.data import get_dataset, get_config

app = FastAPI(
    title="Fairness Mitigation Engine",
    description="Automated de-biasing via Preprocessing, In-processing, and Post-processing.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/mitigate")
def mitigate_bias(strategy: str = Query("postprocessing", enum=["preprocessing", "inprocessing", "postprocessing"])):
    """
    Automated De-biasing Pipeline:
    - Preprocessing: Sample re-weighing to balance demographics.
    - In-processing: Fairness constraints directly in the loss function (Exponentiated Gradient).
    - Post-processing: Threshold adjustment (ThresholdOptimizer).
    """
    df = get_dataset()
    config = get_config()
    target_col = config.get('target_col', 'Income')
    sensitive_col = config.get('sensitive_col', 'Sex')
    
    # Prepare Data
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
    
    X_train, X_test, y_train, y_test, A_train, A_test = train_test_split(
        X_encoded, y, A, test_size=0.3, random_state=42
    )
    
    # 1. Baseline Model
    base_estimator = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
    base_estimator.fit(X_train, y_train)
    y_pred_base = base_estimator.predict(X_test)
    
    base_acc = accuracy_score(y_test, y_pred_base)
    base_dp_diff = demographic_parity_difference(y_test, y_pred_base, sensitive_features=A_test)
    
    # 2. Mitigation Selection
    strategy_label = "Post-processing (Threshold Optimizer)"
    
    if strategy == "preprocessing":
        strategy_label = "Preprocessing (Sample Re-weighing)"
        # Simple Re-weighing implementation
        # W = P(Y)P(A) / P(Y,A)
        weights = _calculate_weights(y_train, A_train)
        mitigated_model = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
        mitigated_model.fit(X_train, y_train, sample_weight=weights)
        y_pred_mitigated = mitigated_model.predict(X_test)
        
    elif strategy == "inprocessing":
        strategy_label = "In-processing (Fairness Constraints)"
        # Exponentiated Gradient approach
        mitigator = ExponentiatedGradient(
            estimator=RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42),
            constraints=DemographicParity()
        )
        mitigator.fit(X_train, y_train, sensitive_features=A_train)
        y_pred_mitigated = mitigator.predict(X_test)
        
    else: # postprocessing
        postprocess_est = ThresholdOptimizer(
            estimator=base_estimator,
            constraints="demographic_parity",
            predict_method='predict_proba',
            prefit=True
        )
        postprocess_est.fit(X_train, y_train, sensitive_features=A_train)
        y_pred_mitigated = postprocess_est.predict(X_test, sensitive_features=A_test)
    
    mit_acc = accuracy_score(y_test, y_pred_mitigated)
    mit_dp_diff = demographic_parity_difference(y_test, y_pred_mitigated, sensitive_features=A_test)
    
    # Group stats for charting (Positive Selection Rate)
    mf_base = MetricFrame(metrics=selection_rate, y_true=y_test, y_pred=y_pred_base, sensitive_features=A_test)
    mf_mit = MetricFrame(metrics=selection_rate, y_true=y_test, y_pred=y_pred_mitigated, sensitive_features=A_test)
    
    groups = list(mf_base.by_group.index)
    
    # Try to map to privileged/unprivileged based on common knowledge
    priv_group = "Male" if "Male" in groups else groups[0] if groups else "Privileged"
    unpriv_group = "Female" if "Female" in groups else (groups[1] if len(groups) > 1 else "Unprivileged")

    charts_before = [{
        "category": "Pre-Mitigation",
        "privileged": float(mf_base.by_group.get(priv_group, 0)),
        "unprivileged": float(mf_base.by_group.get(unpriv_group, 0))
    }]

    charts_after = [{
        "category": "Post-Mitigation",
        "privileged": float(mf_mit.by_group.get(priv_group, 0)),
        "unprivileged": float(mf_mit.by_group.get(unpriv_group, 0))
    }]

    return {
        "strategy": strategy_label,
        "metrics": {
            "base_acc": round(base_acc * 100, 1),
            "base_dp": round(base_dp_diff, 3),
            "mit_acc": round(mit_acc * 100, 1),
            "mit_dp": round(mit_dp_diff, 3)
        },
        "charts_before": charts_before,
        "charts_after": charts_after
    }

def _calculate_weights(y, A):
    df = pd.DataFrame({'y': y, 'A': A})
    n = len(df)
    weights = np.ones(n)
    for y_val in [0, 1]:
        for a_val in df['A'].unique():
            n_ya = len(df[(df['y'] == y_val) & (df['A'] == a_val)])
            n_y = len(df[df['y'] == y_val])
            n_a = len(df[df['A'] == a_val])
            if n_ya > 0:
                weight = (n_y * n_a) / (n * n_ya)
                weights[(df['y'] == y_val) & (df['A'] == a_val)] = weight
    return weights
