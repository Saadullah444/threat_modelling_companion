"""
FastAPI + Ollama (llama-3.1-8b)
• one local LLM call per threat
• incremental disk-flush after every threat
"""

import json
import logging
import datetime
import pathlib
import subprocess
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse

app = FastAPI(title="Threat-Mitigation API")
log = logging.getLogger(__name__)

# ─── Constants ──────────────────────────────────────────────

SAVE_DIR = pathlib.Path("mitigation_outputs")
SAVE_DIR.mkdir(exist_ok=True)

SYSTEM_MSG = (
    "You are a cybersecurity expert specialising in threat modelling, "
    "mitigation planning, and secure architecture for IoT and medical systems."
)

PER_THREAT_PROMPT = (
    'Read the following threat object (JSON). Return ONLY a JSON object of the form '
    '{"mitigation_strategy": "<2-4 sentences referencing ISO/OWASP/NIST, '
    'covering physical as well as software controls>"}'
)

# ─── Helpers ────────────────────────────────────────────────

def write_json(path: pathlib.Path, data: Any) -> None:
    """Pretty-print JSON to disk (UTF-8, atomic overwrite)."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)

def call_local_model(prompt: str) -> str:
    """
    Shell out to Ollama’s llama-3.1-8b and return its raw output.
    """
    proc = subprocess.Popen(
        ["ollama", "run", "llama-3.1-8b", "--prompt", prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output, err = proc.communicate()
    if proc.returncode != 0:
        log.error("Local LLM error: %s", err.decode().strip())
        raise HTTPException(status_code=500, detail="Local LLM generation failed")
    return output.decode().strip()

def get_mitigation(threat_obj: Dict[str, Any]) -> str:
    """
    Build a single-threat prompt, invoke the local LLM, parse JSON.
    """
    prompt_block = (
        f"{SYSTEM_MSG}\n"
        f"{PER_THREAT_PROMPT}\n"
        f"{json.dumps(threat_obj, ensure_ascii=False)}"
    )
    raw = call_local_model(prompt_block, json_output=True)
    try:
        parsed = json.loads(raw)
        return parsed["mitigation_strategy"]
    except Exception as e:
        log.error("Bad JSON from local LLM: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Invalid JSON from LLM")

# ─── Endpoint ───────────────────────────────────────────────

@app.post("/mitigate")
async def mitigate(request: Request):
    threats = payload.get("threats")
    if not isinstance(threats, list):
        raise HTTPException(status_code=400, detail="`threats` must be a list")

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    outfile = SAVE_DIR / f"mitigations_{timestamp}.json"
    out: list = []

    for idx, th in enumerate(threats):
        try:
            th["mitigation_strategy"] = get_mitigation(th)
        except HTTPException as he:
            th["mitigation_strategy"] = f"⚠️ {he.detail}"
        except Exception:
            th["mitigation_strategy"] = "⚠️ Generation failed"
        finally:
            out.append(th)
            write_json(outfile, out)
            log.info("Processed threat %d/%d", idx + 1, len(threats))

    return JSONResponse(content={"file": str(outfile), "data": out})
