# main.py

from fastapi import FastAPI
from pydantic import BaseModel
from pii_masker import mask_pii

app = FastAPI(
    title="PII Masking API",
    description="Lightweight endpoint for masking personally identifiable information",
    version="1.0"
)

class TextRequest(BaseModel):
    text: str

class MaskedResponse(BaseModel):
    original_text: str
    masked_text: str


@app.get("/")
def health_check():
    return {"status": "PII Masking API running"}


@app.post("/mask", response_model=MaskedResponse)
def mask_text(request: TextRequest):
    masked = mask_pii(request.text)
    return MaskedResponse(
        original_text=request.text,
        masked_text=masked
    )