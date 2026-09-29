import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { fetchGridData } from '../services/api';
import { Layers, Calendar, Filter, Info, Eye } from 'lucide-react';

// Helper component to auto-fit map bounds when points load
function MapBoundsFitter({ points }) {
  const map = useMap();

  useEffect(() => {
    if (points && points.length > 0) {
      // Keep center over India [20.5937, 78.9629]
      map.setView([21.5, 79.0], 5);
    }
  }, [points, map]);

  return null;
}

export default function MapTab() {
  const [selectedDate, setSelectedDate] = useState('2024-09-30');
  const [availableDates, setAvailableDates] = useState([]);
  const [gridPoints, setGridPoints] = useState([]);
  const [activeLayer, setActiveLayer] = useState('corrected'); // 'corrected', 'gfs', 'heavy', 'very_heavy', 'extreme'
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [loading, setLoading] = useState(false);

  // Subsample step for rendering performance (show ~800-1000 representative points on client map)
  const [subsampleRatio, setSubsampleRatio] = useState(4);

  useEffect(() => {
    loadMapData(selectedDate);
  }, [selectedDate]);

  const loadMapData = async (dateStr) => {
    setLoading(true);
    try {
      const data = await fetchGridData(dateStr);
      if (data.available_dates && data.available_dates.length > 0) {
        setAvailableDates(data.available_dates);
        if (!data.available_dates.includes(selectedDate)) {
          setSelectedDate(data.available_dates[data.available_dates.length - 1]);
        }
      }
      setGridPoints(data.grid_points || []);
    } catch (err) {
      console.error('Map data load error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Color helper depending on active layer
  const getMarkerColor = (point) => {
    if (activeLayer === 'corrected' || activeLayer === 'gfs') {
      const val = activeLayer === 'corrected' ? point.corrected_rainfall : point.gfs_rain_24h;
      if (val >= 115.6) return '#c026d3'; // Very heavy - magenta/purple
      if (val >= 64.5) return '#ef4444'; // Heavy - red
      if (val >= 35.0) return '#f97316'; // Moderate - orange
      if (val >= 15.0) return '#eab308'; // Light-moderate - yellow
      if (val >= 2.5) return '#06b6d4'; // Light - cyan
      return '#3b82f6'; // Trace - blue
    } else {
      // Risk probabilities
      let prob = 0;
      if (activeLayer === 'heavy') prob = point.heavy_probability;
      else if (activeLayer === 'very_heavy') prob = point.very_heavy_probability;
      else if (activeLayer === 'extreme') prob = point.extremely_heavy_probability;

      if (prob >= 0.7) return '#dc2626'; // High risk - dark red
      if (prob >= 0.4) return '#f97316'; // Medium risk - orange
      if (prob >= 0.2) return '#eab308'; // Low-medium - yellow
      return '#3b82f6'; // Low risk - blue
    }
  };

  const getMarkerRadius = (point) => {
    if (activeLayer === 'corrected' || activeLayer === 'gfs') {
      const val = activeLayer === 'corrected' ? point.corrected_rainfall : point.gfs_rain_24h;
      if (val >= 64.5) return 7;
      if (val >= 15.0) return 5;
      return 3.5;
    } else {
      let prob = 0;
      if (activeLayer === 'heavy') prob = point.heavy_probability;
      else if (activeLayer === 'very_heavy') prob = point.very_heavy_probability;
      else if (activeLayer === 'extreme') prob = point.extremely_heavy_probability;
      if (prob >= 0.5) return 7;
      return 4;
    }
  };

  // Subsampled points for UI performance
  const displayPoints = gridPoints.filter((_, idx) => idx % subsampleRatio === 0);

  return (
    <div className="space-y-4">
      {/* Top Controls Bar */}
      <div className="bg-slate-900/90 backdrop-blur-md p-4 rounded-2xl border border-slate-800 shadow-xl flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Date Selector */}
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs uppercase tracking-wider">
            <Calendar className="w-4 h-4" /> Date:
          </div>
          <select
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="bg-slate-950 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white font-semibold focus:border-cyan-500 focus:outline-none"
          >
            {availableDates.map((date) => (
              <option key={date} value={date}>
                {date} (September 2024)
              </option>
            ))}
          </select>
          {loading && <span className="text-xs text-slate-400 animate-pulse">Loading map grid...</span>}
        </div>

        {/* Layer Selection Buttons */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
          <span className="text-xs text-slate-400 font-bold uppercase mr-1 hidden lg:inline">Layer:</span>
          {[
            { id: 'corrected', label: 'AI Corrected Rain', color: 'bg-emerald-500' },
            { id: 'gfs', label: 'Raw GFS Rain', color: 'bg-cyan-500' },
            { id: 'heavy', label: 'Heavy Risk (≥64.5mm)', color: 'bg-amber-500' },
            { id: 'very_heavy', label: 'Very Heavy (≥115.6mm)', color: 'bg-rose-500' },
            { id: 'extreme', label: 'Extreme (≥204.5mm)', color: 'bg-purple-500' },
          ].map((layer) => (
            <button
              key={layer.id}
              onClick={() => setActiveLayer(layer.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5 ${
                activeLayer === layer.id
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md shadow-blue-500/20 border border-blue-400/40'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700/80 border border-slate-700/60'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${layer.color}`} />
              {layer.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Map & Detail Panel Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Leaflet Map Canvas */}
        <div className="lg:col-span-3 bg-slate-900/90 rounded-2xl border border-slate-800 shadow-xl p-2 relative h-[580px] overflow-hidden">
          <MapContainer
            center={[21.5, 79.0]}
            zoom={5}
            scrollWheelZoom={true}
            style={{ height: '100%', width: '100%', borderRadius: '1rem' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
              url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            <MapBoundsFitter points={displayPoints} />

            {displayPoints.map((pt, idx) => (
              <CircleMarker
                key={idx}
                center={[pt.latitude, pt.longitude]}
                radius={getMarkerRadius(pt)}
                fillColor={getMarkerColor(pt)}
                color={getMarkerColor(pt)}
                weight={1}
                opacity={0.8}
                fillOpacity={0.7}
                eventHandlers={{
                  click: () => setSelectedPoint(pt),
                }}
              >
                <Popup>
                  <div className="p-1 space-y-1 text-xs">
                    <div className="font-bold text-cyan-400 border-b border-slate-700 pb-1">
                      Location: {pt.latitude}°N, {pt.longitude}°E
                    </div>
                    <div><span className="text-slate-400">Regime:</span> <b>{pt.regime}</b></div>
                    <div><span className="text-slate-400">Raw GFS:</span> <b>{pt.gfs_rain_24h} mm</b></div>
                    <div><span className="text-slate-400">AI Corrected:</span> <b className="text-emerald-400">{pt.corrected_rainfall} mm</b></div>
                    <div><span className="text-slate-400">Bias Delta:</span> <b>{pt.predicted_bias >= 0 ? `+${pt.predicted_bias}` : pt.predicted_bias} mm</b></div>
                    <div><span className="text-slate-400">Heavy Risk (≥64.5mm):</span> <b className="text-amber-400">{(pt.heavy_probability * 100).toFixed(1)}%</b></div>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>

          {/* Map Overlay Legend */}
          <div className="absolute bottom-4 left-4 z-[1000] bg-slate-900/90 backdrop-blur-md p-3 rounded-xl border border-slate-800 shadow-xl text-xs space-y-2">
            <div className="font-bold text-slate-200 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              {activeLayer === 'corrected' && 'AI Corrected Rainfall Legend'}
              {activeLayer === 'gfs' && 'Raw GFS Rainfall Legend'}
              {activeLayer.includes('heavy') || activeLayer === 'extreme' ? 'Risk Probability Legend' : ''}
            </div>

            {(activeLayer === 'corrected' || activeLayer === 'gfs') ? (
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 text-[10px]">
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-[#3b82f6]" /> &lt;15 mm</div>
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-[#06b6d4]" /> 15-35 mm</div>
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-[#eab308]" /> 35-64 mm</div>
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-[#f97316]" /> 64-115 mm</div>
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-[#ef4444]" /> Heavy</div>
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-[#c026d3]" /> Very Heavy</div>
              </div>
            ) : (
              <div className="flex items-center gap-3 text-[10px]">
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-[#3b82f6]" /> &lt;20%</div>
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-[#eab308]" /> 20-40%</div>
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-[#f97316]" /> 40-70%</div>
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-[#dc2626]" /> ≥70% Risk</div>
              </div>
            )}
          </div>
        </div>

        {/* Selected Grid Point Detail Sidebar */}
        <div className="bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-xl space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Eye className="w-4 h-4 text-cyan-400" /> Grid Point Inspector
          </h3>

          {selectedPoint ? (
            <div className="space-y-4 text-xs">
              <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/60 space-y-1">
                <span className="text-[10px] text-slate-400 font-bold uppercase block">Coordinates</span>
                <div className="text-sm font-extrabold text-cyan-400">
                  {selectedPoint.latitude}°N, {selectedPoint.longitude}°E
                </div>
              </div>

              <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/60 space-y-1">
                <span className="text-[10px] text-slate-400 font-bold uppercase block">Weather Regime</span>
                <div className="font-bold text-indigo-300">
                  {selectedPoint.regime}
                </div>
              </div>

              <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/60 space-y-2">
                <span className="text-[10px] text-slate-400 font-bold uppercase block">Rainfall Post-Processing</span>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Raw GFS:</span>
                  <span className="font-bold text-white">{selectedPoint.gfs_rain_24h} mm</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">AI Corrected:</span>
                  <span className="font-bold text-emerald-400 text-sm">{selectedPoint.corrected_rainfall} mm</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Bias Adjustment:</span>
                  <span className="font-bold text-cyan-300">
                    {selectedPoint.predicted_bias >= 0 ? `+${selectedPoint.predicted_bias}` : selectedPoint.predicted_bias} mm
                  </span>
                </div>
              </div>

              <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/60 space-y-2">
                <span className="text-[10px] text-amber-400 font-bold uppercase block">Heavy Rainfall Risk</span>
                <div className="flex justify-between items-center">
                  <span className="text-slate-300">Heavy (≥64.5mm):</span>
                  <span className="font-bold text-amber-300">{(selectedPoint.heavy_probability * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-300">Very Heavy (≥115.6mm):</span>
                  <span className="font-bold text-rose-300">{(selectedPoint.very_heavy_probability * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-300">Extreme (≥204.5mm):</span>
                  <span className="font-bold text-purple-300">{(selectedPoint.extremely_heavy_probability * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-6 text-center text-slate-400 text-xs bg-slate-800/30 rounded-xl border border-slate-800 space-y-2">
              <Info className="w-6 h-6 mx-auto text-slate-500" />
              <p>Click any grid circle on the India map to inspect exact location, regime classification, bias correction, and heavy rainfall probabilities.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
