import React, { useState } from 'react';
import { AlertTriangle, ShieldCheck, Zap, Info, Award, CheckCircle } from 'lucide-react';
import { predictSingle } from '../services/api';

export default function HeavyRainTab() {
  const [testLocation, setTestLocation] = useState({
    latitude: 19.0,
    longitude: 73.0,
    gfs_rain_24h: 95.0,
    r500: 82, r700: 88, r850: 92,
    t500: 265, t700: 280, t850: 290,
    u500: -5, u700: 10, u850: 16,
    v500: 2, v700: 4, v850: 7,
    w500: -0.04, w700: -0.10, w850: -0.05,
    z500: 58400, z700: 30900, z850: 14420
  });

  const [loading, setLoading] = useState(false);
  const [probs, setProbs] = useState({
    heavy: 0.8124,
    very_heavy: 0.4215,
    extreme: 0.0832,
    regime: 'Orographic Rainfall',
    corrected: 88.5
  });

  const runTest = async () => {
    setLoading(true);
    try {
      const res = await predictSingle(testLocation);
      setProbs({
        heavy: res.heavy_probability,
        very_heavy: res.very_heavy_probability,
        extreme: res.extremely_heavy_probability,
        regime: res.regime,
        corrected: res.corrected_rainfall_mm
      });
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 p-6 rounded-2xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Multi-Threshold Heavy Rainfall Risk Probability Models</h2>
            <p className="text-xs text-slate-300 mt-0.5">
              Dedicated XGBoost binary classification models calibrated for early hazard detection and risk quantification over IMD threshold categories.
            </p>
          </div>
        </div>
      </div>

      {/* ROC-AUC Distinction Callout */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-2xl p-4 flex items-start gap-3">
        <Info className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
        <div className="text-xs text-blue-200/90 leading-relaxed">
          <strong>Important Meteorological Distinction:</strong> ROC-AUC measures <strong>model discrimination capability</strong> (the overall mathematical ability to separate heavy rainfall events from non-heavy events across all probability cutoffs). It is a global performance rating and is <strong>not a probability value</strong>. Predicted risk percentages represent the calibrated likelihood of rainfall exceeding the specified threshold.
        </div>
      </div>

      {/* 3 Main Threshold Risk Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Heavy Rainfall */}
        <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-amber-500/30 shadow-xl relative overflow-hidden space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">Category 1</span>
            <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
              <Award className="w-3.5 h-3.5" /> ROC-AUC: 0.8720
            </span>
          </div>

          <div>
            <h3 className="text-lg font-bold text-white">Heavy Rainfall</h3>
            <div className="text-xs text-slate-400">Threshold: <b className="text-amber-300">≥ 64.5 mm / 24h</b></div>
          </div>

          <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/60 space-y-2">
            <span className="text-[11px] text-slate-400 font-semibold block uppercase">Predicted Event Risk</span>
            <div className="text-4xl font-extrabold text-amber-400">
              {(probs.heavy * 100).toFixed(1)}%
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
              <div className="bg-gradient-to-r from-amber-500 to-yellow-400 h-full rounded-full transition-all duration-500" style={{ width: `${probs.heavy * 100}%` }} />
            </div>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            High discrimination accuracy (AUC 0.8720) for detecting significant monsoon rain spells causing localized waterlogging.
          </p>
        </div>

        {/* Card 2: Very Heavy Rainfall */}
        <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-rose-500/30 shadow-xl relative overflow-hidden space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-rose-400 uppercase tracking-wider">Category 2</span>
            <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center gap-1">
              <Award className="w-3.5 h-3.5" /> ROC-AUC: 0.9279
            </span>
          </div>

          <div>
            <h3 className="text-lg font-bold text-white">Very Heavy Rainfall</h3>
            <div className="text-xs text-slate-400">Threshold: <b className="text-rose-300">≥ 115.6 mm / 24h</b></div>
          </div>

          <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/60 space-y-2">
            <span className="text-[11px] text-slate-400 font-semibold block uppercase">Predicted Event Risk</span>
            <div className="text-4xl font-extrabold text-rose-400">
              {(probs.very_heavy * 100).toFixed(1)}%
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
              <div className="bg-gradient-to-r from-rose-500 to-red-400 h-full rounded-full transition-all duration-500" style={{ width: `${probs.very_heavy * 100}%` }} />
            </div>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Excellent discrimination performance (AUC 0.9279) for identifying major convective systems and depression tracks.
          </p>
        </div>

        {/* Card 3: Extremely Heavy Rainfall */}
        <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-purple-500/30 shadow-xl relative overflow-hidden space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">Category 3</span>
            <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-1">
              <Award className="w-3.5 h-3.5" /> ROC-AUC: 0.9432
            </span>
          </div>

          <div>
            <h3 className="text-lg font-bold text-white">Extremely Heavy Rainfall</h3>
            <div className="text-xs text-slate-400">Threshold: <b className="text-purple-300">≥ 204.5 mm / 24h</b></div>
          </div>

          <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/60 space-y-2">
            <span className="text-[11px] text-slate-400 font-semibold block uppercase">Predicted Event Risk</span>
            <div className="text-4xl font-extrabold text-purple-400">
              {(probs.extreme * 100).toFixed(1)}%
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
              <div className="bg-gradient-to-r from-purple-500 to-fuchsia-400 h-full rounded-full transition-all duration-500" style={{ width: `${probs.extreme * 100}%` }} />
            </div>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Superior discrimination metric (AUC 0.9432) for extreme flash-flood & cloudburst risk warnings.
          </p>
        </div>
      </div>

      {/* Interactive Probability Tester */}
      <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" /> Interactive Heavy Rain Risk Classifier
            </h3>
            <p className="text-xs text-slate-400">
              Test how GFS rainfall magnitude and ERA5 moisture levels trigger classification probabilities.
            </p>
          </div>
          <button
            onClick={runTest}
            disabled={loading}
            className="py-2 px-4 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs transition-all shadow-md shadow-amber-600/20 flex items-center gap-2 shrink-0"
          >
            <ShieldCheck className="w-4 h-4" /> Recalculate Risk Probabilities
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-slate-400 block mb-1">GFS 24h Rainfall Input (mm)</label>
            <input
              type="number" step="5"
              value={testLocation.gfs_rain_24h}
              onChange={(e) => setTestLocation(prev => ({ ...prev, gfs_rain_24h: parseFloat(e.target.value) || 0 }))}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs font-bold text-amber-400 focus:border-amber-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Relative Humidity 850hPa (%)</label>
            <input
              type="number"
              value={testLocation.r850}
              onChange={(e) => setTestLocation(prev => ({ ...prev, r850: parseFloat(e.target.value) || 0 }))}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-amber-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Vertical Ascent -w700 (Pa/s)</label>
            <input
              type="number" step="0.02"
              value={-testLocation.w700}
              onChange={(e) => setTestLocation(prev => ({ ...prev, w700: -(parseFloat(e.target.value) || 0) }))}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-amber-500 focus:outline-none"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
