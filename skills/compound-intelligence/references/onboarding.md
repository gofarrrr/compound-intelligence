# Start using Compound Intelligence

Keep the complete skill folder together and install it through your host's local-skill mechanism. Start with [SKILL.md](../SKILL.md). Python 3.10+ is needed only for the supplied helpers. No extra Python packages are required.

## Choose how to use it

- **Local coaching:** describe your case or ask for a lesson. No TypeSafe account or key is needed.
- **TypeSafe/Jev assistance:** the same skill can use Jev for method selection and draft review. The conversation and its questions remain agent-led. You provide your own key; approved API requests may incur usage on your account.

If your preference is already clear, use it. Otherwise offer these choices once in the current conversation, without blocking a clear lesson, urgent help or useful local advice. Enabling Jev does not authorize sending every conversation or saving a case.

## Recommended: launch Codex with Jev

Install the full skill first, using `python3 scripts/install.py` from the extracted portable folder. The installer refuses to overwrite an existing copy. Codex CLI must be installed, on PATH and signed in; see the [Codex CLI guide](https://developers.openai.com/codex/cli/). Helpers require Python 3.10+; no TypeSafe SDK is needed.

1. Create your own key in the [TypeSafe dashboard](https://console.typesafe.ai/). API usage is charged to your account; check its available usage before testing. The [official quick start](https://docs.typesafe.ai/introduction/quickstart) explains keys and bearer authentication.
2. In your own interactive terminal, run:

```bash
python3 "$HOME/.agents/skills/compound-intelligence/scripts/launch_codex.py" --jev
```

On Windows, use `python` and the installed path under your user folder. A repository-local/custom install uses that installation's `scripts/launch_codex.py`. The launcher was tested on macOS; Windows/native desktop installation was not exercised here.

3. If this terminal already has a nonblank `TYPESAFE_API_KEY`, the launcher reuses it. Otherwise paste your key only at its hidden terminal prompt. **Do not run this key-entry command through agent tools or paste the key into chat.** If hidden input is unavailable, setup stops.
4. The launcher starts a new Codex process with `--no-daemon`, the key in its environment and a setup prompt naming this actual skill. It writes no key file or global configuration and resets inherited session-wide TypeSafe sending permission for this new session. Codex's own account/model and sandbox/environment policies remain in effect. The host checks `doctor` in its actual tool environment; a key visible to the launcher can still be filtered by host policy.
5. When you want to verify connectivity, explicitly ask: “Run one synthetic TypeSafe smoke test; I approve that synthetic request and understand it may incur usage.” Only a successful actual response establishes that exchange. No real case or full chat is sent by this setup approval.

After setup, describe one leadership situation. Before the first real Jev request, review/approve its minimized outgoing case and, for draft review, the actual draft. Keep identifying or restricted details local. The host should distinguish **local mode**, **key present / connection unverified**, **live Jev used**, and **provider unavailable** accurately.

The launcher itself makes no TypeSafe requests. Starting Codex uses your normal host account and may use its included limits or API billing. It does not grant standing permission, buy credits or create follow-up memory. For local coaching:

```bash
python3 "$HOME/.agents/skills/compound-intelligence/scripts/launch_codex.py" --local
```

Closing that process ends this launcher's in-memory setup; it does not revoke the provider key. The manual environment route below remains available for other launch methods. Terminal exports cannot configure an already-running desktop application.

## Add your TypeSafe key in your terminal

Manual alternative for other launch methods.

Get a key from the [TypeSafe dashboard](https://console.typesafe.ai/), as described in its [quick start](https://docs.typesafe.ai/introduction/quickstart).

Run the following yourself in an **interactive terminal**. Paste the key only at the hidden `TypeSafe API key:` prompt. The command stores it in the current shell environment, not in a file or the command you enter into history. The Python warning guard stops key entry if a hidden prompt is unavailable. Do not paste the key into chat, replace the prompt with a literal key, or ask the agent to collect it through a tool call.

### macOS / Linux: Bash or Zsh

```bash
export TYPESAFE_API_KEY="$(python3 -c 'import getpass, warnings; warnings.simplefilter("error", getpass.GetPassWarning); print(getpass.getpass("TypeSafe API key: "))')"
```

### Windows: PowerShell with Python on PATH

```powershell
$env:TYPESAFE_API_KEY = python -c "import getpass, warnings; warnings.simplefilter('error', getpass.GetPassWarning); print(getpass.getpass('TypeSafe API key: '))"
```

**Launch your CLI agent from this same terminal after entering the key.** For Codex CLI, run `codex`. This makes the environment available to the newly started process, subject to its environment policy. Setting a key elsewhere does not configure an already-running desktop app or an existing conversation. A setup subprocess cannot change its parent's environment.

For a desktop or remote host, use its supported secret/environment configuration and check from the actual agent session. This package does not provide a universal desktop key field or automatically read `.env` files. Keep credentials outside the installed skill, source control, case state, notes and receipts. A host secret store can provide persistence if supported; this first version supplies session configuration only.

## Check from the place that will run Jev

From the installed skill folder, run:

```bash
python3 scripts/ci.py doctor
```

On Windows use `python` if that is your Python 3 command. Inside an agent session, the agent must resolve the helper from the actual installed skill path rather than assuming its current directory.

| Result | Meaning and next step |
| --- | --- |
| `typesafe_key_present: false` | This process cannot see a nonblank key. Enter it in the launching terminal or configure the host, then check again. Local coaching is available. |
| `typesafe_key_present: true` | The process sees a key. Its validity, API access and connectivity are still unverified. |
| `typesafe_egress_approved_for_session: false` | No session-wide sending permission is set. This is separate from key setup; a specifically approved command can use `--consent-send`. |
| `network_called: false` | Doctor made no API request. It is not a successful live connection test. |

Doctor reveals presence only. Never diagnose by printing environment values or reading secret files. If the launching terminal sees the key but the agent's doctor does not, investigate host/environment inheritance. For Codex, the [shell environment policy](https://learn.chatgpt.com/docs/config-file/config-advanced#shell-environment-policy) can filter variables. Do not write a literal key into `config.toml` or disable unrelated protections as a quick fix.

## Optional connection test

After explicitly approving **one synthetic request**, run from the skill folder:

```bash
python3 scripts/ci.py smoke --consent-send
```

This may incur usage; setup and doctor do not run it automatically. Success reports `kind: live_synthetic_api_smoke_test` and `network_called: true`. It confirms that exchange, not coaching accuracy. On failure, report the returned error code and follow [runtime failure handling](decision-runtime.md#failure-handling). Do not expose the key or provider error bodies, or repeatedly retry authentication/billing failures.

A synthetic smoke approval covers that test only. Before a real case or draft is sent, prepare a minimized packet and get approval for that content/provider scope under the [runtime rules](decision-runtime.md#what-is-sent-and-stored). Restricted cases stay local. The skill must state when a requested Jev step was unavailable or used local help.

## Clear the session key

Bash/Zsh:

```bash
unset TYPESAFE_API_KEY
```

PowerShell:

```powershell
Remove-Item Env:TYPESAFE_API_KEY
```

Clearing the terminal variable does not remove a copy inherited by an already-running agent. End that process/session to stop its use of the inherited key; it does not revoke the key at TypeSafe.

## Instructions for the agent

When setup is requested or the user expects Jev, load this guide and run doctor in your actual execution environment. Give the relevant terminal/host instructions when the key is missing, then wait for the user to perform secret entry. Do not start a key prompt through your tools, configure a secret file, enable session consent or run a paid test on their behalf without the required authorization. If they choose local coaching, proceed without setup.

Report **local mode**, **key present / connection unverified**, **successful live exchange**, or the actual unavailable/error path accurately. Use the established preflight/postflight when helpful and approved. API onboarding is separate from the optional [learning home](workflows/setup.md); it creates no profile, case store, reminder or learning record.
