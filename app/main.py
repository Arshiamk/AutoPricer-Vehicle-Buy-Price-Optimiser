import os
import pickle
import pandas as pd
import numpy as np
import hashlib
from typing import Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from app.schemas import QuoteRequest, QuoteResponse
from app.optimiser import compute_expected_costs, optimise_offer

app = FastAPI(title="AutoPricer API", version="0.1.0")

# CORS Middleware
origins = [
    os.getenv("DASHBOARD_ORIGIN", "*"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Auth
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def get_api_key(api_key: str = Security(api_key_header)):
    expected_key = os.getenv("API_KEY", "default-dev-key")
    if api_key != expected_key:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key


# Model registry
models: Dict[str, Any] = {}


def get_model_path(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "models", filename)


def get_file_hash(filepath: str) -> str:
    if not os.path.exists(filepath):
        return "missing"
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@app.on_event("startup")
def load_models():
    model_source = os.getenv("MODEL_SOURCE", "local")
    if model_source == "mock":
        models["price_model"] = {
            "version_hash": "mock-123",
            "trained_at": "2026-02-20",
            "training_rows": 0,
        }
        models["conversion_model"] = {
            "version_hash": "mock-456",
            "trained_at": "2026-02-20",
            "training_rows": 0,
        }
    else:
        try:
            with open(get_model_path("price_model.pkl"), "rb") as f:
                models["price_model"] = pickle.load(f)
            with open(get_model_path("price_q10.pkl"), "rb") as f:
                models["price_q10"] = pickle.load(f)
            with open(get_model_path("conversion_model.pkl"), "rb") as f:
                models["conversion_model"] = pickle.load(f)

            models["meta"] = {
                "price_model": {
                    "file_hash": get_file_hash(get_model_path("price_model.pkl")),
                    "trained_at": datetime.now().isoformat(),
                    "training_rows": 50000,
                },
                "conversion_model": {
                    "file_hash": get_file_hash(get_model_path("conversion_model.pkl")),
                    "trained_at": datetime.now().isoformat(),
                    "training_rows": 50000,
                },
            }
        except FileNotFoundError:
            print("Warning: Models not found on disk. Run `make train` first.")


@app.get("/health")
def health():
    if os.getenv("MODEL_SOURCE", "local") == "mock":
        return {"status": "ok", "models": models}

    return {"status": "ok", "models": models.get("meta", "Not loaded")}


from app.dvla import fetch_dvla_data


@app.get("/lookup")
async def dvla_lookup(reg: str, api_key: str = Depends(get_api_key)):
    """
    Look up vehicle details using UK Registration Number.
    Powered by official DVLA/DVSA APIs or deterministic mocks if keys are absent.
    """
    result = await fetch_dvla_data(reg)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@app.post("/quote", response_model=QuoteResponse)
def get_quote(req: QuoteRequest, api_key: str = Depends(get_api_key)):
    model_source = os.getenv("MODEL_SOURCE", "local")

    region_risk_score = 0.5
    e_costs = compute_expected_costs(req.damage_flag, req.channel, region_risk_score)

    if model_source == "mock":
        e_sale = 10000.0
        price_q10 = 9000.0

        def mock_p_win(offer: float) -> float:
            import math

            return 1.0 / (1.0 + math.exp(-(offer - 9000) / 500.0))

        result = optimise_offer(e_sale, price_q10, e_costs, mock_p_win)
        return QuoteResponse(**result)

    if "price_model" not in models:
        raise HTTPException(status_code=503, detail="Models are not loaded.")

    damage_map = {"none": 0, "scratches": 1, "dents": 2, "mechanical": 3, "structural": 4}
    damage_severity_score = damage_map.get(req.damage_type or "none", 0)
    month = datetime.now().month
    month_sin = np.sin((month - 1) * (2.0 * np.pi / 12))
    month_cos = np.cos((month - 1) * (2.0 * np.pi / 12))

    features_dict = {
        "make": req.make,
        "fuel_type": req.fuel_type,
        "body_type": "hatchback",
        "channel": req.channel,
        "vehicle_age": max(0, 2025 - req.year),
        "mileage": req.mileage,
        "damage_severity_score": damage_severity_score,
        "risk_score": region_risk_score,
        "month_sin": month_sin,
        "month_cos": month_cos,
    }

    df_features = pd.DataFrame([features_dict])

    e_sale = float(models["price_model"].predict(df_features)[0])
    price_q10 = float(models["price_q10"].predict(df_features)[0])

    def predict_p_win(offer: float) -> float:
        df_conv = df_features.copy()
        df_conv["offer_price"] = offer
        return float(models["conversion_model"].predict_proba(df_conv)[0][1])

    result = optimise_offer(e_sale, price_q10, e_costs, predict_p_win)
    return QuoteResponse(**result)
