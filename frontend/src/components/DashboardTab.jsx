import React, { useState } from 'react';
import { CloudRain, Sparkles, AlertTriangle, ArrowRight, Compass, RefreshCw, CheckCircle2 } from 'lucide-react';
import { predictSingle } from '../services/api';

export default function DashboardTab({ onNavigateToMap }) {
  // Interactive Single-Point Form State
  const [formData, setFormData] = useState({
    latitude: 19.0,
    longitude: 73.0,
    gfs_rain_24h: 82.4,
    r500: 75.0, r700: 82.0, r850: 88.0,
    t500: 265.0, t700: 280.0, t850: 290.0,
    u500: -5.0, u700: 10.0, u850: 15.0,
    v500: 2.0, v700: 4.0, v850: 6.0,
    w500: -0.02, w700: -0.08, w850: -0.04,
    z500: 58500.0, z700: 31000.0, z850: 14500.0
  });

  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState({
    regime: 'Orographic Rainfall',
    regime_id: 3,
    gfs_rainfall_mm: 82.4,
    predicted_bias_mm: 9.3,
    corrected_rainfall_mm: 91.7,
    heavy_probability: 0.81,
    very_heavy_probability: 0.42,
    extremely_heavy_probability: 0.08
  });

  const presets = [
    {
      name: 'Western Ghats Orographic Peak',
      data: { latitude: 19.0, longitude: 73.0, gfs_rain_24h: 82.4, r500: 80, r700: 88, r850: 92, w700: -0.12, z500: 58500, z850: 14500 }
    },
    {
      name: 'Mumbai Coastal Heavy Convective',
      data: { latitude: 18.9, longitude: 72.8, gfs_rain_24h: 112.5, r500: 85, r700: 90, r850: 95, w700: -0.15, z500: 58400, z850: 14450 }
    },
    {
      name: 'Bay of Bengal Depression System',
      data: { latitude: 20.5, longitude: 86.5, gfs_rain_24h: 65.0, r500: 78, r700: 85, r850: 90, w700: -0.09, z500: 58200, z850: 14400 }
    },
    {
      name: 'Delhi Break Monsoon Dry Spells',
      data: { latitude: 28.6, longitude: 77.2, gfs_rain_24h: 2.1, r500: 45, r700: 52, r850: 60, w700: 0.02, z500: 58900, z850: 14650 }
    }
  ];

  const handleInputChange = (field, val) => {
    setFormData(prev => ({ ...prev, [field]: parseFloat(val) || 0 }));
  };

  const applyPreset = (presetData) => {
    const updated = { ...formData, ...presetData };
    setFormData(updated);
    runPrediction(updated);
  };

  const runPrediction = async (dataToPredict = formData) => {
    setLoading(true);
    try {
      const res = await predictSingle(dataToPredict);
      setPrediction(res);
    } catch (err) {
      console.error('Prediction failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Visual Pipeline Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 p-5 rounded-2xl border border-slate-800 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col lg:flex-row items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-2 text-cyan-400 font-semibold text-xs uppercase tracking-wider mb-1">
              <Sparkles className="w-4 h-4" /> End-to-End Forecast Post-Processing Pipeline
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white">
              Regime-Aware NWP Rainfall Bias Correction & Risk Model
            </h2>
            <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-2xl">
              Integrates raw NOAA/NCEP GFS 0.25° NWP rainfall, ERA5 pressure-level thermodynamics (500, 700, 850 hPa), and IMD observations to improve monsoon forecasts over India.
            </p>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto w-full lg:w-auto pb-2 lg:pb-0">
            <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-2 rounded-xl border border-slate-700/80 text-center min-w-[120px]">
              <div>
                <span className="text-[10px] text-slate-400 font-semibold block uppercase">Raw NWP</span>
                <span className="text-xs font-bold text-cyan-400">GFS 0.25°</span>
              </div>
            </div>

            <ArrowRight className="w-4 h-4 text-slate-500 shrink-0" />

            <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-2 rounded-xl border border-slate-700/80 text-center min-w-[120px]">
              <div>
                <span className="text-[10px] text-slate-400 font-semibold block uppercase">Classification</span>
                <span className="text-xs font-bold text-indigo-400">ERA5 Regime</span>
              </div>
            </div>

            <ArrowRight className="w-4 h-4 text-slate-500 shrink-0" />

            <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-2 rounded-xl border border-slate-700/80 text-center min-w-[120px]">
              <div>
                <span className="text-[10px] text-slate-400 font-semibold block uppercase">Post-Process</span>
                <span className="text-xs font-bold text-emerald-400">XGBoost Bias</span>
              </div>
            </div>

            <ArrowRight className="w-4 h-4 text-slate-500 shrink-0" />

            <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-2 rounded-xl border border-slate-700/80 text-center min-w-[120px]">
              <div>
                <span className="text-[10px] text-slate-400 font-semibold block uppercase">Output</span>
                <span className="text-xs font-bold text-amber-400">Heavy Risk</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main KPI Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Weather Regime */}
        <div className="bg-slate-900/80 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-lg relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Synoptic Regime</span>
            <span className="w-8 h-8 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
              <Compass className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3">
            <span className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              Regime #{prediction.regime_id}: {prediction.regime}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Classified from ERA5 thermal & dynamic stability at 850/700/500 hPa.
          </p>
        </div>

        {/* Card 2: GFS vs AI Corrected */}
        <div className="bg-slate-900/80 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-lg relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Raw vs AI Corrected</span>
            <span className="w-8 h-8 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400">
              <CloudRain className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-white">{prediction.corrected_rainfall_mm} <span className="text-sm font-semibold text-slate-400">mm</span></span>
            <span className="text-xs text-slate-400">Raw: {prediction.gfs_rainfall_mm} mm</span>
          </div>
          <div className="mt-2 flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
            <span>Bias Delta: {prediction.predicted_bias_mm >= 0 ? `+${prediction.predicted_bias_mm}` : prediction.predicted_bias_mm} mm</span>
          </div>
        </div>

        {/* Card 3: Heavy Rain Risk (>=64.5mm) */}
        <div className="bg-slate-900/80 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-lg relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-amber-400">Heavy Risk (≥64.5mm)</span>
            <span className="w-8 h-8 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-400">
              <AlertTriangle className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-amber-300">
              {(prediction.heavy_probability * 100).toFixed(1)}%
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
              AUC: 0.8720
            </span>
          </div>
          {/* Progress bar */}
          <div className="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
            <div className="bg-gradient-to-r from-amber-500 to-yellow-400 h-full rounded-full transition-all duration-500" style={{ width: `${Math.min(100, prediction.heavy_probability * 100)}%` }} />
          </div>
        </div>

        {/* Card 4: Very Heavy / Extreme Risk */}
        <div className="bg-slate-900/80 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-lg relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-rose-400">Very Heavy & Extreme</span>
            <span className="w-8 h-8 rounded-xl bg-rose-500/10 flex items-center justify-center text-rose-400">
              <AlertTriangle className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300 font-semibold">≥115.6mm (Very Heavy):</span>
              <span className="font-bold text-rose-300">{(prediction.very_heavy_probability * 100).toFixed(1)}%</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300 font-semibold">≥204.5mm (Extreme):</span>
              <span className="font-bold text-purple-300">{(prediction.extremely_heavy_probability * 100).toFixed(1)}%</span>
            </div>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            ROC-AUC: 0.9279 (Very Heavy) • 0.9432 (Extreme)
          </p>
        </div>
      </div>

      {/* Main Content Grid: Simulator + Presets */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Presets & Info Panel */}
        <div className="space-y-4">
          <div className="bg-slate-900/80 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-lg">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-cyan-400" /> Synoptic Test Presets
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Click a preset to instantly load authentic atmospheric profiles across key Indian monsoon meteorological regimes:
            </p>
            <div className="space-y-2">
              {presets.map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => applyPreset(preset.data)}
                  className="w-full text-left p-3 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 hover:border-cyan-500/40 transition-all flex items-center justify-between group"
                >
                  <div>
                    <div className="text-xs font-bold text-slate-200 group-hover:text-cyan-400 transition-colors">
                      {preset.name}
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {preset.data.latitude}°N, {preset.data.longitude}°E • Raw GFS: {preset.data.gfs_rain_24h} mm
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 transition-colors" />
                </button>
              ))}
            </div>
          </div>

          <div className="bg-slate-900/80 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-lg">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-2">
              <Compass className="w-4 h-4 text-blue-400" /> Explore Regional Grid Map
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Switch to the Interactive Map to explore spatially gridded predictions for all 4,625 points across India for September 2024.
            </p>
            <button
              onClick={onNavigateToMap}
              className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-bold text-xs shadow-lg shadow-blue-500/20 hover:from-blue-500 hover:to-cyan-500 transition-all flex items-center justify-center gap-2"
            >
              Open Interactive India Map <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Live Predictor Form */}
        <div className="lg:col-span-2 bg-slate-900/80 backdrop-blur-md p-6 rounded-2xl border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <RefreshCw className="w-4 h-4 text-cyan-400" /> Single-Point AI Forecast Post-Processing Simulator
              </h3>
              <p className="text-xs text-slate-400">
                Input atmospheric features to compute real-time XGBoost bias correction & heavy rainfall risk probabilities.
              </p>
            </div>
            <button
              onClick={() => runPrediction()}
              disabled={loading}
              className="py-2 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition-all shadow-md shadow-emerald-600/20 flex items-center gap-2 shrink-0 disabled:opacity-50"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
              Run AI Prediction
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Location & NWP */}
            <div className="space-y-3 bg-slate-800/40 p-3.5 rounded-xl border border-slate-800">
              <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Coordinates & GFS</h4>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Latitude (°N)</label>
                <input
                  type="number" step="0.1"
                  value={formData.latitude}
                  onChange={(e) => handleInputChange('latitude', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:border-cyan-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Longitude (°E)</label>
                <input
                  type="number" step="0.1"
                  value={formData.longitude}
                  onChange={(e) => handleInputChange('longitude', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:border-cyan-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Raw GFS 24h Rain (mm)</label>
                <input
                  type="number" step="0.1"
                  value={formData.gfs_rain_24h}
                  onChange={(e) => handleInputChange('gfs_rain_24h', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-bold text-cyan-400 focus:border-cyan-500 focus:outline-none"
                />
              </div>
            </div>

            {/* Relative Humidity & Vert Velocity */}
            <div className="space-y-3 bg-slate-800/40 p-3.5 rounded-xl border border-slate-800">
              <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">ERA5 Moisture & Motion</h4>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Relative Humidity 850hPa (%)</label>
                <input
                  type="number"
                  value={formData.r850}
                  onChange={(e) => handleInputChange('r850', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Relative Humidity 700hPa (%)</label>
                <input
                  type="number"
                  value={formData.r700}
                  onChange={(e) => handleInputChange('r700', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Vertical Velocity w700 (Pa/s)</label>
                <input
                  type="number" step="0.01"
                  value={formData.w700}
                  onChange={(e) => handleInputChange('w700', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>
            </div>

            {/* Dynamics & Geopotential */}
            <div className="space-y-3 bg-slate-800/40 p-3.5 rounded-xl border border-slate-800">
              <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider">Pressure & Winds</h4>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Geopotential z500 (m²/s²)</label>
                <input
                  type="number"
                  value={formData.z500}
                  onChange={(e) => handleInputChange('z500', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:border-amber-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Geopotential z850 (m²/s²)</label>
                <input
                  type="number"
                  value={formData.z850}
                  onChange={(e) => handleInputChange('z850', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:border-amber-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Westerly Wind u850 (m/s)</label>
                <input
                  type="number"
                  value={formData.u850}
                  onChange={(e) => handleInputChange('u850', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:border-amber-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
