# ============================================================================
# PROPOSAL AUTOMATION SYSTEM - Phase 4 (Universal Core & Deep Dive)
# ============================================================================

import streamlit as st
from pydantic import BaseModel, Field, ValidationError
from enum import Enum
from typing import List, Optional
import io
import os
from groq import Groq

# We import python-pptx inside the app. 
try:
    from pptx import Presentation
    from pptx.util import Pt
except ImportError:
    st.error("⚠️ Library 'python-pptx' not found. Please run `pip install python-pptx`.")
    class Presentation: pass

# ============================================================================
# 1. GENERATOR LOGIC
# ============================================================================

TEMPLATE_DIR = "templates"

TEMPLATE_MAP = {
    "Demand Forecasting": "demand_forecasting.pptx",
    "Visual Inspection": "visual_inspection.pptx",
    "Chatbot": "chatbot.pptx"
}


def call_llm_for_text(prompt: str) -> str:
    """
    Helper to call Groq API (using Mixtral).
    """
    api_key = st.secrets.get("GROQ_API_KEY")
    
    if not api_key:
        return "AI_ERROR_NO_KEY"
        
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a senior solution architect and proposal writer. You write concise, high-impact business prose."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
        )
        return completion.choices[0].message.content.strip()
        
    except Exception as e:
        return f"[AI ERROR: {str(e)}]"
    

def generate_narrative_content(data: dict, proposal_type: str) -> dict:
    """
    Orchestrates content generation using Universal Core data.
    """
    
    # 1. Common Formatting
    client = data.get("client_name", "Valued Client")
    vendor = data.get("vendor_name", "Our Company")
    industry = data.get("industry", "Business").title()
    budget = f"${data.get('estimated_budget_usd', 0):,}"
    timeline = data.get("delivery_timeline", "").replace("_", " ").title()
    
    # Architecture Context
    loc = data.get("inference_location", "Cloud")
    provider = data.get("cloud_provider") or data.get("edge_hardware") or "Standard Infrastructure"
    autonomy = data.get("system_autonomy", "Advisory")
    
    # Domain Details
    tech_details = ""
    if proposal_type == "Demand Forecasting":
        tech_details = f"Methods: {', '.join(data.get('forecasting_methods', []))}. Level: {data.get('forecast_level')}."
    elif proposal_type == "Visual Inspection":
        tech_details = f"Type: {data.get('inspection_type')}. Defects: {', '.join(data.get('defect_categories', []))}."
    elif proposal_type == "Chatbot":
        # Extract Architecture Details
        channel = data.get("channel_strategy", "Omnichannel").replace("_", " ").title()
        auth = data.get("auth_method", "Standard").replace("_", " ").title()
        orch = data.get("orchestration_type", "Single Model").replace("_", " ").title()
        hosting = data.get("hosting_strategy", "SaaS").replace("_", " ").title()
        knowledge = data.get("knowledge_strategy", "RAG").replace("_", " ").title()
        
        tech_details = (
            f"Type: {data.get('chatbot_type')}. "
            f"Architecture: {channel}, {auth} Auth, {orch}, {hosting}, {knowledge}."
        )

    prompt = f"""
    You are generating content for a client-facing proposal deck.
    You must stay strictly within the provided context.
    Do not introduce new capabilities, assumptions, metrics, or technologies.

    Output EXACTLY SIX sections separated by "|||".
    Each section must be 3–4 sentences. No more, no less.

    --------------------
    CONTEXT (AUTHORITATIVE)
    --------------------
    - Client: {client} ({industry})
    - Proposal Type: {proposal_type}

    - Current Limitation:
      The system supporting {data.get('decision_supported')} is constrained due to {data.get('failure_mode')}.

    - Objective:
      Deliver a {autonomy} {proposal_type} solution with {data.get('error_tolerance')} tolerance.

    - Data Reality:
      Source type: {data.get('data_source_type')}
      Arrival pattern: {data.get('data_frequency')}
      Data quality: {data.get('data_quality')}

    - Intelligence Constraints:
      System type: {autonomy}
      Optimization priority: {data.get('optimization_goal')}
      Retraining: {data.get('retraining_frequency')}

    - Execution Constraints:
      Deployment location: {loc}
      Cloud provider: {provider}
      Execution trigger: {data.get('execution_trigger')}
      Failure handling: {data.get('failure_handling')}

    - Commercial Context:
      Budget: {budget}
      Timeline: {timeline}

    --------------------
    SECTION 1: Executive Summary
    --------------------
    Write 3–4 sentences that:
    - Clearly state the existing limitation ({data.get('failure_mode')})
    - Propose the {autonomy} {proposal_type} system as a response
    - Explain the value specifically in terms of {data.get('decision_supported')}
    - Reference budget and timeline without guarantees

    Tone: Strategic, concise, executive-level.
    Do NOT use marketing buzzwords or absolute claims.

    |||

    --------------------
    SECTION 2: Technical Rationale
    --------------------
    Write 3–4 sentences that:
    - Justify the deployment choice ({loc} on {provider}) based on data arrival ({data.get('data_frequency')})
    - Explain why the chosen technical approach ({tech_details}) aligns with the stated data quality and optimization priority
    - Emphasize feasibility and constraints over innovation

    Tone: Technical, grounded, authoritative.
    Do NOT speculate beyond the provided context.

    |||

    --------------------
    SECTION 3: Problem Statement & Outcome
    --------------------
    Write 3–4 sentences that:
    - Elaborate on the pain of {data.get('failure_mode')} in the {industry} context
    - Define the operational gap in {data.get('decision_supported')}
    - State the target outcome with {data.get('error_tolerance')} tolerance

    Tone: Analytical, problem-focused.

    |||

    --------------------
    SECTION 4: Data Reality
    --------------------
    Write 3–4 sentences that:
    - Discuss handling {data.get('data_source_type')} data at {data.get('data_frequency')} scale
    - Address the challenge of {data.get('data_quality')} quality and mitigation strategies

    Tone: Realistic, data-driven.

    |||

    --------------------
    SECTION 5: Intelligence Layer
    --------------------
    Write 3–4 sentences that:
    - Justify the {autonomy} approach for {data.get('optimization_goal')}
    - Explain how the model will adapt (Retraining: {data.get('retraining_frequency')})

    Tone: Sophisticated, forward-looking.

    |||

    --------------------
    SECTION 6: Execution Strategy
    --------------------
    Write 3–4 sentences that:
    - Detail the deployment on {loc} ({provider})
    - Explain the {data.get('execution_trigger')} workflow and {data.get('failure_handling')} protocol

    Tone: Operational, reliable.
    """
    
    # 3. Call the AI
    ai_response = call_llm_for_text(prompt)
    
    # 4. Parse Response
    if "|||" in ai_response:
        parts = ai_response.split("|||")
    else:
        parts = [ai_response]

    # Ensure we have 6 parts, filling missing ones with placeholders
    narratives = [p.strip() for p in parts]
    while len(narratives) < 6:
        narratives.append("Content generation failed for this section.")

    summary_text = narratives[0]
    tech_narrative = narratives[1]
    problem_narrative = narratives[2]
    data_narrative = narratives[3]
    intel_narrative = narratives[4]
    exec_narrative = narratives[5]

    # 3. Replacements
    replacements = {
        "{{CLIENT}}": client,
        "{{VENDOR}}": vendor,
        "{{INDUSTRY}}": industry,
        "{{USE_CASE}}": data.get("decision_supported", "") + " optimization", # Fallback for old template tag
        "{{TIMELINE}}": timeline,
        "{{BUDGET}}": budget,
        "{{CLOUD}}": f"{loc} ({provider})".upper(),
        "{{QUALITY}}": data.get("data_quality", "").title(),
        "{{ASSUMPTIONS}}": data.get("key_assumptions", "Standard commercial assumptions apply."),
        "{{EXECUTIVE_SUMMARY}}": summary_text, 
        "{{TECH_NARRATIVE}}": tech_narrative,
        "{{PROBLEM_NARRATIVE}}": problem_narrative,
        "{{DATA_NARRATIVE}}": data_narrative,
        "{{INTELLIGENCE_NARRATIVE}}": intel_narrative,
        "{{EXECUTION_NARRATIVE}}": exec_narrative
    }

    # 4. Domain Specific Logic
    if proposal_type == "Demand Forecasting":
        methods = ", ".join([m.replace('_', ' ').title() for m in data.get("forecasting_methods", [])])
        replacements["{{METHODS}}"] = methods
        replacements["{{HORIZON}}"] = f"{data.get('forecast_horizon_days')} Days"
        replacements["{{FREQUENCY}}"] = data.get("data_frequency", "").title()
        replacements["{{FEATURES_NARRATIVE}}"] = tech_narrative

    elif proposal_type == "Visual Inspection":
        replacements["{{INSPECTION_TYPE}}"] = data.get("inspection_type", "").replace('_', ' ').title()
        replacements["{{DEFECTS}}"] = ", ".join(data.get("defect_categories", []))
        replacements["{{ACCURACY}}"] = f"{data.get('accuracy_requirement', 0)*100:.1f}%"
        replacements["{{IMAGE_SOURCE}}"] = f"{data.get('image_source', '').replace('_', ' ').title()}. {tech_narrative}"

    elif proposal_type == "Chatbot":
        replacements["{{CHATBOT_TYPE}}"] = data.get("chatbot_type", "").replace('_', ' ').title()
        replacements["{{PLATFORMS}}"] = ", ".join([p.title() for p in data.get("integration_platforms", [])])
        replacements["{{QUERIES}}"] = f"{data.get('expected_queries_per_day'):,} queries/day"
        langs = data.get("languages_required", [])
        lang_text = ", ".join(langs) if langs else "English Only"
        replacements["{{LANGUAGES}}"] = f"{lang_text}.\n\n{tech_narrative}"

        # Architecture Placeholders
        replacements["{{CHANNEL_STRATEGY}}"] = data.get("channel_strategy", "").replace('_', ' ').title()
        replacements["{{AUTH_METHOD}}"] = data.get("auth_method", "").replace('_', ' ').title()
        replacements["{{ORCHESTRATION}}"] = data.get("orchestration_type", "").replace('_', ' ').title()
        
        # Hosting + Detail
        host_strat = data.get("hosting_strategy", "").replace('_', ' ').title()
        if data.get("hosting_provider_detail"):
            host_strat += f" ({data.get('hosting_provider_detail')})"
        replacements["{{HOSTING_STRATEGY}}"] = host_strat

        # Knowledge + Frequency
        know_strat = data.get("knowledge_strategy", "").replace('_', ' ').title()
        if data.get("knowledge_update_freq"):
            know_strat += f" - {data.get('knowledge_update_freq')} Updates"
        replacements["{{KNOWLEDGE_STRATEGY}}"] = know_strat

        replacements["{{GUARDRAILS}}"] = data.get("guardrail_level", "").replace('_', ' ').title()
        replacements["{{DEPLOYMENT_PHASE}}"] = data.get("deployment_phase", "").title()

    return replacements

def replace_text_in_shape(shape, replacements):
    """Helper to replace text in a specific shape"""
    if not shape.has_text_frame:
        return
    for paragraph in shape.text_frame.paragraphs:
        for run in paragraph.runs:
            for key, value in replacements.items():
                if key in run.text:
                    run.text = run.text.replace(key, str(value))
                    if "Title" not in shape.name:
                        try:
                            run.font.size = Pt(24)
                        except: pass

def create_presentation(data: dict, proposal_type: str) -> io.BytesIO:
    """Loads a template, injects data, and returns the file in memory."""
    template_filename = TEMPLATE_MAP.get(proposal_type)
    template_path = os.path.join(TEMPLATE_DIR, template_filename)

    if os.path.exists(template_path):
        prs = Presentation(template_path)
    else:
        print(f"Template missing: {template_path}")
        prs = Presentation() 
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = f"MISSING TEMPLATE: {proposal_type}"

    replacements = generate_narrative_content(data, proposal_type)

    for slide in prs.slides:
        for shape in slide.shapes:
            replace_text_in_shape(shape, replacements)
            if shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        replace_text_in_shape(cell, replacements)

    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    return output

# ============================================================================
# 2. ENUMS
# ============================================================================

class Industry(str, Enum):
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    LOGISTICS = "logistics"
    OTHER = "other"

class ErrorTolerance(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class DataSourceType(str, Enum):
    DATABASE = "database"
    API = "api"
    FILES = "files"
    IMAGES = "images"
    VIDEO = "video"
    MIXED = "mixed"

class SystemAutonomy(str, Enum):
    ADVISORY = "advisory"
    AUTONOMOUS = "autonomous"

class OptimizationGoal(str, Enum):
    ACCURACY = "accuracy"
    LATENCY = "latency"
    EXPLAINABILITY = "explainability"

class InferenceLocation(str, Enum):
    CLOUD = "cloud"
    EDGE = "edge"
    HYBRID = "hybrid"

class CloudProvider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    OTHER = "other"

class EdgeHardware(str, Enum):
    NVIDIA_JETSON = "nvidia_jetson"
    RASPBERRY_PI = "raspberry_pi"
    MOBILE_DEVICE = "mobile_device"
    INDUSTRIAL_PC = "industrial_pc"
    OTHER = "other"

class ExecutionTrigger(str, Enum):
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    USER_ACTION = "user_action"

class ForecastingMethod(str, Enum):
    TIME_SERIES = "time_series"
    REGRESSION = "regression"
    ENSEMBLE = "ensemble"
    DEEP_LEARNING = "deep_learning"

class DataFrequency(str, Enum):
    REAL_TIME = "real_time"
    BATCH_DAILY = "batch_daily"
    BATCH_WEEKLY = "batch_weekly"
    BATCH_MONTHLY = "batch_monthly"

class DataQuality(str, Enum):
    CLEAN = "clean"
    USABLE_WITH_GAPS = "usable_with_gaps"
    NOISY = "noisy"

class DeliveryTimeline(str, Enum):
    WEEKS_4 = "4_weeks"
    WEEKS_8 = "8_weeks"
    WEEKS_12 = "12_weeks"
    WEEKS_16 = "16_weeks"

class InspectionType(str, Enum):
    DEFECT_DETECTION = "defect_detection"
    QUALITY_CONTROL = "quality_control"
    ANOMALY_DETECTION = "anomaly_detection"
    CLASSIFICATION = "classification"

class ImageSource(str, Enum):
    CAMERA = "camera"
    SCANNER = "scanner"
    MOBILE = "mobile"
    EXISTING_DATASET = "existing_dataset"

class ChatbotType(str, Enum):
    CUSTOMER_SUPPORT = "customer_support"
    FAQ = "faq"
    SALES_ASSISTANT = "sales_assistant"
    INTERNAL_HELPDESK = "internal_helpdesk"

class IntegrationPlatform(str, Enum):
    WEBSITE = "website"
    SLACK = "slack"
    TEAMS = "teams"
    WHATSAPP = "whatsapp"
    MOBILE_APP = "mobile_app"

class ChannelStrategy(str, Enum):
    SINGLE = "single"
    MULTI = "multi_channel"
    OMNICHANNEL = "omnichannel"

class AuthMethod(str, Enum):
    PUBLIC = "public_anonymous"
    INTERNAL_SSO = "internal_sso_iam"
    OAUTH = "customer_oauth"
    HYBRID = "hybrid"

class OrchestrationType(str, Enum):
    SINGLE_MODEL = "single_model"
    RAG_PIPELINE = "rag_pipeline"
    AGENTIC = "agentic_workflow"
    MULTI_AGENT = "multi_agent_swarm"

class HostingStrategy(str, Enum):
    MANAGED_SAAS = "managed_saas"
    VPC = "vpc_private_cloud"
    HYBRID = "hybrid_cloud"
    ON_PREM = "on_prem_edge"

class KnowledgeStrategy(str, Enum):
    PRETRAINED = "pretrained_only"
    RAG_VECTOR = "rag_vector_search"
    RAG_GRAPH = "rag_knowledge_graph"
    HYBRID = "hybrid_rag"

class GuardrailLevel(str, Enum):
    BASIC = "basic_filtering"
    MODERATE = "moderate_safety"
    STRICT = "strict_enterprise"
    COMPLIANCE = "compliance_regulated"

# ============================================================================
# 3. PYDANTIC MODELS
# ============================================================================

class UniversalProposalCore(BaseModel):
    # 1. Problem & Outcome
    decision_supported: str = Field(..., min_length=5)
    failure_mode: str = Field(..., min_length=5)
    error_tolerance: ErrorTolerance
    
    # 2. Data Reality
    data_source_type: DataSourceType
    data_frequency: DataFrequency
    data_quality: DataQuality
    
    # 3. Intelligence Layer
    system_autonomy: SystemAutonomy
    optimization_goal: OptimizationGoal
    retraining_frequency: str = Field(default="Monthly")
    
    # 4. Execution
    inference_location: InferenceLocation
    cloud_provider: Optional[CloudProvider] = None
    edge_hardware: Optional[EdgeHardware] = None
    execution_trigger: ExecutionTrigger
    failure_handling: str = Field(default="Human Review")

    # Common Commercials
    client_name: str = Field(..., min_length=2)
    vendor_name: str = Field(..., min_length=2)
    industry: Industry
    # use_case_description: str = Field(..., min_length=10) # Removed in favor of decision_supported
    delivery_timeline: DeliveryTimeline
    estimated_budget_usd: int = Field(default=50000)
    key_assumptions: Optional[str] = Field(default="")

    class Config: use_enum_values = True

class DemandForecastingProposal(UniversalProposalCore):
    # Domain Specifics
    forecasting_methods: List[ForecastingMethod]
    forecast_horizon_days: int = Field(default=30)
    historical_data_years: int = Field(default=2)
    features_available: List[str] = Field(default_factory=list)
    
    # New Deep Dive Fields
    forecast_level: str = Field(default="SKU Level")
    demand_volatility: str = Field(default="Stable")
    planning_decision: str = Field(default="Inventory Replenishment")

class VisualInspectionProposal(UniversalProposalCore):
    # Domain Specifics
    inspection_type: InspectionType
    defect_categories: List[str]
    accuracy_requirement: float = Field(default=0.95)
    image_source: ImageSource
    existing_images_count: int = Field(default=0)
    requires_labeling: bool = Field(default=True)
    
    # New Deep Dive Fields
    inspection_points: str = Field(default="Single View")
    cost_matrix: str = Field(default="Missed Defect is worse")
    existing_dataset_size: Optional[int] = Field(default=None)

class ChatbotProposal(UniversalProposalCore):
    # Domain Specifics
    chatbot_type: ChatbotType
    integration_platforms: List[IntegrationPlatform]
    expected_queries_per_day: int = Field(default=100)
    requires_multilingual: bool = Field(default=False)
    languages_required: List[str] = Field(default_factory=list)
    
    # Restored Legacy Fields
    response_type: str = Field(default="Generated")
    requires_human_handoff: bool = Field(default=True)
    document_formats: Optional[List[str]] = Field(default=None)
    traceability_required: bool = Field(default=True)

    # 1. Channels & Experience
    channel_strategy: ChannelStrategy
    
    # 2. Security & Access
    auth_method: AuthMethod
    
    # 3. Intelligence Topology
    orchestration_type: OrchestrationType
    
    # 4. Model Hosting Strategy
    hosting_strategy: HostingStrategy
    hosting_provider_detail: Optional[str] = Field(default=None)
    
    # 5. Knowledge & RAG
    knowledge_strategy: KnowledgeStrategy
    knowledge_sources: List[str] = Field(default_factory=list)
    knowledge_update_freq: Optional[str] = Field(default="Daily")
    
    # 6. Observability & Governance
    guardrail_level: GuardrailLevel
    analytics_depth: str = Field(default="Standard")
    
    # 7. Delivery Context
    deployment_phase: str = Field(default="POC")

# ============================================================================
# 4. HELPER FUNCTIONS
# ============================================================================

def format_enum_options(enum_cls):
    """Returns list of values for streamlit selectboxes"""
    return [e.value for e in enum_cls]

def dropdown_with_other(label, options, key_prefix):
    """
    Renders a selectbox with an 'other' option.
    Returns the selected value or the custom input.
    """
    options_with_other = options + ["other"]
    selected = st.selectbox(label, options_with_other, key=f"{key_prefix}_select")
    
    if selected == "other":
        custom_val = st.text_input(f"Specify {label}", key=f"{key_prefix}_custom")
        return custom_val if custom_val else "other"
    return selected

def handle_submission(model_class, data, type_label):
    try:
        # Filter out None values to let Pydantic defaults handle them if needed
        clean_data = {k: v for k, v in data.items() if v is not None}
        validated_proposal = model_class(**clean_data)
        st.success(f"✅ {type_label} Config Validated!")
        with st.expander("View Raw Configuration Data"):
            st.json(validated_proposal.dict())
        with st.spinner(f"Generating {type_label} Deck..."):
            pptx_file = create_presentation(validated_proposal.dict(), type_label)
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
# 5. STREAMLIT UI
# ============================================================================

st.set_page_config(page_title="Proposal Automation", page_icon="🚀", layout="wide")
st.title("🚀 Proposal Automation System")
st.sidebar.header("Global Settings")

with st.container():
    c_global1, c_global2 = st.columns(2)
    with c_global1:
        global_client = st.text_input("Client Name *", "Acme Corp", key="global_client")
    with c_global2:
        global_vendor = st.text_input("Vendor Name *", "My AI Agency", key="global_vendor")
    
    global_industry = st.selectbox("Industry *", format_enum_options(Industry), key="global_industry")

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

        with st.expander("Commercials", expanded=False):
            c1, c2 = st.columns(2)
            with c1: timeline = st.selectbox("Timeline *", format_enum_options(DeliveryTimeline), key="dt_demand")
            with c2: budget = st.number_input("Budget (USD)", 10000, 1000000, 50000, step=5000, key="b_demand")
            assumptions = st.text_area("Key Assumptions", key="asm_demand")

        submitted_demand = st.form_submit_button("Generate Demand Proposal", type="primary")

    if submitted_demand:
        data = {
            **core_data,
            "client_name": global_client, "vendor_name": global_vendor, "industry": global_industry,
            "forecasting_methods": methods, "forecast_horizon_days": horizon,
            "historical_data_years": history, "features_available": features_selected,
            "forecast_level": level, "demand_volatility": vol, "planning_decision": plan,
            "delivery_timeline": timeline, "estimated_budget_usd": budget, "key_assumptions": assumptions
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
                # Conditional Dataset Size
                ds_size = None
                if img_src == ImageSource.EXISTING_DATASET.value:
                    ds_size = st.number_input("Dataset Size (Images)", 100, 1000000, 5000)
            with c2: points = st.text_input("Inspection Points", "Single Camera")
            
            c3, c4 = st.columns(2)
            with c3: cost_mx = st.text_input("Cost Matrix", "Missed defect > False Positive")
            with c4: labeling = st.checkbox("Requires Data Labeling", value=True)

        with st.expander("Commercials", expanded=False):
            c1, c2 = st.columns(2)
            with c1: timeline = st.selectbox("Timeline *", format_enum_options(DeliveryTimeline), key="dt_visual")
            with c2: budget = st.number_input("Budget (USD)", 15000, 1000000, 60000, step=5000, key="b_visual")
            assumptions = st.text_area("Key Assumptions", key="asm_visual")

        submitted_visual = st.form_submit_button("Generate Visual Inspection Proposal", type="primary")

    if submitted_visual:
        defects_list = [x.strip() for x in defect_str.split(',')] if defect_str else []
        data = {
            **core_data,
            "client_name": global_client, "vendor_name": global_vendor, "industry": global_industry,
            "inspection_type": insp_type, "defect_categories": defects_list,
            "accuracy_requirement": accuracy, "image_source": img_src,
            "existing_dataset_size": ds_size, "inspection_points": points,
            "cost_matrix": cost_mx, "requires_labeling": labeling,
            "delivery_timeline": timeline, "estimated_budget_usd": budget, "key_assumptions": assumptions
        }
        handle_submission(VisualInspectionProposal, data, "Visual Inspection")

# === TAB 3: CHATBOT ===
# Domain & Architecture Refactor
with tab_chat:
    st.header("Chatbot Config")
    with st.form("form_chatbot"):
        # 1. Strategic Context (Universal)
        with st.expander("Strategic Context", expanded=True):
            core_data = render_universal_core("chat")
        
        # 2. Domain Details (Capabilities)
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

        # 3. Architecture & Implementation (New Groups)
        with st.expander("Domain & Architecture Details", expanded=True):
            
            # Group 1: Channels & Experience
            st.markdown("#### 1. Channels & Experience")
            chan_strat = st.selectbox("Channel Strategy", format_enum_options(ChannelStrategy), help="How are channels coordinated?")
            
            # Group 2: Security & Access
            st.markdown("#### 2. Security & Access")
            auth_meth = st.selectbox("Auth Method", format_enum_options(AuthMethod))

            # Group 3: Intelligence Topology
            st.markdown("#### 3. Intelligence Topology")
            orch_type = st.selectbox("Orchestration Type", format_enum_options(OrchestrationType))

            # Group 4: Model Hosting
            st.markdown("#### 4. Model Hosting Strategy")
            c_host1, c_host2 = st.columns(2)
            with c_host1: host_strat = st.selectbox("Hosting Strategy", format_enum_options(HostingStrategy))
            with c_host2:
                # Conditional Cascading
                host_detail = None
                if host_strat == HostingStrategy.MANAGED_SAAS.value:
                    host_detail = st.text_input("Preferred Provider", "OpenAI / Anthropic")
                elif host_strat == HostingStrategy.ON_PREM.value:
                    host_detail = st.text_input("Target Hardware", "NVIDIA Jetson / Local Server")
            
            # Group 5: Knowledge & RAG
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
            
            # Group 6: Observability & Governance
            st.markdown("#### 6. Observability & Governance")
            c_obs1, c_obs2 = st.columns(2)
            with c_obs1: 
                guard_level = st.selectbox("Guardrail Level", format_enum_options(GuardrailLevel))
                trace = st.checkbox("Traceability Required", value=True)
            with c_obs2: analytics = st.selectbox("Analytics Depth", ["Basic", "Standard", "Advanced (Conversational Intelligence)"], index=1)
            
            # Group 7: Delivery Context
            st.markdown("#### 7. Delivery Context")
            del_phase = st.selectbox("Deployment Phase", ["POC", "MVP", "Production Pilot", "Scale Rollout"])

        with st.expander("Commercials", expanded=False):
            c1, c2 = st.columns(2)
            with c1: timeline = st.selectbox("Timeline *", format_enum_options(DeliveryTimeline), key="dt_chat")
            with c2: budget = st.number_input("Budget (USD)", 10000, 1000000, 40000, step=5000, key="b_chat")
            assumptions = st.text_area("Key Assumptions", key="asm_chat")

        submitted_chat = st.form_submit_button("Generate Chatbot Proposal", type="primary")

    if submitted_chat:
        languages = [x.strip() for x in lang_str.split(',')] if (multilingual and lang_str) else []
        knowledge_srcs = [x.strip() for x in know_src_str.split(',')] if (know_strat != "pretrained_only" and know_src_str) else []
        doc_formats = [x.strip() for x in doc_fmt_str.split(',')] if (know_strat != "pretrained_only" and doc_fmt_str) else []

        data = {
            **core_data,
            "client_name": global_client, "vendor_name": global_vendor, "industry": global_industry,
            "chatbot_type": cb_type, "integration_platforms": platforms,
            "expected_queries_per_day": queries, 
            "requires_multilingual": multilingual, "languages_required": languages,
            "requires_human_handoff": handoff,
            "response_type": resp_type,
            
            # New Architecture Fields
            "channel_strategy": chan_strat,
            "auth_method": auth_meth,
            "orchestration_type": orch_type,
            "hosting_strategy": host_strat, "hosting_provider_detail": host_detail,
            "knowledge_strategy": know_strat, "knowledge_sources": knowledge_srcs, 
            "knowledge_update_freq": know_freq, "document_formats": doc_formats,
            "guardrail_level": guard_level, "analytics_depth": analytics, "traceability_required": trace,
            "deployment_phase": del_phase,
            "delivery_timeline": timeline, "estimated_budget_usd": budget, "key_assumptions": assumptions
        }
        handle_submission(ChatbotProposal, data, "Chatbot")