import boto3
import json
import os

# Bedrock model to use — swap this string to change models
BEDROCK_MODEL_ID = "meta.llama3-8b-instruct-v1:0"
BEDROCK_REGION   = "ap-south-1"   # Mumbai — change if using a different region

def call_llm_for_text(prompt: str, api_key: str = None) -> str:
    """
    Calls AWS Bedrock (Llama 3 8B) to generate text.
    - Locally: authenticates via ~/.aws/credentials (run `aws configure`)
    - On Lambda: authenticates via the IAM execution role automatically
    """
    try:
        bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

        body = json.dumps({
            "prompt": (
                "<|begin_of_text|>"
                "<|start_header_id|>system<|end_header_id|>\n"
                "You are a senior solution architect and proposal writer. "
                "You write concise, high-impact business prose.\n"
                "<|eot_id|>"
                "<|start_header_id|>user<|end_header_id|>\n"
                f"{prompt}\n"
                "<|eot_id|>"
                "<|start_header_id|>assistant<|end_header_id|>\n"
            ),
            "max_gen_len": 800,
            "temperature": 0.7,
            "top_p": 0.9,
        })

        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        result = json.loads(response["body"].read())
        return result.get("generation", "").strip()

    except Exception as e:
        return f"[AI ERROR: {str(e)}]"
    

def generate_narrative_content(data: dict, proposal_type: str, api_key: str) -> dict:
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

    # RFP-Specific Fields
    success_dims = ", ".join([s.replace('_',' ').title() for s in data.get("success_dimensions", [])])
    val_strat = data.get("validation_strategy", "")
    sec_stds = ", ".join([s.replace('_',' ').title() for s in data.get("security_standards", [])]) or "Standard"
    sec_ctrls = ", ".join([s.replace('_',' ').title() for s in data.get("security_controls", [])])
    data_formats = ", ".join([f.upper() for f in data.get("data_format", [])])
    data_vol = f"{data.get('data_volume', '')} {data.get('data_volume_unit', '')}".strip()

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

    - RFP Requirements:
      Success Dimensions: {success_dims or 'Accuracy, Cost Efficiency'}
      Validation Strategy: {val_strat or 'Standard'}
      Security Standards: {sec_stds}
      Security Controls: {sec_ctrls or 'Standard controls'}
      Data Formats: {data_formats or 'Not specified'}
      Data Volume: {data_vol or 'Not specified'}

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
    ai_response = call_llm_for_text(prompt, api_key)
    
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
        "{{SUCCESS_DIMS}}": success_dims or "Accuracy, Cost Efficiency",
        "{{VALIDATION_STRATEGY}}": val_strat or "Human-in-the-loop validation",
        "{{SECURITY_STANDARDS}}": sec_stds,
        "{{SECURITY_CONTROLS}}": sec_ctrls or "VPC, IAM",
        "{{DATA_FORMATS}}": data_formats or "Standard formats",
        "{{DATA_VOLUME}}": data_vol or "Not specified",
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
