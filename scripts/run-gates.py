#!/usr/bin/env python3
"""run-gates.py — run the CI gates a project's language standard declares (data-driven).

Reads the gate manifest (`gates.toml`, the machine-readable mirror of each language standard's gate set) and
runs the gates for whatever language(s) the target project uses. It hardcodes no toolchain, so adding a
language is adding a manifest section, not editing this script. The review agent calls this; it also works
standalone and in CI.

A language with no manifest section (no standard yet) yields a "judgment-only" result: there are no gates to
run, and the cross-language review reasons from the umbrella standards instead.

Usage:
  run-gates.py [--list] [--json] [TARGET]
    TARGET   the project directory to check (default: the current directory)
    --list   show the gates that would run; do not execute them
    --json   emit a machine-readable result (for an agent or CI to consume)

Exit code: 0 if no gate failed (passes, skips, and judgment-only are all non-failing); 1 if any gate FAILED.
A gate whose tool is not installed is reported SKIP, not FAIL.

An executed run also emits a one-line **evidence** string (verdict + gate counts + a content hash) and
includes it as `evidence` in `--json` — paste it into the phase ledger so a "verified" phase references a
real recorded run rather than a bare assertion.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # tomllib is stdlib on 3.11+; the operator floor is 3.12 (ADR-PY-001).
    print("run-gates.py needs Python 3.11+ (stdlib tomllib) to read gates.toml.", file=sys.stderr)
    raise SystemExit(2)

MANIFEST = Path(__file__).resolve().parent.parent / "gates.toml"


def detect_languages(target: Path, manifest: dict) -> list[str]:
    """Languages whose marker files are present in the target project."""
    return [
        lang
        for lang, spec in manifest.items()
        if any((target / marker).exists() for marker in spec.get("detect", []))
    ]


def run_gate(name: str, command: str, target: Path) -> dict:
    """Run one gate. PASS on exit 0, SKIP if the tool is missing (exit 127), else FAIL."""
    try:
        proc = subprocess.run(command, shell=True, cwd=target, capture_output=True, text=True)
    except OSError as exc:  # could not spawn a shell at all
        return {"name": name, "command": command, "status": "ERROR", "detail": str(exc)}
    if proc.returncode == 127:
        status = "SKIP"  # tool not installed; the review notes it, it is not a code defect
    elif proc.returncode == 0:
        status = "PASS"
    else:
        status = "FAIL"
    detail = "" if status == "PASS" else (proc.stdout + proc.stderr).strip()[-400:]
    return {"name": name, "command": command, "status": status, "detail": detail}


def evidence_line(report: dict) -> str:
    """A compact, paste-able evidence line for a phase ledger entry: verdict + gate counts + a content hash,
    so a "verified" phase references a real recorded run rather than a bare assertion. Empty for a --list
    (planned) preview; a judgment-only note when the language has no gates."""
    results = report["results"]
    if not results:
        if report["judgment_only"]:
            return ("gates: JUDGMENT-ONLY — no gate manifest for this language; reviewed from the umbrella "
                    "(no green run to record)")
        return ""
    if any(r["status"] == "PLANNED" for r in results):
        return ""  # a --list preview is not evidence of a run
    canon = "\n".join(f"{r['language']}/{r['name']}::{r['command']}::{r['status']}" for r in results)
    digest = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:10]
    npass = sum(r["status"] == "PASS" for r in results)
    nfail = sum(r["status"] == "FAIL" for r in results)
    nskip = sum(r["status"] == "SKIP" for r in results)
    verdict = "FAIL" if nfail else "PASS"
    langs = ", ".join(report["languages"]) or "none"
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    return (f"gates: {verdict} ({langs} — {len(results)} gate(s): {npass} pass / {nfail} fail / "
            f"{nskip} skip) · {stamp} · run {digest}")


def build_report(target: Path, manifest: dict, list_only: bool, fast: bool = False) -> dict:
    langs = detect_languages(target, manifest)
    report: dict = {"target": str(target), "languages": langs, "results": [], "judgment_only": []}
    if not langs:
        report["judgment_only"].append("(no manifest language detected)")
    for lang in langs:
        gates = manifest[lang].get("gates", [])
        if not gates:
            report["judgment_only"].append(lang)
            continue
        for gate in gates:
            if fast and gate.get("fast", True) is False:
                continue  # --fast (e.g. a pre-commit gate) skips gates marked fast=false (the slow ones)
            if list_only:
                report["results"].append(
                    {"language": lang, "name": gate["name"], "command": gate["command"], "status": "PLANNED"}
                )
            else:
                result = run_gate(gate["name"], gate["command"], target)
                result["language"] = lang
                report["results"].append(result)
    report["evidence"] = evidence_line(report)
    return report


def print_human(report: dict) -> None:
    marks = {"PASS": "[pass]", "FAIL": "[FAIL]", "SKIP": "[skip]", "ERROR": "[err ]", "PLANNED": "[ -> ]"}
    print(f"Gate run for {report['target']}")
    print(f"  languages detected: {', '.join(report['languages']) or 'none'}")
    for r in report["results"]:
        print(f"  {marks.get(r['status'], '[ ?  ]')} {r['language']}/{r['name']}: {r['command']}")
        if r.get("detail"):
            print(f"        {r['detail'].splitlines()[0][:120]}")
    for j in report["judgment_only"]:
        print(f"  judgment-only: {j} has no gate manifest; the review reasons from the umbrella standards.")
    if report.get("evidence"):
        print(f"  evidence: {report['evidence']}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run the CI gates a project's language standard declares.")
    parser.add_argument("target", nargs="?", default=".", help="project dir to check (default: cwd)")
    parser.add_argument("--list", action="store_true", help="show the gates that would run; do not execute")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--fast", action="store_true",
                        help="skip slow gates (those marked fast=false, e.g. the full test run); for a pre-commit gate")
    args = parser.parse_args(argv)

    if not MANIFEST.exists():
        print(f"Error: gate manifest not found at {MANIFEST}", file=sys.stderr)
        return 2
    manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"Error: target '{target}' is not a directory.", file=sys.stderr)
        return 2

    report = build_report(target, manifest, list_only=args.list, fast=args.fast)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human(report)
    failed = any(r["status"] == "FAIL" for r in report["results"])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
