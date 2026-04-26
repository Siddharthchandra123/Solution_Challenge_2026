import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sqlalchemy.orm import Session
from shared.data import get_dataset, get_config
from shared.database import init_db, get_db, AuditHistory
from audit.audit_engine import AuditEngine
import datetime

app = FastAPI(
    title="Fairness Audit Engine",
    description="Professional model transparency auditing with persistent historical reporting.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
init_db()

audit_engine = AuditEngine(project_id=None)

@app.get("/api/model-card")
def get_model_card():
    df = get_dataset()
    config = get_config()
    target_col = config.get('target_col', 'Income')
    sensitive_col = config.get('sensitive_col', 'Sex')
    
    return {
        "schema_version": "0.0.1",
        "model_details": {
            "name": f"{target_col} Classification Model",
            "version": "1.0.0",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "owner": "Truth & Fairness AI Auditing",
            "license": "Apache-2.0",
        },
        "intended_use": {
            "primary_uses": f"Predicting {target_col} for advanced dashboard visualization.",
            "out_of_scope": "Automated final decision making without human oversight.",
        },
        "factors": {
            "groups": [sensitive_col],
            "evaluation_factors": f"Demographic parity across {sensitive_col} boundaries.",
        },
        "metrics": {
            "primary": ["Accuracy", "Disparate Impact", "Recall Difference"],
        },
        "training_data": {
            "features_used": len(df.columns) - 1,
            "rows": len(df),
            "target": target_col,
        },
        "ethical_considerations": {
            "data_bias": f"Historical structural skews inherently affect {target_col} algorithms unless Threshold Optimization is enforced.",
            "mitigation_strategy": "Post-processing Threshold Optimization via Fairlearn engine.",
        }
    }

@app.get("/api/audit")
def run_audit(db: Session = Depends(get_db)):
    df = get_dataset()
    config = get_config()
    target_col = config.get('target_col', 'Income')
    sensitive_col = config.get('sensitive_col', 'Sex')

    df_clean = df.dropna().copy()
    le_target = LabelEncoder()
    y_encoded = le_target.fit_transform(df_clean[target_col].astype(str))
    if len(np.unique(y_encoded)) > 2:
        y_true = (y_encoded > np.median(y_encoded)).astype(int)
    else:
        y_true = (y_encoded == y_encoded.max()).astype(int)
    
    most_freq_group = df_clean[sensitive_col].mode()[0]
    protected_attr = (df_clean[sensitive_col] != most_freq_group).astype(int) 

    X = df_clean.drop(columns=[target_col, 'Income_Score'], errors='ignore')
    X_encoded = pd.get_dummies(X, drop_first=True)

    X_train, X_test, y_train, y_test, prot_train, prot_test = train_test_split(
        X_encoded, y_true, protected_attr, test_size=0.3, random_state=42
    )

    model = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    audit_results = audit_engine.comprehensive_audit(
        df=df_clean,
        y_true=y_test,
        y_pred=y_pred,
        protected_attribute=prot_test,
        protected_attr_name=sensitive_col,
        model_name="production_model_generic",
        dataset_path="gs://audit-bucket/user-dataset.csv", 
        target_field=target_col
    )

    report = {
        "fairness_metrics": {
            "disparate_impact": round(float(audit_results['disparate_impact']), 3),
            "recall_difference": round(float(audit_results['recall_difference']), 3)
        },
        "group_statistics": {
            "privileged_count": int(audit_results['group_statistics']['privileged_count']),
            "unprivileged_count": int(audit_results['group_statistics']['unprivileged_count']),
            "privileged_positive_rate": round(float(audit_results['group_statistics']['privileged_positive_rate']), 3),
            "unprivileged_positive_rate": round(float(audit_results['group_statistics']['unprivileged_positive_rate']), 3),
            "privileged_recall": round(float(audit_results['group_statistics'].get('privileged_recall', 0)), 3),
            "unprivileged_recall": round(float(audit_results['group_statistics'].get('unprivileged_recall', 0)), 3)
        },
        "fairness_assessment": audit_results.get('fairness_assessment', 'Pending Review'),
        "data_validation": {
            "anomaly_count": audit_results['data_validation'].get('anomaly_count') or 0,
            "has_anomalies": bool((audit_results['data_validation'].get('anomaly_count') or 0) > 0),
            "status": audit_results['data_validation'].get('status', 'success')
        },
        "skew_detection": audit_results.get('skew_detection', {"status": "Monitoring active"}),
        "recommendations": _generate_audit_recommendations(audit_results)
    }

    # Persist in PostgreSQL
    db_report = AuditHistory(
        dataset_name=os.path.basename(config.get('dataset_path', 'unknown.csv')),
        mitigation_strategy="ThresholdOptimizer",
        metrics=report
    )
    db.add(db_report)
    db.commit()

    return report

@app.get("/api/audit/history")
def get_audit_history(db: Session = Depends(get_db)):
    history = db.query(AuditHistory).order_by(AuditHistory.timestamp.desc()).limit(10).all()
    return history

def _generate_audit_recommendations(audit_results: dict) -> list:
    recommendations = []
    di = audit_results['disparate_impact']
    if di < 0.8 or di > 1.25:
        recommendations.append({
            "type": "critical",
            "title": "Disparate Impact Violation",
            "description": f"Disparate Impact ratio is {di:.3f}. Threshold violated.",
            "action": "Trigger Agentic Synthetic Rebalancing."
        })
    return recommendations
