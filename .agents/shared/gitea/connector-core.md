# Gitea connector core

Use this reference only to resolve a phase's semantic Gitea operations against the live connector. The active phase contract is the sole authority for reads, writes, fallbacks, and verification.

## Resolve capabilities

1. Inspect the tools exposed in the current session before the first remote operation.
2. Select an enabled connector by its advertised Gitea capabilities and input schema, never by server or package name.
3. Map every required semantic operation in the active contract to one advertised tool and method. The live schema is authoritative.
4. Stop and report each missing required capability. Do not invent REST calls, install or reconfigure connectors, or source alternate credentials.

## Complete and verify

Paginate advertised list operations until complete. If issue-comment completeness still cannot be proved and the phase contract permits a fallback, load [comment-pagination-fallback.md](comment-pagination-fallback.md).

After each authorized write, read back the fields required by the phase contract. Preserve unrelated labels and fields; never infer success from a write response alone.

Connector credentials are server configuration, never command arguments. Do not echo, copy, or expose them. Attachment downloads belong only to `$gitea-issue-evidence`.
