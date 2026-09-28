import React, { useState } from 'react';
import { ResponsiveContainer, BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ScatterChart, Scatter } from 'recharts';
import { Activity, BarChart2, TrendingUp } from 'lucide-react';

export default function ComparisonTab() {
  // Sample time series comparison data across September dates
  const [timeSeriesData] = useState([
    { date: 'Sep 01', raw_gfs: 42.5, corrected: 48.2, imd_obs: 51.0 },
    { date: 'Sep 05', raw_gfs: 18.2, corrected: 14.5, imd_obs: 12.8 },
    { date: 'Sep 10', raw_gfs: 78.4, corrected: 84.1, imd_obs: 89.5 },
    { date: 'Sep 15', raw_gfs: 125.0, corrected: 108.6, imd_obs: 114.2 },
    { date: 'Sep 20', raw_gfs: 5.4, corrected: 3.1, imd_obs: 2.5 },
    { date: 'Sep 25', raw_gfs: 94.2, corrected: 88.5, imd_obs: 91.0 },
    { date: 'Sep 30', raw_gfs: 62.0, corrected: 54.8, imd_obs: 57.3 },
  ]);

  // Scatter plot data comparing Raw GFS vs Corrected against IMD Ground Truth
  const [scatterData] = useState([
    { imd: 15.0, raw_gfs: 22.4, corrected: 17.8 },
    { imd: 45.0, raw_gfs: 62.1, corrected: 48.9 },
    { imd: 85.0, raw_gfs: 110.5, corrected: 91.2 },
    { imd: 120.0, raw_gfs: 165.2, corrected: 132.0 },
    { imd: 5.0, raw_gfs: 14.8, corrected: 6.2 },
    { imd: 68.0, raw_gfs: 88.0, corrected: 72.4 },
    { imd: 140.0, raw_gfs: 198.0, corrected: 154.0 },
    { imd: 32.0, raw_gfs: 44.0, corrected: 35.1 }
  ]);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 p-6 rounded-2xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Triple-Source Rainfall Forecast Comparison</h2>
            <p className="text-xs text-slate-300 mt-0.5">
              Direct performance evaluation: Raw GFS 0.25° NWP Forecast vs AI Post-Processed Forecast vs Ground-Truth IMD 0.25° Observation.
            </p>
          </div>
        </div>
      </div>

      {/* Chart Grid: Line Chart + Bar Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Line Chart: Daily Time Series */}
        <div className="bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" /> Daily Rainfall Forecast Hydrograph
            </h3>
            <span className="text-[11px] text-slate-400 font-semibold">September 2024</span>
          </div>

          <div className="h-[320px] w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} label={{ value: 'Rainfall (mm)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Line type="monotone" dataKey="raw_gfs" name="Raw GFS NWP" stroke="#06b6d4" strokeWidth={2.5} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="corrected" name="AI Corrected" stroke="#10b981" strokeWidth={3} dot={{ r: 5 }} />
                <Line type="monotone" dataKey="imd_obs" name="IMD Observation" stroke="#f59e0b" strokeWidth={2.5} strokeDasharray="4 4" dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar Chart: Comparative Accumulation */}
        <div className="bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-indigo-400" /> Regional Forecast Comparison
            </h3>
            <span className="text-[11px] text-slate-400 font-semibold">24-hour Accumulation (mm)</span>
          </div>

          <div className="h-[320px] w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="raw_gfs" name="Raw GFS NWP" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                <Bar dataKey="corrected" name="AI Corrected" fill="#10b981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="imd_obs" name="IMD Observation" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Scatter Plot: Bias Reduction against Ground Truth */}
      <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" /> Forecast Scatter & Overestimation Bias Correction
            </h3>
            <p className="text-xs text-slate-400">
              Comparing raw GFS NWP vs AI Corrected Rainfall against IMD ground-truth observations. The AI model systematically reduces overestimation bias.
            </p>
          </div>
        </div>

        <div className="h-[350px] w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis type="number" dataKey="imd" name="IMD Observation (mm)" stroke="#94a3b8" fontSize={11} unit=" mm" label={{ value: 'IMD Observed Rainfall (mm)', position: 'insideBottom', offset: -10, fill: '#94a3b8', fontSize: 11 }} />
              <YAxis type="number" dataKey="raw_gfs" name="Forecast Rainfall (mm)" stroke="#94a3b8" fontSize={11} unit=" mm" label={{ value: 'Forecasted Rainfall (mm)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }} />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Scatter name="Raw GFS NWP (High Overestimation)" data={scatterData.map(d => ({ imd: d.imd, raw_gfs: d.raw_gfs }))} fill="#ef4444" shape="circle" />
              <Scatter name="AI Corrected (Aligned with 1:1 line)" data={scatterData.map(d => ({ imd: d.imd, raw_gfs: d.corrected }))} fill="#10b981" shape="triangle" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
