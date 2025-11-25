import json, math, time
from .gemini_client import GeminiClient
from core.utils import detect_red_flags

# Instantiate Gemini client (will fallback to mock if not configured)
gem = GeminiClient()

# Strict JSON prompt template with schema and 2 short examples
PROMPT_TEMPLATE = """
You are a clinical triage assistant. Given a short free-text patient symptom description and duration, produce a JSON array (only JSON, nothing else) of up to 5 possible conditions ordered by likelihood.
Each array element must be an object with these keys:
  - condition: string (name of likely condition)
  - confidence: number (0.0 - 1.0) representing model's estimated likelihood
  - evidence: short string (1-2 sentences) describing which symptoms or facts support this suggestion

Be concise. Provide real-world plausible conditions but do NOT give definitive diagnoses. If red flags are present (e.g., chest pain, sudden severe headache, loss of consciousness), include them in the evidence and ensure severity is set accordingly in the wrapper.

Examples (the model should mimic this exact JSON format):

Example 1:
Input: symptoms: ["fever","cough"], duration: "3 days"
Output JSON:
[
  {"condition": "Upper respiratory infection", "confidence": 0.75, "evidence": "fever and cough over multiple days consistent with URI"},
  {"condition": "Influenza", "confidence": 0.45, "evidence": "systemic viral symptoms may indicate influenza"},
  {"condition": "COVID-19", "confidence": 0.3, "evidence": "overlapping symptoms possible; test recommended if exposure"}
]

Example 2:
Input: symptoms: ["chest pain","sweating"], duration: "immediate"
Output JSON:
[
  {"condition": "Acute coronary syndrome", "confidence": 0.85, "evidence": "sudden chest pain and sweating are high-risk for ACS"},
  {"condition": "Musculoskeletal chest pain", "confidence": 0.2, "evidence": "mechanical onset possible if related to movement"}
]

Now produce the JSON array for the following input:
symptoms: {symptoms}
duration: {duration}
Respond ONLY with valid JSON (an array as above).
"""

# Helper: normalize confidences to [0,1] and ensure sum<=1 without strict requirement (we keep raw)
def normalize_confidences(ddx):
    # Ensure numeric and clamp 0..1
    for item in ddx:
        try:
            v = float(item.get("confidence", 0.0))
        except Exception:
            v = 0.0
        item["confidence"] = max(0.0, min(1.0, v))
    # optional: sort by confidence desc
    ddx.sort(key=lambda x: x.get("confidence",0.0), reverse=True)
    return ddx

def triage(parsed: dict, max_tokens: int = 512) -> dict:
    # Build prompt using replace (not str.format) so JSON examples' braces are preserved
    symptoms = parsed.get("symptoms", [])
    duration = parsed.get("duration", "unspecified")
    # Use JSON dump for symptoms to preserve quotes etc.
    prompt = PROMPT_TEMPLATE.replace("{symptoms}", json.dumps(symptoms)).replace("{duration}", str(duration))

    # Call Gemini via wrapper
    resp = gem.generate_structured(prompt, max_output_tokens=max_tokens)
    
    ddx = []
    # If response returned parsed JSON (list/dict), handle each case
    if isinstance(resp, list):
        ddx = resp
    elif isinstance(resp, dict):
        # If model returned {"text": "..."} attempt to parse the text
        if "text" in resp:
            try:
                ddx = json.loads(resp["text"])
            except Exception:
                # try to salvage by searching for JSON substring
                txt = resp["text"]
                start = txt.find("[")
                end = txt.rfind("]") + 1
                if start != -1 and end != -1:
                    try:
                        ddx = json.loads(txt[start:end])
                    except Exception:
                        ddx = []
        elif "ddx" in resp and isinstance(resp["ddx"], list):
            # mock fallback structure
            ddx = resp["ddx"]
        else:
            ddx = []
    else:
        ddx = []

    # Final fallback to a deterministic mock if nothing parsed
    if not ddx:
        ddx = [
            {"condition": "Viral illness", "confidence": 0.4, "evidence": "non-specific viral symptoms"},
            {"condition": "Bacterial infection", "confidence": 0.15, "evidence": "possible bacterial cause depending on fever severity"}
        ]
    
    ddx = normalize_confidences(ddx)

    # Severity heuristics
    red_flags = detect_red_flags(parsed)
    severity = "stable"
    if red_flags:
        severity = "emergency"
    else:
        top_conf = ddx[0].get("confidence", 0.0) if ddx else 0.0
        if top_conf >= 0.8:
            severity = "urgent"
        elif top_conf >= 0.5:
            severity = "urgent"
        else:
            severity = "stable"

    return {"differential": ddx, "severity": severity, "red_flags": red_flags}