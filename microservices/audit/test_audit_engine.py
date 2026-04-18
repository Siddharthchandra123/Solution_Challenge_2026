import pandas as pd
import numpy as np
import json
from audit_engine import AuditEngine

def run_test():
    np.random.seed(42) # For reproducible results
    
    # Generate mock data: 100 samples
    y_true = np.random.randint(0, 2, 100)
    y_pred = np.random.randint(0, 2, 100)
    
    # Protected attribute (0 = privileged, 1 = unprivileged)
    protected_attribute = np.random.randint(0, 2, 100)
    
    # FORCE the edge case: Unprivileged group gets zero positive predictions
    # This specifically tests that our Division by Zero fix (999.0 instead of 'inf') works
    unprivileged_mask = protected_attribute == 1
    privileged_mask = protected_attribute == 0
    
    y_pred[unprivileged_mask] = 0
    # Ensure privileged gets at least one positive
    if np.sum(y_pred[privileged_mask]) == 0:
        y_pred[np.where(privileged_mask)[0][0]] = 1
        
    df = pd.DataFrame({'feature_a': np.random.rand(100), 'target': y_true})
    
    print("Starting AuditEngine Test...\n")
    engine = AuditEngine()
    
    # Test 1: Standard audit without providing specific GCP resources
    print("--- Test 1: Core Engine & Edge Cases ---")
    results1 = engine.comprehensive_audit(
        df=df,
        y_true=y_true,
        y_pred=y_pred,
        protected_attribute=protected_attribute
    )
    
    # Print the specific parts we fixed
    print(f"Fairness Assessment: {json.dumps(results1['fairness_assessment'])}")
    print(f"Disparate Impact Score (testing DivByZero fix): {results1['disparate_impact']}")
    print(f"Data Validation Object: {json.dumps(results1['data_validation'])}")
    print(f"Skew Detection Status: {json.dumps(results1['skew_detection'])}\n")
    
    
    # Test 2: Simulating Vertex AI parameters dynamically
    print("--- Test 2: Dynamic Vertex AI Integration ---")
    results2 = engine.comprehensive_audit(
        df=df,
        y_true=y_true,
        y_pred=y_pred,
        protected_attribute=protected_attribute,
        model_name="credit_risk_v2",
        dataset_path="gs://my-bucket/credit-data.csv",
        target_field="loan_approved"
    )
    print(f"Skew Detection Configuration:\n{json.dumps(results2['skew_detection'], indent=2)}")

if __name__ == "__main__":
    run_test()
