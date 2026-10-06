# Distribution boundaries

The [public file manifest](../scripts/public-release-files.json) is the explicit allowlist for both formats. Unknown additions are excluded until deliberately reviewed and listed. Known secret/private/cache paths are rejected even if listed; this is still not a comprehensive content-level secret scanner.

| Format | Public content |
| --- | --- |
| Full project/plugin | Canonical skill, manifests, adapters and original examples; presentation; executable scripts/tests/evals; curated user/developer guides and explicit original synthetic technical evidence. |
| Portable skill | The entire reviewed canonical skill, including all 21 cards, runtime assets, onboarding and home templates. No presentation, project research or coordinator artifacts. |
| Internal handoff | Explicitly selected development/PM records and reproducibility artifacts, transferred separately when needed. Never credentials, personal cases or original book files. A whole-directory ZIP is not a safe handoff. |

Public exceptions are individually listed: the archived G diagnostic/ablation evidence and governance records are original technical evidence, not copies of the book-research reports. No `docs/research/`, `docs/internal/`, private `.local/` snapshots, current session handoff or private comparison mapping is shipped. Public validation is summarized in [PUBLIC-VALIDATION.md](PUBLIC-VALIDATION.md); internal development histories remain separate.

The builder validates all relative Markdown links against the actual member set, refuses symlinks and overwriting, and writes exact per-format contents/hashes beside the ZIPs. The full archive remains an executable/testable project. The portable archive remains self-contained. Declared but missing files fail the build.

From the project root, use a new external destination:

```bash
python3 scripts/build_releases.py --output /absolute/path/to/new-directory
```

This runs offline tests and creates local artifacts only. It does not install, upload, make model calls, change VERSION or choose a license. Package version plus recorded file/archive hashes identify the working tree; unreleased changes sharing a version are not identical releases. The maintainer adopted MIT for original work and selected experimental package 0.3.2 on 2026-10-06; both formats retain LICENSE and NOTICE with their third-party boundaries. The maintainer confirmed revocation of the potentially shared old key; no credential value was inspected. Publication remains a separate operator action using the reviewed artifacts, with applicable installation/browser limits stated accurately.

Test exclusions with synthetic contents only. Do not inspect a real key to prove it was excluded. Never treat `.gitignore` as an archive policy, and never disable link checks to hide a missing internal document.
