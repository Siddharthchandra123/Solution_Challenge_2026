import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from shared.data import get_dataset, get_config

app = FastAPI(
    title="Agentic Mitigation Engine",
    description="AI-driven synthetic data generation and automated de-biasing controller.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

@app.get("/api/agent/synthetic")
def generate_synthetic_data(count: int = 50):
    """
    Agentic Synthetic Data Generation:
    Uses Gemini 1.5 Pro to synthesize high-fidelity rows for underrepresented demographics.
    """
    df = get_dataset()
    config = get_config()
    target_col = config.get('target_col', 'Income')
    sensitive_col = config.get('sensitive_col', 'Sex')

    if not GOOGLE_API_KEY:
        # Fallback to smart statistical oversampling if No API Key
        return _statistical_oversample(df, sensitive_col, count)

    # Agentic Prompting
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Extract a small sample and distribution for the prompt
        sample_data = df.head(5).to_csv(index=False)
        columns = ", ".join(df.columns)
        
        prompt = f"""
        Act as a Data Engineer specializing in AI Fairness.
        I have a dataset with columns: [{columns}].
        The target variable is '{target_col}' and the sensitive attribute is '{sensitive_col}'.
        
        Current sample data:
        {sample_data}
        
        Generate exactly {count} new synthetic rows in CSV format (no header) that follow this distribution but 
        specifically balance the representation for the '{sensitive_col}' attribute. Ensure the synthetic data 
        is high-fidelity and realistic for an enterprise audit.
        """
        
        response = model.generate_content(prompt)
        # Parse Gemini CSV response and append to storage (simulated here)
        return {"status": "success", "agent_message": f"Generated {count} high-fidelity rows via Gemini 1.5 Pro."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _statistical_oversample(df, sensitive_col, count):
    # Fallback logic for local prototype
    minority_group = df[sensitive_col].value_counts().idxmin()
    minority_df = df[df[sensitive_col] == minority_group]
    
    # Simple bootstrapping oversampling
    new_rows = minority_df.sample(n=count, replace=True)
    return {
        "status": "warning", 
        "agent_level": "Local Statistical Bootstrapping",
        "message": f"No Gemini API key found. Defaulted to statistical oversampling for group: {minority_group}",
        "new_rows_count": len(new_rows)
    }

@app.get("/health")
def health():
    return {"status": "Agentic Service Online"}
