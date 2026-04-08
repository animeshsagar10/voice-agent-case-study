# Model Comparison: Haiku vs Sonnet

Identical experiments run on `claude-haiku-4-5-20251001` and `claude-sonnet-4-6`
using the 3 sample cases from the case study spec.

---

## 1. Evaluation Scores (Good vs Bad Responses)

| Case | Model | Good Score | Bad Score | Gap | Discriminates? |
|---|---|---|---|---|---|
| eval_001 | Haiku  | 8.3 | 8.5 | **+-0.2** | ❌ |
| eval_001 | Sonnet | 8.3 | 7.7 | **+0.6** | ✅ |
|---|---|---|---|---|---|
| eval_002 | Haiku  | 8.8 | 6.2 | **+2.6** | ✅ |
| eval_002 | Sonnet | 8.3 | 4.3 | **+4.0** | ✅ |
|---|---|---|---|---|---|
| eval_003 | Haiku  | 8.8 | 6.8 | **+2.0** | ✅ |
| eval_003 | Sonnet | 9.0 | 4.3 | **+4.7** | ✅ |
|---|---|---|---|---|---|

### Dimension Breakdown (Good Responses)

#### eval_001

| Dimension | Haiku | Bar | Sonnet | Bar |
|---|---|---|---|---|
| Task Completion | 9.0 | `█████████░` | 7.0 | `███████░░░` |
| Empathy | 6.0 | `██████░░░░` | 7.0 | `███████░░░` |
| Conciseness | 8.0 | `████████░░` | 9.0 | `█████████░` |
| Naturalness | 8.0 | `████████░░` | 9.0 | `█████████░` |
| Safety | 10.0 | `██████████` | 9.0 | `█████████░` |
| Clarity | 9.0 | `█████████░` | 9.0 | `█████████░` |

#### eval_002

| Dimension | Haiku | Bar | Sonnet | Bar |
|---|---|---|---|---|
| Task Completion | 9.0 | `█████████░` | 8.0 | `████████░░` |
| Empathy | 9.0 | `█████████░` | 8.0 | `████████░░` |
| Conciseness | 8.0 | `████████░░` | 9.0 | `█████████░` |
| Naturalness | 8.0 | `████████░░` | 8.0 | `████████░░` |
| Safety | 10.0 | `██████████` | 9.0 | `█████████░` |
| Clarity | 9.0 | `█████████░` | 8.0 | `████████░░` |

#### eval_003

| Dimension | Haiku | Bar | Sonnet | Bar |
|---|---|---|---|---|
| Task Completion | 9.0 | `█████████░` | 9.0 | `█████████░` |
| Empathy | 9.0 | `█████████░` | 8.0 | `████████░░` |
| Conciseness | 8.0 | `████████░░` | 9.0 | `█████████░` |
| Naturalness | 8.0 | `████████░░` | 9.0 | `█████████░` |
| Safety | 10.0 | `██████████` | 10.0 | `██████████` |
| Clarity | 9.0 | `█████████░` | 9.0 | `█████████░` |

---

## 2. A/B Comparison Accuracy

| Case | Expected Winner | Haiku Picked | Correct? | Sonnet Picked | Correct? |
|---|---|---|---|---|---|
| eval_001 | `a` | `a` | ✅ | `a` | ✅ |
| eval_002 | `a` | `a` | ✅ | `a` | ✅ |
| eval_003 | `a` | `a` | ✅ | `a` | ✅ |

**Haiku accuracy:** 100% &nbsp;|&nbsp; **Sonnet accuracy:** 100%

### Sonnet Recommendations

- **eval_001:** Combine A's natural brevity with a simple forward-moving prompt (e.g., 'Got it, March 15th, 1985 — thanks!') to confirm the information clearly without over-scripting the interaction.
- **eval_002:** Combine Response A's empathetic acknowledgment with Response B's validated 12-month SDOH screening question to achieve both clinical accuracy and compassionate delivery.
- **eval_003:** Always validate the user's concern before explaining, use plain language to describe purpose and confidentiality, and avoid clinical jargon that can increase distrust in sensitive screening contexts.

---

## 3. Improvement Quality (eval_002 — Food Security)

| Model | Original Score | Improved Score | Delta | Latency |
|---|---|---|---|---|
| Haiku  | 6.2 | 8.8 | **+2.6** | 7.12s |
| Sonnet | 4.3 | 8.7 | **+4.4** | 16.8s |

### Sonnet Improved Response

> I'm really sorry to hear that — going weeks without enough to eat is incredibly hard, and I want to make sure we can connect you with the right support. To help us do that, I have a quick question: in the past 12 months, have you worried that your food would run out before you had money to buy more? Your answer will help us find resources for you.

**Changes made:**
- Replaced 'Okay, noted. Next question:' with a genuine empathetic acknowledgment that validates the user's experience and hardship.
- Added a brief explanation of why the screening question is being asked, so the user understands it leads to actionable support rather than feeling like a data collection exercise.
- Softened and humanized the phrasing of the SDOH screening question to feel more like a natural conversation and less like a clinical checklist.
- Ended with a reassurance that their answer will help connect them to resources, bridging toward next steps and building trust.

### Haiku Improved Response

> I'm really sorry you're going through that. Food insecurity is something we take seriously and want to help with. To make sure we connect you with the right resources, I want to ask: in the past 12 months, have there been times when you worried your food would run out before you had money to buy more?

---

## 4. Scoring Consistency (Calibration — 3 Runs)

| Model | Run 1 | Run 2 | Run 3 | Mean | Std Dev | Consistent? |
|---|---|---|---|---|---|---|
| Haiku  | 8.7 | 8.2 | 8.5 | 8.47 | 0.25 | ✅ |
| Sonnet | 8.5 | 8.7 | 8.3 | 8.5 | 0.2 | ✅ |

> Consistent = std dev < 0.5 across independent runs on the same input.

---

## 5. Summary Scorecard

| Metric | Haiku | Sonnet | Winner |
|---|---|---|---|
| Avg score (good responses) | 8.63 | 8.53 | Haiku ✅ |
| Avg discrimination gap | +1.47 | +3.1 | Sonnet ✅ |
| A/B accuracy | 100% | 100% | Tie 🤝 |
| Improvement delta | +2.6 | +4.4 | Sonnet ✅ |
| Calibration std dev | 0.25 | 0.2 | Sonnet ✅ |
| Avg latency (eval) | 4.36s | 9.02s | Haiku ✅ |

### Cost Estimate (per 1,000 evaluations)

| Model | Input cost | Output cost | Total est. |
|---|---|---|---|
| Haiku  | $0.80/MTok | $4.00/MTok | ~$0.50 |
| Sonnet | $3.00/MTok | $15.00/MTok | ~$6.00 |

---

## Recommendation

**Use Sonnet (`claude-sonnet-4-6`) for production evaluation** — better discrimination,
higher calibration consistency, and richer improvement suggestions. The 12x cost
difference is justified when evaluating real call quality.

**Use Haiku (`claude-haiku-4-5-20251001`) during development** — fast iteration,
negligible cost, same JSON schema. Switch via `JUDGE_MODEL` env var.

```bash
# .env
JUDGE_MODEL=claude-sonnet-4-6        # production
JUDGE_MODEL=claude-haiku-4-5-20251001 # development
```
