# Privacy, credentials, and boundaries

The runtime reads `TYPESAFE_API_KEY` only from its process environment. It does not load credential files, accept a key in CLI arguments, log the key, or include it in generated archives. `doctor` reports a boolean only. Its HTTP client uses the key solely for the Authorization header to the fixed TypeSafe HTTPS endpoint and refuses redirects.

A user can separately authorize private local test storage in the Git-ignored root `.env.local`, with owner-only `0600` permissions. The test shell or host explicitly loads that value into its environment; this is not automatic runtime configuration. The release builder excludes `.env` paths. Keeping a local key does not authorize additional paid calls or data transfer.

Network access is opt-in. An explicit `--consent-send` or the user's session setting `CI_ALLOW_TYPESAFE=1` is required. The state schema cannot set consent, endpoint, policy, or tools. `data_class=restricted` is the default and is never sent even with approval. User-supplied classification and approval are not organizational permission: only use the provider when the applicable organization allows it.

Before sending a case, minimize it and replace names and identifying details. Common secret-like tokens and email addresses are filtered, and private-key markers are refused. This does **not** remove all PII, names, phone numbers, identifiers, diagnoses, or distinctive narratives. It is not DLP or proof of anonymity. Provider contracts, retention settings, and data residency are not configured or certified by this package.

The preflight receives the approved case and compact question/card-fit instructions. The postflight additionally receives the proposed answer and the actual source-summary cards; approval must cover the draft as well. The EPUB and original full book text are not part of any request. An external API call may incur usage, including repeated calls after transport failures.

Raw state/drafts are read from user-authorized files or host-created transient files, not persisted automatically by the helper. A host may still retain its own transcript, terminal output, or scratch artifacts under its own settings. Use owner-only scratch files outside installations and remove them when no longer needed. Preview output contains the minimized state and must also be handled appropriately.

Receipts contain derived judgments and hashes, which can still be sensitive even without raw stories. An explicit `--output` is required for file persistence; writes are owner-only and do not overwrite, follow symlinks, or target the installed package. These checks reduce accidental misdirection, but are not a security boundary against a concurrently hostile local filesystem. Reflection requires explicit approval and remains provisional, user-reported evidence.

Model risk flags supplement human/host checks; they cannot authorize actions or prove safety by returning a low value. The program never sends messages, changes employee status, or approves tool execution. Code only computes an advisory route. Native-host instruction following and final response delivery are outside this helper's enforceable boundary.

To stop optional calls, use `--backend offline`, remove `CI_ALLOW_TYPESAFE`, or remove the key from the relevant process environment. No background process continues to call the provider. No fallback sends data to another provider.
