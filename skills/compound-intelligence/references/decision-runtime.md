# Decision runtime — package 0.3.1

This is implementation design, not a Caroline Webb framework. The canonical runtime is [ci.py](../scripts/ci.py); all referenced files are inside this portable skill.

## Division of work

| Component | Responsibility | Not its responsibility |
|---|---|---|
| Book cards | Frameworks, fit boundaries, coaching principles and source locations. | Proof that a particular recommendation will succeed. |
| Jev | Narrow semantic judgments over supplied, minimized evidence. | Hidden causes, motives, clinical diagnoses, permission, or prose coaching. |
| Python policy | Validate responses, exclude disallowed routes, preserve uncertainty, produce a bounded shortlist. | Making consequential decisions about people. |
| Host LLM | Read evidence and selected cards, reason through the case, apply and teach. | Treating its own confidence as evidence or blindly obeying a routing hint. |
| User / organization | Goals, consent, authoritative decisions and external actions. | Being silently replaced by the classifier. |

The preflight is one request with **10 contextual questions plus 21 independent card-applicability questions**. See [questions.py](../scripts/ci_runtime/questions.py) and [card registry](../assets/decision/cards.json). A 21-card catalog does not require a multiround tournament. Larger future catalogs may warrant retrieval first; that is not implemented here.

We use **Noul for independent applicability**, not a 21-way forced Choice. Several methods can be relevant at once, and none can fit. Score rates the specificity of supplied evidence on the declared **0–2** scale. Choice is supported by the HTTP response validator and exercised by the synthetic live smoke check, but is deliberately not used to force this multi-label routing problem into one class.

## Ten contextual questions

| ID | Type | What it checks | How code uses it |
|---|---|---|---|
| leadership_relevance | Noul | Whether the request concerns this library's scope. | Can return no book fit. |
| evidence_quality | Score | Specificity of a bounded case or explicit learning goal, not a person's competence. | Thin evidence prompts clarification. |
| motive_attribution | Noul | Unsupported claims about another person's motives/character. | Combined with a missing perspective, favors inquiry. |
| missing_perspective | Noul | Relevant other-person information is absent. | Keeps uncertainty visible; does not always force a question. |
| self_reported_pressure | Noul | The user explicitly reports acute pressure they want help with. | May add a short reset as support. |
| structural_overload | Noul | Continuing team demands exceed time/resources. | Puts work/capacity before a mindset-only solution. |
| colleague_struggle | Noul | Reported difficulty with context not yet understood. | Adds a supportive-inquiry fit check, not a diagnosis. |
| consequential_action | Noul | The request asks the assistant to decide employment outcomes. | Human-review boundary; never grants authority. |
| immediate_harm | Noul | Supplied text indicates a need for support/incident handling. | Human-support route; not a complete safety detector. |
| completed_attempt | Noul | An action and outcome already happened. | Checks whether reflection has an actual attempt to learn from. |

Each `fit_01`–`fit_21` asks whether that method is a candidate for the stated objective. Its complete question includes the existing card's “Select this when” and “Route elsewhere when” boundaries. The registry pins each source card's hash. Full cards are loaded by the host only after selection.

The questions are independent API evaluations, not statistically independent evidence. They may overlap or disagree. Code combines them; it never multiplies their values as independent probabilities or interprets a Noul as severity. Question IDs have no hidden instructional meaning: the full question is in `instructions`.

## Running the helper

For initial configuration, follow [onboarding](onboarding.md). It offers local coaching or a user-supplied TypeSafe key, explains hidden terminal entry and environment inheritance, and distinguishes local readiness from an approved live connection test. The agent never collects a key through chat or tool input. No setup command automatically persists credentials, creates a learning home or approves sending a case.

From the containing skill folder:

```bash
python3 scripts/ci.py doctor
python3 scripts/ci.py demo
python3 scripts/ci.py preview --state assets/decision/example-state.json
python3 scripts/ci.py route --state assets/decision/example-state.json --backend offline
```

The demo is explicitly **canned offline data**, not a model prediction. The first API connection check is:

```bash
python3 scripts/ci.py smoke --consent-send
```

It needs `TYPESAFE_API_KEY` already in the environment, sends only a short synthetic learning request, and checks all three response shapes. It may incur usage. No API key is bundled, read from a file, or accepted as a CLI argument.

For an approved anonymized case, add `--backend typesafe --consent-send` to `route`. `auto` requires both an environment key and consent; otherwise it uses local coaching. A user may opt into repeated approved packets for one shell session with `CI_ALLOW_TYPESAFE=1`. Do not set this on their behalf. The host process and its shell must inherit the environment; a terminal variable may not reach a separately launched desktop or cloud process.

## What is sent and stored

The state schema accepts only explicit fields. `case_id` and `data_class` remain local. The model sees a redacted request/goal, attributed observations, interpretations, unknowns, constraints, selected mode, and bounded context flags. Secret-like tokens and email addresses receive limited filtering. **Names, phone numbers, identifying events, and all sensitive meaning are not guaranteed to be removed.** A human-approved packet and provider approval are still necessary. `restricted` is the default classification and is never sent even with consent.

The review call additionally sends the redacted draft and the exact local summary cards used for it; it does not send the EPUB. Review authorization covers that additional draft content, not merely the original case. Preview or inspect it before granting consent when appropriate.

The helper returns a receipt on stdout. It writes only when `--output` names an explicit destination. Persistent receipt and reflection files are owner-only, create-exclusive, and outside the installed package. Parent directories must already exist. No automatic chat-history store, global cache, training upload, background hook, or hidden memory is present. Host transcripts and terminal capture remain subject to the host's own data handling.

Receipts contain model-requested/model-returned IDs, complete validated answers, token usage, transport attempts/timing, contract hashes, source references, reason codes and the selected branch. They omit raw case/draft text but can still reveal sensitive classifications. Source/state/question changes invalidate reuse. The integrity hash detects accidental changes; it is **not a signature or a security boundary against someone who can rewrite the file**. Review receipts expire for reuse after 24 hours; a changed real situation needs new state even sooner.

## Policy and uncertainty

[policy.json](../assets/decision/policy.json) contains visible engineering defaults. They are **not fitted to representative leadership cases**. The API's confidence statistic is derived from its returned distribution, not independent evidence. Several high card-fit Nouls may indicate complementary methods, not uncertainty within a mutually exclusive distribution.

A low or ambiguous result means compare candidates, clarify, or use qualified local coaching. It does not prove that a method is wrong. Even a clear suggestion requires a host fit check. The normal retrieval budget is three candidates, while the application budget remains one main method and at most one distinct support. Chapter 20 cannot enter the ordinary candidate set without a user-reported confirmed process and communication-only intent. Source teaching of Chapter 20 remains available.

Use `--rollout shadow` to obtain a proposed route without using it to guide the coaching answer. The host must honor `effective_decision`, not leak the experimental proposal into its advice. Shadow mode still sends the packet to TypeSafe when the live backend is enabled; “shadow” means no routing effect, not no network.

## Failure handling

The client uses a fixed HTTPS endpoint and refuses redirects. It validates answer IDs/types, finite numeric ranges, distribution sums, score legends/weighted scores, and model pins. It whitelists returned fields and never prints provider error bodies. A timeout, malformed response, invalid key, or missing answer returns an observable fallback with no fabricated model values.

The default transport permits at most two attempts, a ten-second socket timeout per attempt, and a 22-second best-effort request budget. It retries selected transient statuses and network failures, not authentication, billing or malformed-request failures. It honors Retry-After only within that budget; it does not shorten the provider's requested delay. OS/DNS/socket behavior means this is not a hard realtime latency guarantee. A retried POST may have been processed before the response was lost, so usage may exceed one billed evaluation.

An API success validates the exchange, not correctness or source effectiveness. `advisory_pass` is not permission. Failed postflight can request one revision, then a narrower answer or human review. Provider outages fall back to a manual review; they never produce an automatic pass.

## Postflight contract v2.1.0

The assertion question includes the evaluated G clarification: recommendations, imperatives, questions and practices do not assert that an event occurred merely by proposing it. An unsupported fact, cause, permission or promised outcome embedded in advice still counts. The other seven questions, including the original framework-load rubric, are unchanged. H is not included.

The question digest is `aafdc55c31551ada8d9c40d7fa18a14d6338a6e1876b40ab26ba48cb8e411dd0`. Policy remains `ci.policy.v2.0.0`, with the uncalibrated assertion cutoff strictly greater than 0.25 and at most one revision. This contract improves an evaluated semantic boundary; it does not establish calibrated accuracy, authorization or coaching effectiveness.

Known advisory limitations include grounded, dense framework advice and recommendations to discuss reassignment while checking approval authority: both can still trigger an assertion flag. A flag is not a sentence-level finding. Inspect the supplied evidence and draft, distinguish assertion support from goal fit and agency, and use the existing finite revision or narrower/manual review path. Do not resample until a convenient pass appears. Unrelated utility outputs should follow the ordinary task path when coaching scope is absent.

## Where this integration stops

This skill runs **after native Codex skill discovery**. It does not intercept every message or replace the host's global skill router. It has no native-host hook, MCP server, side-effect executor, or independent generative model. Code computes a proposal and the skill instructs the host to apply its constraints; the native host ultimately controls whether the helper is called and what answer is sent. A custom wrapper would be needed for hard workflow enforcement.

Official implementation references, checked 2026-10-02: [API contract](https://docs.typesafe.ai/api), [primitives](https://docs.typesafe.ai/primitives), [confidence](https://docs.typesafe.ai/confidence), [coding-agent boundary](https://docs.typesafe.ai/introduction/coding-agents), [model/version notes](https://docs.typesafe.ai/models). The supplied independent field guide informs the state/decision/LLM/policy separation; its recommendations do not independently validate this implementation.
