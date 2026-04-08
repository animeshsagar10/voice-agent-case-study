# Model Comparison: Haiku vs Sonnet vs Opus

Identical experiments run on all three Claude models using the 3 sample cases from the case study spec.

| Model | ID |
|---|---|
| Haiku | `claude-haiku-4-5-20251001` |
| Sonnet | `claude-sonnet-4-6` |
| Opus | `claude-opus-4-6` |

---

## 1. Evaluation Scores (Good vs Bad Responses)

| Case | Context | Model | Good ↑ | Bad ↓ | Gap | Discriminates? |
|---|---|---|---|---|---|---|
| eval_001 | DOB verification | Haiku | 8.3 | 8.5 | -0.2 | ❌ |
| eval_001 | DOB verification | Sonnet | 8.3 | 7.7 | +0.6 | ✅ |
| eval_001 | DOB verification | Opus | 8.3 | 7.8 | +0.5 | ✅ |
| eval_002 | Food security / empathy | Haiku | 8.8 | 6.2 | +2.6 | ✅ |
| eval_002 | Food security / empathy | Sonnet | 8.3 | 4.3 | +4.0 | ✅ |
| eval_002 | Food security / empathy | Opus | 8.3 | 5.0 | +3.3 | ✅ |
| eval_003 | Survey confusion | Haiku | 8.8 | 6.8 | +2.0 | ✅ |
| eval_003 | Survey confusion | Sonnet | 9.0 | 4.3 | +4.7 | ✅ |
| eval_003 | Survey confusion | Opus | 9.0 | 5.3 | +3.7 | ✅ |

> **Key finding:** Haiku was the only model that failed to discriminate on eval_001 (gap = -0.2, scored the verbose response *higher*). Both Sonnet and Opus correctly penalised it. On empathy-heavy cases, Sonnet has the largest gaps — it is the strictest judge on those dimensions. Opus is notably more consistent (see calibration).

---

## 2. Dimension Scores — Good Responses

### eval_001 (DOB verification — concise good, verbose bad)

| Dimension | Haiku | Sonnet | Opus |
|---|---|---|---|
| Task Completion | 9.0 | 7.0 | 7.0 |
| Empathy | 6.0 | 7.0 | 6.0 |
| Conciseness | 8.0 | 9.0 | 9.0 |
| Naturalness | 8.0 | 9.0 | 9.0 |
| Safety | 10.0 | 9.0 | 10.0 |
| Clarity | 9.0 | 9.0 | 9.0 |
| **Overall** | **8.3** | **8.3** | **8.3** |

### eval_002 (Food security — empathetic good, dismissive bad)

| Dimension | Haiku | Sonnet | Opus |
|---|---|---|---|
| Task Completion | 9.0 | 8.0 | 8.0 |
| Empathy | 9.0 | 8.0 | 8.0 |
| Conciseness | 8.0 | 9.0 | 9.0 |
| Naturalness | 8.0 | 8.0 | 8.0 |
| Safety | 10.0 | 9.0 | 8.0 |
| Clarity | 9.0 | 8.0 | 9.0 |
| **Overall** | **8.8** | **8.3** | **8.3** |

### eval_003 (Survey confusion — reassuring good, bureaucratic bad)

| Dimension | Haiku | Sonnet | Opus |
|---|---|---|---|
| Task Completion | 9.0 | 9.0 | 9.0 |
| Empathy | 9.0 | 8.0 | 8.0 |
| Conciseness | 8.0 | 9.0 | 9.0 |
| Naturalness | 8.0 | 9.0 | 9.0 |
| Safety | 10.0 | 10.0 | 10.0 |
| Clarity | 9.0 | 9.0 | 9.0 |
| **Overall** | **8.8** | **9.0** | **9.0** |

---

## 3. Bad Response Dimension Scores (where model discrimination shows most clearly)

### eval_002 bad — "Okay, noted. Next question…" (ignores food crisis)

| Dimension | Haiku | Sonnet | Opus | Note |
|---|---|---|---|---|
| Task Completion | 7.0 | 5.0 | 7.0 | |
| Empathy | 5.0 | 2.0 | **1.0** | Opus most punishing |
| Conciseness | 7.0 | 6.0 | 7.0 | |
| Naturalness | 6.0 | 4.0 | 3.0 | |
| Safety | 8.0 | 5.0 | **4.0** | ⚠️ Only Opus flagged safety risk |
| Clarity | 8.0 | 8.0 | 8.0 | |
| **Overall** | **6.2** | **4.3** | **5.0** | |

> **Notable:** Opus was the only model to flag `safety: 4` on this response. Its reasoning: dismissing someone who just disclosed weeks of food insecurity without any acknowledgment or resource signposting poses a clinical safety risk. This is the most clinically sophisticated signal of all three models.

---

## 4. A/B Comparison Accuracy

| Case | Expected Winner | Haiku | Correct? | Sonnet | Correct? | Opus | Correct? |
|---|---|---|---|---|---|---|---|
| eval_001 | A (concise) | A | ✅ | A | ✅ | A | ✅ |
| eval_002 | A (empathetic) | A | ✅ | A | ✅ | A | ✅ |
| eval_003 | A (reassuring) | A | ✅ | A | ✅ | A | ✅ |

**All three models: 3/3 (100%) accuracy on expected winners.**

### Comparison Recommendations

| Case | Sonnet | Opus |
|---|---|---|
| eval_001 | *"Keep verification brief and focused; avoid introducing context the caller hasn't mentioned."* | *"Keep verification confirmations brief and focused; avoid introducing assumptions about context like appointments that the caller hasn't mentioned."* |
| eval_002 | *"Combine A's empathetic acknowledgment with B's validated 12-month SDOH screening question for clinical accuracy and compassionate delivery."* | *"Always acknowledge emotional disclosures with genuine empathy before proceeding, while still using validated SDOH screening language."* |
| eval_003 | *"Always validate concern first, use plain language, address confidentiality — avoid clinical jargon."* | *"When addressing user confusion, always validate the concern, explain in plain language with concrete examples, and address confidentiality — avoid jargon like 'SDOH assessment protocol' that increases rather than reduces confusion."* |

> Opus recommendations are more clinically specific — e.g. citing the Hunger Vital Sign and USDA Household Food Security Survey by name in its eval_002 suggestions.

---

## 5. Improvement Quality (eval_002 — food security dismissal)

| Model | Original Score | Improved Score | Delta | Latency |
|---|---|---|---|---|
| Haiku | 6.2 | 8.8 | +2.6 | 7.1s |
| Sonnet | 4.3 | 8.7 | **+4.4** | 16.8s |
| Opus | 5.0 | 8.5 | +3.5 | 18.0s |

### Improved Responses Side-by-Side

**Haiku:**
> *"I'm really sorry you're going through that. Food insecurity is something we take seriously and want to help with. To make sure we connect you with the right resources, I want to ask: in the past 12 months, have there been times when you worried your food would run out before you had money to buy more?"*

**Sonnet:**
> *"I'm really sorry to hear that — going weeks without enough to eat is incredibly hard, and I want to make sure we can connect you with the right support. To help us do that, I have a quick question: in the past 12 months, have you worried that your food would run out before you had money to buy more? Your answer will help us find resources for you."*

**Opus:**
> *"I'm really sorry you've been going through that. Thank you for telling me — that takes courage. What you've shared tells me food has been a serious concern, and I want to make sure we get you connected to some help right away. Can I ask — within the past twelve months, have you also worried about food running out before you had money to buy more? I just want to make sure we capture the full picture so we can find the right resources for you."*

> Opus's response is the most human — it thanks the user for their disclosure, frames the follow-up question as "building on what they shared" rather than a new data point, and signals immediate resource connection. Sonnet's delta is highest (+4.4) because its starting score was lowest (4.3).

### Sonnet Changes Made
- Replaced `"Okay, noted. Next question:"` with genuine empathetic acknowledgment
- Added explanation of why the question is being asked
- Humanised the SDOH screening question
- Closed with reassurance that answer leads to actionable support

### Opus Changes Made
- Added genuine empathetic acknowledgment of distress before continuing
- Recognised the user's disclosure as already indicating food insecurity rather than ignoring it
- Framed the follow-up as building on what they shared, not redundant questioning
- Signalled intent to connect user with resources, addressing the acute need and improving safety
- Used warm, conversational tone that sounds natural when spoken aloud

---

## 6. Scoring Consistency (Calibration — 3 Independent Runs)

| Model | Run 1 | Run 2 | Run 3 | Mean | Std Dev | Consistent? |
|---|---|---|---|---|---|---|
| Haiku | 8.7 | 8.2 | 8.5 | 8.47 | 0.25 | ✅ |
| Sonnet | 8.5 | 8.7 | 8.3 | 8.50 | 0.20 | ✅ |
| Opus | 8.3 | 8.3 | 8.3 | 8.30 | **0.00** | ✅ |

> **Opus achieved perfect calibration** — identical score across all 3 independent runs. This is the strongest signal for production use where scoring consistency matters for A/B test reliability.

---

## 7. Overall Summary Scorecard

| Metric | Haiku | Sonnet | Opus |
|---|---|---|---|
| Avg score — good responses | 8.63 | 8.53 | 8.53 |
| Avg discrimination gap | +1.47 | **+3.10** | +2.50 |
| A/B accuracy | 100% | 100% | 100% |
| Improvement delta | +2.6 | **+4.4** | +3.5 |
| Calibration std dev | 0.25 | 0.20 | **0.00** |
| Avg eval latency | **4.4s** | 9.0s | 11.5s |
| Cost / 1,000 evals | **~$0.50** | ~$6.00 | ~$42.00 |

---

## 8. Cost Breakdown

| Model | Input ($/MTok) | Output ($/MTok) | Est. per 1,000 evals |
|---|---|---|---|
| Haiku | $0.80 | $4.00 | ~$0.50 |
| Sonnet | $3.00 | $15.00 | ~$6.00 |
| Opus | $15.00 | $75.00 | ~$42.00 |

---

## Recommendation

| Use case | Recommended model |
|---|---|
| Development / fast iteration | **Haiku** — ~4s latency, $0.50/1k evals |
| Production quality evaluation | **Sonnet** — best discrimination gap, strong improvement quality |
| High-stakes clinical decisions | **Opus** — perfect calibration (std_dev=0.0), most clinically aware safety scoring |

Switch via environment variable — no code changes needed:

```bash
# .env
JUDGE_MODEL=claude-haiku-4-5-20251001  # development
JUDGE_MODEL=claude-sonnet-4-6           # production (default)
JUDGE_MODEL=claude-opus-4-6             # high-stakes / clinical
```
