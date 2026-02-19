from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ============================================================================
# ENUMS
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

class SuccessDimension(str, Enum):
    ACCURACY = "accuracy"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    COST = "cost_efficiency"
    USER_ADOPTION = "user_adoption"
    COVERAGE = "coverage"

class SecurityStandard(str, Enum):
    SOC2 = "soc2"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    NONE = "none"

class SecurityControl(str, Enum):
    VPC = "vpc_deployment"
    IAM = "iam_access_control"
    ENCRYPTION_REST = "encryption_at_rest"
    ENCRYPTION_TRANSIT = "encryption_in_transit"
    AUDIT_LOGGING = "audit_logging"
    MFA = "multi_factor_auth"

class DataFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    PARQUET = "parquet"

class DataVolumeUnit(str, Enum):
    MB = "mb"
    GB = "gb"
    TB = "tb"
    RECORDS_MILLION = "million_records"
    RECORDS_THOUSAND = "thousand_records"


# ============================================================================
# PYDANTIC MODELS
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
    delivery_timeline: DeliveryTimeline
    estimated_budget_usd: int = Field(default=50000)
    key_assumptions: Optional[str] = Field(default="")

    # RFP Specific Enhancements
    success_dimensions: List[SuccessDimension] = Field(default_factory=list)
    validation_strategy: str = Field(default="Human in the loop validation")
    
    security_standards: List[SecurityStandard] = Field(default_factory=list)
    security_controls: List[SecurityControl] = Field(default_factory=list)
    
    data_format: List[DataFormat] = Field(default_factory=list)
    data_volume: float = Field(default=1.0)
    data_volume_unit: DataVolumeUnit = Field(default=DataVolumeUnit.GB)
    
    # Assets
    client_logo_path: Optional[Any] = Field(default=None)
    company_logo_path: Optional[Any] = Field(default=None)
    architecture_diagram_path: Optional[Any] = Field(default=None)
    
    # Rich Content
    timeline_data: Optional[List] = Field(default=None) # List of row dicts from data editor

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
