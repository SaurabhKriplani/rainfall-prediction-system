import React from 'react';
import { Cpu, ArrowDown, Database, Compass, Sparkles, CheckCircle2, ShieldAlert } from 'lucide-react';

export default function MethodologyTab() {
  const steps = [
    {
      step: '01',
      title: 'Raw NWP Forecast Retrieval',
      source: 'NOAA/NCEP GFS 0.25°',
      desc: 'Retrieves 0.25° gridded global numerical weather prediction data. 24-hour accumulated rainfall is constructed from four 6-hour forecast accumulation steps: f006 + f012 + f018 + f024.'
    },
    {
      step: '02',
      title: 'Atmospheric State Extraction',
      source: 'ERA5 Reanalysis (500, 700, 850 hPa)',
      desc: 'Extracts 6 core thermodynamic and dynamic pressure-level variables: Geopotential (z), Relative Humidity (r), Temperature (t), U/V Wind components, and Vertical Velocity (w).'
    },
    {
      step: '03',
      title: 'Synoptic Weather Regime Classification',
      source: '6 Synoptic Regimes',
      desc: 'Classifies the prevailing meteorological state into 1 of 6 synoptic regimes (Active Monsoon, Break Monsoon, Low/Depression, Orographic, Coastal, Western Disturbance).'
    },
    {
      step: '04',
      title: 'Regime-Aware XGBoost Bias Regression',
      source: 'XGBRegressor Model',
      desc: 'Trained on 286,750 July+August samples to predict localized GFS bias target: bias = IMD_Observed - GFS_Forecast. Features include GFS rain, location, ERA5 levels & regime ID.'
    },
    {
      step: '05',
      title: 'Physical Corrected Rainfall Calculation',
      source: 'Post-Processed Output',
      desc: 'Applies physics-constrained adjustment: Corrected_Rainfall = max(0, GFS_Rainfall + Predicted_Bias), preventing physically invalid negative rainfall estimates.'
    },
    {
      step: '06',
      title: 'Multi-Threshold Heavy Risk Classification',
      source: '3 XGBClassifiers',
      desc: 'Trains dedicated binary classification models with scale_pos_weight for imbalance to estimate calibrated risk probabilities for Heavy (≥64.5mm), Very Heavy (≥115.6mm), and Extreme (≥204.5mm).'
    },
    {
      step: '07',
      title: 'Grid & District Forecast Product Generation',
      source: 'FastAPI + React Dashboard',
      desc: 'Exposes persistent REST endpoints and interactive Leaflet map layers to present gridded bias-corrected forecasts and risk probability products to forecasters.'
    },
    {
      step: '08',
      title: 'Verification & Performance Assessment',
      source: 'IMD Ground Truth Evaluation',
      desc: 'Evaluates performance against IMD high-resolution observations using RMSE, MAE, CSI, POD, FAR, ETS, and spatial Fractions Skill Score (FSS).'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 p-6 rounded-2xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">System Architecture & Pipeline Methodology</h2>
            <p className="text-xs text-slate-300 mt-0.5">
              Comprehensive 8-step regime-aware machine learning pipeline for post-processing monsoon rainfall forecasts over India.
            </p>
          </div>
        </div>
      </div>

      {/* Step by Step Vertical Pipeline */}
      <div className="space-y-4">
        {steps.map((item, idx) => (
          <div key={idx} className="relative">
            <div className="bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4 group hover:border-slate-700 transition-all">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-600 text-white font-extrabold flex items-center justify-center text-sm shrink-0 shadow-md">
                  {item.step}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-white group-hover:text-cyan-400 transition-colors">{item.title}</h3>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-cyan-400 border border-slate-700">
                      {item.source}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                    {item.desc}
                  </p>
                </div>
              </div>
            </div>

            {idx < steps.length - 1 && (
              <div className="flex justify-center my-1">
                <ArrowDown className="w-4 h-4 text-slate-600 animate-bounce" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
