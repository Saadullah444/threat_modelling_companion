import json
from typing import Any, Dict

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from prompts import threat_json_prompts

app = FastAPI(title="Threat-Model API")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"

# Inference settings from Section 2.1 of the paper
MODEL_OPTIONS = {
    "temperature": 0.2,
    "num_predict": 4000,
    "num_ctx": 16384,  # large enough for the architecture JSON plus the baseline threat list
}


class ThreatModelRequest(BaseModel):
    threat_model: Dict[str, Any]
    detected_threats: Dict[str, Any]


def call_local_model(prompt: str, json_output: bool = False) -> str:
    """Send a prompt to the locally running Ollama server and return the model's text output."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": MODEL_OPTIONS,
    }
    if json_output:
        payload["format"] = "json"

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=900)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Local LLM generation failed: {e}")

    return response.json()["response"].strip()


@app.post("/process-threat-model")
def process_threat_model(req: ThreatModelRequest):
    try:
        prompt = threat_json_prompts.format(
            detected_threats=json.dumps(req.detected_threats, indent=2),
            threat_model=json.dumps(req.threat_model, indent=2),
        )
        raw = call_local_model(prompt)
        return {"response": raw}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
