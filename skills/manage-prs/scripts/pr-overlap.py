#!/usr/bin/env python3
"""Print PR pairs that share at least one changed file path.

Usage:
  gh pr list --json number,title,files --limit 100 > prs.json
  python pr-overlap.py prs.json
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: pr-overlap.py <prs.json>", file=sys.stderr)
        return 2

    data = json.loads(Path(sys.argv[1]).read_text())
    pr_files: dict[int, set[str]] = {}
    titles: dict[int, str] = {}

    for pr in data:
        num = pr["number"]
        titles[num] = pr.get("title", "")
        paths = {f["path"] for f in pr.get("files", []) if "path" in f}
        pr_files[num] = paths

    found = False
    for a, b in combinations(sorted(pr_files), 2):
        shared = pr_files[a] & pr_files[b]
        if not shared:
            continue
        found = True
        paths = ", ".join(sorted(shared)[:5])
        more = len(shared) - 5
        suffix = f" (+{more} more)" if more > 0 else ""
        print(f"#{a} <-> #{b}: {paths}{suffix}")
        print(f"  #{a}: {titles.get(a, '')[:72]}")
        print(f"  #{b}: {titles.get(b, '')[:72]}")

    if not found:
        print("No overlapping file paths among listed PRs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
