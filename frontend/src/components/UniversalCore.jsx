// Shared "Universal Core" section — Problem, Data, Intelligence, Execution
// Mirrors UniversalProposalCore fields from src/models.py

const ERROR_TOLERANCES = [["low","Low"],["medium","Medium"],["high","High"]];
const DATA_SOURCES = [["database","Database"],["api","API"],["files","Files"],["images","Images"],["video","Video"],["mixed","Mixed"]];
const DATA_FREQS = [["real_time","Real-time"],["batch_daily","Daily Batch"],["batch_weekly","Weekly Batch"],["batch_monthly","Monthly Batch"]];
const DATA_QUALITIES = [["clean","Clean"],["usable_with_gaps","Usable with Gaps"],["noisy","Noisy"]];
const AUTONOMY = [["advisory","Advisory (human in loop)"],["autonomous","Autonomous"]];
const OPT_GOALS = [["accuracy","Accuracy"],["latency","Latency"],["explainability","Explainability"]];
const INFERENCE_LOCS = [["cloud","Cloud"],["edge","Edge"],["hybrid","Hybrid"]];
const CLOUD_PROVIDERS = [["aws","AWS"],["azure","Azure"],["gcp","GCP"],["other","Other"]];
const EDGE_HW = [["nvidia_jetson","NVIDIA Jetson"],["raspberry_pi","Raspberry Pi"],["mobile_device","Mobile Device"],["industrial_pc","Industrial PC"],["other","Other"]];
const EXEC_TRIGGERS = [["scheduled","Scheduled"],["event_based","Event-Based"],["user_action","User Action"]];

export default function UniversalCore({ values, onChange }) {
  function set(field, val) { onChange({ ...values, [field]: val }); }

  return (
    <>
      {/* Problem & Outcome */}
      <div className="card">
        <div className="card-title"><span className="card-title-icon">⚠️</span> Problem & Outcome</div>
        <div className="grid-2" style={{ marginBottom: 14 }}>
          <div className="field">
            <label>Decision Being Supported *</label>
            <input value={values.decision_supported} onChange={e => set("decision_supported", e.target.value)} placeholder="e.g. Weekly replenishment planning" />
          </div>
          <div className="field">
            <label>Current Failure Mode *</label>
            <input value={values.failure_mode} onChange={e => set("failure_mode", e.target.value)} placeholder="e.g. Manual spreadsheet errors" />
          </div>
        </div>
        <div className="field">
          <label>Error Tolerance</label>
          <select value={values.error_tolerance} onChange={e => set("error_tolerance", e.target.value)}>
            {ERROR_TOLERANCES.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
      </div>

      {/* Data Reality */}
      <div className="card">
        <div className="card-title"><span className="card-title-icon">🗄️</span> Data Reality</div>
        <div className="grid-3">
          <div className="field">
            <label>Data Source</label>
            <select value={values.data_source_type} onChange={e => set("data_source_type", e.target.value)}>
              {DATA_SOURCES.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Arrival Frequency</label>
            <select value={values.data_frequency} onChange={e => set("data_frequency", e.target.value)}>
              {DATA_FREQS.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Data Quality</label>
            <select value={values.data_quality} onChange={e => set("data_quality", e.target.value)}>
              {DATA_QUALITIES.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
        </div>
      </div>

      {/* Intelligence Layer */}
      <div className="card">
        <div className="card-title"><span className="card-title-icon">🧠</span> Intelligence Layer</div>
        <div className="grid-3">
          <div className="field">
            <label>System Autonomy</label>
            <select value={values.system_autonomy} onChange={e => set("system_autonomy", e.target.value)}>
              {AUTONOMY.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Optimization Priority</label>
            <select value={values.optimization_goal} onChange={e => set("optimization_goal", e.target.value)}>
              {OPT_GOALS.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Retraining Frequency</label>
            <input value={values.retraining_frequency} onChange={e => set("retraining_frequency", e.target.value)} placeholder="e.g. Monthly" />
          </div>
        </div>
      </div>

      {/* Execution */}
      <div className="card">
        <div className="card-title"><span className="card-title-icon">⚙️</span> Execution</div>
        <div className="grid-3" style={{ marginBottom: 14 }}>
          <div className="field">
            <label>Inference Location</label>
            <select value={values.inference_location} onChange={e => set("inference_location", e.target.value)}>
              {INFERENCE_LOCS.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          {(values.inference_location === "cloud" || values.inference_location === "hybrid") && (
            <div className="field">
              <label>Cloud Provider</label>
              <select value={values.cloud_provider || ""} onChange={e => set("cloud_provider", e.target.value)}>
                <option value="">— Select —</option>
                {CLOUD_PROVIDERS.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>
          )}
          {(values.inference_location === "edge" || values.inference_location === "hybrid") && (
            <div className="field">
              <label>Edge Hardware</label>
              <select value={values.edge_hardware || ""} onChange={e => set("edge_hardware", e.target.value)}>
                <option value="">— Select —</option>
                {EDGE_HW.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>
          )}
          <div className="field">
            <label>Execution Trigger</label>
            <select value={values.execution_trigger} onChange={e => set("execution_trigger", e.target.value)}>
              {EXEC_TRIGGERS.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
        </div>
        <div className="field">
          <label>Failure Handling</label>
          <input value={values.failure_handling} onChange={e => set("failure_handling", e.target.value)} placeholder="e.g. Human Review" />
        </div>
      </div>
    </>
  );
}
