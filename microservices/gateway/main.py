import os
import httpx
import json
import shutil
from fastapi import FastAPI, Request, HTTPException, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Truth & Fairness API Gateway",
    description="Unified entry point for AI Fairness auditing, mitigation, and monitoring microservices.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "mitigate": os.getenv("MITIGATE_URL", "http://mitigate:8002"),
    "shap": os.getenv("SHAP_URL", "http://shap:8003"),
    "monitor": os.getenv("MONITOR_URL", "http://monitor:8004"),
    "explorer": os.getenv("EXPLORER_URL", "http://explorer:8005"),
    "diagnostics": os.getenv("DIAGNOSTICS_URL", "http://diagnostics:8006"),
    "audit": os.getenv("AUDIT_URL", "http://audit:8007"),
    "agent": os.getenv("AGENT_URL", "http://agent:8008"),
}

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "shared", "uploads"))
DATA_FILE = os.path.join(UPLOAD_DIR, "current_dataset.csv")
CONFIG_FILE = os.path.join(UPLOAD_DIR, "config.json")

# Ensure upload dir exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Receives the CSV dataset and saves it to the shared Docker volume."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
        
    try:
        with open(DATA_FILE, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read headers to return to frontend for configuration
        import pandas as pd
        df = pd.read_csv(DATA_FILE, nrows=0)
        columns = df.columns.tolist()
        
        return {"status": "success", "columns": columns, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/configure")
async def configure_dataset(target_col: str = Form(...), sensitive_col: str = Form(...)):
    """Saves the target and sensitive column mappings."""
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=400, detail="No dataset uploaded yet.")
        
    config = {
        "target_col": target_col,
        "sensitive_col": sensitive_col
    }
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
        
    return {"status": "success", "config": config}

@app.get("/api/config")
async def get_config():
    """Returns the current target and sensitive variables for Frontend labels."""
    default_config = {"target_col": "Income", "sensitive_col": "Sex"}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return default_config

@app.get("/api/model-card")
async def proxy_model_card(request: Request):
    target_url = f"{SERVICES['audit']}/api/model-card"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            proxy_req = client.build_request("GET", target_url, params=request.query_params)
            response = await client.send(proxy_req)
            response.raise_for_status()
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Bad Gateway: Unable to fetch model card.")

@app.get("/api/{service_name}")
async def proxy_get(service_name: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
        
    target_url = f"{SERVICES[service_name]}/api/{service_name}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            proxy_req = client.build_request("GET", target_url, params=request.query_params)
            response = await client.send(proxy_req)
            response.raise_for_status()
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Bad Gateway: Unable to connect to {service_name} service.")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error from upstream service: {exc}")

@app.get("/health")
def health_check():
    return {"status": "Gateway online"}
