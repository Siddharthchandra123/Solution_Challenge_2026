import pandas as pd
import json
import os
from google.cloud import storage

# Centralized Path Management
BASE_UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared', 'uploads'))
CONFIG_PATH = os.path.join(BASE_UPLOAD_DIR, "config.json")
GCS_BUCKET = os.getenv("GCS_BUCKET")

def get_dataset():
    """
    Scalable Data Access Layer:
    Detects if Google Cloud Storage is configured, otherwise falls back to local volume.
    """
    config = get_config()
    dataset_path = config.get("dataset_path")

    if not dataset_path:
        # Fallback to local default if no config
        local_csv = os.path.join(BASE_UPLOAD_DIR, "current_dataset.csv")
        return pd.read_csv(local_csv)

    # Check for GCS URL vs Local Path
    if dataset_path.startswith("gs://"):
        return _read_from_gcs(dataset_path)
    
    # Standard Local Access
    return pd.read_csv(dataset_path)

def _read_from_gcs(gs_path):
    """Internal helper for GCP-native blob access."""
    try:
        bucket_name = gs_path.split("/")[2]
        blob_name = "/".join(gs_path.split("/")[3:])
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Download as string and parse
        data = blob.download_as_text()
        from io import StringIO
        return pd.read_csv(StringIO(data))
    except Exception as e:
        print(f"GCS Access Error: {e}")
        # Final fallback to standard local default
        local_csv = os.path.join(BASE_UPLOAD_DIR, "current_dataset.csv")
        return pd.read_csv(local_csv)

def get_config():
    if not os.path.exists(CONFIG_PATH):
        return {
            "target_col": "Income",
            "sensitive_col": "Sex",
            "privileged_group": "Male",
            "unprivileged_group": "Female",
            "dataset_path": ""
        }
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config_data):
    if not os.path.exists(BASE_UPLOAD_DIR):
        os.makedirs(BASE_UPLOAD_DIR)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config_data, f)
