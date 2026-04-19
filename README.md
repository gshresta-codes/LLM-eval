# 🧪 LLM Evaluation Project — Groq (Free)

Evaluate LLM responses on Q&A tasks using **Groq's free API** (Llama 3.3 70B).
No credit card required.

---

## ⚙️ Setup

### 1. Get a free Groq API key
1. Go to → **console.groq.com**
2. Sign up for free
3. Click **"API Keys"** in the left sidebar
4. Click **"Create API Key"** and copy it (starts with `gsk_...`)

### 2. Set your API key (PowerShell)
```powershell
$env:GROQ_API_KEY = "gsk_your_key_here"
```

To make it permanent (so you don't retype it every session):
```powershell
[System.Environment]::SetEnvironmentVariable("GROQ_API_KEY", "gsk_your_key_here", "User")
```
Then **restart your terminal**.

### 3. Install the Groq Python package
```powershell
pip install groq
```

### 4. Run your first eval
```powershell
python eval_runner.py --scorer exact_match
```

---

## 🚀 Usage

```powershell
python eval_runner.py                        # default scorer (llm_judge)
python eval_runner.py --scorer llm_judge     # Llama grades 1-5 with reasoning
python eval_runner.py --scorer exact_match   # keyword overlap (fast, no API calls for scoring)
python eval_runner.py --scorer human         # you score each response manually
python eval_runner.py --tags python          # only Python questions
python eval_runner.py --ids q001 q003        # specific questions only
python report.py                             # reprint last report without re-running
```

---

## 📊 Scorer Guide

| Scorer | Best for | Speed |
|---|---|---|
| `llm_judge` | Open-ended, nuanced answers | ~1s/item |
| `exact_match` | Factual, short answers | Instant |
| `human` | Ground truth, calibration | Manual |

---

## 📁 Project Structure

```
llm-eval/
├── eval_runner.py   ← Main entry point
├── scorers.py       ← Three scoring strategies
├── report.py        ← CLI report printer
├── config.py        ← All settings (model, thresholds, etc.)
├── dataset.json     ← Your evaluation dataset
└── results.json     ← Created after each run
```

---

## ➕ Adding Your Own Questions

Edit `dataset.json`:

```json
{
  "id": "q009",
  "input": "Your question here",
  "expected": "The ideal answer",
  "tags": ["your-tag"]
}
```

---

## 🆓 Groq Free Tier Limits

- 30 requests/minute
- 14,400 requests/day
- 6,000 tokens/minute

More than enough for running hundreds of eval runs per day.
