# ─────────────────────────────────────────────
#  config.py  –  Central configuration (Groq)
# ─────────────────────────────────────────────

# Model to evaluate (free on Groq)
TARGET_MODEL = "llama-3.3-70b-versatile"

# Model used as the LLM judge
JUDGE_MODEL = "llama-3.3-70b-versatile"

# Max tokens for the model being evaluated
MAX_TOKENS = 512

# Path to your evaluation dataset
DATASET_PATH = "dataset.json"

# Output file for results
RESULTS_PATH = "results.json"

# Default scorer: "llm_judge" | "exact_match" | "human"
DEFAULT_SCORER = "llm_judge"

# LLM judge score threshold to consider a response "passing" (1–5 scale)
PASS_THRESHOLD = 3

# System prompt for the chatbot/model under evaluation
SYSTEM_PROMPT = (
    "You are a helpful, concise assistant. "
    "Answer questions clearly and accurately."
)
