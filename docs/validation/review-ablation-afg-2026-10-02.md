# Controlled review ablation — 2026-10-02

**The advice/question clarification lowered the assertion signal consistently on all four AI-negative examples.** Sentence-type annotations produced smaller, mixed changes. This supports further testing of the question boundary; it does not establish a better detector or justify changing the cutoff.

The [original result file](review-ablation-afg-2026-10-02.json) was archived byte-for-byte after local verification of the frozen experiment, schedule, exact outgoing packets, question/policy/source/corpus bindings, all typed provider responses, and recomputed summary statistics. Its SHA-256 is `8ebc21487fca31d8a30f084a31f5e12cd620b78703f5b5a964475104312f6ca6`. It contains synthetic cases and the existing internal chapter cards, with no credentials or personal cases.

## Experiment and execution

The user ran **60 requests** against pinned model `jev-1.13.0`: four unchanged drafts, A/F/G, five repeats each. A used the original packet and all eight production questions. F added AI-authored sentence-type hints to state. G changed only the assertion question by clarifying that advice, questions and suggested practices do not assert that an event already happened; asserted events, causes, permissions and promised outcomes within advice still require support.

Each repeat used an interleaved case/condition schedule with seed `20261002`. Every request succeeded on one HTTP attempt. Reported usage totaled **150,605 input tokens and 8,940 output tokens**. Client elapsed times ranged from **359.30 to 654.01 ms**, with median **409.16 ms**. Monetary cost was not measured; this is not a latency benchmark.

The experiment digest matched the pre-run plan: `50d13f76c9ee10505424779584b84fe42c38008a8989e7ddb41e91b43b31ed1b`. No production question, source card or policy changed. The assertion rule remained strictly **P(unsupported) > 0.25**. The optional H framework-rubric condition did not run.

## Assertion findings

All entries below are means of five returned Noul values. The labels remain the corpus author's provisional AI judgments, not independent human findings.

| Case | Draft | A original | F annotations | G clarification | G − A |
| --- | --- | ---: | ---: | ---: | ---: |
| ua-001 | Grounded baseline | 0.288 | 0.256 | 0.188 | −0.100 |
| ua-004 | Marked hypothesis | 0.266 | 0.264 | 0.202 | −0.064 |
| ua-010 | Grounded framework overload | 0.552 | 0.512 | 0.302 | −0.250 |
| ua-012 | Two justified methods | 0.252 | 0.290 | 0.174 | −0.078 |

G's observed range sat entirely below A's range for every case: ua-001 **0.17–0.21 versus 0.26–0.30**; ua-004 **0.19–0.21 versus 0.25–0.28**; ua-010 **0.29–0.32 versus 0.53–0.57**; ua-012 **0.17–0.19 versus 0.23–0.27**. Each same-repeat G observation was lower than its A observation. These descriptive differences are larger than the observed within-condition variation in this small run, but five repeats do not establish deployment stability or a population effect.

At the unchanged cutoff, A flagged **17/20** observations, F **16/20**, and G **5/20**. G's five flags all belonged to ua-010: the overloaded draft's signal decreased sharply but remained above 0.25 on every repeat. The earlier single-shot ua-004 result of 0.30 was above this run's A range, illustrating why small differences between separate runs should not be interpreted as precise semantic changes.

F reduced ua-001 and ua-010 by 0.032 and 0.040 on average, changed ua-004 by only −0.002, and increased ua-012 by 0.038. These hints therefore did not consistently resolve the disagreements. They also add AI interpretation to the packet, so any response to them would not be independent corroboration.

## Framework load stayed separate

| Case | A mean framework Score | G mean framework Score |
| --- | ---: | ---: |
| ua-001 | 0.296 | 0.284 |
| ua-004 | 0.220 | 0.220 |
| ua-010 | 1.990 | 1.990 |
| ua-012 | 1.314 | 1.328 |

The overloaded draft remained at Score **1.99**, confidence **0.99**, on all A and G repeats. The two-method draft remained above the existing load cutoff under every condition: A **1.27–1.36**, F **1.24–1.28**, G **1.27–1.36**. Clarifying assertions therefore did not resolve the separate framework-rubric disagreement. The full distributions and confidences are preserved in the raw results; neither is converted into P(unsupported).

## Interpretation and next evidence

The large, consistent ua-010 decrease is compatible with the hypothesis that the old assertion boundary treats some advice as unsupported claims. The experiment does not identify the triggering sentence or prove that mechanism: G might also make the detector more lenient generally. Residual probability on ua-010 is still unexplained, and a probability alone does not establish an actual unsupported assertion.

Keep G experimental and the 0.25 cutoff frozen. The next check should compare A/G on the seven deliberately unsupported drafts from the diagnostic corpus, particularly unsupported permissions or promised outcomes embedded in advice. Lower values on AI-negative drafts are useful only if detection of genuinely unsupported claims survives. Independent, score-blind human labels remain necessary; the prepared reviewer packets are still blank. These reused, authored examples are diagnostic controls, not a held-out calibration set.

Test the proposed framework proportionality rubric independently through H before adopting it. A/F/G neither tested that rubric nor resolved whether two methods for distinct requested subgoals should count as excessive machinery. No routing evaluation, automatic draft revisions, host coaching quality or workplace outcomes were measured here.
