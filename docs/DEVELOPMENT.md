# Development guide

The canonical skill is under `skills/compound-intelligence/`; keep one discoverable SKILL.md. Read [architecture](../ARCHITECTURE.md), the [runtime guide](../skills/compound-intelligence/references/decision-runtime.md) and the affected component's guide before editing. Internal maintainers additionally use `docs/SESSION-HANDOFF.md` when present; private session/research records are not part of public distributions.

## Keep the boundaries clear

The host understands the conversation and writes advice. Jev answers bounded contextual and fit questions; Python composes advisory outcomes. The host reads selected full cards and a relevant example, then checks the actual action. Presentation only renders already-decided content. Native host compliance is not enforced by this package.

One primary method and at most one distinct support keep the advice focused. Unknown cause can justify an invitation without blocking preparation. Authority, available capacity and approval are different prerequisites. A concrete decision brief can be useful before its implementation is authorized. The [worked examples](../skills/compound-intelligence/references/examples/README.md) illustrate these distinctions without importing fictional facts into a live case.

Preserve source-card identity and hashes. Do not silently attach an outside author's procedure or an effectiveness claim to Webb. Add knowledge only when it improves a recognizable decision and has actual source coverage. The internal research corpus is not an installed retrieval service.

## Evaluate changes

Use the [existing evaluation](../evals/README.md) as historical evaluation tooling. The completed internal one-shot comparisons did not demonstrate the required incremental value over a strong plain host. The current direction is a coaching cycle across a real case; do not reopen closed comparisons or claim that their answers establish continuity or effectiveness. Internal authored examples remain illustrations rather than model-run results.

The first continuity MVP uses the [resumption workflow](../skills/compound-intelligence/references/workflows/resume.md), a compact [case template](../skills/compound-intelligence/assets/case-record-template.md) and an optional [file helper](../skills/compound-intelligence/scripts/case_file.py). Load resumption detail only for a save or return. The host decides what the new account changes and verifies actual authorization. The helper checks case/path/section scope and stale reads; it does not make those decisions. Keep the record bounded to current understanding, the relevant prior position and the latest return. No person timeline or automatic case discovery. Offline tests exercise real temporary files; authored semantic deltas are not proof that the host interprets natural language correctly. A live continuity trial needs separate review and authorization.

Run `python3 -m unittest discover -s tests -v` for offline software checks. Live model execution requires a separately approved environment and budget. Preserve failures; do not fit thresholds or silently replace failed answers. Keep saving user lessons explicitly approved.

## Prepare a distribution

Read [distribution policy](DISTRIBUTION.md). Change the explicit public file list deliberately; do not zip the working directory. Both formats must retain their assets and valid links. Public technical evidence is curated separately from internal reports. License choice, credential incident closure and publication remain maintainer decisions; a local build does not satisfy them.
