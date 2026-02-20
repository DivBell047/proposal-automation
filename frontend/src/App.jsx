import { useState } from "react";
import "./index.css";
import { generateProposal } from "./api";
import GlobalSettings from "./components/GlobalSettings";
import UniversalCore from "./components/UniversalCore";
import TimelineSection from "./components/TimelineSection";
import RFPSection from "./components/RFPSection";
import DemandTab from "./components/tabs/DemandTab";
import VisualTab from "./components/tabs/VisualTab";
import ChatbotTab from "./components/tabs/ChatbotTab";

// Default form state — mirrors Pydantic model defaults
const BASE_DEFAULTS = {
  // Global
  client_name: "", vendor_name: "Oneture", industry: "retail",
  client_logo_path: null, company_logo_path: null,
  // Universal Core
  decision_supported: "", failure_mode: "", error_tolerance: "medium",
  data_source_type: "database", data_frequency: "batch_daily", data_quality: "clean",
  system_autonomy: "advisory", optimization_goal: "accuracy", retraining_frequency: "Monthly",
  inference_location: "cloud", cloud_provider: "aws", edge_hardware: null,
  execution_trigger: "scheduled", failure_handling: "Human Review",
  // Timeline & Commercials
  delivery_timeline: "8_weeks", estimated_budget_usd: 50000, key_assumptions: "", timeline_data: [],
  // RFP
  success_dimensions: [], validation_strategy: "Human-in-the-loop validation",
  security_standards: [], security_controls: [],
  data_format: [], data_volume: 1.0, data_volume_unit: "gb",
  architecture_diagram_path: null,
};

const DEMAND_DEFAULTS = {
  ...BASE_DEFAULTS,
  estimated_budget_usd: 50000,
  forecasting_methods: ["time_series"],
  forecast_horizon_days: 30, historical_data_years: 2,
  forecast_level: "SKU Level", demand_volatility: "Stable",
  planning_decision: "Inventory Replenishment",
  features_available: [],
};
const VISUAL_DEFAULTS = {
  ...BASE_DEFAULTS,
  estimated_budget_usd: 60000,
  inspection_type: "defect_detection", defect_categories: [],
  accuracy_requirement: 0.95, image_source: "camera",
  existing_images_count: 0, requires_labeling: true,
  inspection_points: "Single View", cost_matrix: "Missed Defect is worse",
};
const CHATBOT_DEFAULTS = {
  ...BASE_DEFAULTS,
  estimated_budget_usd: 40000,
  chatbot_type: "customer_support",
  integration_platforms: ["website"],
  expected_queries_per_day: 100,
  requires_multilingual: false, languages_required: [],
  response_type: "Generated", requires_human_handoff: true,
  document_formats: [], traceability_required: true,
  channel_strategy: "single", auth_method: "public_anonymous",
  orchestration_type: "single_model", hosting_strategy: "managed_saas",
  hosting_provider_detail: null,
  knowledge_strategy: "pretrained_only", knowledge_sources: [],
  knowledge_update_freq: "Daily", guardrail_level: "basic_filtering",
  analytics_depth: "Standard", deployment_phase: "POC",
};

const TABS = [
  { id: "demand", label: "📈 Demand Forecasting" },
  { id: "visual", label: "🔍 Visual Inspection" },
  { id: "chatbot", label: "🤖 Chatbot" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("demand");
  const [demand, setDemand] = useState(DEMAND_DEFAULTS);
  const [visual, setVisual] = useState(VISUAL_DEFAULTS);
  const [chatbot, setChatbot] = useState(CHATBOT_DEFAULTS);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null); // { type: "ok"|"err", msg }

  const [formState, setFormState] = activeTab === "demand"
    ? [demand, setDemand]
    : activeTab === "visual"
    ? [visual, setVisual]
    : [chatbot, setChatbot];

  const apiType = activeTab; // "demand" | "visual" | "chatbot"

  async function handleGenerate() {
    setLoading(true);
    setStatus(null);
    try {
      // Split comma-string fields → arrays before sending to backend
      const split = s => typeof s === "string" ? s.split(",").map(x=>x.trim()).filter(Boolean) : (s || []);
      const payload = {
        ...formState,
        defect_categories:    split(formState.defect_categories),
        languages_required:   split(formState.languages_required),
        knowledge_sources:    split(formState.knowledge_sources),
        document_formats:     split(formState.document_formats),
      };
      await generateProposal(apiType, payload);
      setStatus({ type: "ok", msg: "✅ Proposal downloaded!" });
    } catch (err) {
      setStatus({ type: "err", msg: "❌ " + err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      {/* Header */}
      <div className="app-header">
        <div className="app-header-icon">📄</div>
        <div>
          <h1>Proposal Automation</h1>
          <p>Generate client-facing RFP proposal decks powered by AI</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="tab-bar">
        {TABS.map(t => (
          <button key={t.id} className={`tab-btn ${activeTab===t.id?"active":""}`}
            onClick={() => { setActiveTab(t.id); setStatus(null); }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Global Settings (shared across all tabs) */}
      <GlobalSettings values={formState} onChange={setFormState} />

      {/* Universal Core */}
      <UniversalCore values={formState} onChange={setFormState} />

      {/* Domain-specific tab content */}
      {activeTab === "demand" && <DemandTab values={formState} onChange={setFormState} />}
      {activeTab === "visual" && <VisualTab values={formState} onChange={setFormState} />}
      {activeTab === "chatbot" && <ChatbotTab values={formState} onChange={setFormState} />}

      {/* RFP Specifics */}
      <RFPSection values={formState} onChange={setFormState} />

      {/* Timeline & Commercials */}
      <TimelineSection values={formState} onChange={setFormState} />

      {/* Generate Bar */}
      <div className="generate-bar">
        {status && <span className={`status-msg ${status.type}`}>{status.msg}</span>}
        <button className="btn-primary" onClick={handleGenerate} disabled={loading}>
          {loading ? <><div className="spinner" /> Generating…</> : <>⚡ Generate Proposal</>}
        </button>
      </div>
    </div>
  );
}
