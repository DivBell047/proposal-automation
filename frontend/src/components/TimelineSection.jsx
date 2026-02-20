import { useState } from "react";

// Timeline options → number of week columns
const TIMELINE_OPTIONS = [
  ["4_weeks", "4 Weeks", 4],
  ["8_weeks", "8 Weeks", 8],
  ["12_weeks", "12 Weeks", 12],
  ["16_weeks", "16 Weeks", 16],
];

const DEFAULT_ROWS = [
  { phase: "Discovery & Scoping", task: "Requirements gathering, stakeholder interviews" },
  { phase: "Data Pipeline", task: "Source integration, transformation, validation" },
  { phase: "Model Development", task: "Training, evaluation, iteration" },
  { phase: "Integration & Testing", task: "API integration, UAT, performance testing" },
  { phase: "Go-Live & Handover", task: "Deployment, documentation, knowledge transfer" },
];

function buildWeekCols(n) {
  return Array.from({ length: n }, (_, i) => `Wk${i + 1}`);
}

function buildEmptyRow(weeks) {
  const row = { phase: "", task: "" };
  weeks.forEach(w => { row[w] = ""; });
  return row;
}

function initRows(weeks) {
  return DEFAULT_ROWS.map(r => {
    const row = { ...r };
    weeks.forEach(w => { row[w] = ""; });
    return row;
  });
}

export default function TimelineSection({ values, onChange }) {
  function set(field, val) { onChange({ ...values, [field]: val }); }

  // Derive week columns from selected timeline
  const selectedOption = TIMELINE_OPTIONS.find(o => o[0] === values.delivery_timeline) || TIMELINE_OPTIONS[0];
  const numWeeks = selectedOption[2];
  const weeks = buildWeekCols(numWeeks);

  // Initialise timeline_data if not yet set or if weeks changed
  const rows = (() => {
    const existing = values.timeline_data;
    if (!existing || existing.length === 0) return initRows(weeks);
    // If number of week columns changed, reshape rows
    const hasCorrectCols = weeks.every(w => w in existing[0]);
    if (!hasCorrectCols) {
      return existing.map(r => {
        const newRow = { phase: r.phase || "", task: r.task || "" };
        weeks.forEach(w => { newRow[w] = r[w] || ""; });
        return newRow;
      });
    }
    return existing;
  })();

  function handleTimelineChange(newTimeline) {
    const newOpt = TIMELINE_OPTIONS.find(o => o[0] === newTimeline);
    const newWeeks = buildWeekCols(newOpt[2]);
    // Reshape existing rows to match new week count
    const reshapedRows = rows.map(r => {
      const newRow = { phase: r.phase || "", task: r.task || "" };
      newWeeks.forEach(w => { newRow[w] = r[w] || ""; });
      return newRow;
    });
    onChange({ ...values, delivery_timeline: newTimeline, timeline_data: reshapedRows });
  }

  function updateCell(rowIdx, col, val) {
    const updated = rows.map((r, i) => i === rowIdx ? { ...r, [col]: val } : r);
    set("timeline_data", updated);
  }

  function addRow() {
    set("timeline_data", [...rows, buildEmptyRow(weeks)]);
  }

  function removeRow(idx) {
    set("timeline_data", rows.filter((_, i) => i !== idx));
  }

  return (
    <div className="card">
      <div className="card-title"><span className="card-title-icon">🗓️</span> Timeline & Commercials</div>

      <div className="grid-3" style={{ marginBottom: 18 }}>
        <div className="field">
          <label>Delivery Timeline</label>
          <select value={values.delivery_timeline} onChange={e => handleTimelineChange(e.target.value)}>
            {TIMELINE_OPTIONS.map(([v,,label]) => <option key={v} value={v}>{label}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Estimated Budget (USD)</label>
          <input type="number" value={values.estimated_budget_usd} min={0} step={1000}
            onChange={e => set("estimated_budget_usd", parseInt(e.target.value) || 0)} />
        </div>
        <div className="field">
          <label>Key Assumptions</label>
          <input value={values.key_assumptions || ""} onChange={e => set("key_assumptions", e.target.value)}
            placeholder="e.g. Client provides labelled data" />
        </div>
      </div>

      {/* Gantt Table */}
      <div style={{ overflowX: "auto" }}>
        <table className="tl-table">
          <thead>
            <tr>
              <th style={{ width: 150, textAlign: "left" }}>Phase</th>
              <th style={{ textAlign: "left", minWidth: 180 }}>Task</th>
              {weeks.map(w => <th key={w} style={{ minWidth: 36 }}>{w}</th>)}
              <th style={{ width: 30 }}></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri}>
                <td>
                  <input className="tl-cell-text" value={row.phase} onChange={e => updateCell(ri, "phase", e.target.value)} placeholder="Phase name" />
                </td>
                <td>
                  <input className="tl-cell-text" value={row.task} onChange={e => updateCell(ri, "task", e.target.value)} placeholder="Task description" />
                </td>
                {weeks.map(w => (
                  <td key={w} className={row[w] === "X" || row[w] === "x" ? "filled" : ""}>
                    <input className="tl-cell-input" value={row[w] || ""} maxLength={1}
                      onChange={e => updateCell(ri, w, e.target.value.toUpperCase())} />
                  </td>
                ))}
                <td style={{ textAlign: "center" }}>
                  <button className="btn-ghost" style={{ padding: "2px 8px", fontSize: 11 }}
                    onClick={() => removeRow(ri)}>×</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button className="tl-add-row" onClick={addRow}>+ Add Row</button>
    </div>
  );
}
