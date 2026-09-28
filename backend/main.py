from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os

from backend.services.prediction import prediction_service
from backend.services.regime import REGIME_DETAILS, classify_regime
from backend.services.data_service import data_service

app = FastAPI(
    title="Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts API",
    description="FastAPI Backend serving XGBoost Bias Correction and Heavy Rainfall Risk Models for MoES/NCMRWF (Problem ID 26080)",
    version="1.0.0"
)

# CORS middleware for local React frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models and data ONCE at startup
@app.on_event("startup")
def startup_event():
    print("Initializing FastAPI application...")
    try:
        prediction_service.load_models()
        data_service.load_data()
        print("FastAPI startup complete!")
    except Exception as e:
        print(f"Error during startup model/data load: {e}")

# Pydantic Schemas
class SinglePredictionRequest(BaseModel):
    date: Optional[str] = "2024-09-15"
    latitude: float = Field(..., example=19.0, description="Latitude in degrees North")
    longitude: float = Field(..., example=73.0, description="Longitude in degrees East")
    gfs_rain_24h: float = Field(..., example=45.2, description="Raw GFS 24-hour rainfall in mm")
    r500: float = Field(..., example=75.0, description="Relative Humidity at 500 hPa (%)")
    r700: float = Field(..., example=82.0, description="Relative Humidity at 700 hPa (%)")
    r850: float = Field(..., example=88.0, description="Relative Humidity at 850 hPa (%)")
    t500: float = Field(..., example=265.0, description="Temperature at 500 hPa (K)")
    t700: float = Field(..., example=280.0, description="Temperature at 700 hPa (K)")
    t850: float = Field(..., example=290.0, description="Temperature at 850 hPa (K)")
    u500: float = Field(..., example=-5.0, description="U-wind at 500 hPa (m/s)")
    u700: float = Field(..., example=10.0, description="U-wind at 700 hPa (m/s)")
    u850: float = Field(..., example=15.0, description="U-wind at 850 hPa (m/s)")
    v500: float = Field(..., example=2.0, description="V-wind at 500 hPa (m/s)")
    v700: float = Field(..., example=4.0, description="V-wind at 700 hPa (m/s)")
    v850: float = Field(..., example=6.0, description="V-wind at 850 hPa (m/s)")
    w500: float = Field(..., example=-0.02, description="Vertical Velocity at 500 hPa (Pa/s)")
    w700: float = Field(..., example=-0.08, description="Vertical Velocity at 700 hPa (Pa/s)")
    w850: float = Field(..., example=-0.04, description="Vertical Velocity at 850 hPa (Pa/s)")
    z500: float = Field(..., example=58500.0, description="Geopotential at 500 hPa (m^2/s^2)")
    z700: float = Field(..., example=31000.0, description="Geopotential at 700 hPa (m^2/s^2)")
    z850: float = Field(..., example=14500.0, description="Geopotential at 850 hPa (m^2/s^2)")
    regime: Optional[str] = None
    regime_id: Optional[int] = None

class BatchPredictionRequest(BaseModel):
    grid_points: List[SinglePredictionRequest]

# API Endpoints
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Regime-Aware AI Post-Processing API",
        "models_loaded": prediction_service.models_loaded,
        "dataset_samples": 425500,
        "period": "July 1, 2024 – September 30, 2024"
    }

@app.get("/regimes")
def get_regimes():
    """Returns all 6 supported synoptic weather regimes with details and sample counts."""
    return {
        "total_regimes": len(REGIME_DETAILS),
        "regimes": REGIME_DETAILS
    }

@app.get("/metrics")
def get_metrics():
    """Returns overall and categorical verification metrics (RMSE, MAE, CSI, POD, FAR, ETS, FSS, ROC-AUC)."""
    return data_service.get_metrics_summary()

@app.post("/predict")
def predict_single_point(request: SinglePredictionRequest):
    """Predicts rainfall bias correction and heavy rainfall probabilities for a single location."""
    try:
        result = prediction_service.predict_single(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/grid-data")
def get_grid_data(date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (defaults to latest date)")):
    """Returns September grid-level predictions for map rendering."""
    try:
        return data_service.get_grid_data(date_str=date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data query error: {str(e)}")

@app.post("/predict-grid")
def predict_batch_grid(request: BatchPredictionRequest):
    """Batch prediction endpoint for a list of grid points."""
    try:
        results = []
        for point in request.grid_points:
            pred = prediction_service.predict_single(point.dict())
            results.append(pred)
        return {
            "total_processed": len(results),
            "predictions": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")
