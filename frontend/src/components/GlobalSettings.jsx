import { useState } from "react";
import { uploadLogo } from "../api";

const INDUSTRIES = [
  ["retail","Retail"],["manufacturing","Manufacturing"],["healthcare","Healthcare"],
  ["finance","Finance"],["logistics","Logistics"],["other","Other"],
];

export default function GlobalSettings({ values, onChange }) {
  const [uploading, setUploading] = useState(false);

  function set(field, val) { onChange({ ...values, [field]: val }); }

  async function handleLogoUpload(e, field) {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      const { path } = await uploadLogo(file);
      set(field, path);
    } catch (err) {
      alert("Logo upload failed: " + err.message);
    } finally { setUploading(false); }
  }

  return (
    <div className="card">
      <div className="card-title"><span className="card-title-icon">🏢</span> Project Identity</div>
      <div className="grid-2" style={{ marginBottom: 14 }}>
        <div className="field">
          <label>Client Name *</label>
          <input value={values.client_name} onChange={e => set("client_name", e.target.value)} placeholder="e.g. Acme Corp" />
        </div>
        <div className="field">
          <label>Vendor Name *</label>
          <input value={values.vendor_name} onChange={e => set("vendor_name", e.target.value)} placeholder="e.g. Oneture" />
        </div>
      </div>
      <div className="field" style={{ marginBottom: 14 }}>
        <label>Industry</label>
        <select value={values.industry} onChange={e => set("industry", e.target.value)}>
          {INDUSTRIES.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      </div>
      <div className="grid-2">
        <LogoUpload label="Client Logo" path={values.client_logo_path} uploading={uploading}
          onChange={e => handleLogoUpload(e, "client_logo_path")} />
        <LogoUpload label="Company Logo" path={values.company_logo_path} uploading={uploading}
          onChange={e => handleLogoUpload(e, "company_logo_path")} />
      </div>
    </div>
  );
}

function LogoUpload({ label, path, uploading, onChange }) {
  return (
    <div className="field">
      <label>{label}</label>
      <label className="logo-upload" style={{ cursor: uploading ? "wait" : "pointer" }}>
        {path
          ? <p style={{ color: "var(--accent)", fontSize: 12 }}>✅ {path.split(/[\\/]/).pop()}</p>
          : <p>{uploading ? "Uploading…" : "Click to upload"}</p>
        }
        <input type="file" accept="image/*" onChange={onChange} disabled={uploading} />
      </label>
    </div>
  );
}
