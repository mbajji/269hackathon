# Herding AI Cats — Gemini chatbot experiment

Small reproduction of the prompt-interference phenomenon from *Herding AI Cats* (2023), not a full CarlaBot recreation.

## Setup
Install Python 3.10+, unzip, open the project folder in VS Code, then run:

```bash
python3 -m pip install -r requirements.txt
```

Create a Gemini API key at https://aistudio.google.com/api-keys. Keep it private.

Mac/Linux:
```bash
export GEMINI_API_KEY="your-key"
```

Windows PowerShell:
```powershell
$env:GEMINI_API_KEY="your-key"
```

Chat interactively:
```bash
python3 chat.py --recipe pasta --condition combined
```

Run a small real experiment (60 calls, 3 recipes × 5 inputs × 4 conditions):
```bash
python3 experiment.py --provider gemini --repeats 1 --out results.csv
python3 analyze.py --input results.csv
```

Demo mode (synthetic data, not empirical evidence):
```bash
python3 experiment.py --provider demo --out demo.csv
```

Conditions: pacing only, humor only, combined, combined with instructions separated into labeled sections. Gemini uses one system instruction, so the last condition is formatting separation, not separate message roles. Inspect responses manually before drawing conclusions; the included heuristics are crude. Free-tier model access and rate limits depend on your account.
