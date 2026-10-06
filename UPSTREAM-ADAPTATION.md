# What was retained, removed, and rebuilt

**Architectural source:** EveryInc/compound-writing, commit `8fd0ec88c00976cf0274cb76552dc7ad9405ca92`, upstream manifest version 2.4.1. The primary book was read first; the upstream architecture and governing workflows were then inspected. This is a fresh implementation of the useful patterns, not a blind search-and-replace or a vendored copy of the repository.

| Upstream surface or pattern | Compound Intelligence implementation | Decision |
|---|---|---|
| `cw-scribe` context-first front door | `compound-intelligence` | Retained orchestration pattern; rebuilt diagnosis and outcome routing around the 21 management challenges. |
| Context contract and authority order | `references/context-contract.md` | Retained maintained-source preference and write safety; explicitly separated instruction authority from factual evidence. |
| Full toolbox, progressive disclosure | Chapter cards with internal `ci-` aliases (0.2) | Retained. The main skill is usable without memorizing specialist names. |
| `VOICE.md`, `STYLE.md`, optional audience guide | `CONTEXT.md`, `PRINCIPLES.md`, `PRACTICE.md` | Replaced with genuinely different responsibilities; not renamed writing profiles. No colleague personality database. |
| Writing-home setup and no-overwrite creator | `ci-setup` and a new `create_home.py` | Retained opt-in portable-home pattern; fresh standard-library implementation with dry-run, add-missing, and path safety checks. |
| Draft folders and curated writing examples | Authorized case records and anonymous practice examples | Rebuilt around actions, observations, and learning. Existing workspaces retain their conventions. |
| `cw-save` | `ci-save` | Retained exact destination and confirmation; added scoped experiments, counterevidence, privacy, and process/outcome distinctions. |
| `cw-final-pass` | `ci-review` | Rebuilt as action-readiness assessment. Publication polish and readiness are removed. A review never authorizes a real-world action. |
| `cw-panel` | `ci-panel` | Retained selective review and synthesis; replaced literary reviewers with the three book pillars. No claim that model consensus is evidence. |
| `cw-debate` | `ci-debate` | Retained bounded challenge and resolution; preserves unresolved value trade-offs and stops for missing evidence. |
| `cw-emergent` | `ci-compose` | Retained outcome-driven composition; does not invent a new source framework or a nonexistent tool. |
| Canonical `skills/`, dual packaging, optional agents | Self-contained canonical main skill, internal specialists, three review adapters, manifests | Retained cross-runtime source-of-truth design; also emits a portable single-skill archive. |
| Legacy help commands | `ci-help` | Handled inside the main skill; no duplicate command logic. |
| Thesis, hooks, prose generation, developmental/line editing, voice matching, AI-pattern removal, literary personas | None | Removed. Chapter 10 remains because leadership communication is part of the book, not because the old writing engine was retained. |
| No equivalent mandatory educational contract | `coaching-contract`, `ci-learn`, `ci-rehearse`, `ci-reflect` | Added from the user’s educational requirement, informed by GUIDE, Show and Explain, and Reflect, Repeat, Remind. |

## Explicit departures and safeguards

The book’s framework names and central moves are preserved, but the software layer must not pretend to possess clinical authority, legal knowledge it has not verified, or authorization to decide employment outcomes. Employment-process support stays with accountable humans. The package will not call an exit mutual unless true, create false social proof, infer private motives as facts, or label a strained employee from a brief account.

These safeguards, the routing algorithm, example dialogue, teaching format, and learning-record schema are implementation additions. They are not silently presented as the author’s words or scientific findings.

## Source versus product claims

The book’s notes were read, not independently audited. Role-model narratives are not converted into proof that a move always works. Static tests can verify packaging and file safety; they cannot establish the correctness of every future model response or the effectiveness of this coaching product.

## 0.2.0 decision-layer addition

The 0.1 chapter/toolbox knowledge is preserved, while only the main skill remains discoverable. TypeSafe integration adds an optional executable decision-support layer, not a change to Webb's source methods. See the [public validation record](docs/PUBLIC-VALIDATION.md) for evidence limits and the [development guide](docs/DEVELOPMENT.md) for implementation boundaries. The runtime is internal to the selected skill and does not override native Codex discovery.
