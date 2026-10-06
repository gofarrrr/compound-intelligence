# Final-response presentation MVP

This optional component turns an **already-decided coaching response** into a standalone local HTML workspace. It lives outside `skills/compound-intelligence/`, imports no skill/runtime code, calls no models and adds no discoverable skill. The renderer remains independent of coaching; the portable release now bundles its executable and default template.

Open the [synthetic demo](examples/handoffs.html). Choose **Prepare**, **Practise** or **Reflect**. The next move and transferable principle stay beside the task. Click **Example**, **Evidence** or **Sources** to change the reserved reference panel while keeping your writing in place. Try exporting notes and loading that export. The demo is a source-informed illustration, not a live-reviewed result or effectiveness test.

The user accepted the workspace behaviour on 2026-10-03, then requested a complete visual rebuild using their `DESIGN (2).md` Ramp style reference. Both templates now use the new design; the cream/sage theme has been replaced. A new development session should start with the [development guide](../docs/DEVELOPMENT.md); internal maintainers additionally read `docs/SESSION-HANDOFF.md` when present for the latest checks and stopping point. Keep the JSON fixed for layout experiments and regenerate the checked-in demo deliberately when its template changes.

## Where it belongs

```text
Agent follows Compound Intelligence
    → selects sources, reasons, drafts and completes applicable review/revision
    → final content and any unresolved limitations
    → ci.presentation.v1 handoff
    → presentation/render.py + developer-owned workspace.html
    → local HTML artifact
```

The generative host remains responsible for the coaching. This is a presentation adapter at the end, not another reasoning pass or a routing component. The MVP is explicitly invoked by the host; it is not an automatic end-of-turn hook or native host enforcement.

### Host rules

1. Finish the requested skill workflow and applicable review first. Preserve clarification, no-fit, manual-review and provider-failure outcomes in the final content.
2. Put the final, user-facing content into the handoff. Use existing wording; do not ask a second model to improve, reinterpret or extend it. Any practice example, reflection prompt or qualification must already be part of the prepared content. If new coaching content is needed, return to drafting and applicable review before rendering.
3. Keep the important uncertainty in `notice`, which stays visible across all views. Select `kind` from the host's actual outcome, not a Jev probability. `advice` is a display category, not an approval or correctness certificate. Provider failure that requires a manual check belongs in `manual_review` with an accurate notice.
4. Invoke the renderer with a new, explicitly chosen output path. It validates presentation structure and escapes text; it does not validate coaching correctness, review receipts or source fidelity. On rendering failure, deliver the original final answer in its ordinary text form.
5. Return a link to the HTML artifact and a concise next-move summary so the answer remains useful without opening a browser. Human decisions and action authority remain unchanged.
6. Practice text is not automatically evaluated. Notes are temporary until the user explicitly exports them. Export/import is a local file workflow, not an approved learning rule, saved skill memory, reminder or external action.

An opt-in instruction for a host with access to this repository:

> Use Compound Intelligence for the task. After completing its workflow, read presentation/README.md and render the final content using presentation/render.py. Keep its existing wording and unresolved limitations; include only examples and prompts already prepared. Return the HTML link plus the next move in text.

This instruction requires actual filesystem/tool access. The portable release bundles this component under the installed skill’s presentation directory. Source checkouts retain this sibling directory.

## Render a new brief

From the project root, choose an existing output directory and an unused filename:

```bash
python3 presentation/render.py \
  --input presentation/examples/handoffs.json \
  --output /absolute/path/to/new-brief.html
```

No API key or network approval is needed. Python 3.10+ standard library only. Output files are created owner-only, never overwritten and refused inside the canonical skill. For real cases, keep both the handoff and output in an authorised private location outside the repository; they contain the actual coaching content. The checked-in demo is synthetic.

## Handoff: ci.presentation.v1

The independent presentation version does not change state, receipt, question, policy or package versions. [handoffs.json](examples/handoffs.json) is a complete example.

| Field | Required | Meaning |
| --- | --- | --- |
| `schema_version` | Yes | Exactly `ci.presentation.v1`. |
| `kind` | Yes | `advice`, `clarification`, `no_fit` or `manual_review`; chosen by the host. |
| `title` | Yes | Already-prepared title. |
| `goal` | Yes | The user's actual goal. |
| `notice` | Yes | Material uncertainty, delivery limitations or relevant review status. Always visible. |
| `next_move` | Yes | The decided action or question; plain text and line breaks. |
| `why` | No | Prepared explanation of method fit. |
| `principle` | No | Prepared transferable lesson. |
| `facts` / `unknowns` / `sources` | No | Lists of supplied plain-text statements or source references. Reports must remain reports. |
| `practice` | No | `prompt` and `observe`; optional `example`. All are prepared content, not generated by the renderer. |
| `reflection` | No | `prompt` and `adjustment_prompt`, prepared for reflection after an actual attempt. |

Unknown fields, duplicate JSON keys, incomplete sections, invalid types and oversized inputs are rejected. Each supplied text field is rendered verbatim as escaped plain text; the renderer does not interpret Markdown or user-provided HTML. There is no model score, authority flag or simulated response invented by the page.

An omitted practice or reflection section removes its view. A short clarification can contain only the six required fields; there is no mandatory lesson before answering. The component adds presentation labels and file controls, not new coaching claims.

## Experiment without changing the skill

- Change [workspace.html](workspace.html) for typography, spacing, information hierarchy and interactions. It is developer-owned executable code, not case content. The previous document layout remains in [page.html](page.html), with the same new visual language; select it with `--template presentation/page.html` to compare the same content in the two layouts.
- Keep the handoff fixed to compare presentation variants. Use `--template /path/to/variant.html` and a fresh output filename. The renderer rejects templates that omit supplied text. Preserve the always-visible notice and test the layout when creating variants; checking text inclusion alone does not establish visual accessibility.
- Change the prepared handoff only when experimenting with content. That is a separate coaching/drafting change, with its own applicable review; it should not masquerade as a layout change.
- Keep rendering outside the skill. The root plugin archive includes this development component; the portable skill archive includes render.py and workspace.html from this same source. No duplicate renderer source is maintained.

The design uses Bone (`#f4f2f0`) canvas, white panels, Ink (`#0c0a08`) text and an Obsidian (`#1a1919`) next-move panel. Chartreuse (`#e4f222`) marks the active task and notes export; references use a monochrome selected state. One sans-serif family at weight 400 supplies all headings, labels and controls. The offline font stack prefers locally installed Inter, then Helvetica Neue/Helvetica/Arial; the proprietary reference font is not bundled or fetched. Hierarchy comes from size, surface contrast and spacing. Panels use hairline borders and 12/16px radii, fields 10px, buttons/tags 6px. There are no shadows, gradients or decorative animations; utility transitions respect reduced motion. Compact workspace spacing adapts the editorial guide to the no-backtracking task requirement rather than reproducing a marketing page.

Three stable areas hold the advice, current task and supporting reference. Opening and closing references does not move the editor; changing tasks preserves the selected reference and partial notes. Reflection provides adjacent fields for an actual account and tentative adjustment. It does not build a persistent notebook or automatically generalise a result. The same styling covers the alternate document layout, narrow-screen reflow and printing; print uses a light next-move panel to retain legibility without background printing.

The synthetic demo fits without page scrolling at browser viewports of 1280 × 800 and 1366 × 768 at normal zoom. **Read all** opens a separate reading layout showing every supplied task and reference. Larger content that does not fit automatically uses a vertical layout for the current task instead of being clipped, shortened or made smaller. Selecting a task or reference tries the workspace again. Narrow viewports and enlarged text remain readable in a vertical layout. These are deliberate accessibility fallbacks, not a promise that arbitrary content fits any screen.

## Notes and local behaviour

There is no server, API call, remote font, telemetry, browser autosave or `localStorage`. JavaScript is fixed in the template, and its content hash is allowed by the generated Content Security Policy; network connections are blocked. Case text is escaped rather than inserted as executable code.

**Export notes** requests a browser download of `ci.presentation.notes.v1`: the three text fields and the canonical handoff digest. Check Downloads before closing. Notes are not written into the original HTML. The page warns before leaving with edits, although browsers control whether that warning appears.

**Load an earlier export** validates the entire file before replacing any fields. A digest mismatch rejects notes from another coaching response. Loading over unsaved edits asks for confirmation. Matching a digest prevents accidental case mixups; it is not an authenticity signature. Import/export filenames and browser download behaviour remain browser-controlled.

If JavaScript is disabled, all supplied views remain readable. Printing includes the supplied views. The component cannot semantically evaluate an opening, predict a colleague, communicate with the agent or update learning records. An agent can review deliberately returned notes in a later, explicitly requested workflow.

## Checks

```bash
python3 -m unittest discover -s tests -v
```

The presentation tests cover escaping and content preservation, deterministic rendering, visible outcome notices, incomplete/invalid input, private create-only output and template substitution. These are software checks, not coaching-quality measurements. Browser checks exercise switching, notes import/export and narrow-screen layout using the synthetic demo.

The optional developer browser check uses Node 22+ and an existing Chrome binary; neither is a renderer dependency:

```bash
node presentation/check_browser.mjs
# On another OS, pass the installed Chrome binary as the first argument.
```

It opens an isolated temporary browser profile and uses synthetic notes. It checks no page scrolling at both desktop sizes, keyboard task switching, persistent advice, stable editor position across reference changes, reading mode, long-content reflow, note preservation, file import/export, 390px/320px reflow, printing and script-free reading. Screenshots stay outside the repository. Chrome checks do not certify all browser or assistive-technology behaviour.
