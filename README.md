# Gitea Issue Driven Agent

This Codex agent package implements an Issue-driven development workflow for Gitea and is designed to pair with [pingwcs/gitea-mcp](https://github.com/pingwcs/gitea-mcp).

## Skill architecture

| Skill | Responsibility | Main integration |
|---|---|---|
| `gitea-issue-decomposition` | Split a target into focused child issues and update the parent tracker | `issue_read`, `list_issues`, `issue_write` |
| `gitea-issue-triage` | Read issue/comments, assign P0-P3, split future work, publish code design | `issue_read`, `issue_write`, `label_read` |
| `gitea-issue-evidence` | Download screenshots/logs with local Tea credentials and analyze them | `tea login helper get` plus local scripts/vision |
| `gitea-issue-execution` | Branch from fresh `origin/master`, TDD, verify and commit each step, push | Git and repository test tools |
| `gitea-pr-delivery` | Create/update and verify a PR with accurate description/checklist | `pull_request_write`, `pull_request_read` |

The previous seven overlapping Skills were consolidated into four lifecycle Skills, with decomposition kept as a separate optional fifth Skill because it changes Issue topology. Detailed MCP method tables live in references and are loaded only by the phase that needs them.

## Required setup

1. Install a recent Tea version that supports `tea login helper get` and configure a Gitea login. Interactive login is preferred so a token is not placed in shell history.
2. Install and configure `pingwcs/gitea-mcp` in Codex. A typical stdio configuration is:

```toml
[mcp_servers.gitea]
command = "gitea-mcp"
args = ["-t", "stdio", "--host", "https://git.example.com"]
env_vars = ["GITEA_ACCESS_TOKEN"]
enabled_tools = ["issue_read", "issue_write", "list_issues", "label_read", "pull_request_read", "pull_request_write", "list_pull_requests"]
default_tools_approval_mode = "writes"
```

Adapt the executable and host to the installation. The MCP token needs Issue/label/PR permissions; use the minimum repository scope. Tea and MCP should normally represent the same automation identity.

## Attachment authentication

The attachment collector does not read `GITEA_TOKEN` or accept a token argument. It calls:

```text
tea login helper get [--login <name>]
```

using Git's credential protocol (`protocol` and `host` on stdin). Tea obtains or refreshes its stored credential. The collector captures `password=<token>` in memory, verifies the returned origin, uses it only for same-origin HTTPS downloads, and never writes or prints it. Missing Tea, missing login/token, helper failure, or origin mismatch stops attachment analysis with an explicit error.

Before collection, the Skill runs `--credential-check-only` in the sandbox. A first failure automatically triggers exactly one sandbox-external retry through Codex's approval mechanism. If that retry succeeds, collection uses the same approved permission; if it is denied or fails, evidence processing remains blocked. Escalation never permits token environment fallbacks, plain HTTP, origin mismatch, or relaxed download safeguards.

## Workflow entry points

- “把 Gitea issue `<URL>` 拆成职责清晰的小 Issue” runs decomposition: full read → boundary design → deduplication → child creation → parent tracking-block update.
- “分析 Gitea issue `<URL>` 并写入解决方案” runs Phase A: full read → attachment evidence → priority mark → future issues → modular design comment.
- “按已评论的方案解决 Gitea issue `<URL>` 并创建 PR” runs Phase B: re-read → fetch `origin/master` → issue branch → failing test → step commits → push → verified PR.

When a PR fully resolves its open same-repository source Issue, delivery adds `Closes #<issue-number>` to the PR description. Gitea then closes the Issue only when an authorized user merges the PR; trackers, follow-ups, and partial work are never marked for automatic closure.

A concrete request to run one phase authorizes that phase's normal writes only. Merge, close, delete, force-push, history rewrite, credential changes, and unrelated label changes remain outside the workflow.

## Design markers

- Plan comment: `<!-- gitea-issue-driven:plan:v1 -->`
- Parent tracking block: `<!-- gitea-issue-driven:decomposition:start -->`
- Child issue: `<!-- gitea-issue-driven:child parent=<number> key=<stable-key> -->`
- Follow-up issue: `<!-- gitea-issue-driven:followup source=<number> key=<stable-slug> -->`
- PR body: `<!-- gitea-issue-driven:pr-body:v1 -->`

Markers make retries idempotent and let the execution phase find the latest remote contract.
