#!/usr/bin/env python3
"""Reject empty or unexpectedly incomplete snapshots before publication."""

import pathlib
import sys


def validate(stage, previous=pathlib.Path("docs"), baseline=pathlib.Path("logs/failed.txt")):
    docs = list((stage / "docs").rglob("*.md"))
    if not docs:
        raise ValueError("mirror contains no documents")
    if not (stage / "metadata.yaml").is_file():
        raise ValueError("mirror metadata is missing")
    failures = stage / "logs/failed.txt"
    if not failures.is_file():
        raise ValueError("mirror failure log is missing")
    old_failures = set(baseline.read_text().splitlines()) if baseline.is_file() else set()
    new_failures = set(failures.read_text().splitlines()) - old_failures - {""}
    if new_failures:
        raise ValueError("new fetch failures:\n" + "\n".join(sorted(new_failures)))
    old_count = sum(1 for _ in previous.rglob("*.md"))
    if old_count and len(docs) < old_count * 0.8:
        raise ValueError(f"document count dropped from {old_count} to {len(docs)} (over 20%)")
    print(f"Validated {len(docs)} documents; no new fetch failures")


if __name__ == "__main__":
    try:
        validate(pathlib.Path(sys.argv[1]))
    except (OSError, ValueError) as error:
        sys.exit(str(error))
