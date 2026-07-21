# Gitea Issue Driven Development

Use the phase Skills as the only workflow implementation sources. Select exactly one planning and implementation owner for each change:

- `$gitea-issue-intake` for read-only issue evidence in every mode.
- `$gitea-issue-decomposition` for deliverable child issues.
- **OpenSpec mode:** optional `$gitea-branch-bootstrap`, external OpenSpec planning/apply/sync/archive, `$gitea-change-publish`, then `$gitea-pr-delivery`. Never invoke Gitea triage or execution.
- **Gitea-native mode:** `$gitea-issue-triage`, `$gitea-branch-bootstrap`, `$gitea-issue-execution`, `$gitea-change-publish`, then `$gitea-pr-delivery`. Never invoke OpenSpec planning or apply.
- `$gitea-issue-evidence` only for supported attachments requested by another phase.

Before connector-backed work, the active workflow phase loads the shared connector core and its contract. The live tool schema is authoritative. Pass only identifiers and compact ledgers between phases; each phase rereads current evidence.

The active phase contract is the sole authority for connector operations. A child issue maps to an independent change, not an implementation task. Preserve stable acceptance IDs through plans/specs, tests, commits, and PR checklists. Never merge, directly close, delete, force-push, rewrite history, or modify credentials.
