# Proposal Automation System - Documentation

## 1. Project Overview
The **Proposal Automation System** is a tool designed to streamline the creation of technical sales proposals. It allows a user to input specific project details (client needs, technical constraints, budget) and automatically generates a professionally formatted PowerPoint presentation (`.pptx`).

### Key Features
*   **Three Proposal Types**: Supports *Demand Forecasting*, *Visual Inspection*, and *Chatbot* use cases.
*   **AI-Powered Narrative**: Uses **Groq (Llama 3.3 70B)** to write six different sections of the proposal (Executive Summary, Technical Rationale, etc.) based on the user's technical inputs.
*   **Architecture-Aware**: Captures deep technical details like "Inference Location" (Edge vs. Cloud), "Data Frequency", and "Orchestration Type" to ensure the proposal is technically grounded, not just generic marketing copy.
*   **Template-Based**: Injects content into pre-designed PowerPoint templates, preserving branding and formatting.

---

## 2. Implementation Approach
We built this application using **Streamlit** for the frontend and **Python** for the backend logic.

### The Workflow
1.  **User Input (Streamlit)**: The user fills out a structured form. We use `st.tabs` to separate the three proposal types. Common questions (Project Core) are shared, while domain-specific questions (e.g., "Camera Type" for Vision, "RAG Strategy" for Chatbot) are unique to each tab.
2.  **Validation (Pydantic)**: When the user clicks "Generate", the raw dictionary of inputs is passed to a **Pydantic Model**. This ensures all required fields are present and valid (e.g., budget is a positive integer).
3.  **Content Generation (LLM)**:
    *   We construct a highly specific **Prompt** that includes all the user's architectural choices.
    *   We instruct the AI (Groq) to output exactly **six sections**, separated by a delimiter (`|||`).
    *   This ensures we get distinct blocks of text for "Executive Summary", "Technical Rationale", etc., without having to make 6 separate API calls.
4.  **Presentation Generation (python-pptx)**:
    *   The system loads a specific template (e.g., `chatbot.pptx`) from the `templates/` folder.
    *   It iterates through every slide and shape, looking for placeholders like `{{CLIENT}}`, `{{EXECUTIVE_SUMMARY}}`, or `{{BUDGET}}`.
    *   It replaces these placeholders with either the user's direct input or the AI-generated text.
5.  **Download**: The resulting file is saved to an in-memory buffer (`io.BytesIO`) and offered as a download button.

---

## 3. Code Structure & Explanation

We have refactored the application into a modular architecture to support future scalability (e.g., migrating to AWS Bedrock/S3).

### Directory Structure
```text
proposal-automation/
├── app.py                  # Entry point (Streamlit UI & Orchestration)
├── templates/              # PowerPoint templates (.pptx)
└── src/                    # Core Logic Modules
    ├── models.py           # Data schemas (Pydantic) & Enums
    ├── ai_engine.py        # LLM integration (Groq/Llama 3)
    ├── slide_builder.py    # PowerPoint generation logic
    └── utils.py            # UI helpers
```

### Module Breakdown

#### A. `src/models.py` (The Blueprints)
Contains the "shape" of our data.
*   **Pydantic Models**: `UniversalProposalCore` and specific child classes (`ChatbotProposal`, etc.) ensure strict type validation of user inputs.
*   **Enums**: dozens of `Enum` classes (e.g., `Industry`, `CloudProvider`) to define fixed dropdown options and prevent typos.

#### B. `src/ai_engine.py` (The Brain)
Handles all interaction with the Large Language Model.
*   **`call_llm_for_text`**: Wraps the Groq API call. **Note**: If migrating to AWS Bedrock, this is the only function that needs changing.
*   **`generate_narrative_content`**: The prompts engineer. It takes structured data, builds the prompt, calls the LLM, and parses the returned 6-section text block.

#### C. `src/slide_builder.py` (The Builder)
Manages the `python-pptx` library interactions.
*   **`create_presentation`**: Loads the template, calls the AI engine for content, and iterates through slides to inject text.
*   **`replace_text_in_shape`**: Handles the physical replacement of keys like `{{CLIENT}}` with values, ensuring font consistency.

#### D. `src/utils.py` (Helpers)
*   **`format_enum_options`**: Converts Enums to list of strings for Streamlit.
*   **`dropdown_with_other`**: Custom UI component for "Other" text input fields.

#### E. `app.py` (The Controller)
Now a lightweight entry point (~200 lines).
*   **Renders the UI**: Uses `st.tabs` and `st.form` to collect inputs.
*   **Orchestrates**: imports logic from `src/` to validate data, generate content, and serve the download.
