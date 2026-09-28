import React from 'react';
import { Database, ShieldCheck, Globe, Calendar, Award, Layers } from 'lucide-react';

export default function AboutTab() {
  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 p-6 rounded-2xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">About the Project & Multi-Source Datasets</h2>
            <p className="text-xs text-slate-300 mt-0.5">
              Developed for Problem ID 26080: Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts (MoES / NCMRWF).
            </p>
          </div>
        </div>
      </div>

      {/* Problem Statement Details Card */}
      <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">MoES / NCMRWF Problem Statement #26080</span>
            <h3 className="text-lg font-bold text-white">Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts</h3>
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
            Theme: Smart Automation
          </span>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          The main objective of this project is to build an operational AI/ML rainfall post-processing system that first identifies the prevailing weather regime and then applies suitable correction to raw NWP rainfall forecasts. The goal is to improve rainfall forecasts over India, especially heavy and very heavy rainfall, providing a useful grid/district-level product.
        </p>
      </div>

      {/* Datasets Overview Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Dataset 1: GFS */}
        <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-800 shadow-xl space-y-3">
          <div className="w-9 h-9 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400">
            <Globe className="w-5 h-5" />
          </div>
          <h4 className="text-base font-bold text-white">1. NOAA/NCEP GFS 0.25° NWP</h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            Raw Global Forecast System numerical model data at 0.25° resolution. 24-hour total precipitation is constructed from forecast accumulation steps (f006 + f012 + f018 + f024).
          </p>
          <div className="text-[11px] text-cyan-400 font-semibold pt-2 border-t border-slate-800">
            Role: Input Raw Forecast Feature (gfs_rain_24h)
          </div>
        </div>

        {/* Dataset 2: ERA5 */}
        <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-800 shadow-xl space-y-3">
          <div className="w-9 h-9 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400">
            <Layers className="w-5 h-5" />
          </div>
          <h4 className="text-base font-bold text-white">2. ERA5 Reanalysis Atmospheric Data</h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            ECMWF ERA5 reanalysis at 500, 700, and 850 hPa pressure levels providing 18 thermodynamic variables: Relative Humidity (r), Temperature (t), Winds (u, v), Vertical Velocity (w), Geopotential (z).
          </p>
          <div className="text-[11px] text-purple-400 font-semibold pt-2 border-t border-slate-800">
            Role: Synoptic Weather Regime & Atmospheric State Features
          </div>
        </div>

        {/* Dataset 3: IMD */}
        <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-800 shadow-xl space-y-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400">
            <Award className="w-5 h-5" />
          </div>
          <h4 className="text-base font-bold text-white">3. IMD 0.25° Observed Rainfall</h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            India Meteorological Department high-resolution 0.25° daily gridded rainfall dataset based on rain-gauge network observations over the Indian mainland.
          </p>
          <div className="text-[11px] text-emerald-400 font-semibold pt-2 border-t border-slate-800">
            Role: Target Ground-Truth & Bias Evaluation (imd_rainfall)
          </div>
        </div>
      </div>

      {/* Dataset Metadata Summary Card */}
      <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-800 shadow-xl space-y-3">
        <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Calendar className="w-4 h-4 text-cyan-400" /> Training & Testing Period Statistics
        </h4>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 font-bold uppercase block">Total Valid Samples</span>
            <span className="text-xl font-extrabold text-white">425,500</span>
          </div>

          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 font-bold uppercase block">Total Days</span>
            <span className="text-xl font-extrabold text-cyan-400">92 Days</span>
          </div>

          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 font-bold uppercase block">Period</span>
            <span className="text-xs font-bold text-emerald-400">July 1 – Sept 30, 2024</span>
          </div>

          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 font-bold uppercase block">Missing Values</span>
            <span className="text-xl font-extrabold text-emerald-400">0 (Clean)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
