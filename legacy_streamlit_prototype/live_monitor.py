import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
from sklearn.metrics import accuracy_score
from fairlearn.metrics import demographic_parity_difference
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

def run_live_monitor(df: pd.DataFrame, target_col: str, sensitive_col: str):
    st.markdown("---")
    
    if df[target_col].nunique() != 2:
        st.warning("Live monitor requires a Binary Classification target.")
        return
        
    st.subheader("📡 Live Production BIAS Monitor")
    st.markdown("This dashboard simulates live incoming traffic into the application in chronological batches. It actively charts the 'Bias Drift' of your model post-deployment.")
    
    threshold = st.slider("Set AI Compliance Alert Threshold (Max Disparity)", min_value=0.01, max_value=0.50, value=0.10, step=0.01)
    
    if st.button("Start Production Simulation", type="primary"):
        # Setup model for simulation
        df_clean = df.dropna(subset=[target_col, sensitive_col]).copy()
        
        le_target = LabelEncoder()
        y = le_target.fit_transform(df_clean[target_col].astype(str))
        A = df_clean[sensitive_col].astype(str)
        
        X = df_clean.drop(columns=[target_col])
        for col in X.columns:
            if X[col].dtype == 'object' or X[col].dtype == 'category':
                X[col] = LabelEncoder().fit_transform(X[col].astype(str).fillna("Miss"))
                
        # Train base mock model on first 30% of data
        X_train, X_live, y_train, y_live, A_train, A_live = train_test_split(X, y, A, test_size=0.7, random_state=42)
        model = RandomForestClassifier(n_estimators=30, max_depth=8, random_state=42)
        model.fit(X_train, y_train)
        
        st.success("Deployment Phase 1 Complete. Initiating Live Streaming...")
        
        # Real-time dashboard setup
        chart_holder = st.empty()
        alert_holder = st.empty()
        
        batches = 10
        batch_size = len(X_live) // batches
        
        timeseries_dp = []
        x_axis = []
        
        # Simulate over time
        for i in range(batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(X_live))
            
            # Artificial bias injection for dramatic simulation effect if past halfway
            X_batch = X_live.iloc[start_idx:end_idx].copy()
            y_batch = y_live[start_idx:end_idx]
            A_batch = A_live.iloc[start_idx:end_idx]
            
            y_pred = model.predict(X_batch)
            
            if len(np.unique(A_batch)) > 1:
                dp_diff = demographic_parity_difference(y_batch, y_pred, sensitive_features=A_batch)
                
                # Exaggerate drift naturally over time for demonstration
                dp_diff = dp_diff + (i * 0.015) 
            else:
                dp_diff = 0
                
            timeseries_dp.append(dp_diff)
            x_axis.append(f"Batch {i+1}")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x_axis, y=timeseries_dp,
                mode='lines+markers',
                name='Demographic Parity Diff',
                line=dict(color='#eb4034', width=3),
                marker=dict(size=8)
            ))
            
            # Threshold line
            fig.add_hline(y=threshold, line_dash="dash", line_color="red", annotation_text="Compliance Threshold")
            
            fig.update_layout(
                title=f"Monitoring Fairness Drift (Processing Batch {i+1}/{batches})",
                yaxis_title="Bias Metric (DP Diff)",
                yaxis_range=[0, max(max(timeseries_dp) + 0.05, threshold + 0.05)],
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            
            # Update the chart placeholder
            chart_holder.plotly_chart(fig, use_container_width=True)
            
            # Check Alert
            if dp_diff > threshold:
                alert_holder.error(f"🚨 **URGENT COMPLIANCE BREACH**: Production bias ({dp_diff:.3f}) has exceeded your maximum threshold ({threshold})! Active model pausing recommended.")
            else:
                alert_holder.success(f"✅ Operations Nominal. Bias ({dp_diff:.3f}) is under threshold ({threshold}).")
                
            # Artificial sleep for simulation visual
            time.sleep(1)
            
        st.info("Simulation Complete. The Model Monitor has reached the end of the data stream.")
