---
name: gitea-branch-bootstrap
description: Prepare a non-destructive issue branch from the current origin/master without editing code, committing, pushing, or mutating Gitea. Use before either OpenSpec apply or Gitea-native execution.
---

# Gitea Branch Bootstrap

Prepare the implementation branch and return its verified base.

1. Read repository guidance; inspect status, branch, remotes, and worktrees. Preserve unrelated work and stop if it prevents an isolated branch.
2. Fetch `origin master --prune`, verify `origin/master`, and record its commit.
3. Derive `issue/<number>-<short-slug>`. Create it from the fetched commit, or inspect an existing branch without overwriting it.
4. Verify a new branch point equals the fetched commit. For an existing branch, report its base and divergence instead of rewriting it.

Do not stash, reset, discard, edit code, commit, push, force-update, or call a Gitea connector. Return `{issue_ref, branch, base_sha, existing, divergence, warnings}`.
