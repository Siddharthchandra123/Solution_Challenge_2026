import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import chi2_contingency

def analyze_bias_risk(df: pd.DataFrame, col1: str, col2: str):
    """
    Automated Intelligence Architecture to compute variations, proxies (mules), 
    and output actionable bias warnings before model training.
    """
    st.markdown("### 🧠 Automated Bias Interpretation Engine")
    
    # Check for empty or invalid data
    df_clean = df[[col1, col2]].dropna()
    if len(df_clean) < 10:
        st.warning("Not enough data to perform statistical bias analysis.")
        return

    is_num1 = pd.api.types.is_numeric_dtype(df_clean[col1])
    is_num2 = pd.api.types.is_numeric_dtype(df_clean[col2])
    
    insights = []
    proxy_warning = False
    
    # ---------------------------------------------------------
    # 1. Proxy (Mule) Detection (Categorical vs Categorical)
    # ---------------------------------------------------------
    if not is_num1 and not is_num2:
        # Calculate Cramer's V for correlation between two categorical variables
        xtab = pd.crosstab(df_clean[col1], df_clean[col2])
        chi2, p, dof, ex = chi2_contingency(xtab)
        n = xtab.sum().sum()
        min_dim = min(xtab.shape) - 1
        
        # Cramer's V calculation safeguarding against 0 division
        cramers_v = 0
        if min_dim > 0 and n > 0:
            cramers_v = np.sqrt((chi2 / n) / min_dim)
            
        if cramers_v > 0.7:
            proxy_warning = True
            insights.append({
                "type": "error",
                "title": "🚨 High Proxy Risk (Mule Variable Detected)",
                "text": f"**{col1}** and **{col2}** exhibit a very strong statistical correlation (Cramer's V: {cramers_v:.2f}). **Training Impact:** One of these acts as a 'mule' or proxy for the other. If one is a sensitive attribute (e.g., race) and you remove it, the model will secretly learn the bias anyway through the other variable."
            })
            
        # Check for extreme representation imbalances
        for col in [col1, col2]:
            counts = df_clean[col].value_counts(normalize=True)
            minorities = counts[counts < 0.05]
            if not minorities.empty:
                insights.append({
                    "type": "warning",
                    "title": f"⚠️ Sub-population Underrepresentation in {col}",
                    "text": f"The categories `{', '.join(minorities.index.astype(str))}` represent less than 5% of the data. **Training Impact:** The AI will treat these groups as statistical noise and optimize for the majority class, leading to severe performance disparities (bias) for these minority groups."
                })

    # ---------------------------------------------------------
    # 2. Variation & Disparity (Categorical vs Numeric)
    # ---------------------------------------------------------
    elif (is_num1 and not is_num2) or (not is_num1 and is_num2):
        cat_col = col2 if is_num1 else col1
        num_col = col1 if is_num1 else col2
        
        # Calculate variance across groups
        grouped = df_clean.groupby(cat_col)[num_col]
        means = grouped.mean()
        stds = grouped.std().fillna(0)
        
        # If the max mean is drastically higher than min mean
        mean_diff_ratio = means.max() / (means.min() + 1e-9)
        if mean_diff_ratio > 2.0:
            insights.append({
                "type": "warning",
                "title": f"⚠️ Outcome Variation Disparity between {cat_col} groups",
                "text": f"The average `{num_col}` for the highest group (`{means.idxmax()}`) is disproportionately larger than the lowest group (`{means.idxmin()}`). **Training Impact:** If `{num_col}` is your target or an important feature, the AI will internalize this skewed baseline and unfairly favor specific demographic segments."
            })
            
    # ---------------------------------------------------------
    # 3. Numeric Correlation (Numeric vs Numeric)
    # ---------------------------------------------------------
    elif is_num1 and is_num2:
        corr = df_clean[col1].corr(df_clean[col2])
        if abs(corr) > 0.8:
            insights.append({
                "type": "error",
                "title": f"🚨 Co-linearity Alert",
                "text": f"These fields are near-perfectly correlated (Pearson: {corr:.2f}). **Training Impact:** Feeding both into a linear model causes multi-collinearity, making the AI's feature importance unstable and randomly punishing one of the variables."
            })
            
    # Output the Engine Results
    if not insights:
        st.success("✅ **AI Analysis:** Data distribution and variance between these fields appear stable. No extreme proxies or underrepresentation detected.")
    else:
        for insight in insights:
            if insight["type"] == "error":
                st.error(f"{insight['title']}\n\n{insight['text']}")
            elif insight["type"] == "warning":
                st.warning(f"{insight['title']}\n\n{insight['text']}")

def run_bivariate_analysis(df: pd.DataFrame, col1: str, col2: str):
    """
    Generates user-selected graphs and intelligent bias analysis.
    """
    st.markdown("---")
    
    if col1 == col2:
        st.warning("Please select two different columns to see their relationship.")
        return
        
    nunique_thresh = 15
    is_num1 = pd.api.types.is_numeric_dtype(df[col1]) and df[col1].nunique() > nunique_thresh
    is_num2 = pd.api.types.is_numeric_dtype(df[col2]) and df[col2].nunique() > nunique_thresh
    
    # 1. Run the Intelligence Architecture
    analyze_bias_risk(df, col1, col2)
    st.markdown("---")

    # 2. Render Graphs
    available_plots = [
        "Scatter Plot", 
        "Horizontal Bar Chart", 
        "Vertical Column Chart", 
        "Combined Stacked Bar",
        "Box Plot (Distribution)",
        "2D Heatmap"
    ]

    selected_plots = st.multiselect(
        "Select which plots you want to generate:", 
        options=available_plots, 
        default=[ "Vertical Column Chart", "Combined Stacked Bar", "Scatter Plot"]
    )
    
    if not selected_plots:
        st.info("Please select at least one plot to display.")
        return
        
    df_clean = df[[col1, col2]].dropna()
    cols = st.columns(2)
    idx = 0
    
    # Chart generation logic
    if "Scatter Plot" in selected_plots:
        sample_df = df_clean.sample(min(len(df_clean), 3000)) if len(df_clean) > 3000 else df_clean
        fig = px.scatter(sample_df, x=col1, y=col2, color=col1, title=f"Scatter Plot: {col1} vs {col2}", opacity=0.6)
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        cols[idx % 2].plotly_chart(fig, use_container_width=True)
        idx += 1
            
    if "Horizontal Bar Chart" in selected_plots:
        counts = df_clean.groupby([col1, col2]).size().reset_index(name='count')
        counts = counts.sort_values(by='count', ascending=True)
        fig = px.bar(counts, y=col1, x='count', color=col2, orientation='h', title="Horizontal Bar Chart", barmode='group')
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        cols[idx % 2].plotly_chart(fig, use_container_width=True)
        idx += 1
        
    if "Vertical Column Chart" in selected_plots:
        counts = df_clean.groupby([col1, col2]).size().reset_index(name='count')
        fig = px.bar(counts, x=col1, y='count', color=col2, title="Vertical Column Chart", barmode='group')
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        cols[idx % 2].plotly_chart(fig, use_container_width=True)
        idx += 1
        
    if "Combined Stacked Bar" in selected_plots:
        counts = df_clean.groupby([col1, col2]).size().reset_index(name='count')
        fig = px.bar(counts, x=col1, y='count', color=col2, title="Combined Stacked Bar Chart", barmode='stack')
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        cols[idx % 2].plotly_chart(fig, use_container_width=True)
        idx += 1
        
    if "Box Plot (Distribution)" in selected_plots:
        is_num_col2 = pd.api.types.is_numeric_dtype(df_clean[col2])
        if is_num_col2:
            fig = px.box(df_clean, x=col1, y=col2, color=col1, title=f"Box Distribution of {col2} by {col1}")
        else:
            fig = px.box(df_clean, x=col2, y=col1, color=col2, title=f"Box Distribution of {col1} by {col2}")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        cols[idx % 2].plotly_chart(fig, use_container_width=True)
        idx += 1
        
    if "2D Heatmap" in selected_plots:
        xtab = pd.crosstab(df_clean[col1], df_clean[col2])
        fig = px.imshow(xtab, aspect="auto", title="2D Cross-Tab Heatmap", color_continuous_scale="Teal")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
