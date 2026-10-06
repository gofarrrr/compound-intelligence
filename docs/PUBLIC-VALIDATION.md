# Public validation status

Updated 2026-10-06. Package 0.3.0 is an experimental continuity/onboarding preview. Packaging the current workflow does not promote E/C/D as demonstrated advice improvements. Building it alone does not publish a release.

## Decision runtime

The runtime uses evaluated G as `ci.postflight.v2.1.0`, following the [adopted scoped decision](validation/g-advisory-evidence-standard-2026-10-02.md). Policy remains `ci.policy.v2.0.0`; assertion failure is strictly > 0.25, H is unpromoted, and at most one revision is allowed.

Repeated authored assertion controls showed improved separation with preserved detection on tested unsupported claims. The [original diagnostics](validation/review-diagnostics-2026-10-02.md), [negative ablation](validation/review-ablation-afg-2026-10-02.md), [positive controls](validation/review-ablation-ag-positive-2026-10-02.md) and [follow-ups](validation/review-followup-findings-2026-10-02.md) retain the experiments and limits. Gemini supplied blind AI judgments; these are not human validation. Residual limitations include bc-005 authority-check advice, ua-010 dense grounded advice and out-of-scope ua-011 utility artifacts. See [release notes](../skills/compound-intelligence/references/release-notes.md).

## Product comparisons completed

The previous host-guidance enrichment candidate failed its required comparative gate. A small additive precision candidate produced no pairwise wins; a subtractive owner-brief candidate produced one win and five ties and did not pass its diagnostic gate. They remain closed experiments, not demonstrated advice improvements.

The later core-value comparison used 30 frozen first answers across 15 authored cases: the exact pre-enrichment skill B versus the same strong host without the skill P. A fresh blind model reviewer returned **1 B win, 1 P win, 11 ties and 2 unusable judgments**. Even two additional B wins could not reach the frozen five-win gate. The study did not demonstrate the required incremental value for single answers. It also does not prove equivalence or general uselessness of the skill.

These results came from one generated answer per condition/case and one AI reviewer, not independently sampled real-user cases or a human-review panel. Internal records retain raw answers, failures and mappings; private study bundles are excluded from public exports. The product direction now focuses on work over time: understand → decide → explain → practise → act → reflect → transfer. Its real-user value remains to be measured.

## Case Continuity MVP

The MVP supports an explicitly authorized compact Markdown snapshot, manual return, reading the current file, comparing old understanding with new reports, and scoped updates. Plans, attempts and outcomes remain distinct. No database, automatic retrieval, person profile or scheduler is present.

Implementation review approved the MVP after a section-order fix. A fictional walkthrough exercised actual create → read → update with a proportionate changed move. It is a mechanical demonstration, not a lived outcome or effectiveness evidence. A limited 3–5-case real-user trial is approved; no real case or return has yet been supplied in the recorded project trial.

## Offline and packaging checks

The complete suite contains **155 offline tests**, including 147 retained checks and eight new offline installer/launcher/version checks. The retained suite passed the earlier readiness audit; the 0.3.0 build records its own result. These check structure, typed contracts, receipts, provider-failure paths, finite revision, source preservation, presentation rendering and filesystem behavior. Continuity checks cover consent scope, stale reads, preservation of section order and truthful write status. Authored semantic fixtures illustrate transitions; they do not execute a generative coach or establish that hosts always follow the instructions.

All 21 Webb source cards remain unchanged. Multi-book research and the mental-model inventory are internal editorial material, not additional deployed methods. Current Jev postflight receives the case, draft and actual registered Webb cards; it does not review arbitrary outside supporting sources.

Public packaging uses a reviewed [file manifest](../scripts/public-release-files.json), checks local links in both formats and records member hashes. The renderer reproduces its synthetic demo; byte equality does not establish accessibility or every browser interaction. A fresh repository-local installation was recognized by Codex CLI 0.160.1 through native skills/list metadata, without any inference request. An actual hidden-terminal entry smoke with a synthetic key and fake child verified no input echo and child-only transfer. Launcher unit tests use synthetic keys and a mocked host; they establish child-environment transfer, no key in arguments/output, refused noninteractive entry, absent automatic sending consent and preservation of the parent environment. They do not establish provider connectivity or native-host compliance.

The maintainer adopted [MIT](../LICENSE) for original project work on 2026-10-06, with third-party rights retained in [NOTICE](../NOTICE.md). See [distribution](DISTRIBUTION.md) for build versus publication and internal-handoff boundaries. The maintainer confirmed revocation of the potentially exposed old key on 2026-10-06; no key value or account credential was inspected. New exports remain independently scanned. No production accuracy rate, threshold calibration, human-validation claim or real-world coaching effectiveness is established.
