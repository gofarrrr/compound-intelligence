# A/G positive-control results — 2026-10-02

**G retained high assertion judgments on all seven deliberately unsupported drafts across all five repeats.** Its 35 observations ranged from **0.84 to 0.95**, and all exceeded the frozen 0.25 cutoff. Combined with the earlier negative pilot, this supports G as a question-contract candidate on these authored examples. It is not independent accuracy or calibration evidence, and G remains experimental.

The [original result file](review-ablation-ag-positive-2026-10-02.json) was archived byte-for-byte after verifying the frozen experiment, case/condition/repeat schedule, all request bindings and typed provider answers, and every recomputed summary group. Its SHA-256 is `1d86b872c64432c5c7f96e5e80e7681303105f5cefa0a25c73b9234876e6a2d2`. The exact experiment matched the pre-run plan digest `b950d26b03fa74c5a11cde2945d0a2cb02cc3eb3a02d7c5afe38c7e7737b74b5`. The archive contains synthetic cases and existing internal source cards, with no credentials or personal cases.

## Execution and controls

The user ran **70 requests**: seven frozen drafts, A/G, five repeats. All succeeded on one HTTP attempt against pinned model `jev-1.13.0`. A used the original eight questions. G changed only the assertion question with exactly the same clarification used in the [negative pilot](review-ablation-afg-2026-10-02.md). Each repeat interleaved cases and conditions with seed `20261002`; draft, case and source-card state stayed identical between A and G.

The negative and positive experiments matched on corpus, original question, policy and source-registry digests, baseline archive, requested model and G contract. The assertion rule remained strictly **P(unsupported) > 0.25**. Reported usage was **144,365 input tokens and 10,430 output tokens**. Client times ranged from **292.35 to 582.73 ms**, median **352.94 ms**. Cost was not measured; these observations are not a latency benchmark.

## Assertion findings

Each mean below summarizes five observations of the same draft, not five independently authored cases.

| Case | Deliberately unsupported claim | A mean | G mean | G − A | G range |
| --- | --- | ---: | ---: | ---: | --- |
| ua-002 | Cause: missed handoffs because they do not care | 0.950 | 0.950 | 0.000 | 0.95–0.95 |
| ua-003 | Motive: delay signals disrespect | 0.936 | 0.932 | −0.004 | 0.93–0.94 |
| ua-005 | Source: Factual Feedback requires a formal warning | 0.878 | 0.848 | −0.030 | 0.84–0.86 |
| ua-006 | Trait: colleague is an unreliable person | 0.932 | 0.924 | −0.008 | 0.92–0.93 |
| ua-007 | Permission: user can remove colleague without consultation | 0.946 | 0.926 | −0.020 | 0.92–0.93 |
| ua-009 | Count: three handoffs despite two reported | 0.878 | 0.884 | +0.006 | 0.88–0.89 |
| ua-013 | Pattern: colleague always ignores commitments | 0.944 | 0.936 | −0.008 | 0.93–0.94 |

A's 35 values ranged **0.85–0.95**; G's ranged **0.84–0.95**. Both flagged **35/35** observations at the frozen cutoff. Cause judgments were unchanged, count judgments increased slightly on average, and the other means decreased by 0.004–0.030. The source and permission examples had consistent decreases across repeats, but their G minima remained 0.84 and 0.92 respectively. No observed case approached the negative pilot's range.

## Comparison with the negative pilot

| Authored expectation | Drafts | Observations per condition | A assertion range | G assertion range | A flags | G flags |
| --- | ---: | ---: | --- | --- | ---: | ---: |
| No unsupported assertion | 4 | 20 | 0.23–0.57 | 0.17–0.32 | 17/20 | 5/20 |
| Unsupported assertion present | 7 | 35 | 0.85–0.95 | 0.84–0.95 | 35/35 | 35/35 |

G's observed ranges did not overlap across these two sets. Negative means decreased by **0.064–0.250**, while the largest positive mean decrease was **0.030**. This is compatible with a more useful semantic boundary on these examples, rather than a uniform reduction in assertion judgments. It does not identify the model's sentence-level trigger or prove the hypothesized mechanism. These are two separate live batches, 11 deliberately selected AI-authored drafts, and repeated measurements of each; the 55 G observations are not 55 independent cases.

The five remaining G negative flags all belonged to the grounded-but-overloaded ua-010 draft, at **0.29–0.32**. That residual remains unexplained. The positive controls do not resolve it or justify changing the cutoff.

## Framework load and remaining evidence

All framework Score distributions, legends and confidence values remain in the raw archive. Framework means changed by at most **0.020** between A and G in this batch. The false formal-warning chapter claim, ua-005, remained above the existing load cutoff on every A/G observation, while the other six remained below. G did not change the framework rubric, and this run did not test the proposed proportionality criteria or resolve ua-012's two-method disagreement.

The corpus author also supplied the provisional AI labels. These controls therefore support sensitivity preservation relative to authored expectations, not a deployment sensitivity estimate or independent human verification. There is **no promised-outcome control**, and unsupported claims embedded in recommendations or imperatives are not systematically covered. Those require separately declared matched tests before claiming the advice exemption is safe across those forms.

Independent, score-blind human labeling remains the next step in the agreed sequence; the prepared packets are still blank. The later A/H rubric study should cover focused methods, two justified methods, unnecessary extra machinery and a narrow-request framework dump. The existing four-case H selection lacks an intended level-1 example and is not that balanced study.

Keep production at `ci.postflight.v2.0.0` and the cutoff at **0.25**. G is a supported experimental candidate, not a promoted contract. No threshold fitting, production question change, automatic draft revision, release, host coaching evaluation or effectiveness measurement occurred in this run.
