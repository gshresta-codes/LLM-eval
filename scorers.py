# ─────────────────────────────────────────────
#  scorers.py  –  Scoring strategies
# ─────────────────────────────────────────────
#
#  Three strategies:
#    1. llm_judge   – Claude scores the response 1–5 with reasoning
#    2. exact_match – Keyword / substring presence check
#    3. human       – CLI prompt for manual scoring
#
# ─────────────────────────────────────────────

import anthropic
from config import JUDGE_MODEL, PASS_THRESHOLD

client = anthropic.Anthropic()


# ── 1. LLM-as-Judge ──────────────────────────────────────────────────────────

JUDGE_PROMPT = """You are an expert evaluator assessing the quality of a chatbot response.

Question asked:
{question}

Expected / ideal answer:
{expected}

Actual response from the chatbot:
{actual}

Score the response on a scale of 1 to 5 using these criteria:
  5 – Excellent: Accurate, complete, clear, matches expected answer well
  4 – Good: Mostly correct with minor omissions or slight inaccuracy
  3 – Acceptable: Partially correct but missing key information
  2 – Poor: Largely incorrect or unhelpful
  1 – Wrong: Completely incorrect or irrelevant

Respond in this exact format (no other text):
SCORE: <number>
REASON: <one sentence explanation>"""


def llm_judge(question: str, expected: str, actual: str) -> dict:
    """Score a response using Claude as a judge. Returns score (1-5) + reason."""
    prompt = JUDGE_PROMPT.format(
        question=question,
        expected=expected,
        actual=actual,
    )
    response = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()

    # Parse score and reason
    score, reason = None, raw
    for line in raw.splitlines():
        if line.startswith("SCORE:"):
            try:
                score = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()

    return {
        "method": "llm_judge",
        "score": score,
        "max_score": 5,
        "passed": score is not None and score >= PASS_THRESHOLD,
        "reason": reason,
    }


# ── 2. Exact / Keyword Match ──────────────────────────────────────────────────

def exact_match(question: str, expected: str, actual: str) -> dict:
    """
    Check whether key terms from the expected answer appear in the actual response.
    Scores 1.0 if ALL keywords found, partial credit for partial matches.
    """
    # Tokenise expected into meaningful keywords (words > 3 chars)
    keywords = [w.lower() for w in expected.split() if len(w) > 3]
    if not keywords:
        keywords = expected.lower().split()

    actual_lower = actual.lower()
    matched = [kw for kw in keywords if kw in actual_lower]

    ratio = len(matched) / len(keywords) if keywords else 0
    score = round(ratio, 2)

    return {
        "method": "exact_match",
        "score": score,
        "max_score": 1.0,
        "passed": score >= 0.6,
        "matched_keywords": matched,
        "total_keywords": keywords,
        "reason": f"{len(matched)}/{len(keywords)} keywords matched",
    }


# ── 3. Human Review ───────────────────────────────────────────────────────────

def human_review(question: str, expected: str, actual: str) -> dict:
    """Prompt the evaluator in the terminal to score the response manually."""
    print("\n" + "═" * 60)
    print(f"  QUESTION : {question}")
    print(f"  EXPECTED : {expected}")
    print(f"  ACTUAL   : {actual}")
    print("═" * 60)

    while True:
        raw = input("  Your score (1-5): ").strip()
        try:
            score = int(raw)
            if 1 <= score <= 5:
                break
            print("  ⚠  Please enter a number between 1 and 5.")
        except ValueError:
            print("  ⚠  Invalid input.")

    reason = input("  Optional note (press Enter to skip): ").strip()

    return {
        "method": "human",
        "score": score,
        "max_score": 5,
        "passed": score >= PASS_THRESHOLD,
        "reason": reason or "—",
    }


# ── Dispatcher ────────────────────────────────────────────────────────────────

SCORERS = {
    "llm_judge": llm_judge,
    "exact_match": exact_match,
    "human": human_review,
}


def score(method: str, question: str, expected: str, actual: str) -> dict:
    """Run the chosen scorer and return a result dict."""
    if method not in SCORERS:
        raise ValueError(f"Unknown scorer '{method}'. Choose from: {list(SCORERS)}")
    return SCORERS[method](question, expected, actual)
