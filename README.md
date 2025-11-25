# 🏥 MedGuide Agent – Multi-Agent Healthcare Symptom Triage System
### Powered by Google Gemini + Agent Development Kit (ADK)

MedGuide Agent is an AI-powered, multi-agent clinical triage system designed to interpret user symptoms, generate differential diagnoses, detect clinical red flags, assess severity, recommend specialists, and produce follow-up plans.

This project was built for the **Kaggle Agents Intensive Capstone Project**, using Google’s Agent Development Kit (ADK) and Gemini models, with a focus on **explainability**, **safety**, **observability**, and **real-world usefulness** in healthcare guidance.

> ⚠️ **Disclaimer:** This system does *not* provide medical diagnosis. It offers educational triage guidance only.

---

## 🚀 Key Features

- **Symptom Parsing Agent** – extracts symptoms, durations and key modifiers from free text.
- **Gemini-Powered Triage Agent** – produces a strict JSON differential with confidences and evidence.
- **Referral Agent** – suggests an appropriate specialist based on top diagnosis.
- **Follow-Up Planner** – generates safe next steps and monitoring guidance.
- **Memory & Persistence** – stores sessions in SQLite and supports CSV export.
- **Observability** – logging, metrics, and fallback monitoring.
- **Evaluation Kit** – small labeled dataset + evaluation skeleton for offline validation.

---

## 🧠 Architecture Overview

MedGuide uses a modular, pipeline-oriented, multi-agent architecture:

```
User Input
     │
     ▼
[Symptom Parser Agent] ──► Structured symptoms
     │
     ▼
[Triage Agent (Gemini)] ──► Differential + severity + red flags
     │
     ▼
[Referral Agent] ──► Specialist recommendation
     │
     ▼
[Follow-Up Agent] ──► Care plan
     │
     ▼
[Memory Manager] ──► SQLite sessions + CSV export
     ▲
     └─────────────────────── Observability & Evaluation ──────────────┘
```

---

## 📂 Project Structure

```
healthcare-triage-agent/
├── agents/
│   ├── gemini_client.py        # Gemini wrapper + retries + mock fallback
│   ├── symptom_parser.py
│   ├── triage_agent.py
│   ├── referral_agent.py
│   ├── followup_agent.py
│   └── run_pipeline_demo.py
├── core/
│   ├── memory.py
│   └── utils.py
├── data/
│   └── eval_dataset.csv
├── sessions_export.csv
├── triage_memory.db
├── README.md        <-- this file
├── requirements.txt
└── LICENSE
```

---

## 🛠 Installation

```bash
git clone https://github.com/yourusername/medguide-agent.git
cd medguide-agent

python -m venv myenv
# activate the venv:
# Windows:
myenv\Scripts\activate
# macOS / Linux:
source myenv/bin/activate

pip install -r requirements.txt
pip install -U google-genai
```

---

## 🔐 Environment Variables

### Using Gemini Developer API (AI Studio)
```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"   # macOS / Linux
set GEMINI_API_KEY=YOUR_GEMINI_API_KEY       # Windows (CMD)
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"    # PowerShell
```

### Using Vertex AI (optional)
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export GOOGLE_GENAI_USE_VERTEXAI=True
```

---

## ▶️ Running the Demo

From the project root:

```bash
python -m agents.run_pipeline_demo
```

This runs three sample triage inputs and saves sessions to `triage_memory.db` and exports `sessions_export.csv`.

To call interactively from Python:

```python
from agents.run_pipeline_demo import run_once
run_once("I have fever and cough for 3 days", "test_user")
```

---

## 🔧 Configuration & Customization

- **Change model**: edit `agents/gemini_client.py` to use a different Gemini model name (e.g., `gemini-2.5-flash`).
- **Prompt tuning**: edit `agents/triage_agent.py` to improve JSON schema examples and constraints.
- **Enable deployment**: add `Dockerfile` and Cloud Run / Agent Engine deployment instructions.

---

## 📊 Evaluation

Included `data/eval_dataset.csv` (sample vignettes). Use the evaluation skeleton in `notebooks/` or a small Python script to compute:
- JSON parse success rate
- Severity accuracy
- Red-flag detection recall/precision
- Differential top-1 accuracy

---

## 📌 Notes on Safety & Ethics

- The agent **does not diagnose**. It provides triage suggestions and highlights red flags.
- For any emergency severity, the system advises immediate care.
- Do **not** include API keys in committed code. Use environment variables or secret managers.

---

## 🌟 Future Work

- Voice input (speech-to-text) agent
- Offline specialist locator (no paid APIs)
- Clinician summary export (PDF/Markdown)
- Streamlit / Flask demo UI
- Cloud deployment and continuous evaluation

---

## License

MIT License

---

## Acknowledgements

This project was created for the Kaggle Agents Intensive Capstone Project and uses Google Gemini and ADK concepts for agent orchestration.
