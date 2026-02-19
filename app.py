# ============================================================================
# PROPOSAL AUTOMATION SYSTEM
# ============================================================================

import streamlit as st
from pydantic import ValidationError
import os

# Import modules from src
from src.models import (
    UniversalProposalCore, 
    DemandForecastingProposal, 
    VisualInspectionProposal, 
    ChatbotProposal,
    Industry, ErrorTolerance, DataSourceType, SystemAutonomy, OptimizationGoal, 
    InferenceLocation, CloudProvider, EdgeHardware, ExecutionTrigger,
    ForecastingMethod, DataFrequency, DataQuality, DeliveryTimeline,
    InspectionType, ImageSource, ChatbotType, IntegrationPlatform,
    ChannelStrategy, AuthMethod, OrchestrationType, HostingStrategy,
    KnowledgeStrategy, GuardrailLevel,
    SuccessDimension, SecurityStandard, SecurityControl, DataFormat, DataVolumeUnit
)
import pandas as pd
from PIL import Image
from src.slide_builder import create_presentation
from src.utils import format_enum_options, dropdown_with_other

# ============================================================================
# HELPER: SUBMISSION HANDLER
# ============================================================================

def handle_submission(model_class, data, type_label):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")

    try:
        # ── File objects (UploadedFile / BytesIO) can't be serialised by Pydantic.
        # Pull them out before model creation, restore after model_dump().
        FILE_FIELDS = ["client_logo_path", "company_logo_path", "architecture_diagram_path"]
        raw_files = {}
        clean_data = {}
        for k, v in data.items():
            if v is None:
                continue
            if k in FILE_FIELDS and not isinstance(v, str):
                raw_files[k] = v   # keep the file object aside
            else:
                clean_data[k] = v

        validated_proposal = model_class(**clean_data)
        st.success(f"✅ {type_label} Config Validated!")

        with st.spinner(f"Generating {type_label} Deck..."):
            # model_dump() gives us clean serializables; then patch file objects back in
            payload = validated_proposal.model_dump()
            payload.update(raw_files)   # restore UploadedFile / file-path strings

            pptx_file = create_presentation(payload, type_label, api_key)
            if pptx_file:
                st.markdown("### 📥 Your Proposal is Ready")
                st.download_button(
                    label=f"Download {type_label} Proposal (.pptx)",
                    data=pptx_file,
                    file_name=f"{type_label.replace(' ', '_').lower()}_proposal.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    type="primary"
                )
    except ValidationError as e:
        st.error("❌ Validation Error")
        for error in e.errors():
            st.warning(f"**{error['loc']}**: {error['msg']}")

# ============================================================================
# STREAMLIT UI
# ============================================================================

st.set_page_config(page_title="Proposal Automation", page_icon="🚀", layout="wide")
st.title("🚀 Proposal Automation System")

with st.container():
    c_global1, c_global2 = st.columns(2)
    with c_global1:
        global_client = st.text_input("Client Name *", "Acme Corp", key="global_client")
    with c_global2:
        global_vendor = st.text_input("Vendor Name *", "My AI Agency", key="global_vendor")
    
    global_industry = st.selectbox("Industry *", format_enum_options(Industry), key="global_industry")
    
    st.markdown("### 🖼️ Branding")
    c_logo1, c_logo2 = st.columns(2)
    with c_logo1: 
        client_logo = st.file_uploader("Client Logo", type=["png", "jpg", "jpeg"])
    with c_logo2:
        st.info("🏢 Company logo: **oneture.jpg** (auto-applied)")

COMPANY_LOGO_PATH = os.path.join("assets", "oneture.jpg")


# ============================================================================
# HELPER: ASSET MANAGEMENT
# ============================================================================
ASSETS_DIR = "assets"
TEMP_DIR = "temp"
if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)



def get_asset_diagrams():
    if not os.path.exists(ASSETS_DIR): return []
    return [f for f in os.listdir(ASSETS_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]

# ============================================================================
# HELPER: RFP ENHANCEMENTS RENDERER
# ============================================================================
TIMELINE_WEEKS = {"4_weeks": 4, "8_weeks": 8, "12_weeks": 12, "16_weeks": 16}

def render_timeline_section(key_prefix, default_budget=50000):
    """
    SOW-style timeline section (no @st.fragment).
    Must be called OUTSIDE st.form(). Full-page reruns on cell edits are acceptable
    (same as SOW project). Return value is used directly by the submit handler.
    """
    st.markdown("### 🗓️ Timeline, Commercials & Phasing")
    c1, c2 = st.columns(2)
    with c1:
        timeline = st.selectbox(
            "Delivery Timeline *", format_enum_options(DeliveryTimeline),
            key=f"{key_prefix}_tl"
        )
    with c2:
        budget = st.number_input(
            "Estimated Budget (USD)", 10000, 1000000, default_budget,
            step=5000, key=f"{key_prefix}_budget"
        )

    assumptions = st.text_area("Key Assumptions", key=f"{key_prefix}_assumptions")

    num_weeks = TIMELINE_WEEKS.get(timeline, 4)
    wk_cols = [f"Wk{i+1}" for i in range(num_weeks)]
    new_cols = ["Phase", "Task"] + wk_cols

    tl_key = f"{key_prefix}_tl_data"
    if tl_key not in st.session_state:
        st.session_state[tl_key] = pd.DataFrame([
            {"Phase": "Discovery",   "Task": "Kickoff & Data Access"},
            {"Phase": "Development", "Task": "Core Logic Implementation"},
            {"Phase": "Testing",     "Task": "UAT & Refinement"},
        ])

    # SOW-style column-preserving reshape
    old_df = st.session_state[tl_key]
    if list(old_df.columns) != new_cols:
        new_df = old_df[["Phase", "Task"]].copy() if "Phase" in old_df.columns \
                 else pd.DataFrame(columns=["Phase", "Task"])
        for wk in wk_cols:
            new_df[wk] = old_df[wk] if wk in old_df.columns else ""
        st.session_state[tl_key] = new_df

    # Dynamic key forces widget recreation when week count changes (SOW trick)
    st.session_state[tl_key] = st.data_editor(
        st.session_state[tl_key],
        num_rows="dynamic",
        key=f"{key_prefix}_tl_editor_{num_weeks}",
        width="stretch"
    )

    return {
        "delivery_timeline": timeline,
        "estimated_budget_usd": budget,
        "key_assumptions": assumptions,
        "timeline_data": st.session_state[tl_key].to_dict(orient="records"),
    }


def render_rfp_enhancements(key_prefix, default_diagram=None):
    """
    Renders Success Criteria, Security, Data Details, and Architecture Diagram.
    Called INSIDE st.form(). Timeline/Budget/Table are handled by render_timeline_section().
    """
    st.markdown("### 5️⃣ Proposal Strategy & Success Metrics")
    c1, c2 = st.columns(2)
    with c1:
        success_dims = st.multiselect(
            "Success Dimensions *", format_enum_options(SuccessDimension),
            default=["accuracy", "cost_efficiency"], key=f"{key_prefix}_success"
        )
    with c2:
        val_strat = st.text_area(
            "Validation Strategy", "Human-in-the-loop review of 100 samples.",
            height=100, key=f"{key_prefix}_val"
        )

    st.markdown("### 6️⃣ Security & Compliance")
    c1, c2 = st.columns(2)
    with c1:
        sec_stds = st.multiselect("Security Standards", format_enum_options(SecurityStandard), key=f"{key_prefix}_std")
    with c2:
        sec_ctrls = st.multiselect(
            "Security Controls", format_enum_options(SecurityControl),
            default=["vpc_deployment", "iam_access_control"], key=f"{key_prefix}_ctrl"
        )

    st.markdown("### 7️⃣ Data Details")
    c1, c2, c3 = st.columns(3)
    with c1:
        d_fmt = st.multiselect("Data Formats", format_enum_options(DataFormat), default=["pdf", "json"], key=f"{key_prefix}_dfmt")
    with c2:
        d_vol = st.number_input("Volume Value", 0.1, 1000.0, 1.0, key=f"{key_prefix}_dvol")
    with c3:
        d_unit = st.selectbox("Volume Unit", format_enum_options(DataVolumeUnit), key=f"{key_prefix}_dunit")

    st.markdown("### 8️⃣ Architecture Diagram")
    asset_files = get_asset_diagrams()
    diagram_source = None

    if asset_files:
        default_name = os.path.basename(default_diagram) if default_diagram else None
        default_idx = asset_files.index(default_name) if default_name and default_name in asset_files else 0
        selected_asset = st.selectbox(
            "Select Diagram (from assets)", asset_files,
            index=default_idx, key=f"{key_prefix}_asset_sel"
        )
        diagram_source = os.path.join(ASSETS_DIR, selected_asset)
    else:
        st.warning("No diagram assets found in 'assets/'.")
        if default_diagram and os.path.exists(default_diagram):
            diagram_source = default_diagram

    uploaded_diag = st.file_uploader(
        "📤 Upload Custom Diagram (overrides dropdown)",
        type=["png", "jpg", "jpeg"], key=f"{key_prefix}_diag_up"
    )
    if uploaded_diag:
        diagram_source = uploaded_diag

    return {
        "success_dimensions": success_dims, "validation_strategy": val_strat,
        "security_standards": sec_stds, "security_controls": sec_ctrls,
        "data_format": d_fmt, "data_volume": d_vol, "data_volume_unit": d_unit,
        "architecture_diagram_path": diagram_source,
    }


def render_universal_core(key_prefix):
    """Renders the 12 Universal Core questions"""
    st.markdown("### 1️⃣ Problem & Outcome")
    c1, c2, c3 = st.columns(3)
    with c1: decision = st.text_input("Decision to Support *", "Inventory Replenishment", key=f"{key_prefix}_decision", help="What operational decision will this system support?")
    with c2: failure = st.text_input("Current Failure Mode *", "High Variance", key=f"{key_prefix}_failure", help="Why is the current process failing?")
    with c3: tolerance = st.selectbox("Error Tolerance *", format_enum_options(ErrorTolerance), key=f"{key_prefix}_tolerance")

    st.markdown("### 2️⃣ Data Reality")
    c1, c2, c3 = st.columns(3)
    with c1: dtype = st.selectbox("Data Source Type *", format_enum_options(DataSourceType), key=f"{key_prefix}_dtype")
    with c2: freq = st.selectbox("Data Frequency *", format_enum_options(DataFrequency), key=f"{key_prefix}_freq")
    with c3: quality = st.selectbox("Data Quality *", format_enum_options(DataQuality), key=f"{key_prefix}_quality")

    st.markdown("### 3️⃣ Intelligence Layer")
    c1, c2, c3 = st.columns(3)
    with c1: autonomy = st.selectbox("System Autonomy *", format_enum_options(SystemAutonomy), key=f"{key_prefix}_autonomy")
    with c2: goal = st.selectbox("Optimization Goal *", format_enum_options(OptimizationGoal), key=f"{key_prefix}_goal")
    with c3: retrain = st.text_input("Retraining Freq", "Monthly", key=f"{key_prefix}_retrain")

    st.markdown("### 4️⃣ Execution & Deployment")
    c1, c2, c3 = st.columns(3)
    with c1: 
        loc = st.selectbox("Inference Location *", format_enum_options(InferenceLocation), key=f"{key_prefix}_loc")
        # Conditional Logic for Cloud/Edge
        cloud_prov = None
        edge_hw = None
        if loc in [InferenceLocation.CLOUD.value, InferenceLocation.HYBRID.value]:
            cloud_prov = st.selectbox("Cloud Provider", format_enum_options(CloudProvider), key=f"{key_prefix}_cp")
        if loc in [InferenceLocation.EDGE.value, InferenceLocation.HYBRID.value]:
            edge_hw = st.selectbox("Edge Hardware", format_enum_options(EdgeHardware), key=f"{key_prefix}_hw")
            
    with c2: trigger = st.selectbox("Execution Trigger *", format_enum_options(ExecutionTrigger), key=f"{key_prefix}_trigger")
    with c3: fail_handle = st.text_input("Failure Handling", "Human Review", key=f"{key_prefix}_fail")

    return {
        "decision_supported": decision, "failure_mode": failure, "error_tolerance": tolerance,
        "data_source_type": dtype, "data_frequency": freq, "data_quality": quality,
        "system_autonomy": autonomy, "optimization_goal": goal, "retraining_frequency": retrain,
        "inference_location": loc, "cloud_provider": cloud_prov, "edge_hardware": edge_hw,
        "execution_trigger": trigger, "failure_handling": fail_handle
    }

tab_demand, tab_visual, tab_chat = st.tabs(["Demand Forecasting", "Visual Inspection", "Chatbot"])

# === TAB 1: DEMAND FORECASTING ===
with tab_demand:
    st.header("Demand Forecasting Config")

    with st.form("form_demand"):
        with st.expander("Strategic & Technical Core", expanded=True):
            core_data = render_universal_core("demand")
        
        with st.expander("Domain Details", expanded=True):
            st.subheader("Forecasting Specifics")
            methods = st.multiselect("Forecasting Methods *", format_enum_options(ForecastingMethod))
            c1, c2 = st.columns(2)
            with c1: horizon = st.number_input("Forecast Horizon (Days)", 1, 365, 30)
            with c2: history = st.number_input("Historical Data (Years)", 1, 10, 2)
            
            st.subheader("Deep Dive")
            c1, c2, c3 = st.columns(3)
            with c1: level = st.text_input("Forecast Level", "SKU-Location")
            with c2: vol = st.text_input("Demand Volatility", "Seasonal")
            with c3: plan = st.text_input("Planning Decision", "Procurement")
            
            st.markdown("**Available Features**")
            feature_opts = ['price', 'promotions', 'seasonality', 'weather', 'holidays']
            features_selected = []
            cols = st.columns(5)
            for i, f in enumerate(feature_opts):
                if cols[i].checkbox(f.title(), key=f"df_feat_{f}"): features_selected.append(f)

        with st.expander("RFP Specifics", expanded=True):
            rfp_data = render_rfp_enhancements("demand", default_diagram=os.path.join(ASSETS_DIR, "demand_forecasting.jpg"))

        submitted_demand = st.form_submit_button("Generate Demand Proposal", type="primary")

    # Timeline AFTER the form (visually at the bottom), SOW-style
    with st.expander("🗓️ Timeline & Commercials", expanded=True):
        demand_tl_data = render_timeline_section("demand", default_budget=50000)

    if submitted_demand:
        data = {
            **core_data, **rfp_data, **demand_tl_data,
            "client_name": global_client, "vendor_name": global_vendor, "industry": global_industry,
            "forecasting_methods": methods, "forecast_horizon_days": horizon,
            "historical_data_years": history, "features_available": features_selected,
            "forecast_level": level, "demand_volatility": vol, "planning_decision": plan,
            "client_logo_path": client_logo, "company_logo_path": COMPANY_LOGO_PATH
        }
        handle_submission(DemandForecastingProposal, data, "Demand Forecasting")

# === TAB 2: VISUAL INSPECTION ===
with tab_visual:
    st.header("Visual Inspection Config")

    with st.form("form_visual"):
        with st.expander("Strategic & Technical Core", expanded=True):
            core_data = render_universal_core("visual")
            
        with st.expander("Domain Details", expanded=True):
            st.subheader("Inspection Scope")
            insp_type = st.selectbox("Inspection Type *", format_enum_options(InspectionType))
            defect_str = st.text_input("Defect Categories *", placeholder="scratches, dents")
            accuracy = st.slider("Accuracy Requirement", 0.80, 0.99, 0.95)
            
            st.subheader("Deep Dive")
            c1, c2 = st.columns(2)
            with c1: 
                img_src = st.selectbox("Image Source *", format_enum_options(ImageSource))
                ds_size = None
                if img_src == ImageSource.EXISTING_DATASET.value:
                    ds_size = st.number_input("Dataset Size (Images)", 100, 1000000, 5000)
            with c2: points = st.text_input("Inspection Points", "Single Camera")
            
            c3, c4 = st.columns(2)
            with c3: cost_mx = st.text_input("Cost Matrix", "Missed defect > False Positive")
            with c4: labeling = st.checkbox("Requires Data Labeling", value=True)

        with st.expander("RFP Specifics", expanded=True):
            rfp_data = render_rfp_enhancements("visual", default_diagram=os.path.join(ASSETS_DIR, "visual_inspection.png"))

        submitted_visual = st.form_submit_button("Generate Visual Inspection Proposal", type="primary")

    with st.expander("🗓️ Timeline & Commercials", expanded=True):
        visual_tl_data = render_timeline_section("visual", default_budget=60000)

    if submitted_visual:
        defects_list = [x.strip() for x in defect_str.split(',')] if defect_str else []
        data = {
            **core_data, **rfp_data, **visual_tl_data,
            "client_name": global_client, "vendor_name": global_vendor, "industry": global_industry,
            "inspection_type": insp_type, "defect_categories": defects_list,
            "accuracy_requirement": accuracy, "image_source": img_src,
            "existing_dataset_size": ds_size, "inspection_points": points,
            "cost_matrix": cost_mx, "requires_labeling": labeling,
            "client_logo_path": client_logo, "company_logo_path": COMPANY_LOGO_PATH
        }
        handle_submission(VisualInspectionProposal, data, "Visual Inspection")

# === TAB 3: CHATBOT ===
with tab_chat:
    st.header("Chatbot Config")

    with st.form("form_chatbot"):
        with st.expander("Strategic Context", expanded=True):
            core_data = render_universal_core("chat")
        
        with st.expander("Domain Details", expanded=True):
            st.subheader("Bot Scope")
            c1, c2 = st.columns(2)
            with c1: cb_type = st.selectbox("Chatbot Type *", format_enum_options(ChatbotType))
            with c2: queries = st.number_input("Expected Queries/Day", 10, 500000, 1000)
            
            platforms = st.multiselect("Integration Platforms *", format_enum_options(IntegrationPlatform))
            
            c3, c4 = st.columns(2)
            with c3: 
                multilingual = st.checkbox("Multilingual Support")
                lang_str = st.text_input("Languages", "Spanish, French") if multilingual else ""
            with c4:
                handoff = st.checkbox("Human Handoff", value=True)
            
            resp_type = st.selectbox("Response Type", ["Generated", "Deterministic", "Hybrid"])

        with st.expander("Domain & Architecture Details", expanded=True):
            st.markdown("#### 1. Channels & Experience")
            chan_strat = st.selectbox("Channel Strategy", format_enum_options(ChannelStrategy))
            
            st.markdown("#### 2. Security & Access")
            auth_meth = st.selectbox("Auth Method", format_enum_options(AuthMethod))

            st.markdown("#### 3. Intelligence Topology")
            orch_type = st.selectbox("Orchestration Type", format_enum_options(OrchestrationType))

            st.markdown("#### 4. Model Hosting Strategy")
            c_host1, c_host2 = st.columns(2)
            with c_host1: host_strat = st.selectbox("Hosting Strategy", format_enum_options(HostingStrategy))
            with c_host2:
                host_detail = None
                if host_strat == HostingStrategy.MANAGED_SAAS.value:
                    host_detail = st.text_input("Preferred Provider", "OpenAI / Anthropic")
                elif host_strat == HostingStrategy.ON_PREM.value:
                    host_detail = st.text_input("Target Hardware", "NVIDIA Jetson / Local Server")
            
            st.markdown("#### 5. Knowledge & RAG")
            c_know1, c_know2 = st.columns(2)
            with c_know1: know_strat = st.selectbox("Knowledge Strategy", format_enum_options(KnowledgeStrategy))
            with c_know2:
                know_src_str = ""
                doc_fmt_str = ""
                know_freq = "Daily"
                if know_strat != KnowledgeStrategy.PRETRAINED.value:
                    know_src_str = st.text_input("Knowledge Sources", "SharePoint, Confluence, PDFs")
                    doc_fmt_str = st.text_input("Document Formats", "PDF, Docx")
                    know_freq = st.selectbox("Update Frequency", ["Real-time", "Hourly", "Daily", "Weekly"])
            
            st.markdown("#### 6. Observability & Governance")
            c_obs1, c_obs2 = st.columns(2)
            with c_obs1: 
                guard_level = st.selectbox("Guardrail Level", format_enum_options(GuardrailLevel))
                trace = st.checkbox("Traceability Required", value=True)
            with c_obs2: analytics = st.selectbox("Analytics Depth", ["Basic", "Standard", "Advanced (Conversational Intelligence)"], index=1)
            
            st.markdown("#### 7. Delivery Context")
            del_phase = st.selectbox("Deployment Phase", ["POC", "MVP", "Production Pilot", "Scale Rollout"])

        with st.expander("RFP Specifics", expanded=True):
            rfp_data = render_rfp_enhancements("chat", default_diagram=os.path.join(ASSETS_DIR, "chatbot.png"))

        submitted_chat = st.form_submit_button("Generate Chatbot Proposal", type="primary")

    with st.expander("🗓️ Timeline & Commercials", expanded=True):
        chat_tl_data = render_timeline_section("chat", default_budget=40000)

    if submitted_chat:
        languages = [x.strip() for x in lang_str.split(',')] if (multilingual and lang_str) else []
        knowledge_srcs = [x.strip() for x in know_src_str.split(',')] if (know_strat != "pretrained_only" and know_src_str) else []
        doc_formats = [x.strip() for x in doc_fmt_str.split(',')] if (know_strat != "pretrained_only" and doc_fmt_str) else []

        data = {
            **core_data, **rfp_data, **chat_tl_data,
            "client_name": global_client, "vendor_name": global_vendor, "industry": global_industry,
            "chatbot_type": cb_type, "integration_platforms": platforms,
            "expected_queries_per_day": queries,
            "requires_multilingual": multilingual, "languages_required": languages,
            "requires_human_handoff": handoff,
            "response_type": resp_type,
            "channel_strategy": chan_strat,
            "auth_method": auth_meth,
            "orchestration_type": orch_type,
            "hosting_strategy": host_strat, "hosting_provider_detail": host_detail,
            "knowledge_strategy": know_strat, "knowledge_sources": knowledge_srcs,
            "knowledge_update_freq": know_freq, "document_formats": doc_formats,
            "guardrail_level": guard_level, "analytics_depth": analytics, "traceability_required": trace,
            "deployment_phase": del_phase,
            "client_logo_path": client_logo, "company_logo_path": COMPANY_LOGO_PATH
        }
        handle_submission(ChatbotProposal, data, "Chatbot")