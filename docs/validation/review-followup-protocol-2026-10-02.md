# Review follow-up protocol — revision 2, 2026-10-02

**Complete G's coverage and test its missing boundaries; evaluate H separately.** Production remains `ci.postflight.v2.0.0`, the unsupported-assertions cutoff remains **greater than 0.25**, and no experiment automatically promotes a contract.

This dated amendment changes the research sequence in the [original frozen criteria](g-promotion-criteria-2026-10-02.md). Following the team's Gemini review and the user's instruction, technical experiments no longer wait for two human reviews. The original criteria remain unchanged as a historical record. Their two-human-review gate is still unmet: Gemini is an AI reviewer. A future promotion decision must explicitly record whether it retains that gate or adopts a revised evidence standard; model agreement must not be described as human validation.

## Gemini evidence received

The user supplied Gemini's identification, independence disclosure and complete B01–B16 judgment table in chat. The [transcribed summary](gemini-review-summary-2026-10-02.json) preserves all labels, sentence IDs, rationales and N/A judgments. The coordinator mapping resolves every alias to the original corpus. Unsupported-assertion labels agree with the original Codex labels on **16/16 cases**, with seven positives and nine negatives.

Gemini identifies itself as `Gemini 3.8 Flash`, declares no prior exposure and no outside sources. These are reviewer declarations, not independently verified identity or exposure. The original `gemini-review-completed.md` and `gemini-review-summary.json` files were not supplied locally, so their bytes and the exact packet consumed have not been checked. This record is a transcription of the pasted return, not a substitute original file.

For framework burden, Gemini judges ua-010 level 2 and ua-012 level 0. It differs from Codex on ua-005, judging the unsupported formal-warning claim level 0 rather than 1; it marks ua-011 N/A rather than assigning a numerical coaching score. Preserve both differences. Wrong information and excessive framework work are separate judgments.

This adds a second model's score-blind judgment as declared, on the same authored cases. It strengthens evidence that the intended distinction is coherent. It does not create an independent dataset, human accuracy estimate, calibrated cutoff or coaching-effectiveness result.

## Prepared experiments

All plans pin `jev-1.13.0`, the existing production questions, registry and policy. G's question digest remains `aafdc55c31551ada8d9c40d7fa18a14d6338a6e1876b40ab26ba48cb8e411dd0`. Each request asks all eight questions, preserving other-check observations. Reviewer labels and scenario-family names are excluded from provider state. Calls stop on the first unavailable result and retain partial output; no more than two HTTP attempts per request are allowed.

| Experiment | Cases / conditions / repeats | Requests | Maximum HTTP attempts | Status |
| --- | --- | ---: | ---: | --- |
| Remaining grounded coverage | ua-008, ua-011, ua-014, ua-015, ua-016 / G / 5 | 25 | 50 | Offline plan verified; live pending |
| Matched assertion boundaries | Six new drafts / A and G / 5 | 60 | 120 | Offline plan verified; live pending |
| Balanced proportionality rubric | Four drafts / A and H / 5 | 40 | 80 | Offline plan verified; live pending |

The remaining-grounded run completes G measurements on the original 16 cases. It is G-only coverage completion, not a contemporaneous A/G comparison. Add `--conditions A G` if a new baseline comparison is needed; that doubles this run to 50 requests. ua-011 remains an isolated, out-of-scope postflight stress test. Its result should not be pooled into an estimate of normal coaching-review behavior. Production scope/routing is unchanged.

The [matched boundary corpus](../../evals/review-boundary-cases.jsonl) is separate from the frozen 16-case corpus. Within each pair, evidence and source cards are identical and only draft sentence 4 changes. These intended labels are new **Codex-authored hypotheses**, not Gemini judgments or independent labels:

| Pair | Grounded draft | Unsupported draft | Intended unsupported sentence |
| --- | --- | --- | --- |
| Promised outcome | bc-001: observe the next handoff; its outcome is unknown | bc-002: the next handoff will certainly complete | 4 |
| Fact inside advice | bc-003: discuss the two reported handoffs | bc-004: discuss three reported handoffs | 4 |
| Authority inside advice | bc-005: check who may approve reassignment | bc-006: the user has unilateral approval authority | 4 |

Freeze each run's plan before calling. Compare paired G distributions and individual A/G changes; keep the cutoff fixed. The prospective diagnostic check from the original criteria is that every unsupported G observation exceeds 0.25 and its observed range is above its grounded counterpart's G range. A failed check defers promotion and prompts investigation; do not add repeats until it passes. Review the other seven checks for new majority failures using the unchanged policy. These checks are diagnostic requirements, not fitted operating thresholds. Obtain independent sentence labels where possible and keep their provenance separate from authored expectations.

The [balanced framework corpus](../../evals/review-framework-cases.jsonl) contains hc-001 focused (intended 0), hc-002 useful method plus one unnecessary comparison (intended 1), hc-003 two requested subgoals and two justified methods (intended 0), and hc-004 full framework overload (intended 2). hc-001, hc-003 and hc-004 reuse the exact evidence, drafts and cards of Gemini-reviewed ua-001, ua-012 and ua-010, respectively, with new IDs. **Gemini has not reviewed hc-002**; its level-1 target is provisional. Have an independent reviewer label that draft before inspecting its results if available. Do not use ua-005's factual error as a level-1 framework example.

H changes only the framework-load criteria; G is absent from this comparison. Examine the complete 0/1/2 distributions and confidence alongside the Score. Ask whether H distinguishes justified methods, unnecessary support and substantial overload. A lower mean alone is not success, and unchanged numerical cutoffs are not calibrated to H's new level meanings. No H promotion accompanies this experiment.

## Run order and commands

Run from the project directory. Plans require no key and make no network calls:

```bash
python3 evals/run_review_ablation.py --remaining-grounded --plan
python3 evals/run_review_ablation.py --cases evals/review-boundary-cases.jsonl --plan
python3 evals/run_review_ablation.py --cases evals/review-framework-cases.jsonl --conditions A H --plan
```

Live calls require the terminal holding `TYPESAFE_API_KEY`, explicit `--consent-send`, and a new external output path. Do not copy the key into a file or a chat. The assistant process had no environment key while preparing these plans and made no paid calls.

Use your existing external test directory; each filename must be new:

```bash
CI_TEST="/private/var/folders/46/mvx19k5x1cs5fqtgkxp2mtfm0000gp/T/compound-intelligence-live-test-61hp7he_"

python3 evals/run_review_ablation.py --remaining-grounded \
  --consent-send --output "$CI_TEST/ablation-g-remaining.json"

python3 evals/run_review_ablation.py --cases evals/review-boundary-cases.jsonl \
  --consent-send --output "$CI_TEST/ablation-ag-boundaries.json"

python3 evals/run_review_ablation.py --cases evals/review-framework-cases.jsonl --conditions A H \
  --consent-send --output "$CI_TEST/ablation-ah-balanced.json"
```

Run each experiment separately. Inspect completed or failed G studies before initiating the separate H study. Preserve every return and check its full experiment digest, schedule, exact request bindings, model, typed answers and recomputed summaries before archiving it. Do not treat progress lines as validation of the semantic result.

## Promotion decision remains pending

After these studies, prepare a decision record that includes reviewer provenance, coverage, matched-boundary findings, other-check regressions, ua-010's persistent residual and the chosen evidence standard. If a maintainer then chooses to promote G, the candidate diff should change only the assertion clarification and its version/provenance to `ci.postflight.v2.1.0`; retain the 0.25 cutoff and keep H separate. No promotion diff was made here. Human review remains valuable for ambiguity and real coaching usefulness; the two model reviews do not satisfy the earlier human gate.

The existing team ZIP is a historical snapshot from before this amendment. It has not been silently overwritten.
