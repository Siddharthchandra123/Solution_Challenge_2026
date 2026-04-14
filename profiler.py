import streamlit as st
import streamlit.components.v1 as components
from ydata_profiling import ProfileReport
import pandas as pd
import tempfile
import os

def generate_profile(df: pd.DataFrame):
    """
    Generates a Pandas Profiling (YData Profiling) report and embeds it in Streamlit.
    """
    # Create the profile report object
    # We use minimal=True to speed up computation for very large datasets, 
    # but for standard datasets, minimal=False gives richer correlation matrices.
    st.info("Computing correlations and distributions...")
    
    # We use a try-except to handle potential types issues with standard ydata-profiling
    try:
        profile = ProfileReport(df, title="Comprehensive Data Profile", explorative=True, dark_mode=True)
        
        # Export to HTML string
        st.info("Rendering HTML Report...")
        html_content = profile.to_html()
        
        # Display via Streamlit component
        st.success("Profile Generated Successfully!")
        components.html(html_content, height=1000, scrolling=True)
    except Exception as e:
        st.error(f"An error occurred during profiling: {str(e)}")
        st.warning("Consider sampling the dataset or removing complex Object-type columns.")
