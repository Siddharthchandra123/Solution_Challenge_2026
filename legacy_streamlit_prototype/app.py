import streamlit as st
import pandas as pd
from profiler import generate_profile
from bias_detector import run_bivariate_analysis

st.set_page_config(page_title="Data Analyzer & Bias Profiler", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for dark theme and glassmorphism
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1, h2, h3 {
        color: #e0e6ed;
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ AI Fairness - Part One: Data Analyzer")
st.markdown("Analyze your dataset for hidden systemic biases, demographic imbalances, and proxy variables before training your models. Built for enterprise data auditing.")


@st.cache_data
def load_data(source="adult"):
    if source == "adult":
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
        columns = ["age", "workclass", "fnlwgt", "education", "education-num", "marital-status",
                   "occupation", "relationship", "race", "sex", "capital-gain", "capital-loss",
                   "hours-per-week", "native-country", "income"]
        df = pd.read_csv(url, names=columns, na_values=" ?", skipinitialspace=True)
        return df.dropna()
    return None

# Sidebar Configuration
st.sidebar.header("Dataset Configuration")
dataset_option = st.sidebar.selectbox("Choose a Dataset", ["UCI Adult Dataset", "Upload Custom CSV"])

df = None
if dataset_option == "UCI Adult Dataset":
    with st.spinner("Loading UCI Adult Dataset..."):
        df = load_data()
    st.sidebar.success("Adult Dataset Loaded!")
else:
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("Custom Dataset Loaded!")

if df is not None:
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Raw Data Explorer", 
        "📈 Automated EDA", 
        "⚖️ Interactive Field Analysis", 
        "🤖 Model Fixer", 
        "🧠 Explainable AI (SHAP)",
        "📡 Live Monitor"
    ])
    
    with tab1:
        st.header("Dataset Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", f"{len(df):,}")
        col2.metric("Total Columns", f"{len(df.columns)}")
        try:
            missing_pct = (df.isnull().sum().sum() / (df.shape[0]*df.shape[1])) * 100
        except ZeroDivisionError:
            missing_pct = 0
            
        col3.metric("Overall Missing Data", f"{missing_pct:.2f}%")
        
        st.subheader("Data Sample")
        st.dataframe(df.head(100), use_container_width=True)
        
    with tab2:
        st.header("Automated Exploratory Data Analysis")
        st.markdown("Generates a comprehensive distribution, correlation, and missingness report.")
        if st.button("Generate YData Profile"):
            with st.spinner("Generating deep profile... (This may take a minute)"):
                generate_profile(df)
            
    with tab3:
        st.header("Interactive Field Analysis")
        st.markdown("Select any two fields to automatically generate all relevant charts and relationships.")
        
        col1, col2 = st.columns(2)
        with col1:
            field_1 = st.selectbox("Select Column 1", df.columns, index=0)
        with col2:
            # Try to pick a different default for col 2
            default_idx = 1 if len(df.columns) > 1 else 0
            field_2 = st.selectbox("Select Column 2", df.columns, index=default_idx)
            
        with st.spinner("Generating all graphs for selected fields..."):
            from bias_detector import run_bivariate_analysis
            run_bivariate_analysis(df, field_1, field_2)
            
    with tab4:
        st.header("Model Inspector & Active Bias Fixer")
        st.markdown("Train a Random Forest classifier. The system will audit its inherent bias, then enforce mathematical fairness Constraints using active threshold optimization.")
        
        # User defined Configuration setup
        col1, col2, col3 = st.columns(3)
        with col1:
            # Set 'income' as default target if available
            default_tgt_idx = list(df.columns).index("income") if "income" in df.columns else len(df.columns)-1
            tgt_col = st.selectbox("Target Variable (Must be Binary)", df.columns, index=default_tgt_idx)
            
        with col2:
            # Set 'sex' as default sensitive if available
            default_sens_idx = list(df.columns).index("sex") if "sex" in df.columns else 0
            sens_col = st.selectbox("Sensitive Attribute", df.columns, index=default_sens_idx)
            
        with col3:
            strategy = st.selectbox("Fairness Constraint Strategy", ["Demographic Parity", "Equalized Odds"])
            
        if st.button("Train, Audit & Fix Model", type="primary"):
            from model_fixer import run_model_inspector
            run_model_inspector(df, tgt_col, sens_col, strategy)
            
    with tab5:
        st.header("Explainable Insights (SHAP)")
        st.markdown("Dive into exactly *how* and *why* the AI makes its decisions. SHAP calculates the true impact of every feature.")
        
        tgt_col_shap = st.selectbox("Select Target Variable to Explain", df.columns, index=list(df.columns).index("income") if "income" in df.columns else len(df.columns)-1, key="shap_tgt")
        
        if st.button("Generate SHAP Visualizations"):
            from explainability import run_shap_analysis
            run_shap_analysis(df, tgt_col_shap)
            
    with tab6:
        st.header("Real-Time Production Bias Tracker")
        st.markdown("Ensure your model stays fair over time.")
        
        col1, col2 = st.columns(2)
        with col1:
            tgt_col_live = st.selectbox("Target Outcome", df.columns, index=list(df.columns).index("income") if "income" in df.columns else len(df.columns)-1, key="live_tgt")
        with col2:
            sens_col_live = st.selectbox("Attribute to Protect", df.columns, index=list(df.columns).index("sex") if "sex" in df.columns else 0, key="live_sens")
            
        from live_monitor import run_live_monitor
        run_live_monitor(df, tgt_col_live, sens_col_live)

else:
    st.info("Please select or upload a dataset to begin profiling.")
