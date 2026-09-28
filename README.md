# Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts
**Problem ID 26080 • Ministry of Earth Sciences (MoES) / NCMRWF**
*Theme: Smart Automation*

An operational AI/ML rainfall post-processing application that identifies prevailing synoptic weather regimes over the Indian subcontinent and applies regime-aware XGBoost bias corrections to raw GFS numerical weather prediction (NWP) forecasts alongside multi-threshold heavy rainfall risk classification.

---

## 🌟 Key System Architecture

```
Raw GFS 0.25° NWP (f006+f012+f018+f024)
              ↓
ERA5 Atmospheric Thermodynamics (500, 700, 850 hPa)
              ↓
Synoptic Weather Regime Classification (6 Regimes)
              ↓
Regime-Aware XGBoost Bias Regression (bias = IMD - GFS)
              ↓
Corrected Rainfall Calculation = max(0, GFS + Bias)
              ↓
Multi-Threshold Heavy Rainfall Risk Classification (XGBClassifiers)
              ↓
FastAPI Backend (Port 8000) ↔ React Leaflet Interactive Dashboard (Port 5173)
```

---

## 📊 Dataset & Model Performance Summary

- **Training & Testing Period**: July 1, 2024 – September 30, 2024 (92 Days, 425,500 Valid Grid Samples)
- **Target Observation**: IMD 0.25° High-Resolution Gridded Rainfall
- **Raw Forecast**: NOAA/NCEP GFS 0.25° 24-hour Accumulated Rainfall
- **Atmospheric Features**: ERA5 Relative Humidity, Temperature, U/V Winds, Vertical Velocity (w), Geopotential (z) across 500, 700, and 850 hPa levels.

### Verification Highlights

- **Overall RMSE Improvement**: **15.22%** (Raw GFS RMSE `16.2247` mm → AI Corrected RMSE `13.7553` mm)
- **Overall MAE**: Raw GFS MAE `7.1413` mm → AI Corrected MAE `7.2744` mm
- **Heavy Rainfall Risk Discrimination (ROC-AUC)**:
  - Heavy Rainfall (≥64.5 mm): **0.8720**
  - Very Heavy Rainfall (≥115.6 mm): **0.9279**
  - Extremely Heavy Rainfall (≥204.5 mm): **0.9432**

---

## 🌀 Synoptic Weather Regimes

The system classifies meteorological conditions into **6 distinct regimes**:
1. `0 = Active Monsoon` (RH > 70%, active monsoon trough)
2. `1 = Break Monsoon` (RH < 65%, trough shifted to Himalayan foothills)
3. `2 = Monsoon Low / Depression` (Intense upward velocity -w700 > 0.05 Pa/s)
4. `3 = Orographic Rainfall` (Western Ghats 8–21°N & Himalayas 27–35°N)
5. `4 = Coastal Rainfall` (Maritime coastal convergence, lon ≤ 75.5°E or ≥ 88°E, lat ≤ 23°N)
6. `5 = Western Disturbance` *(Framework supported; 0 genuine samples during July–September 2024 monsoon)*

---

## 📁 Directory & Model File Structure

```
rainfall project/
├── models/
│   ├── bias_correction_model.pkl
│   ├── heavy_rain_model.pkl
│   ├── very_heavy_rain_model.pkl
│   └── extremely_heavy_rain_model.pkl
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── services/
│       ├── prediction.py
│       ├── regime.py
│       └── data_service.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DashboardTab.jsx
│   │   │   ├── MapTab.jsx
│   │   │   ├── RegimesTab.jsx
│   │   │   ├── ComparisonTab.jsx
│   │   │   ├── HeavyRainTab.jsx
│   │   │   ├── VerificationTab.jsx
│   │   │   ├── MethodologyTab.jsx
│   │   │   └── AboutTab.jsx
│   │   ├── services/api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── data/final/
│   ├── master_regime_final_jul_sep_2024.csv
│   ├── bias_corrected_sep_2024.csv
│   ├── heavy_rain_probabilities_sep_2024.csv
│   └── verification_results.csv
│
└── scripts/regime/ml/export_models.py
```

---

## 🚀 Quickstart Instructions

### 1. Launch FastAPI Backend

```bash
# From workspace root
.venv\Scripts\uvicorn.exe backend.main:app --reload --host 0.0.0.0 --port 8000
```
Backend API will run at `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`).

### 2. Launch React Frontend

```bash
# In a new terminal window
cd frontend
npm run dev
```
Frontend dashboard will run at `http://localhost:5173`.

---

## 📡 API Endpoints Summary

- `GET /health` : API & loaded model health status
- `GET /regimes` : List all 6 synoptic weather regimes & metadata
- `GET /metrics` : Detailed verification metrics (RMSE, MAE, CSI, POD, FAR, ETS, FSS, ROC-AUC)
- `POST /predict` : Single-point bias correction & risk prediction
- `GET /grid-data?date=YYYY-MM-DD` : India spatial grid predictions for interactive map layer rendering
