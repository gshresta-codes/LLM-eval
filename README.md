# 🧪 LLM Evaluation Project — Q&A / Chatbot

A lightweight, batteries-included CLI tool for evaluating LLM responses on Q&A tasks.
Supports three scoring strategies so you can pick what fits your use case.

---

## 📁 Project Structure

```
llm-eval/
├── eval_runner.py   ← Main entry point — run this
├── scorers.py       ← Three scoring strategies
├── report.py        ← CLI report (also usable standalone)
├── config.py        ← All settings in one place
├── dataset.json     ← Your evaluation dataset
└── results.json     ← Created after each run
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install anthropic
```

### 2. Set your API key
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Configure (optional)
Edit `config.py` to change the model, system prompt, scorer, or thresholds.

---

## 🚀 Usage

### Run with default scorer (llm_judge)
```bash
python eval_runner.py
```

### Choose a specific scorer
```bash
python eval_runner.py --scorer llm_judge     # Claude grades 1-5 with reasoning
python eval_runner.py --scorer exact_match   # Keyword overlap check (fast, free)
python eval_runner.py --scorer human         # You score each response in the terminal
```

### Filter by tag
```bash
python eval_runner.py --tags python          # Only Python questions
python eval_runner.py --tags factual math    # Factual OR math questions
```

### Run specific items
```bash
python eval_runner.py --ids q001 q003 q007
```

### Re-print the last report without re-running
```bash
python report.py
```

---

## 📊 Scorer Guide

| Scorer | Best for | Cost | Speed |
|---|---|---|---|
| `llm_judge` | Open-ended, nuanced answers | ~$0.001/item | ~2s/item |
| `exact_match` | Factual, short answers | Free | Instant |
| `human` | Ground truth, calibration | Your time | Manual |

**Recommendation**: Start with `exact_match` to get a quick baseline, then use
`llm_judge` for a deeper view. Use `human` to calibrate whether your LLM judge
is scoring fairly.

---

## ➕ Adding Your Own Questions

Edit `dataset.json` and add items in this format:

```json
{
  "id": "q009",
  "input": "Your question here",
  "expected": "The ideal answer you expect",
  "tags": ["your-tag"]
}
```

---

## 🔧 Customising the Judge

Edit the `JUDGE_PROMPT` in `scorers.py` to change scoring criteria.
For example, you can add dimensions like tone, conciseness, or safety.

---

## 📈 Next Steps

Once you have baseline results, consider:
- **Prompt iteration** — change `SYSTEM_PROMPT` in `config.py` and re-run to compare
- **Model comparison** — change `TARGET_MODEL` and run again; diff `results.json` files
- **CI integration** — run `eval_runner.py` in GitHub Actions on every prompt change
- **Expand dataset** — add 50–100 real queries from production logs
