#!/usr/bin/env python3
"""Normalize Obsidian workspace state before Git stores it."""

import json
import sys


IGNORED_TOP_LEVEL_KEYS = {"active", "lastOpenFiles"}


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        sys.stdout.write(raw)
        return 0

    if not isinstance(data, dict):
        sys.stdout.write(raw)
        return 0

    for key in IGNORED_TOP_LEVEL_KEYS:
        data.pop(key, None)

    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
