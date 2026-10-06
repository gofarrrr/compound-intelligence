# Present the prepared next move

This separately invoked renderer presents already-decided content; it does not select methods, call models, evaluate practice or save a case.

When a substantive plan is ready and a workspace would help preparation or a later return, offer the interactive HTML workspace once. If the user already requested HTML, proceed within that request. Respect a text-only preference and a clear wish to finish. Do not turn a thank-you into permission to write files. A short return cue can identify the planned move and what to bring back.

After the applicable advice/review, use the existing renderer, never generate a new page or redesign it. Resolve the installed `presentation/render.py` under this SKILL.md's directory; in a full source checkout the component is at the repository's `presentation/render.py`. If neither exists, report that packaging gap rather than invent a substitute.

With an authorized new output destination outside the installation, prepare a minimal UTF-8 JSON handoff from the already-prepared content:

```json
{
  "schema_version": "ci.presentation.v1",
  "kind": "advice",
  "title": "Prepared next move",
  "goal": "The user's stated goal",
  "notice": "The actual uncertainty and review/provider status",
  "next_move": "The already-prepared next action"
}
```

Replace placeholders; retain the user's language. `kind` is `advice`, `clarification`, `no_fit` or `manual_review`, describing the actual outcome, not certification. Optional `why` and `principle` are plain text; `facts`, `unknowns`, `sources` are lists of plain text. Optional `practice` contains `prompt`, `observe`, and optionally `example`; optional `reflection` contains `prompt` and `adjustment_prompt`. Include only content already prepared and reviewed. Omit unused views. Do not invent activities just to fill tabs.

```bash
python3 "$PRESENTATION_DIR/render.py" --input "$HANDOFF_JSON" --output "$NEW_HTML"
```

Keep private handoff files outside the installation, under actual file consent; remove temporary input when appropriate. The renderer creates new owner-only HTML, refuses overwrite and preserves supplied text. Return the HTML link and a short next move in text. Try the host's normal browser-opening mechanism once if requested; if unavailable, give the link without installing tools or starting a debugging project.

The approved workspace keeps advice beside the current task, opens references without moving the editor, and reflows for long content, small screens and enlarged text. Notes remain temporary until explicitly exported. Export/import does not update a Markdown case, confer ongoing write consent, or communicate with the agent. A saved case for continuity remains a separate, authorized operation using [resume](resume.md).
