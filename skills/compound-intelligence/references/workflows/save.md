# Save only approved, scoped learning

**Architecture:** adapted from Compound Writing’s maintained-context learning contract. **Book foundation:** Reflect, Repeat, Remind; process/outcome distinction. Status fields, consent checks, and privacy restrictions are implementation design.

## Classify before writing

An explicit lasting preference belongs in the governing `CONTEXT.md`. A user-endorsed decision principle belongs in `PRINCIPLES.md`. An approved reusable practice rule belongs in `PRACTICE.md`. A one-case observation or uncertain explanation stays in `cases/<slug>/reflection.md` or the user’s existing case record. Use existing equivalent files, not a second memory system.

Do not save a raw sensitive conversation, health information, protected traits, or an inferred colleague motive as a rule. Convert an approved useful insight into a minimal, anonymous behavioral rule about the user's own practice. If that would change its meaning, do not store it in a general practice record.

For a case snapshot or manual follow-up, use [case continuity](resume.md). It preserves proposals, agreed plans, attempts and outcomes separately. Snapshot-only permission allows no later overwrite; ongoing permission is limited to the actual authorized case, destination and content scope. Case persistence does not approve a general practice lesson.

## Decide how far it can generalize

Distinguish **explicit preference**, **endorsed principle**, **provisional experiment**, **supported local pattern**, and **retired or contradicted rule**. One good result is not a supported local pattern. Several relevant observations may support a narrow pattern, but still preserve context, alternative explanations, counterexamples, and the user’s judgment; there is no magical minimum sample count.

A user’s direct instruction to save a stated rule at a clear permitted destination authorizes that narrow write. If the lesson is inferred, present the exact proposed rule and its scope for approval first. Do not ask again when the user already approved that exact content. Never promote a tentative explanation to source guidance or quietly rewrite the book card.

## Minimum learning record

Use the [practice-record template](../../assets/practice-record-template.md) or the existing project format. Record: the atomic rule; kind and status; where it applies; trigger and action; why it might help; source framework and chapter when relevant; observed evidence and its limits; counterexamples or conditions where not to use it; explicit approval; updated date; and a proposed review trigger. Unknown information stays unknown. The [JSON schema](../../assets/practice-record.schema.json) is optional for structured records, not a requirement to create a database.

## Perform the write safely

Resolve the actual destination and check permissions. Read it first. Update the narrow relevant section, preserving user-authored material and recording contradictions rather than silently dropping them. No writes inside the installed skill, plugin, or cache. No automatic edits to shared policies or high-authority principles outside the user’s authorization.

After a successful write, report the exact rule, destination, and status. If storage is unavailable or permission is absent, return **Proposed entry — not saved**. Do not imply platform memory was changed or that future sessions can retrieve anything beyond the accessible maintained record.

Do not add automatic periodic monitoring or a reminder. An explicit scheduling request uses actual available scheduling tools separately from saving the lesson.


## Shared requirements
Follow the [context](../context-contract.md), [coaching](../coaching-contract.md), and [safety](../safety.md) contracts. Use only the [chapter cards](../routing.md) needed for the requested outcome.
