// Demand Forecasting tab — domain-specific fields
const METHODS = [
  ["time_series","Time Series"],["regression","Regression"],["ensemble","Ensemble"],["deep_learning","Deep Learning"],
];
const FORECAST_LEVELS = ["SKU Level","Category Level","Store Level","Region Level","National Level"];
const VOLATILITY = ["Stable","Seasonal","Highly Volatile","Intermittent"];
const PLANNING_DECISIONS = ["Inventory Replenishment","Production Planning","Logistics Scheduling","Pricing Optimization"];
const FEATURE_OPTS = ["price","promotions","seasonality","weather","holidays"];

function ChipGroup({ options, selected, onChange }) {
  function toggle(val) {
    onChange(selected.includes(val) ? selected.filter(v=>v!==val) : [...selected, val]);
  }
  return (
    <div className="checkbox-group">
      {options.map(([v,l]) => (
        <label key={v} className={`chip ${selected.includes(v)?"selected":""}`}>
          <input type="checkbox" checked={selected.includes(v)} onChange={()=>toggle(v)} />{l}
        </label>
      ))}
    </div>
  );
}

export default function DemandTab({ values, onChange }) {
  function set(f, v) { onChange({ ...values, [f]: v }); }
  const features = values.features_available || [];

  function toggleFeature(f) {
    onChange({ ...values, features_available: features.includes(f) ? features.filter(x=>x!==f) : [...features, f] });
  }

  return (
    <div className="card">
      <div className="card-title"><span className="card-title-icon">📈</span> Demand Forecasting Specifics</div>

      {/* Forecasting Methods — multi-select chips */}
      <div className="field" style={{ marginBottom: 14 }}>
        <label>Forecasting Methods * (select all that apply)</label>
        <ChipGroup options={METHODS} selected={values.forecasting_methods || []}
          onChange={v => set("forecasting_methods", v)} />
      </div>

      <div className="grid-3" style={{ marginBottom: 14 }}>
        <div className="field">
          <label>Forecast Horizon (days)</label>
          <input type="number" value={values.forecast_horizon_days || 30} min={1}
            onChange={e => set("forecast_horizon_days", parseInt(e.target.value)||30)} />
        </div>
        <div className="field">
          <label>Historical Data (years)</label>
          <input type="number" value={values.historical_data_years || 2} min={1} max={20}
            onChange={e => set("historical_data_years", parseInt(e.target.value)||2)} />
        </div>
        <div className="field">
          <label>Forecast Level</label>
          <select value={values.forecast_level || "SKU Level"} onChange={e => set("forecast_level", e.target.value)}>
            {FORECAST_LEVELS.map(v => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 14 }}>
        <div className="field">
          <label>Demand Volatility</label>
          <select value={values.demand_volatility || "Stable"} onChange={e => set("demand_volatility", e.target.value)}>
            {VOLATILITY.map(v => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Planning Decision</label>
          <select value={values.planning_decision || "Inventory Replenishment"} onChange={e => set("planning_decision", e.target.value)}>
            {PLANNING_DECISIONS.map(v => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
      </div>

      {/* Available Features — checkboxes */}
      <div className="field">
        <label>Available Features</label>
        <div className="checkbox-group">
          {FEATURE_OPTS.map(f => (
            <label key={f} className={`chip ${features.includes(f)?"selected":""}`}>
              <input type="checkbox" checked={features.includes(f)} onChange={()=>toggleFeature(f)} />
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
