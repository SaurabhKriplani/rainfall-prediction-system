// API Service for communicating with FastAPI backend
const API_BASE = '/api';

export const fetchHealth = async () => {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (err) {
    console.warn('Backend API unreachable, running in demo/offline mode:', err.message);
    return { status: 'offline', models_loaded: false, dataset_samples: 425500 };
  }
};

export const fetchRegimes = async () => {
  try {
    const res = await fetch(`${API_BASE}/regimes`);
    if (!res.ok) throw new Error('Failed to fetch regimes');
    return await res.json();
  } catch (err) {
    return {
      regimes: [
        { id: 0, name: 'Active Monsoon', description: 'Widespread monsoon rainfall driven by active trough position, high moisture (RH > 70%), and strong low-level westerly monsoon flow.', samples_2024: 127600, days_represented: 28 },
        { id: 1, name: 'Break Monsoon', description: 'Monsoon trough shifts north to Himalayan foothills resulting in suppressed rainfall over central India and reduced moisture (RH < 65%).', samples_2024: 154750, days_represented: 34 },
        { id: 2, name: 'Monsoon Low/Depression', description: 'Cyclonic vortex / low-pressure system forming in Bay of Bengal or land with intense upward motion (-w700 > 0.05 Pa/s) and heavy rainfall.', samples_2024: 63700, days_represented: 14 },
        { id: 3, name: 'Orographic Rainfall', description: 'Forced topographic ascent of moist monsoon winds along Western Ghats (8–21°N, 72.5–76.5°E) and Himalayan region (27–35°N, 73–97°E).', samples_2024: 45500, days_represented: 10 },
        { id: 4, name: 'Coastal Rainfall', description: 'Convective and boundary layer moisture convergence along east/west maritime coastline regions (lon <= 75.5°E or >= 88°E, lat <= 23°N).', samples_2024: 33950, days_represented: 6 },
        { id: 5, name: 'Western Disturbance', description: 'Extratropical synoptic systems originating over the Mediterranean. Supported by the system framework but 0 genuine samples exist during July–September 2024 monsoon.', samples_2024: 0, days_represented: 0, note: 'Western Disturbance is supported by the system but is not represented in the selected July–September 2024 training period.' }
      ]
    };
  }
};

export const fetchMetrics = async () => {
  try {
    const res = await fetch(`${API_BASE}/metrics`);
    if (!res.ok) throw new Error('Failed to fetch metrics');
    return await res.json();
  } catch (err) {
    return {
      overall: {
        dataset_samples: 425500,
        days_total: 92,
        period: "July 1, 2024 – September 30, 2024",
        raw_gfs_rmse: 16.2247,
        corrected_rmse: 13.7553,
        rmse_improvement_pct: 15.22,
        raw_gfs_mae: 7.1413,
        corrected_mae: 7.2744
      },
      roc_auc: {
        heavy_rain_64_5mm: 0.8720,
        very_heavy_rain_115_6mm: 0.9279,
        extremely_heavy_rain_204_5mm: 0.9432
      },
      categorical_verification: [
        { category: "Heavy (>=64.5 mm)", threshold_mm: 64.5, raw_csi: 0.0925, corrected_csi: 0.0640, raw_pod: 0.1404, corrected_pod: 0.0738, raw_far: 0.7867, corrected_far: 0.6752, raw_ets: 0.0866, corrected_ets: 0.0612, raw_fss: 0.1533, corrected_fss: 0.1123 },
        { category: "Very Heavy (>=115.6 mm)", threshold_mm: 115.6, raw_csi: 0.0380, corrected_csi: 0.0039, raw_pod: 0.0597, corrected_pod: 0.0041, raw_far: 0.9055, corrected_far: 0.9130, raw_ets: 0.0366, corrected_ets: 0.0038, raw_fss: 0.0795, corrected_fss: 0.0155 },
        { category: "Extremely Heavy (>=204.5 mm)", threshold_mm: 204.5, raw_csi: 0.0000, corrected_csi: 0.0000, raw_pod: 0.0000, corrected_pod: 0.0000, raw_far: 1.0000, corrected_far: 0.0000, raw_ets: -0.0001, corrected_ets: 0.0000, raw_fss: 0.0014, corrected_fss: 0.0000 }
      ]
    };
  }
};

export const fetchGridData = async (date = '') => {
  try {
    const url = date ? `${API_BASE}/grid-data?date=${date}` : `${API_BASE}/grid-data`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch grid data');
    return await res.json();
  } catch (err) {
    console.error('Grid data fetch error:', err);
    return { date: '2024-09-30', available_dates: ['2024-09-30'], grid_points: [] };
  }
};

export const predictSingle = async (inputData) => {
  const res = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(inputData)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Prediction failed');
  }
  return await res.json();
};
