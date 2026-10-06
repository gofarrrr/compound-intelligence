# Frozen review follow-ups — executed 2026-10-02

**All 125 planned requests succeeded. G preserved the tested unsupported-claim distinctions, with a remaining grounded-advice flag. The current H candidate is not ready for promotion.** Neither production questions nor thresholds changed.

The user explicitly approved the three frozen studies and then authorized a private local key file. A hidden macOS prompt saved `.env.local` with owner-only `0600` permissions; its value was loaded into the test process without printing it. Git and release exclusions were checked. The portable runtime still reads only its process environment; no automatic dotenv loading or session-wide spending setting was added.

The earlier first launch failed locally with `typesafe_key_missing`, before any HTTP request. That file remains intact. The successful G coverage run used a new output filename. This was credential recovery, not additional model sampling. The CLI now shows the fixed failure code in its progress line instead of only `unavailable`; its missing-key regression check confirms that no transport runs in that case.

## Execution and verification

| Study | Successful requests | Input / output tokens | Original return |
| --- | ---: | ---: | --- |
| Remaining grounded G coverage | 25 | 48,745 / 3,725 | [JSON](review-ablation-g-remaining-2026-10-02.json) |
| Matched assertion boundaries, A/G | 60 | 122,950 / 8,940 | [JSON](review-ablation-ag-boundaries-2026-10-02.json) |
| Balanced framework proportionality, A/H | 40 | 103,360 / 5,960 | [JSON](review-ablation-ah-balanced-2026-10-02.json) |

All calls returned the pinned `jev-1.13.0` on one HTTP attempt each. Total reported usage was **275,055 input tokens and 18,625 output tokens**. Monetary cost was not measured. Client times ranged from 292.47 to 851.66 ms; these exchanges are not a latency benchmark.

Local validation matched the complete experiment objects to the frozen plans, checked schedules, outgoing/draft/request hashes and every typed answer, and recomputed all grouped summaries. The original returned bytes were archived unchanged. The [verification record](review-followup-validation-2026-10-02.json) includes hashes, usage, the paired checks, other-question policy comparisons and full H distribution summaries. **116 offline tests passed** before live execution. No repeats, criteria, cutoffs or model pins were changed after observing results.

## G coverage on the original corpus is complete

| Remaining case | G unsupported-assertion range | Mean | Flags at > 0.25 |
| --- | --- | ---: | ---: |
| ua-008, strong supported wording | 0.17–0.19 | 0.178 | 0/5 |
| ua-011, literal text conversion | 0.37–0.46 | 0.436 | 5/5 |
| ua-014, attributed causal account | 0.17–0.17 | 0.170 | 0/5 |
| ua-015, supported framework terminology | 0.20–0.23 | 0.214 | 0/5 |
| ua-016, bounded uncertainty | 0.18–0.19 | 0.186 | 0/5 |

Every original draft now has five G observations across the three executed batches: **16 authored cases, 80 repeated measurements**. Gemini's supplied binary judgments cover that original corpus, not the newly authored boundary controls.

The four additional coaching negatives stayed below the unchanged cutoff. ua-011 remains an out-of-scope postflight stress test; Gemini judged framework review N/A. Its high assertion signal is a limitation of applying this coaching review to an unrelated utility artifact, not evidence that the string conversion contains a fabricated claim. Keep it separate from normal coaching behavior. The earlier ua-010 dense-advice residual remains 0.29–0.32 and is still unexplained.

## Matched assertion boundaries

Each pair changes only sentence 4, holding case evidence and source cards constant. Within each draft, A/G differs only in the assertion clarification. The labels below remain Codex-authored expectations; these six drafts were not independently reviewed by Gemini or humans.

| Pair | Grounded G range (mean) | Unsupported G range (mean) | Grounded / unsupported flags |
| --- | --- | --- | --- |
| Outcome observation vs certain promised completion | 0.17–0.19 (0.186) | 0.88–0.89 (0.886) | 0/5 vs 5/5 |
| Two reported handoffs vs three, inside advice | 0.17–0.20 (0.180) | 0.84–0.86 (0.850) | 0/5 vs 5/5 |
| Check approval authority vs assert unilateral authority | 0.53–0.56 (0.552) | 0.83–0.87 (0.850) | 5/5 vs 5/5 |

All **15 unsupported G observations** exceed 0.25, and every unsupported range is above its matched grounded range. Those prospective diagnostic checks pass on these authored examples. The largest positive mean drop is 0.092 on unsupported authority, from A 0.942 to G 0.850; report this alongside the preserved separation. No new majority policy failure appeared in the other seven unchanged questions across these six A/G comparisons, using the frozen at-least-3/5 versus at-most-2/5 rule.

The grounded authority case bc-005 remains a concern. Its sentence asks the user to discuss reassignment and check who may approve it; it does not assert that the user has approval authority. G reduces its mean from A 0.834 to 0.552, but every repeat still flags it. The draft also moves away from the requested factual conversation and is flagged for goal fit and agency under both conditions. That is a plausible cross-dimension interaction to investigate, not a sentence-level explanation supplied by Jev. An independent reviewer should judge this case before treating its authored negative label as established.

G is a stronger promotion candidate after these controls, while bc-005, ua-010 and out-of-scope ua-011 must remain explicit limitations. The observed score gap is not a reason to select a new threshold. The original two-human-review gate remains unmet; accepting an AI-only evidence standard would require a deliberate, separately recorded maintainer decision.

## H remains a separate, unpromoted candidate

| Case / intended burden | A Score mean | H Score mean | H mean mass on levels 0 / 1 / 2 |
| --- | ---: | ---: | --- |
| hc-001: one focused method, 0 | 0.312 | 0.568 | 0.472 / 0.486 / 0.042 |
| hc-002: useful method plus unnecessary comparison, 1 | 1.058 | 1.054 | 0.202 / 0.542 / 0.256 |
| hc-003: two methods for two requested subgoals, 0 | 1.304 | 0.886 | 0.356 / 0.398 / 0.246 |
| hc-004: substantial unrequested overload, 2 | 1.990 | 1.974 | 0.002 / 0.016 / 0.982 |

The focused, justified-two-method and overload drafts reuse Gemini-reviewed examples. The level-1 example is new and its target is still provisional. H changes only the framework criteria; G is absent.

H retains a strong overload response, but does not clearly recognize the justified two-method draft as level 0. Its five scores remain 0.82–0.93, above the current 0.75 operating cutoff, with confidence only 0.00–0.11. The focused draft becomes less clearly level 0, and the level-1 draft's confidence declines from A 0.71–0.74 to H 0.30–0.35. A lower mean for hc-003 alone does not establish a better rubric.

**Recommendation: do not promote this H wording.** Its changed level meanings also make the unchanged numerical cutoff an uncalibrated operational comparison. Preserve the full distributions and obtain independent judgments on the ambiguous/new cases before any further contract change; do not tune the cutoff or add repeats to rescue this study.

## Decision status

Production remains `ci.postflight.v2.0.0`; the assertion cutoff remains **greater than 0.25**. G is still experimental and H is a no-go for promotion in its current form on this authored study. No automatic upgrade, calibration claim or coaching-effectiveness claim follows from successful API exchanges. The next useful evidence is independent review of the authority recommendation and rubric boundaries, followed by an explicit promotion/evidence-standard decision.

The r2 team ZIP is a prior snapshot. It has not been overwritten with these new results or the private credential file.

A focused five-case independent-review packet was subsequently prepared for bc-005 and hc-001–hc-004. It preserves the original evidence, numbered drafts and source-card bytes, replaces case IDs with shuffled neutral aliases, and omits model results and authored labels. The reviewer-only ZIP contains instructions, the packet and a blank JSON return template; the mapping and coordinator notes stay separate. Exposure to draft texts and exposure to scores/findings are disclosed separately, since three drafts reuse earlier reviewed examples. Packet SHA-256 is `b6fb023ecb6270c5afcfbe96256d33ea2c6ae45b3fed2acf618dfe21b407326a`. No new review return, API call, promotion or evidence-standard amendment was produced by preparing this packet.

**Subsequent return, verified 2026-10-02:** Gemini's original five-case Markdown and JSON files are now preserved externally and verified against that packet. It judges bc-005 to contain no unsupported assertion and assigns hc-001–hc-004 framework levels 0, 1, 0, 2. This independently corroborates the new level-1 expectation and the authority-advice residual relative to an AI reviewer. The [focused findings and provenance](gemini-focused-review-2026-10-02.md) qualify the reviewer's rationale and preserve its disclosures. Earlier statements above about the new labels being unreviewed describe the state before this return. The other five boundary drafts remain independently unreviewed; no human gate, production question or threshold changed.
