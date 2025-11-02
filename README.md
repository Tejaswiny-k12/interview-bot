#  Cyber-interview-bot

This Project is an interactive cybersecurity interview coach that asks technical, scenario, and behavioral interview questions, evaluates answers with simple heuristics, and provides actionable feedback to help you practice and improve.

## 🚀 Features

💬 Interactive Chat UI: Clean, responsive, and user-friendly interface.

🤖 AI-Driven Q&A: Generates real-time technical, behavioral & scenario questions

🧠 Smart Feedback: Evaluates answers and suggests instant improvements.

📊 Progress Tracking: Monitors performance and highlights weak areas.

🗂️ Adaptive Learning: Adjusts question difficulty based on user level.

## Setup

1. From the repository root create and activate a virtual environment:

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

2. Install dependencies into the venv:

```powershell
# preferred: use the venv python to avoid PATH issues
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r cyber-interview-bot\requirements.txt
```

3. Run the Web UI (from the package directory):

```powershell
cd cyber-interview-bot
python -m webapp.app
```

4. Open your browser to http://127.0.0.1:5000
