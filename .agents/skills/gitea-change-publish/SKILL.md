---
name: gitea-change-publish
description: Turn an already implemented and verified change into scoped commits and a non-force branch push without editing code or creating a PR. Use after OpenSpec apply or Gitea-native execution.
---

# Gitea Change Publish

Publish existing implementation evidence; never implement or redesign the change.

## Inputs

Require the issue reference, workflow mode (`openspec` or `gitea-native`), branch/base SHA, acceptance mapping, exact test outcomes, and explicit changed paths. In OpenSpec mode also require the change name and artifact fingerprint.

## Workflow

1. Verify the current branch/base, status, full diff, and absence of unrelated paths. Stop rather than stash, reset, discard, or mix user work.
2. Confirm every changed path maps to an acceptance ID or required supporting artifact. Treat unrun and failed checks distinctly.
3. Stage explicit paths only. Create the smallest coherent commit set supported by the supplied acceptance mapping; do not amend published commits or create failing checkpoints.
4. Verify commit order, clean scoped status, and local `HEAD`.
5. Push only when the caller has explicitly authorized network publication. Use `git push -u origin <branch>` without force and verify the remote head SHA.

Do not edit implementation or planning artifacts, run new planning, create a PR, merge, or rewrite history. Return a compact commit/test ledger plus `{branch, base_sha, head_sha, remote_head_sha, pushed}` for `$gitea-pr-delivery`.
