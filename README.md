# Gitea Issue Driven Agent

This Codex agent package implements an issue-driven development workflow for Gitea and is designed to pair with [pingwcs/gitea-mcp](https://github.com/pingwcs/gitea-mcp).

## Runtime architecture

| Layer | Sole responsibility |
|---|---|
| `AGENTS.md` | Route repository work to phase Skills and state the minimal destructive-action boundary |
| `.codex/agents/gitea-issue-driven.toml` | Dispatch an installed agent to the same phase Skills |
| `.agents/skills/gitea-*/SKILL.md` | Define one authority-bounded phase |
| Per-Skill `references/capability-contract.md` | Authorize that phase's exact remote reads and writes |
| `.agents/shared/gitea/connector-core.md` | Resolve semantic operations against the live connector schema |
| `.agents/shared/gitea/comment-pagination-fallback.md` | Provide the bounded Tea read fallback only when needed |
| Per-Skill `assets/` and `scripts/` | Hold output templates and deterministic operations |

```text
.agents/
├── shared/gitea/                 # non-discoverable, shared runtime references
└── skills/
    ├── gitea-issue-intake/
    ├── gitea-issue-decomposition/
    ├── gitea-issue-triage/
    ├── gitea-issue-evidence/
    ├── gitea-branch-bootstrap/
    ├── gitea-issue-execution/
    ├── gitea-change-publish/
    └── gitea-pr-delivery/
```

The eight public Skill names and all remote markers are stable workflow interfaces. Phase details have one owner; only mode exclusivity and the short destructive-action prohibition are intentionally repeated at both entry points.

The runtime does not load a fixed tool-name map. Each remote phase inspects the live connector schema and maps only the semantic operations in its capability contract. Normal phases load the small connector core; the Tea pagination rules load only when comment completeness cannot otherwise be proved. This keeps stable entry prompts small and prevents phase edits from invalidating unrelated instruction prefixes.

## Skill responsibilities

| Skill | Outcome |
|---|---|
| `gitea-issue-intake` | Immutable, read-only `IssuePacket` with stable acceptance IDs |
| `gitea-issue-decomposition` | Independently deliverable child issues plus a reconciled parent tracker |
| `gitea-issue-triage` | Existing repository label reuse, deduplicated follow-ups, and a verified marked plan |
| `gitea-issue-evidence` | Bounded, redacted screenshot and log evidence |
| `gitea-branch-bootstrap` | Non-destructive issue branch prepared from verified `origin/master` |
| `gitea-issue-execution` | Gitea-native code implementation and verification only |
| `gitea-change-publish` | Scoped commits and an explicitly authorized non-force push |
| `gitea-pr-delivery` | A verified PR with evidence, labels, checklist, and conditional close-on-merge |

## Workflow modes

- **OpenSpec:** intake → optional decomposition → branch bootstrap → external OpenSpec planning/apply/sync/archive → change publish → PR delivery. OpenSpec is the only planning, specification, task, and implementation-state authority; do not run Gitea triage or execution.
- **Gitea-native:** intake → triage → branch bootstrap → execution → change publish → PR delivery. Do not run OpenSpec planning or apply for the same change.

One child issue represents one independently deliverable change, never one OpenSpec task. Keep `AC-*` identifiers stable across issue evidence, specs or native plans, tests, commits, and PR checklists. In OpenSpec mode, Gitea may carry a change reference and fingerprint but must not duplicate design or task content.

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

Python 3.10 or newer can install the eight Skills, shared Gitea runtime, and agent configuration into the current user's Codex home. Preview a fresh install first:

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

The installer copies only the eight `gitea-*` Skill directories, `.agents/shared/gitea/` to `shared/gitea/`, and `agents/gitea-issue-driven.toml`; it never modifies `config.toml`. Caches are excluded and installation remains transactional.

## Attachment authentication

The attachment collector does not read `GITEA_TOKEN` or accept a token argument. It calls:

```text
tea login helper get [--login <name>]
```

using Git's credential protocol (`protocol` and `host` on stdin). Tea obtains or refreshes its stored credential. The collector captures `password=<token>` in memory, verifies the returned origin, uses it only for same-origin HTTPS downloads, and never writes or prints it. Missing Tea, missing login/token, helper failure, or origin mismatch stops attachment analysis.

Before collection, the Skill runs `--credential-check-only` in the sandbox. A first failure triggers exactly one sandbox-external retry through Codex approval. If that retry succeeds, collection uses the approved permission; if denied or failed, evidence processing remains blocked. Escalation never permits token environment fallbacks, plain HTTP, origin mismatch, or relaxed download safeguards.

## Workflow entry points

- “把 Gitea issue `<URL>` 拆成职责清晰的小 Issue” runs decomposition: full read → boundary design → deduplication → child creation → parent tracking-block update.
- “读取 Gitea issue `<URL>`” runs intake and returns an immutable `IssuePacket` without remote writes.
- “用 OpenSpec 解决 Gitea issue `<URL>`” runs intake and Gitea transport/delivery around the caller's OpenSpec workflow; it never publishes a marked Gitea plan.
- “不用 OpenSpec，分析并解决 Gitea issue `<URL>`” runs Gitea-native triage, branch bootstrap, execution, publish, and PR delivery.

When a PR fully resolves its open same-repository source Issue, delivery adds `Closes #<issue-number>` to the PR description. Gitea then closes the Issue only after an authorized merge; trackers, follow-ups, and partial work are never marked for automatic closure.

A concrete phase request authorizes only the writes in that phase's capability contract. Merge, direct closure, deletion, force-push, history rewriting, credential changes, and unrelated mutations remain outside the workflow.

## Design markers

- Plan comment: `<!-- gitea-issue-driven:plan:v1 -->`
- Parent tracking block: `<!-- gitea-issue-driven:decomposition:start -->`
- Child issue: `<!-- gitea-issue-driven:child parent=<number> key=<stable-key> -->`
- Follow-up issue: `<!-- gitea-issue-driven:followup source=<number> key=<stable-slug> -->`
- PR body: `<!-- gitea-issue-driven:pr-body:v1 -->`

Markers make retries idempotent and let later phases locate the latest remote contract.
