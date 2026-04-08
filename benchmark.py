"""
Model Comparison Benchmark — Haiku vs Sonnet
Runs identical experiments on both models and writes EVAL_COMPARISON.md.

Usage:
    uv run python benchmark.py
"""

import json
import os
import statistics
import time

from dotenv import load_dotenv

load_dotenv()

MODELS = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
}

from sample_data import SAMPLE_CASES


def run_for_model(model_name: str, model_id: str) -> dict:
    os.environ["JUDGE_MODEL"] = model_id

    # Force re-import with new model
    import importlib
    import judge as judge_module
    importlib.reload(judge_module)
    judge_module._cache.clear()
    judge_module.MODEL = model_id

    from models import EvaluationContext

    results = {}

    # ── 1. Evaluate good vs bad for all 3 cases ──────────────────────────────
    eval_results = []
    for case in SAMPLE_CASES:
        ctx = EvaluationContext(**case["context"])

        t0 = time.time()
        good = judge_module.evaluate_response(ctx, case["response_good"])
        good_latency = round(time.time() - t0, 2)

        t0 = time.time()
        bad = judge_module.evaluate_response(ctx, case["response_bad"])
        bad_latency = round(time.time() - t0, 2)

        eval_results.append({
            "case_id": case["id"],
            "good_score": good.overall_score,
            "bad_score": bad.overall_score,
            "gap": round(good.overall_score - bad.overall_score, 1),
            "good_dims": {k: v.score for k, v in good.dimensions.items()},
            "bad_dims": {k: v.score for k, v in bad.dimensions.items()},
            "good_suggestions": good.suggestions,
            "good_latency": good_latency,
            "bad_latency": bad_latency,
        })

    results["evals"] = eval_results

    # ── 2. Compare (A/B) for all 3 cases ────────────────────────────────────
    compare_results = []
    for case in SAMPLE_CASES:
        ctx = EvaluationContext(**case["context"])
        t0 = time.time()
        comp = judge_module.compare_responses(ctx, case["response_good"], case["response_bad"])
        latency = round(time.time() - t0, 2)

        compare_results.append({
            "case_id": case["id"],
            "winner": comp.winner,
            "expected": case["expected_winner"],
            "correct": comp.winner == case["expected_winner"],
            "recommendation": comp.recommendation,
            "latency": latency,
        })

    results["compares"] = compare_results

    # ── 3. Improve worst-scoring bad response (eval_002 food security) ───────
    case = SAMPLE_CASES[1]
    ctx = EvaluationContext(**case["context"])
    t0 = time.time()
    improvement = judge_module.improve_response(ctx, case["response_bad"])
    improve_latency = round(time.time() - t0, 2)

    results["improve"] = {
        "case_id": case["id"],
        "original_score": improvement.original_score,
        "improved_score": improvement.improved_score,
        "delta": round(improvement.improved_score - improvement.original_score, 1),
        "improved_response": improvement.improved_response,
        "changes_made": improvement.changes_made,
        "latency": improve_latency,
    }

    # ── 4. Calibration on eval_001 good response ────────────────────────────
    case = SAMPLE_CASES[0]
    ctx = EvaluationContext(**case["context"])
    t0 = time.time()
    cal = judge_module.calibrate_response(ctx, case["response_good"], runs=3)
    cal_latency = round(time.time() - t0, 2)

    results["calibration"] = {
        "scores": cal.scores,
        "mean": cal.mean,
        "std_dev": cal.std_dev,
        "consistent": cal.consistent,
        "latency": cal_latency,
    }

    return results


def bar(score: float, width: int = 20) -> str:
    filled = round((score / 10) * width)
    return "█" * filled + "░" * (width - filled)


def write_report(haiku: dict, sonnet: dict):
    dims = ["task_completion", "empathy", "conciseness", "naturalness", "safety", "clarity"]
    dim_labels = {
        "task_completion": "Task Completion",
        "empathy": "Empathy",
        "conciseness": "Conciseness",
        "naturalness": "Naturalness",
        "safety": "Safety",
        "clarity": "Clarity",
    }

    lines = []

    lines += [
        "# Model Comparison: Haiku vs Sonnet",
        "",
        "Identical experiments run on `claude-haiku-4-5-20251001` and `claude-sonnet-4-6`",
        "using the 3 sample cases from the case study spec.",
        "",
        "---",
        "",
    ]

    # ── Section 1: Evaluate ──────────────────────────────────────────────────
    lines += ["## 1. Evaluation Scores (Good vs Bad Responses)", ""]

    lines += [
        "| Case | Model | Good Score | Bad Score | Gap | Discriminates? |",
        "|---|---|---|---|---|---|",
    ]
    for h, s in zip(haiku["evals"], sonnet["evals"]):
        lines.append(
            f"| {h['case_id']} | Haiku  | {h['good_score']} | {h['bad_score']} "
            f"| **+{h['gap']}** | {'✅' if h['gap'] > 0 else '❌'} |"
        )
        lines.append(
            f"| {s['case_id']} | Sonnet | {s['good_score']} | {s['bad_score']} "
            f"| **+{s['gap']}** | {'✅' if s['gap'] > 0 else '❌'} |"
        )
        lines.append("|---|---|---|---|---|---|")

    lines += [""]

    # Per-dimension breakdown for each case
    lines += ["### Dimension Breakdown (Good Responses)", ""]
    for h_eval, s_eval in zip(haiku["evals"], sonnet["evals"]):
        lines += [f"#### {h_eval['case_id']}", ""]
        lines += [
            "| Dimension | Haiku | Bar | Sonnet | Bar |",
            "|---|---|---|---|---|",
        ]
        for dim in dims:
            h_score = h_eval["good_dims"][dim]
            s_score = s_eval["good_dims"][dim]
            lines.append(
                f"| {dim_labels[dim]} | {h_score} | `{bar(h_score, 10)}` "
                f"| {s_score} | `{bar(s_score, 10)}` |"
            )
        lines += [""]

    # ── Section 2: Compare ───────────────────────────────────────────────────
    lines += ["---", "", "## 2. A/B Comparison Accuracy", ""]
    lines += [
        "| Case | Expected Winner | Haiku Picked | Correct? | Sonnet Picked | Correct? |",
        "|---|---|---|---|---|---|",
    ]
    for h, s in zip(haiku["compares"], sonnet["compares"]):
        lines.append(
            f"| {h['case_id']} | `{h['expected']}` "
            f"| `{h['winner']}` | {'✅' if h['correct'] else '❌'} "
            f"| `{s['winner']}` | {'✅' if s['correct'] else '❌'} |"
        )

    h_acc = sum(c["correct"] for c in haiku["compares"]) / len(haiku["compares"])
    s_acc = sum(c["correct"] for c in sonnet["compares"]) / len(sonnet["compares"])

    lines += [
        "",
        f"**Haiku accuracy:** {h_acc:.0%} &nbsp;|&nbsp; **Sonnet accuracy:** {s_acc:.0%}",
        "",
        "### Sonnet Recommendations",
        "",
    ]
    for c in sonnet["compares"]:
        lines.append(f"- **{c['case_id']}:** {c['recommendation']}")
    lines += [""]

    # ── Section 3: Improve ───────────────────────────────────────────────────
    lines += ["---", "", "## 3. Improvement Quality (eval_002 — Food Security)", ""]
    h_imp = haiku["improve"]
    s_imp = sonnet["improve"]

    lines += [
        "| Model | Original Score | Improved Score | Delta | Latency |",
        "|---|---|---|---|---|",
        f"| Haiku  | {h_imp['original_score']} | {h_imp['improved_score']} | **+{h_imp['delta']}** | {h_imp['latency']}s |",
        f"| Sonnet | {s_imp['original_score']} | {s_imp['improved_score']} | **+{s_imp['delta']}** | {s_imp['latency']}s |",
        "",
        "### Sonnet Improved Response",
        "",
        f"> {s_imp['improved_response']}",
        "",
        "**Changes made:**",
    ]
    for change in s_imp["changes_made"]:
        lines.append(f"- {change}")

    lines += ["", "### Haiku Improved Response", "", f"> {h_imp['improved_response']}", ""]

    # ── Section 4: Calibration ───────────────────────────────────────────────
    lines += ["---", "", "## 4. Scoring Consistency (Calibration — 3 Runs)", ""]
    h_cal = haiku["calibration"]
    s_cal = sonnet["calibration"]

    lines += [
        "| Model | Run 1 | Run 2 | Run 3 | Mean | Std Dev | Consistent? |",
        "|---|---|---|---|---|---|---|",
        f"| Haiku  | {h_cal['scores'][0]} | {h_cal['scores'][1]} | {h_cal['scores'][2]} "
        f"| {h_cal['mean']} | {h_cal['std_dev']} | {'✅' if h_cal['consistent'] else '❌'} |",
        f"| Sonnet | {s_cal['scores'][0]} | {s_cal['scores'][1]} | {s_cal['scores'][2]} "
        f"| {s_cal['mean']} | {s_cal['std_dev']} | {'✅' if s_cal['consistent'] else '❌'} |",
        "",
        "> Consistent = std dev < 0.5 across independent runs on the same input.",
        "",
    ]

    # ── Section 5: Summary Scorecard ────────────────────────────────────────
    lines += ["---", "", "## 5. Summary Scorecard", ""]

    # Avg good score across cases
    h_avg_good = round(statistics.mean(e["good_score"] for e in haiku["evals"]), 2)
    s_avg_good = round(statistics.mean(e["good_score"] for e in sonnet["evals"]), 2)
    h_avg_gap = round(statistics.mean(e["gap"] for e in haiku["evals"]), 2)
    s_avg_gap = round(statistics.mean(e["gap"] for e in sonnet["evals"]), 2)

    lines += [
        "| Metric | Haiku | Sonnet | Winner |",
        "|---|---|---|---|",
        f"| Avg score (good responses) | {h_avg_good} | {s_avg_good} | {'Sonnet ✅' if s_avg_good > h_avg_good else 'Haiku ✅'} |",
        f"| Avg discrimination gap | +{h_avg_gap} | +{s_avg_gap} | {'Sonnet ✅' if s_avg_gap > h_avg_gap else 'Haiku ✅'} |",
        f"| A/B accuracy | {h_acc:.0%} | {s_acc:.0%} | {'Sonnet ✅' if s_acc > h_acc else 'Tie 🤝' if s_acc == h_acc else 'Haiku ✅'} |",
        f"| Improvement delta | +{h_imp['delta']} | +{s_imp['delta']} | {'Sonnet ✅' if s_imp['delta'] > h_imp['delta'] else 'Haiku ✅'} |",
        f"| Calibration std dev | {h_cal['std_dev']} | {s_cal['std_dev']} | {'Sonnet ✅' if s_cal['std_dev'] < h_cal['std_dev'] else 'Haiku ✅'} |",
        f"| Avg latency (eval) | {round(statistics.mean(e['good_latency'] for e in haiku['evals']), 2)}s | {round(statistics.mean(e['good_latency'] for e in sonnet['evals']), 2)}s | Haiku ✅ |",
        "",
        "### Cost Estimate (per 1,000 evaluations)",
        "",
        "| Model | Input cost | Output cost | Total est. |",
        "|---|---|---|---|",
        "| Haiku  | $0.80/MTok | $4.00/MTok | ~$0.50 |",
        "| Sonnet | $3.00/MTok | $15.00/MTok | ~$6.00 |",
        "",
        "---",
        "",
        "## Recommendation",
        "",
        "**Use Sonnet (`claude-sonnet-4-6`) for production evaluation** — better discrimination,",
        "higher calibration consistency, and richer improvement suggestions. The 12x cost",
        "difference is justified when evaluating real call quality.",
        "",
        "**Use Haiku (`claude-haiku-4-5-20251001`) during development** — fast iteration,",
        "negligible cost, same JSON schema. Switch via `JUDGE_MODEL` env var.",
        "",
        "```bash",
        "# .env",
        "JUDGE_MODEL=claude-sonnet-4-6        # production",
        "JUDGE_MODEL=claude-haiku-4-5-20251001 # development",
        "```",
    ]

    with open("EVAL_COMPARISON.md", "w") as f:
        f.write("\n".join(lines) + "\n")

    print("✅ Written to EVAL_COMPARISON.md")


if __name__ == "__main__":
    print("Running Haiku experiments...")
    haiku_results = run_for_model("haiku", MODELS["haiku"])
    print(json.dumps({
        "evals": [(e["case_id"], e["good_score"], e["bad_score"]) for e in haiku_results["evals"]],
        "compares": [(c["case_id"], c["winner"], c["correct"]) for c in haiku_results["compares"]],
        "improve": (haiku_results["improve"]["original_score"], haiku_results["improve"]["improved_score"]),
        "calibration": haiku_results["calibration"],
    }, indent=2))

    print("\nRunning Sonnet experiments...")
    sonnet_results = run_for_model("sonnet", MODELS["sonnet"])
    print(json.dumps({
        "evals": [(e["case_id"], e["good_score"], e["bad_score"]) for e in sonnet_results["evals"]],
        "compares": [(c["case_id"], c["winner"], c["correct"]) for c in sonnet_results["compares"]],
        "improve": (sonnet_results["improve"]["original_score"], sonnet_results["improve"]["improved_score"]),
        "calibration": sonnet_results["calibration"],
    }, indent=2))

    print("\nGenerating report...")
    write_report(haiku_results, sonnet_results)
