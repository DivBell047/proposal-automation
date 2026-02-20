// RFP Specifics — mirrors the RFP enhancement fields from UniversalProposalCore
import { uploadLogo } from "../api";
import { useState } from "react";

const SUCCESS_DIMS = [
  ["accuracy","Accuracy"],["latency","Latency"],["throughput","Throughput"],
  ["cost_efficiency","Cost Efficiency"],["user_adoption","User Adoption"],["coverage","Coverage"],
];
const SECURITY_STANDARDS = [
  ["soc2","SOC 2"],["hipaa","HIPAA"],["gdpr","GDPR"],["iso27001","ISO 27001"],["pci_dss","PCI DSS"],["none","None"],
];
const SECURITY_CONTROLS = [
  ["vpc_deployment","VPC"],["iam_access_control","IAM"],["encryption_at_rest","Encryption at Rest"],
  ["encryption_in_transit","Encryption in Transit"],["audit_logging","Audit Logging"],["multi_factor_auth","MFA"],
];
const DATA_FORMATS = [
  ["json","JSON"],["csv","CSV"],["pdf","PDF"],["image","Image"],
  ["video","Video"],["audio","Audio"],["text","Text"],["parquet","Parquet"],
];
const DATA_VOL_UNITS = [["mb","MB"],["gb","GB"],["tb","TB"],["million_records","M Records"],["thousand_records","K Records"]];

function ChipGroup({ options, selected, onChange }) {
  function toggle(val) {
    onChange(selected.includes(val) ? selected.filter(v => v !== val) : [...selected, val]);
  }
  return (
    <div className="checkbox-group">
      {options.map(([v, l]) => (
        <label key={v} className={`chip ${selected.includes(v) ? "selected" : ""}`}>
          <input type="checkbox" checked={selected.includes(v)} onChange={() => toggle(v)} />
          {l}
        </label>
      ))}
    </div>
  );
}

export default function RFPSection({ values, onChange }) {
  const [uploading, setUploading] = useState(false);
  function set(field, val) { onChange({ ...values, [field]: val }); }

  async function handleDiagramUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      const { path } = await uploadLogo(file);   // reuse same endpoint
      set("architecture_diagram_path", path);
    } catch (err) {
      alert("Upload failed: " + err.message);
    } finally { setUploading(false); }
  }

  return (
    <div className="card">
      <div className="card-title"><span className="card-title-icon">📋</span> RFP Specifics</div>

      {/* Architecture Diagram */}
      <div className="field" style={{ marginBottom: 14 }}>
        <label>Architecture Diagram</label>
        <label className="logo-upload" style={{ textAlign:"left", display:"flex", alignItems:"center", gap:12, cursor: uploading?"wait":"pointer" }}>
          {values.architecture_diagram_path
            ? <span style={{ color:"var(--accent)", fontSize:12 }}>✅ {values.architecture_diagram_path.split(/[\\/]/).pop()}</span>
            : <span style={{ color:"var(--text-dim)", fontSize:12 }}>{uploading ? "Uploading…" : "Click to upload diagram image"}</span>
          }
          <input type="file" accept="image/*" onChange={handleDiagramUpload} disabled={uploading} />
        </label>
      </div>

      {/* Success Dimensions */}
      <div className="field" style={{ marginBottom: 14 }}>
        <label>Success Dimensions</label>
        <ChipGroup options={SUCCESS_DIMS} selected={values.success_dimensions || []}
          onChange={v => set("success_dimensions", v)} />
      </div>

      {/* Validation strategy */}
      <div className="field" style={{ marginBottom: 14 }}>
        <label>Validation Strategy</label>
        <input value={values.validation_strategy || ""} onChange={e => set("validation_strategy", e.target.value)}
          placeholder="e.g. Human-in-the-loop validation" />
      </div>

      {/* Security */}
      <div className="grid-2" style={{ marginBottom: 14 }}>
        <div className="field">
          <label>Security Standards</label>
          <ChipGroup options={SECURITY_STANDARDS} selected={values.security_standards || []}
            onChange={v => set("security_standards", v)} />
        </div>
        <div className="field">
          <label>Security Controls</label>
          <ChipGroup options={SECURITY_CONTROLS} selected={values.security_controls || []}
            onChange={v => set("security_controls", v)} />
        </div>
      </div>

      {/* Data */}
      <div className="field" style={{ marginBottom: 14 }}>
        <label>Data Formats</label>
        <ChipGroup options={DATA_FORMATS} selected={values.data_format || []}
          onChange={v => set("data_format", v)} />
      </div>
      <div className="grid-2">
        <div className="field">
          <label>Data Volume</label>
          <input type="number" value={values.data_volume || 1} min={0} step={0.1}
            onChange={e => set("data_volume", parseFloat(e.target.value) || 0)} />
        </div>
        <div className="field">
          <label>Volume Unit</label>
          <select value={values.data_volume_unit || "gb"} onChange={e => set("data_volume_unit", e.target.value)}>
            {DATA_VOL_UNITS.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
      </div>
    </div>
  );
}
