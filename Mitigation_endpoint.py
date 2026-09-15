"""
FastAPI + Ollama (llama3.1:8b)
One local LLM call per threat, with an incremental disk flush after every threat.
"""

import datetime
import json
import logging
import pathlib
from typing import Any, Dict

import requests
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="Threat-Mitigation API")
log = logging.getLogger(__name__)

# Constants

SAVE_DIR = pathlib.Path("mitigation_outputs")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"

# Inference settings from Section 2.1 of the paper
MODEL_OPTIONS = {
    "temperature": 0.2,
    "num_predict": 4000,
    "num_ctx": 8192,
}

SYSTEM_MSG = (
    "You are a cybersecurity expert specialising in threat modelling, "
    "mitigation planning, and secure architecture for IoT and medical systems."
)

PER_THREAT_PROMPT = (
    "Read the following threat object (JSON). Return ONLY a JSON object of the form "
    '{"mitigation_strategy": "<2-4 sentences referencing ISO/OWASP/NIST, '
    'covering physical as well as software controls>"}'
)

# Helpers


def write_json(path: pathlib.Path, data: Any) -> None:
    """Pretty-print JSON to disk (UTF-8, atomic overwrite)."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


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
        log.error("Local LLM error: %s", e)
        raise HTTPException(status_code=500, detail=f"Local LLM generation failed: {e}")

    return response.json()["response"].strip()


def get_mitigation(threat_obj: Dict[str, Any]) -> str:
    """Build a single-threat prompt, invoke the local LLM, and parse the JSON reply."""
    prompt_block = (
        f"{SYSTEM_MSG}\n"
        f"{PER_THREAT_PROMPT}\n"
        f"{json.dumps(threat_obj, ensure_ascii=False)}"
    )
    raw = call_local_model(prompt_block, json_output=True)
    try:
        return json.loads(raw)["mitigation_strategy"]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        log.error("Bad JSON from local LLM: %s", e)
        raise HTTPException(status_code=500, detail="Invalid JSON from LLM")


# Endpoint


@app.post("/mitigate")
def mitigate(payload: Dict[str, Any] = Body(...)):
    threats = payload.get("threats")
    if not isinstance(threats, list):
        raise HTTPException(status_code=400, detail="`threats` must be a list")

    SAVE_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    outfile = SAVE_DIR / f"mitigations_{timestamp}.json"
    out: list = []

    for idx, threat in enumerate(threats):
        try:
            threat["mitigation_strategy"] = get_mitigation(threat)
        except HTTPException as he:
            threat["mitigation_strategy"] = f"Generation failed: {he.detail}"
        except Exception as e:
            threat["mitigation_strategy"] = f"Generation failed: {e}"
        finally:
            out.append(threat)
            write_json(outfile, out)
            log.info("Processed threat %d/%d", idx + 1, len(threats))

    return JSONResponse(content={"file": str(outfile), "data": out})
