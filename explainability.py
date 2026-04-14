import streamlit as st
import pandas as pd
import shap
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

@st.cache_data
def get_explainer_data(df: pd.DataFrame, target_col: str):
    df_clean = df.dropna(subset=[target_col]).copy()
    
    le_target = LabelEncoder()
    y = le_target.fit_transform(df_clean[target_col].astype(str))
    
    X = df_clean.drop(columns=[target_col])
    
    # Label encode categorical instead of one-hot for cleaner SHAP feature names
    X_encoded = pd.DataFrame()
    for col in X.columns:
        if X[col].dtype == 'object' or X[col].dtype == 'category':
            X_encoded[col] = LabelEncoder().fit_transform(X[col].astype(str).fillna("Missing"))
        else:
            X_encoded[col] = X[col]
            
    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.3, random_state=42)
    return X_train, X_test, y_train, y_test

def run_shap_analysis(df: pd.DataFrame, target_col: str):
    st.markdown("---")
    
    if df[target_col].nunique() != 2:
        st.warning(f"SHAP Analysis requires Binary Classification. Feature '{target_col}' has {df[target_col].nunique()} outcomes.")
        return
        
    with st.spinner("Training explainability model and calculating SHAP values (Optimized Subsample)..."):
        try:
            X_train, X_test, y_train, y_test = get_explainer_data(df, target_col)
            
            # Train model
            model = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
            model.fit(X_train, y_train)
            
            # Subsample for very fast SHAP analysis (user approved)
            sample_size = min(len(X_test), 500)
            X_sub = X_test.sample(sample_size, random_state=42)
            
            # SHAP Explainer
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_sub)
            
            # Handle standard Random Forest Binary Output
            if isinstance(shap_values, list):
                shap_values_to_plot = shap_values[1] # Path to positive class
            elif len(shap_values.shape) == 3:
                shap_values_to_plot = shap_values[:, :, 1]
            else:
                shap_values_to_plot = shap_values
                
            st.success("✅ SHAP analysis complete!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Global Feature Importance")
                st.markdown("Shows which variables universally have the strongest capability of dragging a prediction towards or away from the target.")
                fig1, ax1 = plt.subplots(figsize=(6, 5))
                shap.summary_plot(shap_values_to_plot, X_sub, plot_type="bar", show=False)
                fig1.patch.set_alpha(0.0) # Transparent background
                ax1.set_facecolor('none')
                # Make text white for dark mode
                ax1.tick_params(colors="white")
                ax1.xaxis.label.set_color('white')
                ax1.yaxis.label.set_color('white')
                plt.tight_layout()
                st.pyplot(fig1)
                
            with col2:
                st.subheader("Directional Bias (Beeswarm)")
                st.markdown("Highlights exactly *how* a feature affects the decision. (e.g. Red dots on the right mean high values increase the prediction likelihood)")
                fig2, ax2 = plt.subplots(figsize=(6, 5))
                shap.summary_plot(shap_values_to_plot, X_sub, show=False)
                fig2.patch.set_alpha(0.0)
                ax2.set_facecolor('none')
                ax2.tick_params(colors="white")
                ax2.xaxis.label.set_color('white')
                ax2.title.set_color('white')
                plt.tight_layout()
                st.pyplot(fig2)
                
        except Exception as e:
            st.error(f"Failed to generate SHAP visualizations. Library mismatch or incompatible data types. Error: {e}")
