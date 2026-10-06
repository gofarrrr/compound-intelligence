# Optional learning home

**Architecture:** adapted from Compound Writing’s one-home, no-overwrite setup pattern. These files are an implementation design, not book chapter frameworks.

Start from the actual request. Existing workspace context, even with different filenames, is a valid starting point. Do not initialize a new home because one of these files is missing. A current problem can be coached entirely in chat.

When setup is requested, resolve the destination and inspect its existing instructions. Never place personal learning data in the installed skill/plugin or a runtime cache. Avoid adding another home when the user already named a maintained one.

## Default surfaces

`CONTEXT.md`: explicitly supplied role, goals, authority, constraints, and coaching preferences.

`PRINCIPLES.md`: user-endorsed leadership and decision principles, with source or rationale.

`PRACTICE.md`: approved, scoped rules and experiments, not a transcript archive.

`examples/`: approved, anonymized demonstrations or user examples.

`cases/`: one folder per authorized case, following the user’s existing convention when present.

Do not fill these templates with inferred values or personal details. Empty guidance does not block use.

## Run the supplied creator

Resolve the script relative to this workflow file: [create_home.py](../../scripts/create_home.py). A normal preview is:

```bash
python3 /path/to/compound-intelligence/scripts/create_home.py /path/to/learning-home --dry-run
```

The example is for the portable skill folder. In the full plugin, the script lives at `skills/compound-intelligence/scripts/create_home.py`. Use the actual resolved path, not an assumed current working directory.

After the destination and setup are authorized, run without `--dry-run`. The script creates a new or empty folder, refuses an existing nonempty folder by default, and never overwrites an existing file. To add only missing surfaces to a reviewed existing folder, use `--add-missing`. It rejects symlinked targets and attempts to write within its own installed package. This protects ordinary local use, not against concurrent hostile filesystem mutation.

When execution is unavailable, provide the templates and explain that no files were created. Do not claim setup succeeded by merely showing the tree.

## Finish

Report the actual path, files created, and existing items preserved. Begin useful coaching immediately; optional context calibration can come from the user’s real work. No mandatory questionnaire, hidden onboarding flag, or automatic case logging.


## Shared requirements
Follow the [context](../context-contract.md), [coaching](../coaching-contract.md), and [safety](../safety.md) contracts. Use only the [chapter cards](../routing.md) needed for the requested outcome.
