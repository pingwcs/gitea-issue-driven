#!/usr/bin/env python3
"""Reconcile an idempotent child-issue tracking block into a parent body."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


START = "<!-- gitea-issue-driven:decomposition:start -->"
END = "<!-- gitea-issue-driven:decomposition:end -->"


class ReconcileError(RuntimeError):
    """A malformed input or managed-block error."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-body", required=True, type=Path)
    parser.add_argument("--children-json", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def inline(value: Any) -> str:
    return " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())


def validate_children(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list) or not payload:
        raise ReconcileError("children JSON must be a non-empty list")
    result: list[dict[str, Any]] = []
    numbers: set[int] = set()
    for position, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            raise ReconcileError(f"child {position} must be an object")
        number = item.get("number")
        title = inline(item.get("title"))
        responsibility = inline(item.get("responsibility"))
        if not isinstance(number, int) or number < 1 or not title or not responsibility:
            raise ReconcileError(f"child {position} requires positive number, title, and responsibility")
        if number in numbers:
            raise ReconcileError(f"duplicate child issue number: {number}")
        numbers.add(number)
        dependencies = item.get("depends_on") or []
        if not isinstance(dependencies, list) or any(not isinstance(value, int) or value < 1 for value in dependencies):
            raise ReconcileError(f"child #{number} has invalid depends_on values")
        if number in dependencies:
            raise ReconcileError(f"child #{number} cannot depend on itself")
        result.append({
            "number": number,
            "title": title,
            "url": inline(item.get("url")),
            "responsibility": responsibility,
            "depends_on": dependencies,
            "state": inline(item.get("state") or "open").casefold(),
        })
    return result


def render(children: list[dict[str, Any]]) -> str:
    lines = [START, "## Child issues", ""]
    for child in children:
        checked = "x" if child["state"] == "closed" else " "
        label = f"[#{child['number']}]({child['url']})" if child["url"] else f"#{child['number']}"
        dependencies = ", ".join(f"#{number}" for number in child["depends_on"]) or "None"
        lines.append(
            f"- [{checked}] {label} — {child['title']}: {child['responsibility']}; Depends on: {dependencies}"
        )
    lines.extend(("", END))
    return "\n".join(lines)


def reconcile(parent: str, block: str) -> str:
    start_count, end_count = parent.count(START), parent.count(END)
    if start_count == 0 and end_count == 0:
        separator = "\n\n" if parent.strip() else ""
        return f"{parent.rstrip()}{separator}{block}\n"
    if start_count != 1 or end_count != 1:
        raise ReconcileError("parent body has malformed or duplicate decomposition markers")
    start = parent.index(START)
    end_start = parent.find(END, start)
    if end_start < 0:
        raise ReconcileError("parent body has a closing marker before its opening marker")
    end = end_start + len(END)
    return f"{parent[:start]}{block}{parent[end:]}"


def main() -> int:
    args = parse_args()
    try:
        parent = args.parent_body.read_text(encoding="utf-8")
        children = validate_children(json.loads(args.children_json.read_text(encoding="utf-8")))
        updated = reconcile(parent, render(children))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(updated, encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError, ReconcileError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
