import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from scipy.stats import chi2_contingency
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from fairlearn.metrics import MetricFrame, demographic_parity_difference, equalized_odds_difference
from fairlearn.postprocessing import ThresholdOptimizer
import shap
import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_mock_data():
    """Generates a dataset simulating historic bias between genders on Income"""
    np.random.seed(42)
    n = 1000
    age = np.random.randint(18, 65, n)
    experience = np.random.randint(0, 30, n)
    education = np.random.choice(['HighSchool', 'Bachelors', 'Masters', 'PhD'], n)
    
    # Sensitive attribute
    sex = np.random.choice(['Male', 'Female'], n)
    
    # Introduce historic bias: Male gets artificial bump
    income_score = (experience * 0.4) + (np.where(sex == 'Male', 5, -5)) + np.random.normal(0, 5, n)
    income = np.where(income_score > 5, 'High', 'Low')
    
    df = pd.DataFrame({
        'Age': age,
        'Experience': experience,
        'Education': education,
        'Sex': sex,
        'Income': income,
        'Income_Score': income_score
    })
    return df

@app.get("/api/mitigate")
def mitigate_bias():
    df = get_mock_data()
    target_col = 'Income'
    sensitive_col = 'Sex'
    
    # Prepare Data
    df_clean = df.dropna().copy()
    le_target = LabelEncoder()
    y = le_target.fit_transform(df_clean[target_col].astype(str))
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
    
    mf_base = MetricFrame(metrics=accuracy_score, y_true=y_test, y_pred=y_pred_base, sensitive_features=A_test)
    base_acc_by_group = mf_base.by_group.to_dict()
    
    # 2. Mitigation Engine (The Fixer)
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
    
    mf_mit = MetricFrame(metrics=accuracy_score, y_true=y_test, y_pred=y_pred_mitigated, sensitive_features=A_test)
    mit_acc_by_group = mf_mit.by_group.to_dict()
    
    # 3. Format strictly for React Fast-Render
    return {
        "metrics": {
            "base_acc": round(base_acc * 100, 1),
            "base_dp": round(base_dp_diff, 3),
            "mit_acc": round(mit_acc * 100, 1),
            "mit_dp": round(mit_dp_diff, 3)
        },
        "charts_before": [
            {
                "category": "Baseline Unmitigated", 
                "privileged": round(base_acc_by_group.get('Male', 0), 2), 
                "unprivileged": round(base_acc_by_group.get('Female', 0), 2)
            }
        ],
        "charts_after": [
            {
                "category": "Math Parity Enforced", 
                "privileged": round(mit_acc_by_group.get('Male', 0), 2), 
                "unprivileged": round(mit_acc_by_group.get('Female', 0), 2)
            }
        ]
    }

@app.get("/api/shap")
def compute_shap():
    df = get_mock_data()
    target_col = 'Income'
    sensitive_col = 'Sex'
    
    df_clean = df.dropna().copy()
    le_target = LabelEncoder()
    y = le_target.fit_transform(df_clean[target_col].astype(str))
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
        global_results.append({
            "feature": feature,
            "importance": round(float(global_shaps[i]), 3),
            "direction": direction
        })
        
    global_results = sorted(global_results, key=lambda x: x['importance'], reverse=True)
    
    return {
        "global": global_results
    }

@app.get("/api/monitor")
def get_monitor_data():
    df = get_mock_data()
    target_col = 'Income'
    sensitive_col = 'Sex'
    
    df_clean = df.dropna().copy()
    le_target = LabelEncoder()
    y = le_target.fit_transform(df_clean[target_col].astype(str))
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
            
        batch_time = now - datetime.timedelta(hours=(batches - 1 - i))
        
        timeseries_data.append({
            "time": batch_time.strftime("%I:%M %p"),
            "disparity": round(dp_diff, 3),
            "accuracy": round(acc, 3)
        })
        
    return {
        "status": "healthy",
        "current_disparity": timeseries_data[-1]['disparity'] if timeseries_data else 0.1,
        "current_accuracy": timeseries_data[-1]['accuracy'] if timeseries_data else 0.85,
        "timeseries": timeseries_data
    }

@app.get("/api/explorer")
def get_explorer_data():
    df = get_mock_data()
    
    # 1. Provide a subset of 100 points for the React Scatter plot (Experience vs Income_Score by Sex)
    scatter_subset = df.sample(100, random_state=42)
    scatter_data = []
    for _, row in scatter_subset.iterrows():
        scatter_data.append({
            "x": int(row['Experience']),
            "y": round(float(row['Income_Score']), 2),
            "group": str(row['Sex'])
        })
        
    # 2. Compute a small mock correlation matrix
    correlations = []
    
    # Numeric vs Numeric (Pearson)
    corr_exp_income = df['Experience'].corr(df['Income_Score'])
    corr_age_exp = df['Age'].corr(df['Experience'])
    
    correlations.append({"feature1": "Experience", "feature2": "Income_Score", "correlation": abs(corr_exp_income)})
    correlations.append({"feature1": "Age", "feature2": "Experience", "correlation": abs(corr_age_exp)})
    
    # Categorical vs Categorical (Cramer's V) for Sex vs Target(Income)
    xtab = pd.crosstab(df['Sex'], df['Income'])
    chi2, _, _, _ = chi2_contingency(xtab)
    n = xtab.sum().sum()
    min_dim = min(xtab.shape) - 1
    cramers_v = np.sqrt((chi2 / n) / min_dim) if min_dim > 0 and n > 0 else 0
    
    correlations.append({"feature1": "Sex", "feature2": "Income (Categorical)", "correlation": cramers_v})
    
    # Sort
    correlations = sorted(correlations, key=lambda d: d['correlation'], reverse=True)
    
    return {
        "scatter_data": scatter_data,
        "correlations": correlations,
        "insights": [
            {
                "type": "warning",
                "message": f"Proxy Detected: Sex and Income have a notable statistical correlation (Cramer's V: {cramers_v:.2f}). Removing 'Sex' from the model will not erase bias, as other features may act as proxies."
            }
        ]
    }

@app.get("/api/diagnostics")
def get_diagnostics_data():
    df = get_mock_data()
    
    # Artificially inject NaN values to demonstrate the Profiling scanner capability
    np.random.seed(42)
    df.loc[df.sample(frac=0.04).index, 'Experience'] = np.nan
    df.loc[df.sample(frac=0.015).index, 'Age'] = np.nan
    
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
    missing_pct = round((total_missing / total_cells) * 100, 2)
    clean_pct = round(100 - missing_pct, 2)
    
    quality_stats = [
        {"name": "Complete", "value": clean_pct, "color": "oklch(0.70 0.18 160)"},
        {"name": "Missing", "value": missing_pct, "color": "oklch(0.75 0.18 65)"},
        {"name": "Invalid", "value": 0.0, "color": "oklch(0.55 0.22 30)"}
    ]
    
    # 3. Protected Attributes Detection
    protected_attrs = []
    for col in ['Sex', 'Age']:
        if col in df.columns:
            coverage = round((1 - (df[col].isna().sum() / total_records)) * 100, 1)
            groups = df[col].dropna().unique().tolist()
            if len(groups) > 5:
                # Group numeric attributes into buckets for display
                groups = ["18-30", "31-45", "46-60", "60+"]
            else:
                groups = [str(g) for g in groups]
            protected_attrs.append({
                "attribute": col,
                "groups": groups,
                "coverage": coverage
            })
            
    # 4. Warnings Generation
    warnings = []
    if df['Experience'].isna().sum() > 0:
        warnings.append(f"Experience field has {int(df['Experience'].isna().sum())} missing values. Consider K-Nearest Neighbor imputation.")
    if df['Age'].isna().sum() > 0:
        warnings.append(f"Age attribute has {int(df['Age'].isna().sum())} missing values. Fixing is critical for Demographic Parity compliance.")
        
    return {
        "records": total_records,
        "feature_count": len(features),
        "quality_stats": quality_stats,
        "feature_dist": feature_dist,
        "protected_attributes": protected_attrs,
        "warnings": warnings
    }
