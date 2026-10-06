# Quick start — 0.3.0 experimental preview

Version 0.3.0 includes manual case continuity and installation/Jev setup helpers. Start with local coaching and manual return. TypeSafe/Jev is optional. No personal key or additional Python libraries are needed for the local path; executable helpers require Python 3.10+.

## 1. Install the complete skill

[Download the portable ZIP](https://github.com/gofarrrr/compound-intelligence/releases/download/v0.3.0/compound-intelligence-v0.3.0-skill.zip), extract it, and open a terminal in its `compound-intelligence` folder:

```bash
python3 scripts/install.py
```

For Jev, get your own key from the [TypeSafe dashboard](https://console.typesafe.ai/) and launch from your own interactive terminal:

```bash
python3 "$HOME/.agents/skills/compound-intelligence/scripts/launch_codex.py" --jev
```

The hidden prompt accepts your key without writing a file or putting it in chat. The new Codex process checks local readiness and asks before an optional synthetic connection test or real provider transfer. The launcher itself makes no TypeSafe calls. [Onboarding](../skills/compound-intelligence/references/onboarding.md#recommended-launch-codex-with-jev) explains details and host-policy limits. Replace `--jev` with `--local` to start without an API key. On Windows use `python` and the installed user path; that installation has not been exercised here.

Follow [installation](INSTALLATION.md). From the full project, install `skills/compound-intelligence/`; from the portable archive, install the extracted `compound-intelligence/` folder. Keep the entire folder together and avoid duplicate installations.

Codex user-level skills go under `$HOME/.agents/skills/compound-intelligence`; repository-local skills go under `.agents/skills/compound-intelligence`. Invoke `$compound-intelligence` or select it with `/skills`. Discovery and installation instructions follow the [official Codex guide](https://learn.chatgpt.com/docs/build-skills), checked 2026-10-06. A fresh local install and Codex native skill discovery were checked without inference. Live coaching and provider connectivity were not tested during this build.

## 2. Bring one situation

> $compound-intelligence I need to talk with a teammate about two missed handoffs. I want to understand what happened and agree on the next one. Keep the case local; do not call TypeSafe.

Describe the outcome you want, what you observed or were told, and any important constraints. You do not need to know the book or fill out a form. The host should ask only if the missing answer could change the next move. It should provide a useful opening or action, explain its fit, and leave one small practice or observation.

“Local” here means no TypeSafe transfer and local file helpers. Your normal AI host may still process the conversation remotely. See [privacy](PRIVACY.md).

## 3. Optionally save a case

> Show me a compact case snapshot to review. Keep my interpretations separate from reports, and keep the proposed plan separate from an attempt.

After checking it, authorize one save to a specific Markdown path in a user-owned folder outside the installed package. The folder must exist. The host may use the [case helper](../skills/compound-intelligence/scripts/case_file.py) to check scope and report an actual successful write.

Example instruction, with your real path substituted:

> Save this reviewed snapshot once to `/my/coaching-cases/handoff.md`. This permits only this save, not later updates.

Do not use the illustrative path literally. Saving a case is optional; approving advice alone is not permission to save it. No learning-home setup is required.

## 4. Return with what happened

> $compound-intelligence Resume `/my/coaching-cases/handoff.md`. I had the conversation. My teammate said they had requested a priority change earlier. Show the previous position, the new report, what it changes, and the next move. Do not update the file yet.

The host reads the current file rather than interviewing you from the beginning. The new account remains a report, not proof that a request arrived or was approved. You can also return with “I have not tried it” or “nothing material changed.” See [resume](../skills/compound-intelligence/references/workflows/resume.md).

If you want an update, approve its contents and sections. Snapshot-only consent does not authorize overwriting. Existing ongoing consent can cover an update only within its agreed case/path/section scope. A stale read must be reconciled before writing.

After a return, tell us whether CI recalled the prior position, understood the change, and made the next decision easier. Use fictional or minimized examples for public feedback; do not upload private case records.

## Optional local helper check

From the full project root:

```bash
export CI_SKILL="$PWD/skills/compound-intelligence"
python3 "$CI_SKILL/scripts/ci.py" doctor
python3 "$CI_SKILL/scripts/ci.py" demo
```

From the extracted portable folder, use `export CI_SKILL="$PWD"` instead. `doctor` reports key presence without reading it out or making a provider call. `demo` exercises routing with canned values; it is not a coaching session or a Jev accuracy test.

## Optional TypeSafe/Jev

For your own key, use the [onboarding guide](../skills/compound-intelligence/references/onboarding.md). It explains hidden terminal entry, process-environment inheritance, and explicitly approved synthetic connection testing. Do not paste a key into chat or source. A key alone does not authorize sending a case.

Live `smoke`, `route` and `review` calls may incur usage and require approved outgoing data. The [runtime guide](../skills/compound-intelligence/references/decision-runtime.md) contains the commands, packet preview, receipts and fallback behavior. An unavailable provider result is not a successful judgment. Neither optional Jev nor a reminder is needed for manual case return.

## What has been checked

The [validation status](PUBLIC-VALIDATION.md) separates offline checks, synthetic model comparisons and the still-unmeasured continuity experience. The full project's offline checks run with `python3 -m unittest discover -s tests -v`; they make no live calls. No demonstrated single-answer superiority, calibrated threshold or coaching effectiveness is claimed.
