// Chatbot tab — domain-specific fields (full parity with Streamlit)
const CHATBOT_TYPES = [
  ["customer_support","Customer Support"],["faq","FAQ"],["sales_assistant","Sales Assistant"],["internal_helpdesk","Internal Helpdesk"],
];
const PLATFORMS = [
  ["website","Website"],["slack","Slack"],["teams","Teams"],["whatsapp","WhatsApp"],["mobile_app","Mobile App"],
];
const CHANNEL_STRATEGIES = [["single","Single Channel"],["multi_channel","Multi-Channel"],["omnichannel","Omnichannel"]];
const AUTH_METHODS = [["public_anonymous","Public / Anonymous"],["internal_sso_iam","Internal SSO/IAM"],["customer_oauth","Customer OAuth"],["hybrid","Hybrid"]];
const ORCHESTRATIONS = [["single_model","Single Model"],["rag_pipeline","RAG Pipeline"],["agentic_workflow","Agentic Workflow"],["multi_agent_swarm","Multi-Agent"]];
const HOSTING = [["managed_saas","Managed SaaS"],["vpc_private_cloud","VPC Private Cloud"],["hybrid_cloud","Hybrid Cloud"],["on_prem_edge","On-Prem/Edge"]];
const KNOWLEDGE = [["pretrained_only","Pretrained Only"],["rag_vector_search","RAG Vector Search"],["rag_knowledge_graph","RAG Knowledge Graph"],["hybrid_rag","Hybrid RAG"]];
const GUARDRAILS = [["basic_filtering","Basic Filtering"],["moderate_safety","Moderate Safety"],["strict_enterprise","Strict Enterprise"],["compliance_regulated","Compliance Regulated"]];
const DEPLOY_PHASES = ["POC","MVP","Production Pilot","Scale Rollout"];
const ANALYTICS_DEPTHS = ["Basic","Standard","Advanced (Conversational Intelligence)"];
const KNOW_FREQS = ["Real-time","Hourly","Daily","Weekly"];

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

export default function ChatbotTab({ values, onChange }) {
  function set(f, v) { onChange({ ...values, [f]: v }); }
  const needsRAG = values.knowledge_strategy && values.knowledge_strategy !== "pretrained_only";
  const needsHostingDetail = values.hosting_strategy === "managed_saas" || values.hosting_strategy === "on_prem_edge";

  return (
    <div className="card">
      <div className="card-title"><span className="card-title-icon">🤖</span> Chatbot Specifics</div>

      {/* Bot Scope */}
      <div className="grid-2" style={{ marginBottom: 14 }}>
        <div className="field">
          <label>Chatbot Type</label>
          <select value={values.chatbot_type||"customer_support"} onChange={e=>set("chatbot_type",e.target.value)}>
            {CHATBOT_TYPES.map(([v,l])=><option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Expected Queries / Day</label>
          <input type="number" value={values.expected_queries_per_day||100} min={1}
            onChange={e=>set("expected_queries_per_day", parseInt(e.target.value)||100)} />
        </div>
      </div>

      <div className="field" style={{ marginBottom: 14 }}>
        <label>Integration Platforms * (select all that apply)</label>
        <ChipGroup options={PLATFORMS} selected={values.integration_platforms||[]}
          onChange={v=>set("integration_platforms",v)} />
      </div>

      <div className="grid-3" style={{ marginBottom: 14 }}>
        <div className="field">
          <label>Response Type</label>
          <select value={values.response_type||"Generated"} onChange={e=>set("response_type",e.target.value)}>
            {["Generated","Deterministic","Hybrid"].map(v=><option key={v} value={v}>{v}</option>)}
          </select>
        </div>
        <div className="field" style={{ justifyContent:"flex-end" }}>
          <label>Multilingual?</label>
          <select value={values.requires_multilingual?"yes":"no"} onChange={e=>set("requires_multilingual",e.target.value==="yes")}>
            <option value="no">No</option><option value="yes">Yes</option>
          </select>
        </div>
        <div className="field">
          <label>Human Handoff</label>
          <select value={values.requires_human_handoff===false?"no":"yes"} onChange={e=>set("requires_human_handoff",e.target.value==="yes")}>
            <option value="yes">Yes</option><option value="no">No</option>
          </select>
        </div>
      </div>

      {values.requires_multilingual && (
        <div className="field" style={{ marginBottom: 14 }}>
          <label>Languages (comma-separated)</label>
          <input value={values.languages_required || ""}
            onChange={e => set("languages_required", e.target.value)}
            placeholder="e.g. English, Hindi, French" />
        </div>
      )}

      <hr className="section-divider" />
      <div style={{ fontWeight:600, fontSize:12, color:"var(--text-dim)", marginBottom:12, textTransform:"uppercase", letterSpacing:".05em" }}>Architecture</div>

      <div className="grid-2" style={{ marginBottom: 14 }}>
        <div className="field">
          <label>Channel Strategy</label>
          <select value={values.channel_strategy||"single"} onChange={e=>set("channel_strategy",e.target.value)}>
            {CHANNEL_STRATEGIES.map(([v,l])=><option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Auth Method</label>
          <select value={values.auth_method||"public_anonymous"} onChange={e=>set("auth_method",e.target.value)}>
            {AUTH_METHODS.map(([v,l])=><option key={v} value={v}>{l}</option>)}
          </select>
        </div>
      </div>

      <div className="field" style={{ marginBottom: 14 }}>
        <label>Orchestration Type</label>
        <select value={values.orchestration_type||"single_model"} onChange={e=>set("orchestration_type",e.target.value)}>
          {ORCHESTRATIONS.map(([v,l])=><option key={v} value={v}>{l}</option>)}
        </select>
      </div>

      <div className="grid-2" style={{ marginBottom: 14 }}>
        <div className="field">
          <label>Hosting Strategy</label>
          <select value={values.hosting_strategy||"managed_saas"} onChange={e=>set("hosting_strategy",e.target.value)}>
            {HOSTING.map(([v,l])=><option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        {needsHostingDetail && (
          <div className="field">
            <label>{values.hosting_strategy==="managed_saas" ? "Preferred Provider" : "Target Hardware"}</label>
            <input value={values.hosting_provider_detail||""}
              onChange={e=>set("hosting_provider_detail",e.target.value)}
              placeholder={values.hosting_strategy==="managed_saas" ? "e.g. OpenAI / Anthropic" : "e.g. NVIDIA Jetson"} />
          </div>
        )}
      </div>

      {/* Knowledge & RAG */}
      <div className="grid-2" style={{ marginBottom: needsRAG ? 14 : 0 }}>
        <div className="field">
          <label>Knowledge Strategy</label>
          <select value={values.knowledge_strategy||"pretrained_only"} onChange={e=>set("knowledge_strategy",e.target.value)}>
            {KNOWLEDGE.map(([v,l])=><option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        {needsRAG && (
          <div className="field">
            <label>Update Frequency</label>
            <select value={values.knowledge_update_freq||"Daily"} onChange={e=>set("knowledge_update_freq",e.target.value)}>
              {KNOW_FREQS.map(v=><option key={v} value={v}>{v}</option>)}
            </select>
          </div>
        )}
      </div>

      {needsRAG && (
        <div className="grid-2" style={{ marginBottom: 14 }}>
          <div className="field">
            <label>Knowledge Sources (comma-separated)</label>
            <input value={values.knowledge_sources || ""}
              onChange={e => set("knowledge_sources", e.target.value)}
              placeholder="e.g. SharePoint, Confluence, PDFs" />
          </div>
          <div className="field">
            <label>Document Formats (comma-separated)</label>
            <input value={values.document_formats || ""}
              onChange={e => set("document_formats", e.target.value)}
              placeholder="e.g. PDF, Docx" />
          </div>
        </div>
      )}

      {/* Observability */}
      <hr className="section-divider" />
      <div style={{ fontWeight:600, fontSize:12, color:"var(--text-dim)", marginBottom:12, textTransform:"uppercase", letterSpacing:".05em" }}>Observability & Governance</div>

      <div className="grid-3" style={{ marginBottom: 14 }}>
        <div className="field">
          <label>Guardrail Level</label>
          <select value={values.guardrail_level||"basic_filtering"} onChange={e=>set("guardrail_level",e.target.value)}>
            {GUARDRAILS.map(([v,l])=><option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Analytics Depth</label>
          <select value={values.analytics_depth||"Standard"} onChange={e=>set("analytics_depth",e.target.value)}>
            {ANALYTICS_DEPTHS.map(v=><option key={v} value={v}>{v}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Traceability Required</label>
          <select value={values.traceability_required===false?"no":"yes"} onChange={e=>set("traceability_required",e.target.value==="yes")}>
            <option value="yes">Yes</option><option value="no">No</option>
          </select>
        </div>
      </div>

      <div className="field">
        <label>Deployment Phase</label>
        <select value={values.deployment_phase||"POC"} onChange={e=>set("deployment_phase",e.target.value)}>
          {DEPLOY_PHASES.map(v=><option key={v} value={v}>{v}</option>)}
        </select>
      </div>
    </div>
  );
}
