"""
Opus-only benchmark run. Outputs raw results for appending to EVAL_COMPARISON.md.
Usage: uv run python benchmark_opus.py
"""

import json
import os
import time

os.environ["JUDGE_MODEL"] = "claude-opus-4-6"

from dotenv import load_dotenv
load_dotenv()

import importlib
import judge as judge_module
importlib.reload(judge_module)
judge_module._cache.clear()
judge_module.MODEL = "claude-opus-4-6"

from models import EvaluationContext
from sample_data import SAMPLE_CASES

results = {}

# ── Evaluate good vs bad ─────────────────────────────────────────────────────
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
    print(f"{case['id']}: good={good.overall_score} bad={bad.overall_score} gap={round(good.overall_score - bad.overall_score, 1)}")

results["evals"] = eval_results

# ── Compare ──────────────────────────────────────────────────────────────────
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
    print(f"{case['id']} compare: winner={comp.winner} correct={comp.winner == case['expected_winner']}")

results["compares"] = compare_results

# ── Improve (eval_002) ───────────────────────────────────────────────────────
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
print(f"improve: {improvement.original_score} → {improvement.improved_score} (+{round(improvement.improved_score - improvement.original_score,1)})")

# ── Calibration (eval_001 good) ──────────────────────────────────────────────
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
print(f"calibration: {cal.scores} mean={cal.mean} std_dev={cal.std_dev}")

print("\n── FULL RESULTS ──")
print(json.dumps(results, indent=2))
