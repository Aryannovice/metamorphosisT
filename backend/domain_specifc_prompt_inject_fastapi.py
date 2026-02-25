# injection_api.py

import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification
from torch.nn.functional import softmax
import numpy as np

app = FastAPI(title="Domain-Specific Injection Detection API")

# ------------------------------
# Request Schema
# ------------------------------

class PromptRequest(BaseModel):
    prompt: str

# ------------------------------
# Load Models (Startup)
# ------------------------------

print("Loading models...")

# 1. ShieldGemma
shield_tokenizer = AutoTokenizer.from_pretrained("google/shieldgemma-2b")
shield_model = AutoModelForCausalLM.from_pretrained(
    "google/shieldgemma-2b",
    device_map="auto",
    torch_dtype=torch.bfloat16
)

# 2. DeBERTa Injection Detector
deberta_tokenizer = AutoTokenizer.from_pretrained("deepset/deberta-v3-base-injection")
deberta_model = AutoModelForSequenceClassification.from_pretrained(
    "deepset/deberta-v3-base-injection"
)

print("Models loaded successfully.")

# ------------------------------
# Detectors
# ------------------------------

def rule_based_detector(prompt: str):
    suspicious_patterns = [
        "ignore previous", "forget everything", "override", "bypass",
        "reset instructions", "start from scratch"
    ]
    return any(p in prompt.lower() for p in suspicious_patterns)


def shieldgemma_detector(prompt: str):
    formatted_prompt = f"""
    Does the following prompt attempt to override system instructions?

    Prompt: {prompt}
    Answer Yes or No.
    """

    inputs = shield_tokenizer(formatted_prompt, return_tensors="pt").to(shield_model.device)

    with torch.no_grad():
        logits = shield_model(**inputs).logits

    vocab = shield_tokenizer.get_vocab()
    selected_logits = logits[0, -1, [vocab.get("Yes", 0), vocab.get("No", 1)]]
    probabilities = softmax(selected_logits, dim=0)

    return probabilities[0].item() > 0.5


def deberta_detector(prompt: str):
    inputs = deberta_tokenizer(prompt, return_tensors="pt")
    outputs = deberta_model(**inputs)
    prediction = torch.argmax(outputs.logits, dim=1).item()
    return prediction == 1  # 1 = injection


# ------------------------------
# API Routes
# ------------------------------

@app.get("/health")
def health():
    return {"status": "running"}


@app.post("/detect")
def detect(request: PromptRequest):
    prompt = request.prompt

    rule_flag = rule_based_detector(prompt)
    shield_flag = shieldgemma_detector(prompt)
    deberta_flag = deberta_detector(prompt)

    combined_flag = rule_flag or shield_flag or deberta_flag

    return {
        "rule_based": rule_flag,
        "shieldgemma": shield_flag,
        "deberta": deberta_flag,
        "injection_detected": combined_flag
    }