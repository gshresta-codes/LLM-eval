#!/usr/bin/env python3
# ─────────────────────────────────────────────
#  eval_runner.py  –  Main evaluation runner
# ─────────────────────────────────────────────
#
#  Usage:
#    python eval_runner.py                        # use defaults from config.py
#    python eval_runner.py --scorer llm_judge
#    python eval_runner.py --scorer exact_match
#    python eval_runner.py --scorer human
#    python eval_runner.py --tags python          # filter by tag
#    python eval_runner.py --ids q001 q003        # run specific questions
#
# ─────────────────────────────────────────────

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import anthropic

import config
import scorers
from report import print_report

client = anthropic.Anthropic()


def load_dataset(path: str, tags: list[str] | None, ids: list[str] | None) -> list[dict]:
    data = json.loads(Path(path).read_text())
    if tags:
        data = [item for item in data if any(t in item.get("tags", []) for t in tags)]
    if ids:
        data = [item for item in data if item["id"] in ids]
    return data


def query_model(question: str) -> tuple[str, float]:
    """Send a question to the target model and return (answer, latency_ms)."""
    t0 = time.perf_counter()
    response = client.messages.create(
        model=config.TARGET_MODEL,
        max_tokens=config.MAX_TOKENS,
        system=config.SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    latency_ms = round((time.perf_counter() - t0) * 1000)
    answer = response.content[0].text.strip()
    return answer, latency_ms


def run_eval(scorer_name: str, tags: list[str] | None, ids: list[str] | None):
    dataset = load_dataset(config.DATASET_PATH, tags, ids)
    if not dataset:
        print("⚠  No items matched your filters. Check --tags or --ids.")
        return

    print(f"\n🔍  LLM Evaluation Run")
    print(f"    Model   : {config.TARGET_MODEL}")
    print(f"    Scorer  : {scorer_name}")
    print(f"    Items   : {len(dataset)}")
    print(f"    Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("─" * 55)

    results = []

    for i, item in enumerate(dataset, 1):
        qid = item["id"]
        question = item["input"]
        expected = item["expected"]

        print(f"\n[{i}/{len(dataset)}] {qid}: {question[:60]}{'…' if len(question) > 60 else ''}")

        # Get model response
        try:
            actual, latency_ms = query_model(question)
            print(f"  ↳ Response ({latency_ms}ms): {actual[:80]}{'…' if len(actual) > 80 else ''}")
        except Exception as e:
            print(f"  ✗ Model error: {e}")
            results.append({**item, "actual": None, "latency_ms": None,
                            "score_result": {"method": scorer_name, "score": None, "passed": False,
                                             "reason": str(e)}})
            continue

        # Score the response
        try:
            score_result = scorers.score(scorer_name, question, expected, actual)
            passed = "✅" if score_result["passed"] else "❌"
            print(f"  {passed} Score: {score_result['score']}/{score_result['max_score']}  |  {score_result['reason']}")
        except Exception as e:
            print(f"  ⚠  Scorer error: {e}")
            score_result = {"method": scorer_name, "score": None, "passed": False, "reason": str(e)}

        results.append({
            "id": qid,
            "input": question,
            "expected": expected,
            "actual": actual,
            "latency_ms": latency_ms,
            "tags": item.get("tags", []),
            "score_result": score_result,
        })

    # Save results
    out = {
        "run_at": datetime.now().isoformat(),
        "model": config.TARGET_MODEL,
        "scorer": scorer_name,
        "total": len(results),
        "results": results,
    }
    Path(config.RESULTS_PATH).write_text(json.dumps(out, indent=2))
    print(f"\n💾  Results saved to {config.RESULTS_PATH}")

    print_report(results, scorer_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LLM evaluations for Q&A / Chatbot tasks.")
    parser.add_argument("--scorer", default=config.DEFAULT_SCORER,
                        choices=["llm_judge", "exact_match", "human"],
                        help="Scoring method to use (default: from config.py)")
    parser.add_argument("--tags", nargs="*", help="Filter dataset by tag(s)")
    parser.add_argument("--ids", nargs="*", help="Run only specific item IDs")
    args = parser.parse_args()

    run_eval(args.scorer, args.tags, args.ids)
