# Gitea Issue Driven Development

This context defines the language for taking a Gitea issue from decomposition through a verified pull request while preserving explicit phase authority.

## Language

**Workflow interface**:
The stable, user-facing contract formed by phase entry points, their trigger semantics, and persistent remote markers. Internal files may be reorganized without changing this contract.
_Avoid_: Internal layout, Skill directory structure

**Workflow phase**:
An authority-bounded unit of work that produces one verifiable outcome and refreshes the remote evidence it needs. Decomposition, planning, execution, and pull-request delivery are distinct phases.
_Avoid_: Step, mode

**Phase authority**:
The exact remote reads and writes permitted while a workflow phase is active. A phase cannot inherit mutations owned by another phase.
_Avoid_: Tool access, general permission

**Connector mapping**:
The per-session resolution from a phase's semantic Gitea operations to compatible capabilities in the live connector schema. Static tool names are examples, not authority.
_Avoid_: Connector configuration, fixed tool map

**Managed artifact**:
A file or directory installed at a package-owned path and therefore eligible for explicit transactional replacement or migration. Unknown neighboring files remain user-owned.
_Avoid_: Any file under Codex home
