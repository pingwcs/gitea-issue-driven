# Python agent installer verification evidence

## Agreed constraints

- Install the five public Gitea Skills, the shared runtime, and the agent configuration without modifying global MCP configuration.
- Require explicit `--force` before replacing managed targets or migrating the legacy connector profile.
- Keep `--dry-run` free of filesystem writes.
- Roll back overwritten and migrated managed artifacts after a failed commit.
- Keep validation minimal and do not store test files in the project directory.

## Historical TDD baseline

The original installer was developed regression-first for fresh installation, conflict handling, force, dry-run, and rollback. Before this layout refactor, its temporary-home suite reported 27 passing tests and 100% traced executable-line coverage for `scripts.install_agent`.

Those repository test files were intentionally removed before the current refactor. This historical result is context, not a claim about current coverage.

## Shared-runtime migration verification

Verified on 2026-07-22 with one inline Python harness using only automatically cleaned directories under `C:\tmp`:

| Behavior | Result |
|---|---|
| Installer source parses and the agent TOML loads | PASS |
| Fresh install creates exactly five Skill directories, `shared/gitea`, and the agent config | PASS |
| Fresh install excludes the legacy profile and does not create `config.toml` | PASS |
| A legacy profile blocks installation without `--force` and remains unchanged | PASS |
| `--force` removes only the known legacy profile and installs the shared runtime | PASS |
| An injected mid-commit failure restores the legacy profile and removes partial new targets | PASS |

An additional read-only inline check verified all local Markdown links, all five public Skill names, the five stable marker families, a 330-token approximate stable-entry budget, and approximate remote-phase hot paths between 1,363 and 1,546 tokens. No persistent test file or test artifact was added to the project.
