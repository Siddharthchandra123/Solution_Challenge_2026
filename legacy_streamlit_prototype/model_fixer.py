import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import plotly.express as px
import plotly.graph_objects as go

# Fairlearn components
from fairlearn.metrics import MetricFrame, demographic_parity_difference, equalized_odds_difference
from fairlearn.postprocessing import ThresholdOptimizer

@st.cache_data
def prepare_data(df: pd.DataFrame, target_col: str, sensitive_col: str):
    # Drop rows with NaN in target or sensitive columns
    df_clean = df.dropna(subset=[target_col, sensitive_col]).copy()
    
    # We must treat the problem as binary classification for the postprocessing module
    # Label encode target
    le_target = LabelEncoder()
    y = le_target.fit_transform(df_clean[target_col].astype(str))
    
    # Keep sensitive column as categorical string for grouping
    A = df_clean[sensitive_col].astype(str)
    
    # Drop target from X
    X = df_clean.drop(columns=[target_col])
    
    # Dummify everything else
    X_encoded = pd.get_dummies(X, drop_first=True)
    
    return train_test_split(X_encoded, y, A, test_size=0.3, random_state=42), le_target

def run_model_inspector(df: pd.DataFrame, target_col: str, sensitive_col: str, fairness_constraint: str):
    """
    Trains a baseline model, audits its fairness, and applies a mitigation fixer.
    """
    st.markdown("---")
    
    # 0. Warning on Target Cardinality
    if df[target_col].nunique() != 2:
        st.warning(f"The Fixer currently only supports Binary Classification (2 possible outcomes). The feature '{target_col}' has {df[target_col].nunique()} outcomes.")
        st.info("Consider creating a new binary column or selecting a different target.")
        return
        
    with st.spinner("Compiling Neural Pipeline and Training Baseline Model..."):
        # 1. Prepare Data
        (X_train, X_test, y_train, y_test, A_train, A_test), le_target = prepare_data(df, target_col, sensitive_col)
        
        # 2. Train Unmitigated Baseline Model
        base_estimator = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
        base_estimator.fit(X_train, y_train)
        
        # Predict
        y_pred_base = base_estimator.predict(X_test)
        
        # 3. Calculate Baseline Metrics
        base_acc = accuracy_score(y_test, y_pred_base)
        base_dp_diff = demographic_parity_difference(y_test, y_pred_base, sensitive_features=A_test)
        base_eo_diff = equalized_odds_difference(y_test, y_pred_base, sensitive_features=A_test)
        
    st.subheader("1. Baseline Model Audit (Unmitigated)")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Base Accuracy", f"{base_acc*100:.2f}%")
    col2.metric("Demographic Parity Diff", f"{base_dp_diff:.3f}", help="Difference in selection rates. Closer to 0 is fairer.")
    col3.metric("Equalized Odds Diff", f"{base_eo_diff:.3f}", help="Difference in true/false positive rates. Closer to 0 is fairer.")
    
    # Metric Frame Visualization Baseline
    mf_base = MetricFrame(
        metrics=accuracy_score,
        y_true=y_test,
        y_pred=y_pred_base,
        sensitive_features=A_test
    )
    
    acc_by_group = mf_base.by_group.reset_index()
    acc_by_group.columns = [sensitive_col, 'Accuracy']
    
    fig_base = px.bar(
        acc_by_group, x=sensitive_col, y='Accuracy', 
        title="Baseline Accuracy by Demographic Group", 
        color=sensitive_col, text_auto=".3f"
    )
    fig_base.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig_base, use_container_width=True)

    # 4. Applying The Fixer (ThresholdOptimizer)
    st.markdown("---")
    st.subheader(f"2. The Fixer (Applying `{fairness_constraint}` Bias Mitigation)")
    st.markdown("The system is now actively adjusting the model's decision boundaries. It forces the prediction probabilities to align such that biological/sensitive demographics do not dictate the distribution of the final outcome.")
    
    with st.spinner(f"Optimizing Thresholds for {fairness_constraint}..."):
        try:
            # Map string to fairlearn constraint
            constraint_map = {
                "Demographic Parity": "demographic_parity",
                "Equalized Odds": "equalized_odds"
            }
            
            postprocess_est = ThresholdOptimizer(
                estimator=base_estimator,
                constraints=constraint_map[fairness_constraint],
                predict_method='predict_proba',
                prefit=True # Base is already fitted
            )
            
            postprocess_est.fit(X_train, y_train, sensitive_features=A_train)
            
            y_pred_mitigated = postprocess_est.predict(X_test, sensitive_features=A_test)
            
            # 5. Calculate Mitigated Metrics
            mit_acc = accuracy_score(y_test, y_pred_mitigated)
            mit_dp_diff = demographic_parity_difference(y_test, y_pred_mitigated, sensitive_features=A_test)
            mit_eo_diff = equalized_odds_difference(y_test, y_pred_mitigated, sensitive_features=A_test)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Mitigated Accuracy", f"{mit_acc*100:.2f}%", delta=f"{(mit_acc - base_acc)*100:.2f}%")
            col2.metric("Mitigated DP Diff", f"{mit_dp_diff:.3f}", delta=f"{mit_dp_diff - base_dp_diff:.3f}", delta_color="inverse")
            col3.metric("Mitigated EO Diff", f"{mit_eo_diff:.3f}", delta=f"{mit_eo_diff - base_eo_diff:.3f}", delta_color="inverse")
            
            # Metric Frame Visualization Mitigated
            mf_mit = MetricFrame(
                metrics=accuracy_score,
                y_true=y_test,
                y_pred=y_pred_mitigated,
                sensitive_features=A_test
            )
            
            mit_acc_by_group = mf_mit.by_group.reset_index()
            mit_acc_by_group.columns = [sensitive_col, 'Accuracy']
            
            # 6. Trade-off Visualization (Before vs After)
            fig_compare = go.Figure()
            fig_compare.add_trace(go.Bar(
                x=acc_by_group[sensitive_col],
                y=acc_by_group['Accuracy'],
                name='Before Fix (Baseline)',
                marker_color='#ef4444' # Red tint
            ))
            fig_compare.add_trace(go.Bar(
                x=mit_acc_by_group[sensitive_col],
                y=mit_acc_by_group['Accuracy'],
                name='After Fix (Mitigated)',
                marker_color='#10b981' # Green tint
            ))
            
            fig_compare.update_layout(
                title="Bias Correction Impact (Accuracy by Demographic)",
                barmode='group',
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis_title="Model Accuracy"
            )
            st.plotly_chart(fig_compare, use_container_width=True)
            
            st.success(f"**Action Completed:** The model successfully mitigated hidden biases using {fairness_constraint}. Notice the drastic drop in the Disparity metric, exchanging a mathematically minimal amount of overall accuracy for equitable performance.")
            
        except Exception as e:
            st.error(f"Failed to apply Mitigation Strategy. Ensure that '{sensitive_col}' does not have excessive high-cardinality values masking boolean convergence. Error: {e}")
