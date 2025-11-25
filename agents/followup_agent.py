def build_followup(parsed: dict, triage_result: dict) -> dict:
    plan = []
    sev = triage_result.get('severity','stable')
    if sev == 'emergency':
        plan.append('Seek immediate emergency care (call local emergency number).')
    elif sev == 'urgent':
        plan.append('Arrange an urgent appointment with the suggested specialist.')
    else:
        plan.append('Home care and monitoring for 48 hours. Return if worsening.')
    plan.append('Follow-up in 3-7 days.')
    return {"followup_plan": plan}
