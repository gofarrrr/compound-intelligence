# G advisory evidence standard — adopted 2026-10-02, revision 2

**Status: ADOPTED 2026-10-02.** The maintainer adopts `ci.evidence.advisory.v1` for the evaluated G assertion clarification and approves promotion to `ci.postflight.v2.1.0`. This is a scoped exception to the original frozen criteria for this promotion only. It does not retroactively satisfy the original two-human gate or replace that requirement for other changes.

This revision finalizes the documentation following the maintainer's focused release review. G was applied in package 0.2.1 after the earlier explicit approval; package **0.2.2** carries this finalized record and current-status links. The semantic contract and runtime code are unchanged from 0.2.1. The [initial adopted decision](g-promotion-decision-2026-10-02.md) remains preserved as revision 1 history.

This is a dated amendment to the original [frozen promotion criteria](g-promotion-criteria-2026-10-02.md), whose SHA-256 remains `09a531f72cc405ea3d56c0103618c7b61b26566e8fe143b09763b30818a9cbc4`. Their two-human-review gate was not met. The maintainer explicitly accepts the scoped exception below for G after observing the experimental results; the historical gate is not retrospectively declared satisfied. The earlier [follow-up protocol](review-followup-protocol-2026-10-02.md) already amended the research order.

## Scoped standard: ci.evidence.advisory.v1

For this evaluated G promotion only, the maintainer accepts an exception to the two-human gate because this bounded advisory change does not authorize external actions, change thresholds or claim real-world effectiveness, and has:

- Repeated controlled evidence with frozen questions, inputs, budgets and policy.
- Preserved positive sensitivity on the tested unsupported claims.
- Independent, score-blind model review, with identity and exposure provenance retained.
- Explicit known limitations and their advisory handling.
- Versioned contracts and a concrete rollback path.
- No unresolved high-risk failure, plus a review of other-check regressions.

Future changes still require their own evidence and deliberate maintainer decision. This is not automatic promotion or a global reduction of standards. Human review remains required for consequential policy changes, threshold calibration, employment/authorization decisions and claims of effectiveness. Representative independently human-labeled held-out data is needed for calibration or production-accuracy claims; appropriate outcome evidence is also needed for real-world effectiveness. Neither AI agreement nor this release provides those results.

For G only, this decision explicitly waives the original requirements for two human corpus reviews, human consensus and human labels on matched controls before outputs. Those human steps remain absent and are reported honestly. No authority, consent, safety or revision policy is weakened.

## Evidence accepted and limits retained

All 16 original cases have five G observations. The seven authored positive cases retain **35/35 flags at 0.84–0.95**. Gemini's declared blind labels agree with the original assertion labels on 16/16. The [original positive-control findings](review-ablation-ag-positive-2026-10-02.md) retain the raw ranges and A/G differences.

Matched outcome, count-inside-advice and authority-inside-advice controls retain **15/15 positive G flags**, with each positive range above its paired grounded range. The [follow-up findings](review-followup-findings-2026-10-02.md) preserve all returns and regression comparisons. The other five new boundary drafts remain independently unreviewed: their labels are authored expectations accepted under this narrower standard, not Gemini-confirmed labels.

The [focused return](gemini-focused-review-2026-10-02.md) corroborates bc-005 as advice without an unsupported assertion, while retaining concerns about the advice's quality. Reviewer identity and blindness are declared, not independently authenticated. Both Gemini returns identify the same model; they are not two distinct AI reviewers or human validation.

The original and boundary A/G comparisons show no new majority failure in the seven unchanged checks under the frozen regression rule. This is limited evidence on synthetic controls, not proof of unchanged behavior on all cases. The balanced H study and Gemini's 0/1/0/2 judgments support keeping H unpromoted.

| Known limitation | Observed G values | Advisory handling |
| --- | --- | --- |
| bc-005: approval-check advice can still trigger an assertion flag | 0.53–0.56; 5/5 flags | Separate factual support from goal fit and agency. A flag does not establish an unsupported sentence. |
| ua-010: dense grounded framework advice can remain above cutoff | 0.29–0.32; 5/5 flags | Inspect the actual sentences and reduce unnecessary burden when appropriate; do not assume fabrication. |
| ua-011: unrelated utility artifacts are outside normal coaching review | 0.37–0.46; 5/5 flags in the deliberate stress test | Use the ordinary task path when coaching scope is absent. These stress results are not a normal coaching false-positive rate. |

The residual causes are not established. Keep one revision at most, followed by narrower/manual or human review. Do not resample until a convenient pass appears. No reviewed unresolved high-risk failure was identified in the tested controls; this is not a general safety guarantee.

## Exact implementation and provenance

Only the assertion clarification and postflight version change in the runtime question contract. The new digest equals the evaluated G candidate: `aafdc55c31551ada8d9c40d7fa18a14d6338a6e1876b40ab26ba48cb8e411dd0`. Preflight, all seven other postflight questions including framework load, pinned model, source cards, state/receipt formats, routing policy and consent/authority rules remain unchanged. Policy remains `ci.policy.v2.0.0`, digest `5fb4e7a81e47f49b1d08e74bf86e1204847081d50060211341e5f187f3e741b9`, with the cutoff > 0.25 and one-revision limit unchanged.

The ablation runner now loads the existing archived v2.0.0 A questions rather than the current runtime. Historical experiment objects, schedules, variants and hashes remain reproducible, including G and the unpromoted H. Offline regressions verify the new runtime equals evaluated G, the old A and policy digests are unchanged, and engine requests/receipts identify the promoted contract. Raw reviewer files remain outside public releases.

Supported evidence: improved semantic separation on authored controls, preserved sensitivity on tested unsupported claims and independent AI-review agreement. Not established: human-review agreement, calibration of 0.25, real-world coaching effectiveness or a production accuracy rate. No new paid inference is authorized or run by this promotion.

## Rollback

Restore `POSTFLIGHT_VERSION = 'ci.postflight.v2.0.0'` and remove only the appended G clarification from the assertion question in `questions.py`. The restored question digest must be `cfe7583e66ad259cc4fab55ed1da6394bbae2538532836b6b941d0fb7d475b09`. Keep the frozen ablation baseline, all experimental returns and this decision as history. Update current-status documentation and the contract-pin regression, run the offline suite and create a new package release; do not overwrite 0.2.1 or relabel old receipts as v2.1.0. Package archives carry checksums, and earlier release ZIPs remain intact.

## Final decision: ADOPTED

- Promote evaluated G to `ci.postflight.v2.1.0`.
- Keep the assertion cutoff strictly **> 0.25**.
- Keep H unpromoted and its experimental wording out of the runtime.
- Keep the other seven postflight questions unchanged.
- Keep policy `ci.policy.v2.0.0`, routing and the one-revision limit unchanged.
- Preserve the original promotion criteria and their hash.
- Record bc-005, ua-010 and out-of-scope ua-011 as known limitations.
- Make no human-validation, calibration, production-accuracy or coaching-effectiveness claim.
- Grant no autonomous employment or external-action authority; retain all safety and consent rules.
