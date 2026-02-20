// Visual Inspection tab — domain-specific fields

const INSPECTION_TYPES = [
  ["defect_detection","Defect Detection"],["quality_control","Quality Control"],
  ["anomaly_detection","Anomaly Detection"],["classification","Classification"],
];
const IMAGE_SOURCES = [
  ["camera","Camera"],["scanner","Scanner"],["mobile","Mobile"],["existing_dataset","Existing Dataset"],
];
const INSPECTION_POINTS = ["Single View","Multi-Angle","360°","Sequential Frames"];
const COST_MATRICES = ["Missed Defect is worse","False Alarm is worse","Balanced"];

export default function VisualTab({ values, onChange }) {
  function set(f, v) { onChange({ ...values, [f]: v }); }

  return (
    <div className="card">
      <div className="card-title"><span className="card-title-icon">🔍</span> Visual Inspection Specifics</div>
      <div className="grid-2" style={{ marginBottom: 14 }}>
        <div className="field">
          <label>Inspection Type</label>
          <select value={values.inspection_type || "defect_detection"} onChange={e => set("inspection_type", e.target.value)}>
            {INSPECTION_TYPES.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Image Source</label>
          <select value={values.image_source || "camera"} onChange={e => set("image_source", e.target.value)}>
            {IMAGE_SOURCES.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
      </div>
      <div className="field" style={{ marginBottom: 14 }}>
        <label>Defect Categories (comma-separated)</label>
        <input value={values.defect_categories || ""}
          onChange={e => set("defect_categories", e.target.value)}
          placeholder="e.g. Scratch, Dent, Discolouration" />
      </div>
      <div className="grid-3" style={{ marginBottom: 14 }}>
        <div className="field">
          <label>Accuracy Requirement (%)</label>
          <input type="number" value={Math.round((values.accuracy_requirement||0.95)*100)} min={50} max={100}
            onChange={e => set("accuracy_requirement", (parseInt(e.target.value)||95)/100)} />
        </div>
        <div className="field">
          <label>Existing Images Count</label>
          <input type="number" value={values.existing_images_count||0} min={0}
            onChange={e => set("existing_images_count", parseInt(e.target.value)||0)} />
        </div>
        <div className="field">
          <label>Requires Labeling</label>
          <select value={values.requires_labeling===false?"no":"yes"} onChange={e => set("requires_labeling", e.target.value==="yes")}>
            <option value="yes">Yes</option>
            <option value="no">No</option>
          </select>
        </div>
      </div>
      <div className="grid-2">
        <div className="field">
          <label>Inspection Points</label>
          <select value={values.inspection_points||"Single View"} onChange={e => set("inspection_points", e.target.value)}>
            {INSPECTION_POINTS.map(v => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Cost Matrix</label>
          <select value={values.cost_matrix||"Missed Defect is worse"} onChange={e => set("cost_matrix", e.target.value)}>
            {COST_MATRICES.map(v => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
      </div>
    </div>
  );
}
