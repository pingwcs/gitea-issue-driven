# Gitea Issue Driven Agent

This Codex agent package implements an issue-driven development workflow for Gitea and is designed to pair with [pingwcs/gitea-mcp](https://github.com/pingwcs/gitea-mcp).

## Runtime architecture

| Layer | Sole responsibility |
|---|---|
| `AGENTS.md` | Route repository work to phase Skills and state the minimal destructive-action boundary |
| `.codex/agents/gitea-issue-driven.toml` | Dispatch an installed agent to the same phase Skills |
| `.agents/skills/gitea-*/SKILL.md` | Define one phase's workflow |
| Per-Skill `references/capability-contract.md` | Authorize that phase's exact remote reads and writes |
| `.agents/shared/gitea/connector-core.md` | Resolve semantic operations against the live connector schema |
| `.agents/shared/gitea/comment-pagination-fallback.md` | Provide the bounded Tea read fallback only when needed |
| Per-Skill `assets/` and `scripts/` | Hold output templates and deterministic operations |

```text
.agents/
├── shared/gitea/                 # non-discoverable, shared runtime references
└── skills/
    ├── gitea-issue-decomposition/
    ├── gitea-issue-triage/
    ├── gitea-issue-evidence/
    ├── gitea-issue-execution/
    └── gitea-pr-delivery/
```

The five public Skill names and all remote markers are stable workflow interfaces. Phase details have one owner; only the short prohibition on merge, direct closure, deletion, force-push, history rewriting, and credential mutation is intentionally repeated at both entry points.

The runtime does not load a fixed tool-name map. Each remote phase inspects the live connector schema and maps only the semantic operations in its capability contract. Normal phases load the small connector core; the Tea pagination rules load only when comment completeness cannot otherwise be proved. This keeps stable entry prompts small and prevents phase edits from invalidating unrelated instruction prefixes.

## Skill responsibilities

| Skill | Outcome |
|---|---|
| `gitea-issue-decomposition` | Independently deliverable child issues plus a reconciled parent tracker |
| `gitea-issue-triage` | Existing repository label reuse, deduplicated follow-ups, and a verified marked plan |
| `gitea-issue-evidence` | Bounded, redacted screenshot and log evidence |
| `gitea-issue-execution` | Regression-first implementation, verified commits, and a non-force branch push |
| `gitea-pr-delivery` | A verified PR with evidence, labels, checklist, and conditional close-on-merge |

## Required setup

1. Install a recent Tea version that supports `tea login helper get` and configure a Gitea login. Interactive login is preferred so a token is not placed in shell history.
2. Install and configure a compatible Gitea MCP connector in Codex. For `pingwcs/gitea-mcp`, a typical stdio configuration is:

```toml
[mcp_servers.gitea]
command = "gitea-mcp"
args = ["-t", "stdio", "--host", "https://git.example.com"]
env_vars = ["GITEA_ACCESS_TOKEN"]
enabled_tools = ["issue_read", "issue_write", "list_issues", "label_read", "pull_request_read", "pull_request_write", "list_pull_requests"]
default_tools_approval_mode = "writes"
```

Adapt the executable and host to the installation. The MCP token needs Issue, label, and PR permissions with the minimum repository scope. Tea and MCP should normally represent the same automation identity. At runtime, advertised capabilities and schemas—not these example names—are authoritative.

## Install the Codex agent

Python 3.10 or newer can install the five Skills, shared Gitea runtime, and agent configuration into the current user's Codex home. Preview a fresh install first:

```shell
python scripts/install_agent.py --dry-run
```

Install into the default `~/.codex` location:

```shell
python scripts/install_agent.py
```

The installer stops without changing files if a managed target exists. Review conflicts, then explicitly allow transactional replacement:

```shell
python scripts/install_agent.py --dry-run --force
python scripts/install_agent.py --force
```

`--force` also migrates the previously managed `skills/gitea-connector-profile.md` file to the new shared-runtime layout. The old file is backed up until the install succeeds and restored on failure. No unknown neighboring file is removed. Use `--codex-home <path>` with any command to target another Codex home.

The installer copies only the five `gitea-*` Skill directories, `.agents/shared/gitea/` to `shared/gitea/`, and `agents/gitea-issue-driven.toml`; it never modifies `config.toml`. Caches are excluded and installation remains transactional.

## Attachment authentication

The attachment collector does not read `GITEA_TOKEN` or accept a token argument. It calls:

```text
tea login helper get [--login <name>]
```

using Git's credential protocol (`protocol` and `host` on stdin). Tea obtains or refreshes its stored credential. The collector captures `password=<token>` in memory, verifies the returned origin, uses it only for same-origin HTTPS downloads, and never writes or prints it. Missing Tea, missing login/token, helper failure, or origin mismatch stops attachment analysis.

Before collection, the Skill runs `--credential-check-only` in the sandbox. A first failure triggers exactly one sandbox-external retry through Codex approval. If that retry succeeds, collection uses the approved permission; if denied or failed, evidence processing remains blocked. Escalation never permits token environment fallbacks, plain HTTP, origin mismatch, or relaxed download safeguards.

## Workflow entry points

- “把 Gitea issue `<URL>` 拆成职责清晰的小 Issue” runs decomposition: full read → boundary design → deduplication → child creation → parent tracking-block update.
- “分析 Gitea issue `<URL>` 并写入解决方案” runs planning: full read → attachment evidence → issue labels → future issues → modular design comment.
- “按已评论的方案解决 Gitea issue `<URL>` 并创建 PR” runs delivery: re-read → fetch `origin/master` → issue branch → failing test → step commits → push → verified PR.

When a PR fully resolves its open same-repository source Issue, delivery adds `Closes #<issue-number>` to the PR description. Gitea then closes the Issue only after an authorized merge; trackers, follow-ups, and partial work are never marked for automatic closure.

A concrete phase request authorizes only the writes in that phase's capability contract. Merge, direct closure, deletion, force-push, history rewriting, credential changes, and unrelated mutations remain outside the workflow.

## Design markers

- Plan comment: `<!-- gitea-issue-driven:plan:v1 -->`
- Parent tracking block: `<!-- gitea-issue-driven:decomposition:start -->`
- Child issue: `<!-- gitea-issue-driven:child parent=<number> key=<stable-key> -->`
- Follow-up issue: `<!-- gitea-issue-driven:followup source=<number> key=<stable-slug> -->`
- PR body: `<!-- gitea-issue-driven:pr-body:v1 -->`

Markers make retries idempotent and let later phases locate the latest remote contract.
