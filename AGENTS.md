# Gitea Issue Driven Development

Use the phase Skills as the only workflow implementation sources:

- `$gitea-issue-decomposition` for deliverable child issues.
- `$gitea-issue-triage`, plus `$gitea-issue-evidence` for supported attachments, for verified plans.
- `$gitea-issue-execution`, then `$gitea-pr-delivery`, for implementation and PR delivery.

Before connector-backed work, the active workflow phase loads the shared connector core and its contract. The live tool schema is authoritative. Pass only identifiers and compact ledgers between phases; each phase rereads current evidence.

The active phase contract is the sole authority for connector operations. Never merge, directly close, delete, force-push, rewrite history, or modify credentials.
