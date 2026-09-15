from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
from typing import Dict, Any

from prompts import threat_json_prompts

app = FastAPI(title="Threat-Model API")

class ThreatModelRequest(BaseModel):
    threat_model: Dict[str, Any]
    detected_threats: Dict[str, Any]

def call_local_model(prompt: str) -> str:
    """
    Run the Ollama llama-3.1-8b model locally and return its raw output.
    """
    proc = subprocess.Popen(
        ["ollama", "run", "llama-3.1-8b", "--prompt", prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output, err = proc.communicate()
    if proc.returncode != 0:
        raise HTTPException(status_code=500, detail="Local LLM generation failed")
    return output.decode().strip()

@app.post("/process-threat-model")
async def process_threat_model(req: ThreatModelRequest):
    try:
        # Fill in the system‐style prompt from your prompts.py
        prompt = threat_json_prompts.format(
            detected_threats=req.detected_threats,
            threat_model=req.threat_model
        )
        # Call local LLM
        raw = call_local_model(prompt)
        return {"response": raw}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")