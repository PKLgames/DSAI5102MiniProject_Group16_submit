"""Rebuild the analysis in this package and check it against the shipped results.

    python reproduce.py            # analysis + numeric check  (about 2 min)
    python reproduce.py --full     # also figures, tables, ten split seeds  (about 4 min)

The check compares every number in results/analysis.json with
expected/analysis_reference.json. Floats are compared to 1e-9 relative tolerance;
the zip checksum and anything named like a runtime are ignored.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
EXPECTED = ROOT / "expected"

IGNORE = ("input_zip_sha256", "runtime", "seconds", "elapsed", "duration", "timestamp")


def run(script: str) -> None:
    print(f"\n=== {script} " + "=" * (60 - len(script)))
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True, cwd=ROOT)


def walk(node, path=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}" if path else key)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from walk(value, f"{path}[{i}]")
    else:
        yield path, node


def compare(expected, actual) -> list[str]:
    problems: list[str] = []
    exp = dict(walk(expected))
    act = dict(walk(actual))

    for key in sorted(set(exp) | set(act)):
        if key in exp and key in act:
            continue
        if any(token in key for token in IGNORE):
            continue
        problems.append(f"missing key: {key}" if key not in act else f"extra key: {key}")

    for key, want in exp.items():
        if key not in act or any(token in key for token in IGNORE):
            continue
        got = act[key]
        if isinstance(want, (int, float)) and isinstance(got, (int, float)):
            if isinstance(want, bool) or isinstance(got, bool):
                if want != got:
                    problems.append(f"{key}: {want} != {got}")
            elif not math.isclose(float(want), float(got), rel_tol=1e-9, abs_tol=1e-12):
                problems.append(f"{key}: {want!r} != {got!r}")
        elif want != got:
            problems.append(f"{key}: {want!r} != {got!r}")
    return problems


def compare_splits() -> list[str]:
    """Compare the split-seed table, ignoring the wall-clock column."""
    import csv

    def rows(path: Path) -> list[dict]:
        with path.open() as handle:
            return [{k: v for k, v in row.items() if k != "seconds"} for row in csv.DictReader(handle)]

    want = rows(EXPECTED / "repeat_splits_reference.csv")
    got = rows(RESULTS / "repeat_splits.csv")
    if len(want) != len(got):
        return [f"repeat_splits: {len(got)} rows instead of {len(want)}"]
    problems = []
    for a, b in zip(want, got):
        for key in a:
            if a[key] != b[key]:
                try:
                    same = math.isclose(float(a[key]), float(b[key]), rel_tol=1e-9)
                except ValueError:
                    same = a[key] == b[key]
                if not same:
                    problems.append(f"repeat_splits seed {a['seed']} {key}: {a[key]} != {b[key]}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="also rebuild figures, tables and the split-seed check")
    args = parser.parse_args()

    run("analyse.py")
    problems = compare(json.loads((EXPECTED / "analysis_reference.json").read_text()),
                       json.loads((RESULTS / "analysis.json").read_text()))

    if args.full:
        run("make_figures.py")
        run("add_figures.py")
        run("export_tables.py")
        run("repeat_splits.py")
        problems += compare_splits()

    print("\n" + "=" * 68)
    if problems:
        print(f"CHECK FAILED — {len(problems)} difference(s):")
        for item in problems[:40]:
            print("  " + item)
        return 1
    print("CHECK PASSED — results/analysis.json reproduces expected/analysis_reference.json")
    print("(every number quoted in the report comes from that file)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
