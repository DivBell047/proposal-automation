# ============================================================================
# PROPOSAL AUTOMATION SYSTEM - Phase 3 (Single File Version)
# ============================================================================

import streamlit as st
from pydantic import BaseModel, Field, ValidationError
from enum import Enum
from typing import List, Optional
import io
import os
from groq import Groq

# We import python-pptx inside the app. 
# Make sure to run `pip install python-pptx` in Colab first.
try:
    from pptx import Presentation
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
            max_tokens=500,
        )
        return completion.choices[0].message.content.strip()
        
    except Exception as e:
        return f"[AI ERROR: {str(e)}]"
    

def generate_narrative_content(data: dict, proposal_type: str) -> dict:
    """
    Orchestrates content generation.
    Mixes Deterministic Data (Budget, Dates) with AI Narrative (Summary).
    """
    
    # 1. Common Formatting
    client = data.get("client_name", "Valued Client")
    vendor = data.get("vendor_name", "Our Company")
    industry = data.get("industry", "Business").title()
    budget = f"${data.get('estimated_budget_usd', 0):,}"
    timeline = data.get("delivery_timeline", "").replace("_", " ").title()
    cloud = data.get("cloud_provider", "Cloud").upper()
    
    # Helper to format lists for the prompt (e.g. methods)
    tech_details = data.get('forecasting_methods') or data.get('inspection_type') or data.get('chatbot_type')
    if isinstance(tech_details, list): tech_details = ", ".join(tech_details)

    prompt = f"""
    You are writing sections for a pitch deck. Output exactly two sections separated by "|||".
    
    SECTION 1: Executive Summary (3-4 sentences)
    - Structure: Hook (The Challenge) -> Solution (The approach) -> Value (The Impact).
    - Context: {client} in {industry} needs {data.get('use_case_description')}.
    - We ({vendor}) propose a solution on {cloud} using {tech_details}.
    - Commercials: {budget}, {timeline}.
    - Tone: Strategic, persuasive.
    
    |||
    
    SECTION 2: Technical Rationale (2 sentences)
    - Explain WHY the selected technical features/methods are the right choice for this specific use case.
    - Context: We selected {tech_details} and features like {data.get('features_available') or data.get('defect_categories') or data.get('integration_platforms')}.
    - Tone: Technical, authoritative.
    """
    
    # 3. Call the AI
    ai_response = call_llm_for_text(prompt)
    
    # 4. Parse Response
    if "|||" in ai_response:
        summary_text, tech_narrative = ai_response.split("|||")
    else:
        # Fallback if AI ignores instructions
        summary_text = ai_response
        tech_narrative = f"Our technical approach leverages {tech_details} to ensure robust performance and scalability."

    # Clean up whitespace
    summary_text = summary_text.strip()
    tech_narrative = tech_narrative.strip()

    # 2. Executive Summary Rule (Personalized)
    # summary_text = (
    #     f"{vendor} is pleased to present this {proposal_type} proposal exclusively for {client}. "
    #     f"Designed specifically for the {industry} sector, our solution aims to address {data.get('use_case_description')} "
    #     f"with a projected investment of {budget} over {timeline}. "
    #     f"The system will be architected on {cloud} to ensure enterprise-grade scalability."
    # )
    # ai_summary = call_llm_for_text(summary_prompt)

    # 3. Replacements
    replacements = {
        "{{CLIENT}}": client,
        "{{VENDOR}}": vendor,
        "{{INDUSTRY}}": industry,
        "{{USE_CASE}}": data.get("use_case_description", ""),
        "{{TIMELINE}}": timeline,
        "{{BUDGET}}": budget,
        "{{CLOUD}}": cloud,
        "{{QUALITY}}": data.get("data_quality", "").title(),
        "{{ASSUMPTIONS}}": data.get("key_assumptions", "Standard commercial assumptions apply."),
        "{{EXECUTIVE_SUMMARY}}": summary_text, 
    }

    # 4. Domain Specific Logic
    if proposal_type == "Demand Forecasting":
        methods = ", ".join([m.replace('_', ' ').title() for m in data.get("forecasting_methods", [])])
        replacements["{{METHODS}}"] = methods
        replacements["{{HORIZON}}"] = f"{data.get('forecast_horizon_days')} Days"
        replacements["{{FREQUENCY}}"] = data.get("data_frequency", "").title()
        
        # feats = data.get("features_available", [])
        # feat_text = f"Key drivers: {', '.join(feats)}." if feats else "Historical data only."
        replacements["{{FEATURES_NARRATIVE}}"] = tech_narrative

    elif proposal_type == "Visual Inspection":
        replacements["{{INSPECTION_TYPE}}"] = data.get("inspection_type", "").replace('_', ' ').title()
        replacements["{{DEFECTS}}"] = ", ".join(data.get("defect_categories", []))
        replacements["{{ACCURACY}}"] = f"{data.get('accuracy_requirement', 0)*100:.1f}%"
        # replacements["{{IMAGE_SOURCE}}"] = data.get("image_source", "").replace('_', ' ').title()
        # We repurpose IMAGE_SOURCE to include the narrative if fitting, or just append it
        # Ideally, we would update the template to have {{TECH_NARRATIVE}}, but for now:
        replacements["{{IMAGE_SOURCE}}"] = f"{data.get('image_source', '').replace('_', ' ').title()}. {tech_narrative}"


    elif proposal_type == "Chatbot":
        replacements["{{CHATBOT_TYPE}}"] = data.get("chatbot_type", "").replace('_', ' ').title()
        replacements["{{PLATFORMS}}"] = ", ".join([p.title() for p in data.get("integration_platforms", [])])
        replacements["{{QUERIES}}"] = f"{data.get('expected_queries_per_day'):,} queries/day"
        # langs = data.get("languages_required", [])
        # replacements["{{LANGUAGES}}"] = ", ".join(langs) if langs else "English Only"
        # Inject narrative into Languages or a new field if possible. 
        # For now, let's append it to Languages to ensure it appears.
        langs = data.get("languages_required", [])
        lang_text = ", ".join(langs) if langs else "English Only"
        replacements["{{LANGUAGES}}"] = f"{lang_text}.\n\n{tech_narrative}"

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

def create_presentation(data: dict, proposal_type: str) -> io.BytesIO:
    """Loads a template, injects data, and returns the file in memory."""
    template_filename = TEMPLATE_MAP.get(proposal_type)
    template_path = os.path.join(TEMPLATE_DIR, template_filename)

    if os.path.exists(template_path):
        prs = Presentation(template_path)
    else:
        # Fallback if file missing
        print(f"Template missing: {template_path}")
        prs = Presentation() 
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = f"MISSING TEMPLATE: {proposal_type}"
        try:
            slide.placeholders[1].text = "Please run the Template Factory cell to generate templates."
        except: pass

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

class ForecastingMethod(str, Enum):
    TIME_SERIES = "time_series"
    REGRESSION = "regression"
    ENSEMBLE = "ensemble"
    DEEP_LEARNING = "deep_learning"

class DataFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class DataQuality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

class CloudProvider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ON_PREMISE = "on_premise"

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

# ============================================================================
# 3. PYDANTIC MODELS
# ============================================================================

class DemandForecastingProposal(BaseModel):
    client_name: str = Field(..., min_length=2)
    vendor_name: str = Field(..., min_length=2)
    industry: Industry
    use_case_description: str = Field(..., min_length=10, max_length=500)
    forecasting_methods: List[ForecastingMethod] = Field(..., min_items=1)
    forecast_horizon_days: int = Field(default=30, ge=1, le=365)
    data_frequency: DataFrequency
    historical_data_years: int = Field(default=2, ge=1, le=10)
    data_quality: DataQuality
    features_available: List[str] = Field(default_factory=list)
    cloud_provider: CloudProvider
    requires_real_time: bool = Field(default=False)
    delivery_timeline: DeliveryTimeline
    estimated_budget_usd: int = Field(default=50000, ge=10000)
    key_assumptions: Optional[str] = Field(default="", max_length=1000)
    class Config: use_enum_values = True

class VisualInspectionProposal(BaseModel):
    client_name: str = Field(..., min_length=2)
    vendor_name: str = Field(..., min_length=2)
    industry: Industry
    use_case_description: str = Field(..., min_length=10, max_length=500)
    inspection_type: InspectionType
    defect_categories: List[str] = Field(..., min_items=1)
    accuracy_requirement: float = Field(default=0.95, ge=0.80, le=0.99)
    image_source: ImageSource
    existing_images_count: int = Field(default=0, ge=0)
    data_quality: DataQuality
    requires_labeling: bool = Field(default=True)
    cloud_provider: CloudProvider
    edge_deployment_required: bool = Field(default=False)
    delivery_timeline: DeliveryTimeline
    estimated_budget_usd: int = Field(default=60000, ge=15000)
    key_assumptions: Optional[str] = Field(default="", max_length=1000)
    class Config: use_enum_values = True

class ChatbotProposal(BaseModel):
    client_name: str = Field(..., min_length=2)
    vendor_name: str = Field(..., min_length=2)
    industry: Industry
    use_case_description: str = Field(..., min_length=10, max_length=500)
    chatbot_type: ChatbotType
    integration_platforms: List[IntegrationPlatform] = Field(..., min_items=1)
    expected_queries_per_day: int = Field(default=100, ge=10)
    requires_multilingual: bool = Field(default=False)
    languages_required: List[str] = Field(default_factory=list)
    existing_knowledge_base: bool = Field(default=False)
    knowledge_sources: List[str] = Field(default_factory=list)
    cloud_provider: CloudProvider
    requires_human_handoff: bool = Field(default=True)
    delivery_timeline: DeliveryTimeline
    estimated_budget_usd: int = Field(default=40000, ge=10000)
    key_assumptions: Optional[str] = Field(default="", max_length=1000)
    class Config: use_enum_values = True

# ============================================================================
# 4. HELPER FUNCTIONS
# ============================================================================

def format_enum_options(enum_cls):
    """Returns list of values for streamlit selectboxes"""
    return [e.value for e in enum_cls]

def handle_submission(model_class, data, type_label):
    try:
        validated_proposal = model_class(**data)
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

st.set_page_config(page_title="Proposal Automation", page_icon="🚀", layout="centered")
st.title("🚀 Proposal Automation System")
st.sidebar.header("Global Settings")

with st.container():
    # New Client/Vendor inputs
    c_global1, c_global2 = st.columns(2)
    with c_global1:
        global_client = st.text_input("Client Name *", "Acme Corp", key="global_client")
    with c_global2:
        global_vendor = st.text_input("Vendor Name *", "My AI Agency", key="global_vendor")

    c_global3, c_global4 = st.columns(2)
    with c_global3:
        global_industry = st.selectbox("Industry *", format_enum_options(Industry), key="global_industry")
    with c_global4:
        global_use_case = st.text_area("Use Case Description *", height=68, help="Min 10 chars", key="global_use_case")

tab_demand, tab_visual, tab_chat = st.tabs(["Demand Forecasting", "Visual Inspection", "Chatbot"])

# === TAB 1 ===
with tab_demand:
    st.header("Demand Forecasting Config")
    with st.form("form_demand"):
        st.subheader("Scope & Methods")
        methods = st.multiselect("Forecasting Methods *", format_enum_options(ForecastingMethod))
        horizon = st.number_input("Forecast Horizon (Days)", 1, 365, 30)
        st.subheader("Data Availability")
        c1, c2 = st.columns(2)
        with c1: freq = st.selectbox("Data Frequency *", format_enum_options(DataFrequency))
        with c2: years = st.number_input("Historical Data (Years)", 1, 10, 2)
        quality = st.selectbox("Data Quality *", format_enum_options(DataQuality), key="dq_demand")
        st.markdown("**Available Features**")
        feature_opts = ['price', 'promotions', 'seasonality', 'weather', 'holidays']
        features_selected = []
        c1, c2, c3 = st.columns(3)
        for i, f in enumerate(feature_opts):
            if [c1, c2, c3][i % 3].checkbox(f.title(), key=f"df_feat_{f}"): features_selected.append(f)
        st.subheader("Technical & Commercials")
        cloud = st.selectbox("Cloud Provider *", format_enum_options(CloudProvider), key="cp_demand")
        real_time = st.checkbox("Requires Real-time Predictions")
        timeline = st.selectbox("Timeline *", format_enum_options(DeliveryTimeline), key="dt_demand")
        budget = st.number_input("Budget (USD)", 10000, 1000000, 50000, step=5000, key="b_demand")
        assumptions = st.text_area("Key Assumptions", key="asm_demand")
        submitted_demand = st.form_submit_button("Generate Demand Proposal", type="primary")

    if submitted_demand:
        data = {
            "client_name": global_client, "vendor_name": global_vendor,
            "industry": global_industry, "use_case_description": global_use_case,
            "forecasting_methods": methods, "forecast_horizon_days": horizon,
            "data_frequency": freq, "historical_data_years": years,
            "data_quality": quality, "features_available": features_selected,
            "cloud_provider": cloud, "requires_real_time": real_time,
            "delivery_timeline": timeline, "estimated_budget_usd": budget,
            "key_assumptions": assumptions
        }
        handle_submission(DemandForecastingProposal, data, "Demand Forecasting")

# === TAB 2 ===
with tab_visual:
    st.header("Visual Inspection Config")
    with st.form("form_visual"):
        st.subheader("Scope & Methods")
        insp_type = st.selectbox("Inspection Type *", format_enum_options(InspectionType))
        defect_str = st.text_input("Defect Categories *", placeholder="scratches, dents")
        accuracy = st.slider("Accuracy Requirement", 0.80, 0.99, 0.95)
        st.subheader("Data Availability")
        img_source = st.selectbox("Image Source *", format_enum_options(ImageSource))
        img_count = st.number_input("Existing Images Count", 0, 100000, 0)
        quality = st.selectbox("Data Quality *", format_enum_options(DataQuality), key="dq_visual")
        labeling = st.checkbox("Requires Data Labeling", value=True)
        st.subheader("Technical & Commercials")
        cloud = st.selectbox("Cloud Provider *", format_enum_options(CloudProvider), key="cp_visual")
        edge = st.checkbox("Edge Deployment Required")
        timeline = st.selectbox("Timeline *", format_enum_options(DeliveryTimeline), key="dt_visual")
        budget = st.number_input("Budget (USD)", 15000, 1000000, 60000, step=5000, key="b_visual")
        assumptions = st.text_area("Key Assumptions", key="asm_visual")
        submitted_visual = st.form_submit_button("Generate Visual Inspection Proposal", type="primary")

    if submitted_visual:
        defects_list = [x.strip() for x in defect_str.split(',')] if defect_str else []
        data = {
            "client_name": global_client, "vendor_name": global_vendor,
            "industry": global_industry, "use_case_description": global_use_case,
            "inspection_type": insp_type, "defect_categories": defects_list,
            "accuracy_requirement": accuracy, "image_source": img_source,
            "existing_images_count": img_count, "data_quality": quality,
            "requires_labeling": labeling, "cloud_provider": cloud,
            "edge_deployment_required": edge, "delivery_timeline": timeline,
            "estimated_budget_usd": budget, "key_assumptions": assumptions
        }
        handle_submission(VisualInspectionProposal, data, "Visual Inspection")

# === TAB 3 ===
with tab_chat:
    st.header("Chatbot Config")
    with st.form("form_chatbot"):
        st.subheader("Scope & Methods")
        cb_type = st.selectbox("Chatbot Type *", format_enum_options(ChatbotType))
        platforms = st.multiselect("Integration Platforms *", format_enum_options(IntegrationPlatform))
        queries = st.number_input("Expected Queries/Day", 10, 50000, 100)
        multilingual = st.checkbox("Requires Multilingual Support")
        lang_str = st.text_input("Languages", placeholder="Spanish, French")
        st.subheader("Data Availability")
        has_kb = st.checkbox("Existing Knowledge Base Available")
        kb_str = st.text_input("Knowledge Sources", placeholder="PDFs, Website")
        st.subheader("Technical & Commercials")
        cloud = st.selectbox("Cloud Provider *", format_enum_options(CloudProvider), key="cp_chat")
        handoff = st.checkbox("Requires Human Handoff", value=True)
        timeline = st.selectbox("Timeline *", format_enum_options(DeliveryTimeline), key="dt_chat")
        budget = st.number_input("Budget (USD)", 10000, 1000000, 40000, step=5000, key="b_chat")
        assumptions = st.text_area("Key Assumptions", key="asm_chat")
        submitted_chat = st.form_submit_button("Generate Chatbot Proposal", type="primary")

    if submitted_chat:
        languages = [x.strip() for x in lang_str.split(',')] if (multilingual and lang_str) else []
        kb_sources = [x.strip() for x in kb_str.split(',')] if (has_kb and kb_str) else []
        data = {
            "client_name": global_client, "vendor_name": global_vendor,
            "industry": global_industry, "use_case_description": global_use_case,
            "chatbot_type": cb_type, "integration_platforms": platforms,
            "expected_queries_per_day": queries, "requires_multilingual": multilingual,
            "languages_required": languages, "existing_knowledge_base": has_kb,
            "knowledge_sources": kb_sources, "cloud_provider": cloud,
            "requires_human_handoff": handoff, "delivery_timeline": timeline,
            "estimated_budget_usd": budget, "key_assumptions": assumptions
        }
        handle_submission(ChatbotProposal, data, "Chatbot")