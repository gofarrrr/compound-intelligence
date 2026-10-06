# Exploratory review results — 2026-10-02

**All 16 live requests succeeded; the current assertion cutoff disagreed with eight of nine AI-negative labels.** This was a comparison with provisional AI-authored expectations, not an independent human evaluation. No questions or thresholds were changed.

The [original result file](review-diagnostics-2026-10-02.json) preserves the synthetic cases, numbered drafts, sentence-level reviewer labels and rationales, complete provider answers, model/usage/transport metadata, and contract digests. It was copied byte-for-byte from the user-side run after local checks of the case, label, source-registry, outbound-packet, question and policy bindings, typed answers, and computed decisions. No credentials or personal cases are included.

## Run and scope

- Model: `jev-1.13.0`; questions: `ci.postflight.v2.0.0`; policy: `ci.policy.v2.0.0`.
- Reviewer: Codex, explicitly `reviewer_kind=ai`, also the author of this synthetic corpus. Labels preceded this batch's Jev outputs but are not independent gold labels.
- All 16 requests completed on one transport attempt each. Reported usage: **33,439 input tokens; 2,384 output tokens**. Monetary cost was not measured.
- Client elapsed time: **369.66–577.90 ms**, median **403.535 ms**. These are observations from this run, not a latency benchmark.
- The harness evaluated all eight existing postflight questions once per draft. It did not run preflight routing, generate new coaching text, revise drafts, fit cutoffs, or measure coaching outcomes.

## Unsupported assertions

| AI assertion label | Cases | Returned P(unsupported) | Cases flagged at the unchanged > 0.25 rule |
| --- | ---: | --- | ---: |
| Present | 7 | 0.84–0.95 | 7 |
| Absent | 9 | 0.25–0.56 | 8 |

These counts describe agreement with this reviewer on these authored examples. They are not estimates of deployment accuracy or calibration.

| Case | Scenario | AI unsupported label | Jev P(unsupported) | AI framework level | Jev framework Score | Framework confidence |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| ua-001 | Grounded observations | false | 0.27 | 0 | 0.31 | 0.54 |
| ua-002 | Causal leap | true | 0.95 | 0 | 0.44 | 0.34 |
| ua-003 | Inferred motive | true | 0.93 | 0 | 0.48 | 0.28 |
| ua-004 | Marked hypothesis | false | 0.30 | 0 | 0.22 | 0.67 |
| ua-005 | Unsupported chapter claim | true | 0.87 | 1 | 0.88 | 0.46 |
| ua-006 | Stable trait | true | 0.94 | 0 | 0.39 | 0.41 |
| ua-007 | Unestablished authority | true | 0.95 | 0 | 0.51 | 0.23 |
| ua-008 | Strong supported statement | false | 0.28 | 0 | 0.29 | 0.57 |
| ua-009 | Factual count error | true | 0.84 | 0 | 0.49 | 0.27 |
| ua-010 | Grounded framework overload | false | 0.56 | 2 | 1.99 | 0.99 |
| ua-011 | No Webb fit; literal conversion | false | 0.45 | 0 | 0.09 | 0.87 |
| ua-012 | Two justified methods | false | 0.27 | 0 | 1.36 | 0.33 |
| ua-013 | Overgeneralized pattern | true | 0.94 | 0 | 0.45 | 0.33 |
| ua-014 | Attributed causal evidence | false | 0.26 | 0 | 0.33 | 0.50 |
| ua-015 | Grounded book terminology | false | 0.31 | 0 | 0.63 | 0.05 |
| ua-016 | Marked factual uncertainty | false | 0.25 | 0 | 0.24 | 0.64 |

The assertion signal responded strongly to the deliberate cause, motive, trait, authority, chapter and count errors. Its values were also lower for a clearly uncertain hypothesis (0.30) and an accurately attributed causal account (0.26). The grounded baseline (0.27), stronger grounded wording (0.28), and grounded book terminology (0.31) nevertheless exceeded the existing cutoff. The exact-cutoff case ua-016 was not flagged because the policy uses `>`.

The overloaded but grounded draft scored 0.56 for unsupported assertions. The literal text conversion, which has no Webb source cards, scored 0.45. These are disagreements worth inspecting for contract or context sensitivity; the probabilities do not establish unsupported sentences or reveal the model's rationale. The unrelated-task case also deliberately bypassed preflight scope selection, so it does not establish how the deployed routing path would handle that input.

## Framework load

The framework-load policy flag agreed with the AI rubric label in 15 cases and disagreed on ua-012. The corpus supplies only two AI-positive load examples, so that count is not a general quality measure.

- ua-010's full two-framework preparation curriculum scored **1.99**, with **0.99 confidence**, matching the AI level-2 judgment.
- ua-005's unnecessary formal-warning stage scored **0.88**, matching the AI level-1 judgment.
- ua-012 used inquiry and recovery methods for an explicit investigation-and-recovery goal. The AI labeled this justified support (level 0), but Jev scored **1.36**, with probabilities **0.05 / 0.55 / 0.40** across levels 0/1/2 and confidence **0.33**.
- ua-015's grounded framework terminology produced Score **0.63**, below the cutoff, but confidence **0.05**, with probabilities **0.47 / 0.44 / 0.09**. This is a diffuse rubric judgment despite the unflagged mean.

Score, confidence, and the distribution are preserved separately. Neither Score nor confidence is P(unsupported), and low confidence does not by itself demonstrate a wrong answer.

## Other checks and interpretation

**All 16 drafts returned `revise_once`, and every draft failed `teaches_selection`.** Fifteen also failed unsupported assertions; ua-016 failed teaching alone. These short diagnostic drafts generally name a method without fully explaining its fit. They were not authored as complete passing coaching responses. No further revisions were executed, and the all-revision result must not be attributed solely to the assertion question.

The unrelated text-conversion draft also failed teaching/practice/source checks. This illustrates the scope of the postflight contract; it is not evidence that routine conversion needs leadership coaching. The deployed skill retains its local/no-fit paths.

This batch suggests useful discrimination between the deliberately unsupported examples and the AI-grounded examples, while exposing many flags under the current conservative cutoff. It does **not** justify selecting a new cutoff from these ranges, declaring the labels correct, or proving that splitting fact and inference questions would resolve the disagreements. Both the factual-count error and the unsupported interpretations already elicited high values.

Keep this baseline frozen. The next controlled investigation should check repeat variability and change one aspect of supplied review context at a time on grounded, uncertain-hypothesis, overloaded, and justified-two-method examples. Independent reviewer judgments would strengthen the evidence. No such follow-up experiment or policy change is included in this result.
