"""Referral agent: map top condition to suggested specialist(s)."""
def suggest_specialist(differential: list) -> dict:
    if not differential:
        return {"suggested_specialist":"Primary Care","notes":"No strong condition"}
    top = differential[0].get('condition','Primary Care')
    mapping = {
        "Upper respiratory infection":"Primary Care / ENT",
        "Influenza":"Primary Care",
        "COVID-19":"Infectious disease / Primary Care",
        "Acute coronary syndrome":"Cardiology (ER)",
        "Gastroesophageal reflux disease":"Gastroenterology"
    }
    return {"suggested_specialist": mapping.get(top, "Primary Care"), "notes": f"Top condition: {top}"}
