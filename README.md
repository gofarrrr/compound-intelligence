# Compound Intelligence · 0.3.0 (experimental)

**Prepare a leadership move. Try it. Return with what happened.**

An experimental coaching skill for Codex, grounded in 21 methods from Caroline Webb's *Leadership Intelligence*. It helps you work through one situation, understand why a move fits, and revisit the plan when reality brings new information.

Version **0.3.0** packages manual case continuity and first-use installation/Jev onboarding. It is a preview for trying the coaching workflow, not a demonstrated upgrade in advice quality. Our small synthetic comparison did **not** establish that the core skill gives better single answers than the same strong model without it. Continuity has passed implementation checks and a fictional walkthrough; its value to real users remains unmeasured. See [validation](docs/PUBLIC-VALIDATION.md).

## Download and start

**[Download the portable skill ZIP](https://github.com/gofarrrr/compound-intelligence/releases/download/v0.3.0/compound-intelligence-v0.3.0-skill.zip)** · [All release assets and checksums](https://github.com/gofarrrr/compound-intelligence/releases/tag/v0.3.0)

You need Codex CLI (installed and signed in) and Python 3.10+. Extract the ZIP, open a terminal in its `compound-intelligence` folder, then run:

```bash
python3 scripts/install.py
```

The full skill is copied to your user-level Codex skill folder. Existing copies are preserved: the installer refuses to overwrite them.

**With Jev:** create your own key in the [TypeSafe dashboard](https://console.typesafe.ai/), then run this yourself in an interactive terminal:

```bash
python3 "$HOME/.agents/skills/compound-intelligence/scripts/launch_codex.py" --jev
```

Paste the key only at the hidden prompt. It stays in the new process's environment, not a file or the model prompt. The launcher makes no TypeSafe call and does not enable standing sending consent. Follow the [onboarding guide](skills/compound-intelligence/references/onboarding.md) to check readiness and explicitly approve an optional synthetic connection test. Real case/draft transfers need their own approval and may incur usage.

**Without Jev:** use the same launch command with `--local`. No TypeSafe account or key is required. Your normal AI host account and processing still apply.

On Windows use `python` and the installed user path. macOS launcher behavior is checked; Windows and native desktop installation remain untested. See [installation](docs/INSTALLATION.md) for repository-local and manual paths.

Then ask Codex:

> $compound-intelligence Help me prepare a conversation about two missed handoffs. I want to understand what happened and agree on the next one. Ask before sending a minimized packet to TypeSafe.

There is exactly one discoverable skill; the 21 methods are internal cards. Keep its references, templates and scripts together.

The host uses the conversation, asks only questions that could change the next move, and reads relevant cards and examples. The answer should give you a concrete move, explain why it fits, and teach one useful distinction. A straightforward task should not require a framework or a full interview.

No TypeSafe account or key is required for this path. You still use your own AI host and its normal account; local helper execution does not mean the host model or its chat history stays on your computer. Start with the [quick start](docs/QUICKSTART.md) and [privacy boundaries](docs/PRIVACY.md).

## Save once, return when ready

Saving is optional. Ask to review a compact case snapshot, then authorize its contents and a user-owned Markdown destination outside the installation. Approving a plan is separate from approving a file write.

Later, bring that file back:

> $compound-intelligence Resume the case in this file. Here is what I actually tried and what I learned: … Show what changed, what did not, and what to do next. Do not update the file yet.

The host reads the current record before helping. A proposed plan stays distinct from an actual attempt; another person's reported account stays attributed. You can return without having tried the plan. New information may change the next move, or leave it intact for an explicit reason.

The [resumption workflow](skills/compound-intelligence/references/workflows/resume.md), [case template](skills/compound-intelligence/assets/case-record-template.md) and scoped file helper support this experience. A snapshot-only save does not permit later updates; updates need actual authorization covering the same case, destination and sections. This is manual continuity, with no case database, automatic retrieval, person profiles or scheduled reminders.

## What supplies the knowledge

All **21 Webb cards are preserved byte-for-byte from 0.1.0**. They include fit boundaries, source pages, practical moves, practice and misuse warnings. The [source index](skills/compound-intelligence/references/source-index.md) separates book methods from original coaching and software adaptations.

The host selects the smallest useful material, normally one primary method and at most one support. Broader book research and the mental-model inventory remain internal research, not a library loaded into every answer. Worked examples illustrate intended behavior; they are not evidence of successful coaching.

## Optional components

- **TypeSafe/Jev:** advisory method shortlisting and draft checks. Use your own key and explicitly approve the outgoing case/draft. [Onboarding](skills/compound-intelligence/references/onboarding.md) explains hidden key entry, environment inheritance and optional live testing. These calls can incur usage; they are not required for coaching or manual continuity.
- **HTML workspace:** a separate [presentation component](presentation/README.md) renders already-decided advice beside practice and references. Try the [synthetic demo](presentation/examples/handoffs.html). It adds no advice, model calls or automatic learning and is outside the portable skill.

The active postflight contract is `ci.postflight.v2.1.0` with G adopted. H is unpromoted, the assertion cutoff stays strictly **> 0.25**, policy remains `ci.policy.v2.0.0`, and review permits at most one revision. These are advisory, uncalibrated policies, not authority to act on people. See [release notes](skills/compound-intelligence/references/release-notes.md) and [runtime details](skills/compound-intelligence/references/decision-runtime.md).

## Help us test the return experience

Try one real situation, optionally save a snapshot, and return with what actually happened. We want to learn:

1. Did CI correctly recall where you were?
2. Did it understand what changed?
3. Did that make the next decision easier?

Useful feedback describes the missed distinction or unnecessary step. Share a minimized or fictional reproduction, host/version and whether Jev was used. Keep personal case files, identifying details, credentials and provider receipts out of public issues. The workflow aims to support practice and transferable learning; no coaching-effectiveness claim is established.

## For contributors and packagers

Read [development](docs/DEVELOPMENT.md), [architecture](ARCHITECTURE.md) and [distribution](docs/DISTRIBUTION.md). Run `python3 -m unittest discover -s tests -v` for offline checks. Internal maintainers also read `docs/SESSION-HANDOFF.md` when available.

The public builder creates two formats from explicit file lists: a self-contained **portable skill** for users, and a **full project/plugin** with source, tests, presentation and curated documentation. Build into a new external directory with `python3 scripts/build_releases.py --output /absolute/path/to/new-directory`. Never publish a ZIP of the entire development folder: it contains internal material that belongs outside the public packages.

Public exports exclude original book files, personal cases and credentials. The original project work uses the [MIT license](LICENSE), adopted 2026-10-06. [Rights and provenance](NOTICE.md) distinguish the book and third-party rights from our implementation; the project license does not relicense those materials. This independent project is not endorsed by Webb, Every, TypeSafe or OpenAI. A local build is not publication or proof of real-world effectiveness.
