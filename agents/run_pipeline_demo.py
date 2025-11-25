"""Run a small demo pipeline locally. Replace Gemini key via env var GEMINI_API_KEY before running."""
from agents.symptom_parser import parse_symptoms
from agents.triage_agent import triage
from agents.referral_agent import suggest_specialist
from agents.followup_agent import build_followup
from core.memory import init_db, save_session, export_sessions_csv
from core.utils import detect_red_flags
import json

def run_once(text, patient_id='anon'):
    parsed = parse_symptoms(text)
    triage_res = triage(parsed)
    referral = suggest_specialist(triage_res['differential'])
    followup = build_followup(parsed, triage_res)
    result = {'parsed': parsed, 'triage': triage_res, 'referral': referral, 'followup': followup}
    sid = save_session(patient_id, text, result)
    print('Session:', sid)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    init_db()
    tests = [
        ('I have fever and cough for 3 days', 'patient_1'),
        ('Sudden chest pain and sweating after exercise', 'patient_2'),
        ('Mild abdominal pain and diarrhea', 'patient_3')
    ]
    for t,p in tests:
        run_once(t,p)
    print('Exported:', export_sessions_csv())
