# Architecture — Compound Intelligence 0.3.2

## Boundaries

One discoverable skill contains a book-grounded knowledge library and an optional executable decision layer. The generative host remains the coach. Jev answers narrow questions; the local program composes an advisory decision. Neither has authority to decide consequential employment outcomes or take external actions.

```text
skills/compound-intelligence/
├── SKILL.md                  # Single entry point and coaching procedure
├── agents/openai.yaml        # Codex display / implicit-discovery metadata
├── references/
│   ├── cards/                # 21 preserved source cards
│   ├── workflows/            # Learn, rehearse, reflect, review, save, etc.
│   ├── decision-runtime.md   # Runtime contract and limitations
│   └── source-index.*        # Book source locations and provenance
├── assets/decision/
│   ├── cards.json            # Fit boundaries, aliases and source hashes
│   ├── policy.json           # Explicit uncalibrated policy defaults
│   ├── state.schema.json
│   ├── receipt.schema.json
│   └── example-state.json
└── scripts/
    ├── install.py            # Explicit complete-folder installation; no overwrite
    ├── launch_codex.py       # User-run hidden key entry into a new host process
    ├── ci.py                 # Local CLI; no third-party runtime dependencies
    ├── create_home.py        # Existing optional no-overwrite learning home
    ├── case_file.py          # Explicit scoped Markdown writes; no coaching decisions
    └── ci_runtime/
        ├── state.py          # Validate/minimize/limited redaction
        ├── questions.py      # Preflight + postflight contracts
        ├── client.py         # HTTP / typed-response validation / bounded retry
        ├── policy.py         # Explicit advisory decision composition
        ├── engine.py         # Route, review, receipts and reflection
        ├── metrics.py        # Offline per-contract Noul reliability
        └── common.py         # Hashing, bounded input and safe writes
```

## Runtime path

The host first selects the main skill through its native discovery mechanism. The skill chooses a workflow and follows the [case-understanding procedure](skills/compound-intelligence/references/context-contract.md#understand-one-case-before-selecting-advice): a free opening when needed, a working brief from the available conversation, and one question at a time only when it changes the next move. Corrections update the brief. This phase is agent-led; it adds no Jev calls, state fields or persistent case store. An already clear request or source lesson needs no intake interview.

The brief then feeds the existing method selection. A direct source lesson can bypass Jev. Otherwise, a minimized packet is validated locally. Consent and data-class checks precede any network call. A preflight clarification returns to the same brief; it does not start a second intake. Changes to the packet invalidate its prior routing receipt. Readiness for advice is distinct from action taken or outcome achieved.

One preflight request asks ten contextual questions and 21 independent fit questions. This permits multiple or zero relevant methods. No large-catalog tournament or generated chain of diagnostic decisions is required for 21 cards. Python checks the response contract and produces a suggestion, clarification path, out-of-scope path, human boundary, or local fallback.

The host reads full candidate cards, checks the original evidence, and normally applies one primary method plus at most one distinct support. It explains the choice as coaching. Three retrieved candidates are not three mandatory frameworks. A source-selection override is visible in a review receipt instead of being hidden.

Optional postflight receives the new draft and the actual summary cards used to produce it. A new call is justified because this evidence did not exist during preflight. Eight quality checks lead to an advisory pass, one targeted revision, or narrowing/human review. A failure to call the provider is not a pass. The host still owns final text delivery: a native skill cannot enforce these steps as a hard process boundary.

## Compounding

Approved receipts and user-reported reflections can support later evaluation. No automatic model training, threshold tuning, causal attribution, or installed-skill rewriting occurs. Reliability metrics are computed separately by model, question version/hash, state schema, question and data split. Development and held-out test cases may not overlap.

The book's Reflect, Repeat, Remind practice loop is preserved. The additional receipts and evaluation machinery are software design, not newly discovered book frameworks.

## Manual case continuity — unreleased MVP

After useful preparation, actual user authorization can retain one compact Markdown case outside the installed package. On a manual return, the host loads the [resumption workflow](skills/compound-intelligence/references/workflows/resume.md), reads the current user-identified record and compares the earlier position with the new attributed account. A proposal, an adopted plan, an actual attempt and an outcome remain separate. Corrections update current evidence; conflicting reports remain unresolved. Material information can change the next move; a new detail alone need not.

The [case template](skills/compound-intelligence/assets/case-record-template.md) retains current understanding, the relevant pre-attempt position and the latest return, rather than an unlimited conversation log. Snapshot-only permission does not authorize later updates. Existing ongoing authorization is reused only for that case, path and scope; general lessons need their own approval.

The standalone standard-library helper checks explicit case/path/section grants, uses exclusive creation, and checks the read digest before replacing a file. Stale reads require reconciliation with actual user edits. These are local I/O protections, not proof of user consent, semantic correctness or atomic isolation from hostile writers. The host can use normal file tools for existing equivalent formats under the same contracts. No new Jev/state/receipt field, model call, automatic retrieval or UI is introduced. The MVP has offline persistence checks; real coaching continuity and effectiveness remain untested.

## Optional final-response presentation

The separate `presentation/` component consumes an already-decided `ci.presentation.v1` packet after the host completes applicable review. Its Python standard-library renderer validates structure, escapes all supplied text and creates a private standalone HTML artifact. It does not import the runtime, select methods, generate coaching or call a provider.

The default `workspace.html` keeps advice, the active task and the selected reference adjacent. The earlier `page.html` remains an alternate template. Notes export/import is a local file workflow; it does not approve a lesson or update skill memory. The authoritative component remains separate in the full project; its renderer and default template are bundled with the portable skill and invoked only after advice/review. See the [presentation guide](presentation/README.md) and [development guide](docs/DEVELOPMENT.md).

## Deliberate non-features

No global Codex interception hook; no native model replacement; no autonomous HR workflow; no automatic email/calendar action; no raw-book upload; no hidden memory or global case cache; no adaptive model switching; no training endpoint; no claims of prompt-injection immunity; no claim that probability equals permission. Large-catalog retrieval, empirically calibrated thresholds, independent coaching-quality evidence, and hard harness enforcement remain possible future work, not shipped capabilities.

See [development boundaries](docs/DEVELOPMENT.md), [runtime details](skills/compound-intelligence/references/decision-runtime.md), and [validation](docs/PUBLIC-VALIDATION.md).
