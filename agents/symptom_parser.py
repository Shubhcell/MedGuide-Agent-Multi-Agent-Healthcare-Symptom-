"""Symptom parser agent: simple entity extraction to structured symptoms."""
import re
COMMON_SYMPTOMS = ["fever","cough","headache","chest pain","shortness of breath","rash","nausea","vomiting","diarrhea","abdominal pain","dizziness","bleeding"]

def parse_symptoms(text: str) -> dict:
    t = text.lower()
    found = [s for s in COMMON_SYMPTOMS if s in t]
    # duration heuristic
    duration = None
    m = re.search(r'(\d+)\s*(day|days|hour|hours|week|weeks)', t)
    if m:
        duration = m.group(0)
    return {"symptoms": found, "duration": duration, "raw_text": text}
