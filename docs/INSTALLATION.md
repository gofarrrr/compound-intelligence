# Installation and migration — 0.3.2 experimental

The ZIP contains the complete skill. Installation is explicit: run the supplied installer or copy the full folder manually. The installer and launcher are checked offline; live coaching/TypeSafe setup and native desktop installation are not performed during the build. Plugin packaging/authentication documentation was checked again on 2026-10-03; use your client's supported installation and secret-management mechanisms.

## Choose one format

The full-project/plugin archive contains `compound-intelligence/skills/compound-intelligence/`, plus manifests, tests and documentation. The portable-skill archive contains that same skill directly at `compound-intelligence/`. Keep the full skill folder, including `scripts`, `assets`, `references`, and `agents`. A single copied `SKILL.md` is insufficient.

Both formats now expose **one** skill. The 21 chapter names and `ci-*` aliases are internal instruments, not separate slash commands. Do not install both formats or leave old copies enabled in the same scope.

## Recommended Codex installation

[Download the portable ZIP](https://github.com/gofarrrr/compound-intelligence/releases/download/v0.3.2/compound-intelligence-v0.3.2-skill.zip), extract it and run `python3 scripts/install.py` from the extracted `compound-intelligence` folder. From a cloned full project, use `python3 skills/compound-intelligence/scripts/install.py` instead. The installer copies the complete folder and refuses to overwrite existing or symlinked destinations. An interrupted copy is not success; preserve/reconcile a partial destination before retrying.

Default destination: `$HOME/.agents/skills/compound-intelligence`. A custom repository-local destination is accepted with `--destination /your/repo/.agents/skills/compound-intelligence`. Cases and credentials do not belong in that installed folder.

For Jev start `python3 "$HOME/.agents/skills/compound-intelligence/scripts/launch_codex.py" --jev` yourself in a terminal. It uses your environment key or asks for hidden entry, then starts Codex with `--no-daemon` and no inherited standing TypeSafe consent. It changes no global host configuration. For no-key coaching use `--local`. See [onboarding](../skills/compound-intelligence/references/onboarding.md) for actual tool-environment checks, API approval and manual/desktop alternatives. Codex CLI 0.160.1 exposes `--no-daemon`; older clients may need updating or manual launch. Windows installation was not exercised here.

## Manual Codex local skill installation

Current Codex documentation describes repository skills under `.agents/skills` and user skills under `$HOME/.agents/skills`. For a clean user-level install from the **full project root**, the following command refuses to overwrite an existing destination:

```bash
python3 - <<'PY'
from pathlib import Path
import shutil
source = Path('skills/compound-intelligence').resolve()
destination = Path.home() / '.agents/skills/compound-intelligence'
if not (source / 'SKILL.md').is_file():
    raise SystemExit('Run this from the full project root.')
if destination.exists() or destination.is_symlink():
    raise SystemExit('Destination already exists. Back up and migrate it deliberately; nothing was overwritten.')
destination.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(source, destination, ignore=shutil.ignore_patterns('__pycache__'))
print(f'Copied skill to {destination}')
PY
```

For the portable archive, `source` is the extracted skill directory itself. For a repository-only install, use that repository's `.agents/skills/compound-intelligence` instead of the home directory. Do not put learning records inside this installation.

In Codex CLI/IDE, find the skill through `/skills` or invoke `$compound-intelligence`. The host may also choose it from its description. If an updated skill does not appear, restart the host and check for duplicate installations. `agents/openai.yaml` enables implicit invocation; it does not guarantee that the host selects it on every turn.

Official reference: https://developers.openai.com/codex/skills/

## Full plugin distribution

The package already has a portable root `plugin.json` declaring the Agent Plugins schema, the canonical `skills/` directory, and compatibility manifests in `.codex-plugin/` and `.claude-plugin/`. Current OpenAI documentation uses the root portable manifest and discovers `skills/` automatically; `.codex-plugin/plugin.json` remains a compatibility fallback for OpenAI-specific settings when no inline `extensions.com.openai` object exists. There is no MCP server in this package. See [Package your plugin](https://developers.openai.com/plugins/build/plugins#plugin-structure).

`codex-marketplace.example.json` is an optional local-marketplace example; its `source.path` assumes a matching plugin layout. It is not a configured or published marketplace. Do not overwrite an existing marketplace or client configuration with it. A local marketplace and the universal public directory are separate distribution channels; supported surfaces and installation policies vary. The [packaging guide](https://developers.openai.com/plugins/build/plugins) documents both.

Use the client's supported local-plugin installation workflow. These manifests do not register a TypeSafe account or configure a secret. In the inspected local Codex CLI 0.158.0, `codex plugin --help` exposes plugin and marketplace commands; only help/version were checked, not installation or authentication. The standalone skill-copy method above remains available.

For Claude Code, the full-plugin local workflow retained from v0.1 is:

```bash
claude plugin validate ./compound-intelligence
claude --plugin-dir ./compound-intelligence
```

Those commands are run from the directory containing the extracted folder. The front door is `/compound-intelligence:compound-intelligence`. They are user-side validation/load instructions, not a claim that Claude was run in this build environment. All chapter selection now happens inside that front door.

Reference retained from the previous package: https://code.claude.com/docs/en/plugins/create

## TypeSafe configuration

Follow [QUICKSTART](QUICKSTART.md) to set `TYPESAFE_API_KEY` in the correct process environment and run a synthetic live smoke test. The key is not stored by the project. The local helper needs Python 3.10+ and an approved outbound HTTPS connection to the TypeSafe endpoint. Network restrictions, shell availability, and environment inheritance depend on the host.

The user has selected **a standalone OSS skill with instructions for supplying a personal key** as the current distribution target. The portable [onboarding guide](../skills/compound-intelligence/references/onboarding.md) is now included and linked from the skill entry point. Plugin/MCP distribution is future work, not a prerequisite for this version.

A key alone does not approve personal data transfer. Use a per-call `--consent-send`, or explicitly opt into approved anonymized packets for the current session with `CI_ALLOW_TYPESAFE=1`. Restricted packets never leave the helper. With no approved live path, the host uses source-grounded local coaching.

### First-use experience for an OSS distribution

The current development skill has a guided environment setup using existing `doctor` and explicitly approved synthetic `smoke` commands. It does **not** have a persistent key-entry UI or a hosted account connection. The documented user experience is:

1. Install Compound Intelligence and choose local coaching or TypeSafe-assisted routing/review.
2. For TypeSafe, obtain a personal API key through the [TypeSafe dashboard](https://console.typesafe.ai/). Its [quick start](https://docs.typesafe.ai/introduction/quickstart) documents dashboard keys and bearer authentication.
3. Configure that key through an appropriate secret mechanism outside the conversation and package. For today's local CLI path, use the hidden terminal prompt in [QUICKSTART](QUICKSTART.md), then launch Codex from that environment. Exporting a key in one terminal does not configure an already-running desktop session.
4. Check readiness in the actual execution environment. `doctor` establishes key presence, not validity, credit availability or API connectivity. A live synthetic smoke test requires explicit approval and may incur usage.
5. Before a real case call, approve the minimized case and draft/provider scope. Show whether routing/review actually used Jev or used a local/unavailable path. A connected credential is not permission to send every conversation.

The new case-understanding phase stays agent-led in both modes. Existing preflight/postflight, source cards, policy, consent and finite revision behavior remain authoritative. Setup does not imply saving a case, scheduling follow-up or training a model.

### Two supported design directions

| Direction | User's key and execution | Current status and tradeoff |
| --- | --- | --- |
| Local OSS skill/plugin | The helper reads the user's environment. The user-run terminal launcher accepts hidden key entry and starts a new Codex process with it. | Implemented for Codex CLI with no key file or additional CI service. Desktop/cloud secret setup and persistent key storage remain host-specific; a child cannot configure an already-running parent. |
| Public-directory plugin with an MCP connection | A proposed MCP service authenticates the user and exposes the existing routing/review operations. A separate secure settings flow would associate the user's TypeSafe key with that account. | Not built. Offers a browser connection flow but adds hosting, credential custody, per-user isolation and operations. Public MCP submission currently requires a stable public HTTPS endpoint. Self-hosting can be an OSS option, but a local instance alone is not that public-directory deployment. |

OpenAI plugins do not run Claude `userConfig` key-entry prompts or expand `${user_config.*}`. The marketplace's `authentication: ON_INSTALL` is a policy setting, not a declaration of a TypeSafe key form. OpenAI's [migration guidance](https://developers.openai.com/plugins/guides/submit-claude-plugin#replace-claude-userconfig) distinguishes Codex-local environment settings from credentials for a remote service; the latter use an authenticated MCP integration.

For the remote design, [OpenAI authentication guidance](https://developers.openai.com/plugins/build/auth) specifies OAuth 2.1 to the MCP service. That would authenticate **our MCP account connection**, not magically convert a TypeSafe API key into TypeSafe OAuth. The inspected [TypeSafe API](https://docs.typesafe.ai/api) uses bearer API keys; no ready-made TypeSafe OAuth/plugin connection was verified in this review. A proposed remote key flow must keep credentials out of prompts, tool inputs/results and plugin files. It also changes the current local-only credential boundary and needs deliberate design before implementation.

The maintainer selected the local standalone skill and instruction-based onboarding first. The MCP route remains a possible later direction. No MCP server, persistent key store or public-directory submission is included. The terminal launcher is a local Codex convenience, not an account connection service.

### OSS release status

The maintainer adopted [MIT](../LICENSE) for original project code and instructions on 2026-10-06. Both public formats include a license and [provenance notice](../NOTICE.md); this does not relicense the book or other third-party rights. Public distribution uses explicit file lists, not the whole development tree. Any previously shared active credential must be revoked before distribution. Package 0.3.2 is the experimental continuity/onboarding preview. The decision contracts and policy are unchanged; helper metadata now reports the matching package version.

## Migrating from 0.1.0

Keep the old ZIP as a rollback artifact. Identify which copy the host actually loads before changing anything. Preserve user-owned `CONTEXT.md`, `PRINCIPLES.md`, `PRACTICE.md`, examples and case files outside installed skill directories.

Disable/uninstall the old plugin or back up the old standalone installation before installing this release. Do not merge the 0.2 files on top of old `ci-*` directories: those wrappers would continue to advertise competing skills. No automatic migration deletes your files.

Old use: `$ci-feedback`. New use: `$compound-intelligence` followed by “use Factual Feedback” or “use ci-feedback.” Old use: `$ci-rehearse`. New use: `$compound-intelligence` followed by “rehearse this conversation.” All techniques remain available; the change is discovery granularity.

The new runtime never rewrites installed source cards. It also does not convert previous reflections into classifier training data or assume they are calibrated labels. Existing user-approved lessons retain their original scope and caveats.

## Presentation in 0.3.2

Use the portable release ZIP or the full repository’s installer to install the complete experience. Both include the same separate renderer and workspace template. Installing only the GitHub skill subfolder through a generic downloader omits the sibling presentation source. For an existing install, preserve it outside skill discovery before installing the new complete package; the installer never overwrites it. Personal case files belong outside the installation.
