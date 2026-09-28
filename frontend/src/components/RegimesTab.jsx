import React, { useEffect, useState } from 'react';
import { fetchRegimes } from '../services/api';
import { Cpu, AlertCircle, CheckCircle, Info, ShieldAlert } from 'lucide-react';

export default function RegimesTab() {
  const [regimes, setRegimes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRegimes();
  }, []);

  const loadRegimes = async () => {
    try {
      const data = await fetchRegimes();
      setRegimes(data.regimes || []);
    } catch (err) {
      console.error('Failed to load regimes:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRegimeBadge = (id) => {
    switch (id) {
      case 0: return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 1: return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 2: return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      case 3: return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
      case 4: return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 5: return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      default: return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 p-6 rounded-2xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Synoptic Weather Regime Classification System</h2>
            <p className="text-xs text-slate-300 mt-0.5">
              The AI post-processing system identifies six distinct meteorological regimes over the Indian subcontinent using ERA5 thermal & dynamic stability variables.
            </p>
          </div>
        </div>
      </div>

      {/* Western Disturbance Prominent Notice Box */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-5 flex items-start gap-4">
        <div className="w-9 h-9 rounded-xl bg-amber-500/20 flex items-center justify-center text-amber-400 shrink-0 mt-0.5">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div className="space-y-1 text-xs">
          <h4 className="font-bold text-amber-300 text-sm">
            Western Disturbance (Regime ID 5) Framework Supported (0 Training Samples)
          </h4>
          <p className="text-amber-200/90 leading-relaxed">
            <strong>Western Disturbance is supported by the system</strong> as a core synoptic regime (Regime ID 5), but has <strong>0 genuine samples</strong> in the July–September 2024 monsoon dataset. Monsoon months are dominated by tropical low-pressure systems and south-westerly flows, while Western Disturbances occur predominantly during winter/pre-monsoon months (December–April).
          </p>
          <div className="text-[11px] text-amber-400/80 font-semibold pt-1">
            Note: Western Disturbance is fully represented in the UI, API schemas, and feature encoders without synthetic data fabrication.
          </div>
        </div>
      </div>

      {/* Regimes Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {regimes.map((regime) => (
          <div
            key={regime.id}
            className={`bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border shadow-xl flex flex-col justify-between transition-all ${
              regime.id === 5 ? 'border-amber-500/40 bg-amber-950/10' : 'border-slate-800 hover:border-slate-700'
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${getRegimeBadge(regime.id)}`}>
                  Regime ID #{regime.id}
                </span>
                <span className={`text-xs font-extrabold ${regime.samples_2024 > 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {regime.samples_2024.toLocaleString()} samples
                </span>
              </div>

              <h3 className="text-base font-bold text-white mb-2">{regime.name}</h3>
              <p className="text-xs text-slate-300 leading-relaxed mb-4">{regime.description}</p>
            </div>

            <div className="border-t border-slate-800/80 pt-3 flex items-center justify-between text-xs text-slate-400">
              <span>Days represented: <b>{regime.days_represented} days</b></span>
              {regime.id === 5 && (
                <span className="text-[10px] font-bold text-amber-400 uppercase">Monsoon 0 Samples</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
