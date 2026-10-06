# Compound Intelligence — portable 0.3.2 (experimental)

Prepare a leadership move, try it, and return with what happened. One visible skill provides 21 preserved book-based methods, optional TypeSafe/Jev support and a manual case-return workflow. Start with [SKILL.md](SKILL.md). Keep this entire folder together; importing only the manifest loses the source cards and executable helpers. Version 0.3.2 packages the manual continuity MVP and first-use installation/Jev setup. It is an experimental preview, not a demonstrated advice-quality upgrade.

This release uses `ci.postflight.v2.1.0`, the evaluated G assertion clarification. H remains unpromoted; thresholds and authority rules are unchanged. The [release notes](references/release-notes.md) record the maintainer decision, residual flags and limits of the synthetic/AI-review evidence.

The main skill selects a useful method, applies it to the supplied evidence, explains the coaching move and leaves a small practice or observation. Ask for a lesson, rehearsal, or reflection in the same conversation. `ci-feedback`, `ci-delegate`, and other legacy names are internal aliases, not separate skills to install.

## Install and start

You need Codex CLI (installed and signed in) and Python 3.10+. No third-party Python packages are required. From this extracted folder:

```bash
python3 scripts/install.py
```

This copies the full skill to `$HOME/.agents/skills/compound-intelligence`. It refuses to overwrite an existing installation. For repository-local use, pass `--destination /your/repo/.agents/skills/compound-intelligence`. Keep user case files outside the installation.

For Jev assistance, get your own key from the [TypeSafe dashboard](https://console.typesafe.ai/), then **run this yourself in an interactive terminal**:

```bash
python3 "$HOME/.agents/skills/compound-intelligence/scripts/launch_codex.py" --jev
```

The launcher uses an existing environment key or asks for hidden terminal entry. The key goes into the new Codex process's environment, never its prompt or a key file. It starts without reusing an old daemon and without inherited standing permission to send cases. It makes no TypeSafe calls itself. Read [onboarding](references/onboarding.md#recommended-launch-codex-with-jev) for connection testing, provider consent, failure handling and manual/desktop alternatives. Never paste your key into chat.

For coaching without Jev:

```bash
python3 "$HOME/.agents/skills/compound-intelligence/scripts/launch_codex.py" --local
```

On Windows use `python` and the installed user path. The launcher was exercised on macOS; native desktop and Windows installation were not tested. Codex's own model/account processing and retention still apply.

Inside Codex invoke `$compound-intelligence` or select `/skills`, then describe one situation. Example:

> $compound-intelligence Help me prepare a factual conversation about two missed handoffs. Explain one useful next move. Ask before sending any minimized packet to TypeSafe.

No account or key is required for the local path. A key alone does not authorize a provider request. Connection tests may incur TypeSafe usage; an unavailable response is a fallback, not a successful judgment. `python3 scripts/ci.py doctor` checks presence/files without a call; `demo` uses canned values, not Jev inference. The CLI returns decision data; the host writes advice.

## Details and limits

Read the [runtime guide](references/decision-runtime.md) for consent, API inputs, fallback, draft checks, receipts and model boundaries. The [routing guide](references/routing.md) covers all 21 challenges; the [source index](references/source-index.md) preserves chapter/page references. [Worked examples](references/examples/README.md) illustrate intended coaching, not tested model outputs.

The preflight batches ten contextual questions and 21 independent fit checks. It offers a shortlist rather than a hidden-cause diagnosis. Thresholds are uncalibrated starting policies. Restricted cases stay local. A key alone does not approve data transfer; the limited redaction filter is not full anonymization. Jev does not run before native Codex discovery and cannot force the host to obey the returned suggestion.

No memory or learning-home setup is needed for advice. [Save](references/workflows/save.md) and [setup](references/workflows/setup.md) remain explicitly authorized operations outside the installed folder. Reflection is provisional, not causal proof or automatic retraining.

## Return to a case

With your permission, the host can retain a compact Markdown case at a location you choose. Later, bring that file and describe what you actually tried or learned. The host reads the current record, compares it with the earlier plan, and explains why the next move changes or stays the same. You can return without having tried the plan.

> $compound-intelligence Resume the case in this file. Here is what I actually tried and learned: … Show what changed, what did not, and what to do next. Do not update the file yet.

The [resumption workflow](references/workflows/resume.md) and [case template](assets/case-record-template.md) keep proposals, agreed plans, attempts and attributed outcomes distinct. Saving a snapshot permits only that save; ongoing updates require an agreed case, destination and content scope. The optional [file helper](scripts/case_file.py) checks that scope and detects stale reads. It does not establish consent or interpret the case. No automatic search, reminder or person profile is created. Offline persistence checks do not establish coaching effectiveness.

This portable form has the same runtime and cards as the full project. The full project additionally includes manifests, tests, migration notes and evaluation tools. Both keep one visible skill. No EPUB, original PDF, API key or private case record is included. See [attribution](NOTICE.md).

The core-versus-plain-host synthetic comparison produced 1 skill win, 1 plain-host win, 11 ties and 2 unusable judgments across 15 pairs. It did not demonstrate the required single-answer advantage. Continuity has passed implementation review and a fictional I/O walkthrough; no real-user benefit or coaching effectiveness is established. Feedback should tell us whether the return recalled the prior position, understood new information and made the next decision easier. Use fictional or minimized reproductions in public feedback; do not upload case records or keys.

Primary references: [TypeSafe API](https://docs.typesafe.ai/api), [Codex skills](https://learn.chatgpt.com/docs/build-skills). Local Codex skill paths checked 2026-10-06; fresh local installation and Codex metadata discovery passed without inference. Live coaching and provider connectivity were not tested in the build. Original project work uses the [MIT license](LICENSE), adopted 2026-10-06; third-party rights retain their scope in [NOTICE](NOTICE.md).

## Interactive workspace

The portable ZIP includes the existing HTML renderer and chosen workspace design as a separate component. When a plan is ready, the host offers a workspace; ask for it directly if wanted. See the [presentation workflow](references/workflows/presentation.md). It displays already-decided advice, with task tabs, adjacent references and explicit notes export/import. Saving a case remains separate. A direct GitHub installation of only this subfolder omits the sibling component: use the portable release ZIP or the full repository installer for the complete experience.
