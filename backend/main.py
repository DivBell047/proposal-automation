"""
FastAPI backend — local dev server (mirrors Lambda Function URL behaviour).
On AWS: wrap with mangum → handler = Mangum(app)
"""
import io
import os
import sys
import tempfile
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ── make src/ importable when running from project root ──────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.slide_builder import create_presentation

app = FastAPI(title="Proposal Automation API")

# ── CORS: allow React dev server + any S3 static URL ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],   # tighten for prod
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── SHARED PAYLOAD FIELDS ──────────────────────────────────────────────────
# Mirror the Pydantic models in src/models.py — but as plain dicts here so
# FastAPI can accept JSON directly from React without re-validating everything.
# Validation already happens in src/models.py via create_presentation.

class ProposalPayload(BaseModel):
    class Config:
        extra = "allow"   # accept any field — src/models.py validates them


# ─── LOGO UPLOAD ─────────────────────────────────────────────────────────────

@app.post("/api/upload/logo")
async def upload_logo(file: UploadFile = File(...)):
    """
    Accepts a logo image, saves it to /tmp, returns the temp path.
    React sends this path back as client_logo_path in the generate payload.
    On AWS: swap /tmp write → s3.put_object, return presigned URL or S3 key.
    """
    suffix = os.path.splitext(file.filename)[-1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    return {"path": tmp_path, "filename": file.filename}


# ─── GENERATION ENDPOINTS ─────────────────────────────────────────────────────

def _generate_and_stream(payload: dict, proposal_type: str) -> StreamingResponse:
    """Shared logic: call create_presentation → stream .pptx bytes."""
    try:
        pptx_buffer: io.BytesIO = create_presentation(
            data=payload,
            proposal_type=proposal_type,
            api_key=None,   # Bedrock uses IAM auth — no key needed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    filename = f"{proposal_type.lower().replace(' ', '_')}_proposal.pptx"
    return StreamingResponse(
        pptx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.post("/api/generate/demand")
async def generate_demand(payload: ProposalPayload):
    return _generate_and_stream(payload.model_dump(), "Demand Forecasting")


@app.post("/api/generate/visual")
async def generate_visual(payload: ProposalPayload):
    return _generate_and_stream(payload.model_dump(), "Visual Inspection")


@app.post("/api/generate/chatbot")
async def generate_chatbot(payload: ProposalPayload):
    return _generate_and_stream(payload.model_dump(), "Chatbot")


# ─── HEALTH CHECK ─────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


# ─── LOCAL RUN ────────────────────────────────────────────────────────────────
# Run: uvicorn backend.main:app --reload --port 8000

# ─── LAMBDA HANDLER (uncomment when deploying to AWS) ─────────────────────────
# from mangum import Mangum
# handler = Mangum(app)
