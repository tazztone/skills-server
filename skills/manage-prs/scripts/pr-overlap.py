#!/usr/bin/env python3
"""Find file overlaps and duplicate subsets among PRs grouped by baseRefName.

Usage: python pr-overlap.py prs.json
"""
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: pr-overlap.py <prs.json>", file=sys.stderr)
        return 2

    try:
        data = json.loads(Path(sys.argv[1]).read_text())
    except Exception as e:
        print(f"Error reading JSON: {e}", file=sys.stderr)
        return 1

    if not isinstance(data, list):
        print("Invalid input: expected a JSON list of PRs.", file=sys.stderr)
        return 1

    by_base = defaultdict(list)
    for pr in data:
        if "number" not in pr:
            continue
        if "files" not in pr:
            print(f"Warning: PR #{pr['number']} is missing 'files' key. Run gh pr list with 'files' field included.", file=sys.stderr)
        by_base[pr.get("baseRefName", "unknown")].append(pr)

    for base, prs in by_base.items():
        if len(prs) < 2:
            continue
        print(f"=== Target Branch: {base} ===")
        pr_files = {}
        titles = {}

        for pr in prs:
            num = pr["number"]
            titles[num] = pr.get("title", "")
            files = pr.get("files", [])
            if not files:
                print(f"  Warning: PR #{num} has no files (empty diff or missing field). Classify as Reject if confirmed empty.", file=sys.stderr)
            pr_files[num] = {f["path"] for f in files if isinstance(f, dict) and "path" in f}

        found = False
        for a, b in combinations(sorted(pr_files), 2):
            files_a, files_b = pr_files[a], pr_files[b]
            shared = files_a & files_b
            if not shared:
                continue

            found = True
            paths = ", ".join(sorted(shared))
            print(f"#{a} <-> #{b}: {paths}")

            if files_a and files_b:
                if files_b.issubset(files_a):
                    print(f"  * Duplicate Candidate: #{b} is a subset of #{a}")
                elif files_a.issubset(files_b):
                    print(f"  * Duplicate Candidate: #{a} is a subset of #{b}")

            print(f"  #{a}: {titles.get(a, '')[:72]}")
            print(f"  #{b}: {titles.get(b, '')[:72]}")

        if not found:
            print(f"No overlaps on {base}.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
