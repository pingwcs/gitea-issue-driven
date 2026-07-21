#!/usr/bin/env python3
"""Calculate a deterministic label-driven Gitea priority baseline."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_POLICY = Path(__file__).resolve().parent.parent / "references" / "priority-policy.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", nargs="+", required=True)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold().replace("_", "-")).strip()


def tokens(value: str) -> set[str]:
    normalized = normalize(value)
    return {normalized, *(part for part in re.split(r"::|[/ :]", normalized) if part)}


def main() -> int:
    args = parse_args()
    try:
        policy: dict[str, Any] = json.loads(args.policy.read_text(encoding="utf-8"))
        order = policy["priority_order"]
        priorities = policy["priorities"]
        rules = policy["label_rules"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"could not read priority policy: {exc}", file=sys.stderr)
        return 1

    labels = list(dict.fromkeys(label for label in args.labels if label.strip()))
    matches: list[dict[str, str]] = []
    for label in labels:
        label_tokens = tokens(label)
        for rule, definition in rules.items():
            if normalize(rule) in label_tokens:
                matches.append({"label": label, "rule": rule, "priority": definition["priority"]})

    rank = {priority: position for position, priority in enumerate(order)}
    baseline = policy["default_priority"]
    for match in matches:
        if rank[match["priority"]] < rank[baseline]:
            baseline = match["priority"]

    result = {
        "schema_version": 1,
        "labels": labels,
        "baseline_priority": baseline,
        "strategy": priorities[baseline]["strategy"],
        "matched_rules": sorted(matches, key=lambda item: (rank[item["priority"]], item["rule"])),
        "required_actions": priorities[baseline]["required_actions"],
        "manual_review": "Escalate when verified impact exceeds the label baseline; never auto-downgrade an explicit priority.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
