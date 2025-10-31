# Cybersecurity Interview Coach (CLI)

This is a small interactive command-line chatbot that simulates cybersecurity interview practice sessions (technical, scenario, and behavioral questions). It uses simple heuristics to evaluate answers, provide feedback, and adapt question difficulty.

Files:
- `cyber_interview_bot.py` - main interactive CLI script
- `questions.json` - sample question bank (basic -> advanced; technical/scenario/behavioral)
- `session_log.txt` - appended session logs when you run the bot
- `tests/test_evaluator.py` - small unit tests for evaluation logic

How to run (Windows PowerShell):

```powershell
# create/activate a Python environment (optional but recommended)
python -m venv .venv; .\.venv\Scripts\Activate.ps1
# install test dependency if you want to run tests
pip install pytest
# run the bot
python .\cyber_interview_bot.py
```

Notes and next steps:
- The evaluator is heuristic-based (keyword matching, STAR detection). To upgrade, integrate a model-backed evaluator or more advanced NLP.
- You can extend `questions.json` with your own items. Fields: id, difficulty, type (technical/scenario/behavioral), question, keywords, explanation, references.
- Suggested enhancements: web UI, persistence of user profiles, deeper scoring rubric, LLM-based constructive feedback (requires API keys).
