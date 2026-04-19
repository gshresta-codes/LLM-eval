# ─────────────────────────────────────────────
#  report.py  –  CLI report generator
# ─────────────────────────────────────────────

import json
from pathlib import Path
from collections import defaultdict


def _bar(ratio: float, width: int = 20) -> str:
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)


def print_report(results: list[dict], scorer_name: str):
    if not results:
        print("No results to report.")
        return

    scored = [r for r in results if r["score_result"].get("score") is not None]
    passed = [r for r in scored if r["score_result"]["passed"]]
    pass_rate = len(passed) / len(results) if results else 0

    # ── Average score (normalised to 0–1) ────────────────────────────────────
    avg_norm = None
    if scored:
        norms = [
            r["score_result"]["score"] / r["score_result"]["max_score"]
            for r in scored
        ]
        avg_norm = sum(norms) / len(norms)

    # ── Avg latency ──────────────────────────────────────────────────────────
    latencies = [r["latency_ms"] for r in results if r.get("latency_ms")]
    avg_latency = round(sum(latencies) / len(latencies)) if latencies else None

    # ── Tag breakdown ─────────────────────────────────────────────────────────
    tag_stats: dict[str, dict] = defaultdict(lambda: {"total": 0, "passed": 0})
    for r in results:
        for tag in r.get("tags", []):
            tag_stats[tag]["total"] += 1
            if r["score_result"]["passed"]:
                tag_stats[tag]["passed"] += 1

    # ── Print ─────────────────────────────────────────────────────────────────
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║              📊  EVALUATION REPORT                    ║")
    print("╠════════════════════════════════════════════════════════╣")
    print(f"║  Scorer      : {scorer_name:<37}  ║")
    print(f"║  Total items : {len(results):<37} ║")
    print(f"║  Passed      : {len(passed)}/{len(results):<35}║")
    print(f"║  Pass rate   : {pass_rate * 100:>5.1f}%  {_bar(pass_rate):<28} ║")
    if avg_norm is not None:
        print(f"║  Avg score   : {avg_norm * 100:>5.1f}%  {_bar(avg_norm):<28}║")
    if avg_latency:
        print(f"║  Avg latency : {avg_latency} ms{'':<33}║")
    print("╠══════════════════════════════════════════════════════╣")

    if tag_stats:
        print("║  By tag:                                             ║")
        for tag, stat in sorted(tag_stats.items()):
            ratio = stat["passed"] / stat["total"]
            bar = _bar(ratio, width=12)
            line = f"  {tag:<14} {bar} {stat['passed']}/{stat['total']}"
            print(f"║  {line:<52}║")
        print("╠══════════════════════════════════════════════════════╣")

    print("║  Per-item results:                                   ║")
    for r in results:
        sr = r["score_result"]
        icon = "✅" if sr["passed"] else "❌"
        score_str = f"{sr['score']}/{sr['max_score']}" if sr.get("score") is not None else "ERR"
        label = f"{r['id']}  {icon}  {score_str}"
        reason = sr.get("reason", "")[:30]
        print(f"║    {label:<22}  {reason:<28}║")

    print("╚═══════════════════════════════════════════════════════════╝")
    print()


if __name__ == "__main__":
    # Allow running standalone: python report.py
    data = json.loads(Path("results.json").read_text())
    print_report(data["results"], data["scorer"])
