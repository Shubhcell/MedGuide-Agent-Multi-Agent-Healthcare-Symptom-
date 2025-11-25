import sqlite3, uuid, datetime, json
DB = 'triage_memory.db'
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS patients (
                    patient_id TEXT PRIMARY KEY,
                    name TEXT,
                    created_at TEXT
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    patient_id TEXT,
                    input_text TEXT,
                    result_json TEXT,
                    created_at TEXT
                )""")
    conn.commit()
    conn.close()
def save_session(patient_id:str, input_text:str, result:dict):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    sid = str(uuid.uuid4())
    now = datetime.datetime.utcnow().isoformat()
    c.execute("INSERT OR IGNORE INTO patients(patient_id, name, created_at) VALUES(?,?,?)", (patient_id, patient_id, now))
    c.execute("INSERT INTO sessions(session_id, patient_id, input_text, result_json, created_at) VALUES(?,?,?,?,?)", (sid, patient_id, input_text, json.dumps(result), now))
    conn.commit()
    conn.close()
    return sid
def export_sessions_csv(outfile='sessions_export.csv'):
    import csv
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT session_id, patient_id, input_text, result_json, created_at FROM sessions')
    rows = c.fetchall()
    conn.close()
    with open(outfile,'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['session_id','patient_id','input_text','result_json','created_at'])
        w.writerows(rows)
    return outfile
