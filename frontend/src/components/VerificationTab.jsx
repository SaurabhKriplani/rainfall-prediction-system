import React, { useEffect, useState } from 'react';
import { fetchMetrics } from '../services/api';
import { Activity, AlertTriangle, CheckCircle, Info, ShieldAlert, Award, TrendingUp } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';

export default function VerificationTab() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      const data = await fetchMetrics();
      setMetrics(data);
    } catch (err) {
      console.error(err);
    }
  };

  const csiChartData = [
    { category: 'Heavy (≥64.5mm)', raw: 0.0925, corrected: 0.0640 },
    { category: 'Very Heavy (≥115.6mm)', raw: 0.0380, corrected: 0.0039 },
    { category: 'Extremely Heavy (≥204.5mm)', raw: 0.0000, corrected: 0.0000 },
  ];

  const fssChartData = [
    { category: 'Heavy (≥64.5mm)', raw: 0.1533, corrected: 0.1123 },
    { category: 'Very Heavy (≥115.6mm)', raw: 0.0795, corrected: 0.0155 },
    { category: 'Extremely Heavy (≥204.5mm)', raw: 0.0014, corrected: 0.0000 },
  ];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 p-6 rounded-2xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Model Verification & Transparent Performance Analytics</h2>
            <p className="text-xs text-slate-300 mt-0.5">
              Rigorous meteorological validation across 425,500 grid samples (September 2024 testing period).
            </p>
          </div>
        </div>
      </div>

      {/* Prominent Honesty & Transparency Notice Callout */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-5 flex items-start gap-4 shadow-lg">
        <div className="w-9 h-9 rounded-xl bg-amber-500/20 flex items-center justify-center text-amber-400 shrink-0 mt-0.5">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div className="space-y-1.5 text-xs">
          <h4 className="font-bold text-amber-300 text-sm flex items-center gap-2">
            Transparent Verification Statement & Key Model Trade-offs
          </h4>
          <p className="text-amber-200/90 leading-relaxed">
            <strong>Overall RMSE improved significantly by 15.22%</strong> (reducing error from 16.22 mm to 13.75 mm across the monsoon domain). However, deterministic regression models naturally smooth extreme peak values, causing a slight increase in MAE (from 7.14 to 7.27 mm) and reduced categorical detection scores (CSI, POD, FSS) for heavy rainfall thresholds.
          </p>
          <div className="text-[11px] text-amber-300 font-semibold bg-amber-950/40 p-2 rounded-lg border border-amber-500/20 mt-1">
            <strong>Operational Recommendation:</strong> Use the <em>XGBoost Bias Correction Model</em> for grid-level continuous rainfall estimation (RMSE optimization) and rely on the <em>XGBoost Probability Models</em> (ROC-AUC 0.87–0.94) for extreme rainfall hazard warnings.
          </div>
        </div>
      </div>

      {/* Primary Overall Error Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 p-5 rounded-2xl border border-emerald-500/30 shadow-xl">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">RMSE Improvement</span>
          <div className="text-3xl font-extrabold text-emerald-400 mt-2">+15.22%</div>
          <div className="text-xs text-slate-300 mt-1">Raw: 16.22 mm → <b>Corrected: 13.75 mm</b></div>
        </div>

        <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">MAE Performance</span>
          <div className="text-3xl font-extrabold text-amber-400 mt-2">7.27 mm</div>
          <div className="text-xs text-slate-400 mt-1">Raw GFS MAE: 7.14 mm (+0.13 mm)</div>
        </div>

        <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Heavy Rain ROC-AUC</span>
          <div className="text-3xl font-extrabold text-cyan-400 mt-2">0.8720</div>
          <div className="text-xs text-slate-400 mt-1">Threshold: ≥ 64.5 mm / 24h</div>
        </div>

        <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Extreme Rain ROC-AUC</span>
          <div className="text-3xl font-extrabold text-purple-400 mt-2">0.9432</div>
          <div className="text-xs text-slate-400 mt-1">Threshold: ≥ 204.5 mm / 24h</div>
        </div>
      </div>

      {/* Categorical Verification Table */}
      <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Award className="w-4 h-4 text-cyan-400" /> Categorical Skill Scores (CSI, POD, FAR, ETS, FSS)
        </h3>
        <p className="text-xs text-slate-400">
          Comparing raw GFS vs AI Corrected rainfall across standard IMD heavy rainfall classification thresholds:
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="bg-slate-800/80 text-slate-300 border-b border-slate-700">
                <th className="p-3 font-bold">Category</th>
                <th className="p-3 font-bold">Threshold</th>
                <th className="p-3 font-bold text-cyan-400">Raw CSI</th>
                <th className="p-3 font-bold text-emerald-400">Corr CSI</th>
                <th className="p-3 font-bold text-cyan-400">Raw POD</th>
                <th className="p-3 font-bold text-emerald-400">Corr POD</th>
                <th className="p-3 font-bold text-cyan-400">Raw FAR</th>
                <th className="p-3 font-bold text-emerald-400">Corr FAR</th>
                <th className="p-3 font-bold text-amber-400">Raw FSS</th>
                <th className="p-3 font-bold text-emerald-400">Corr FSS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-200">
              <tr className="hover:bg-slate-800/40">
                <td className="p-3 font-bold text-amber-400">Heavy Rainfall</td>
                <td className="p-3">≥ 64.5 mm</td>
                <td className="p-3 font-mono">0.0925</td>
                <td className="p-3 font-mono text-emerald-400 font-bold">0.0640</td>
                <td className="p-3 font-mono">0.1404</td>
                <td className="p-3 font-mono">0.0738</td>
                <td className="p-3 font-mono">0.7867</td>
                <td className="p-3 font-mono text-emerald-400 font-bold">0.6752</td>
                <td className="p-3 font-mono">0.1533</td>
                <td className="p-3 font-mono">0.1123</td>
              </tr>
              <tr className="hover:bg-slate-800/40">
                <td className="p-3 font-bold text-rose-400">Very Heavy Rainfall</td>
                <td className="p-3">≥ 115.6 mm</td>
                <td className="p-3 font-mono">0.0380</td>
                <td className="p-3 font-mono">0.0039</td>
                <td className="p-3 font-mono">0.0597</td>
                <td className="p-3 font-mono">0.0041</td>
                <td className="p-3 font-mono">0.9055</td>
                <td className="p-3 font-mono">0.9130</td>
                <td className="p-3 font-mono">0.0795</td>
                <td className="p-3 font-mono">0.0155</td>
              </tr>
              <tr className="hover:bg-slate-800/40">
                <td className="p-3 font-bold text-purple-400">Extremely Heavy Rainfall</td>
                <td className="p-3">≥ 204.5 mm</td>
                <td className="p-3 font-mono">0.0000</td>
                <td className="p-3 font-mono">0.0000</td>
                <td className="p-3 font-mono">0.0000</td>
                <td className="p-3 font-mono">0.0000</td>
                <td className="p-3 font-mono">1.0000</td>
                <td className="p-3 font-mono">0.0000</td>
                <td className="p-3 font-mono">0.0014</td>
                <td className="p-3 font-mono">0.0000</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Graphical Comparison Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-xl space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" /> Critical Success Index (CSI) Comparison
          </h3>
          <div className="h-[260px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={csiChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="category" stroke="#94a3b8" fontSize={10} />
                <YAxis stroke="#94a3b8" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '11px' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Bar dataKey="raw" name="Raw GFS CSI" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                <Bar dataKey="corrected" name="Corrected CSI" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-xl space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-amber-400" /> Fractions Skill Score (FSS) Comparison
          </h3>
          <div className="h-[260px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={fssChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="category" stroke="#94a3b8" fontSize={10} />
                <YAxis stroke="#94a3b8" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '11px' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Bar dataKey="raw" name="Raw GFS FSS" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                <Bar dataKey="corrected" name="Corrected FSS" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
