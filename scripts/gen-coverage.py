#!/usr/bin/env python3
"""gen-coverage.py — generate GATE_COVERAGE.md, the self-conformance gate-coverage audit.

For every must-gate in DOCTRINE.md (the handles [A1]..[PY9], defined in doctrine.toml), coverage.toml records
the enforcement arm that catches a violation. This script joins the two, validates that the mapping is
complete and has not drifted, and renders GATE_COVERAGE.md — the artifact that makes "enforced, not
aspirational" checkable rather than asserted.

It mirrors the gates.toml / run-gates.py and doctrine.toml / gen-doctrine.py pattern: data files plus a thin
renderer. The catch never lives in the script.

Validation (any failure exits 2, before writing):
  * every doctrine gate handle has exactly one coverage row, and no row references a missing handle;
  * each row's `must` token is still a substring of that gate's text (a drift guard against rewording/reorder);
  * each row's `catch` is one of the known levels and its `mechanism` is non-empty.

Usage:
  gen-coverage.py            regenerate GATE_COVERAGE.md (writes the file)
  gen-coverage.py --check    verify GATE_COVERAGE.md is current; exit 1 if stale (for CI / pre-commit)
  gen-coverage.py --stdout   print the rendered audit to stdout; write nothing

Exit code: 0 on success; 1 if --check finds the file stale; 2 on a usage, data, or validation error.
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # tomllib is stdlib on 3.11+; the operator floor is 3.12 (ADR-PY-001).
    print("gen-coverage.py needs Python 3.11+ (stdlib tomllib) to read the .toml sources.", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
DOCTRINE_DATA = ROOT / "doctrine.toml"
COVERAGE_DATA = ROOT / "coverage.toml"
OUT_PATH = ROOT / "GATE_COVERAGE.md"

CATCH_LEVELS = ("ci-gate", "auditor", "design", "phase", "advisory")
CATCH_BLURB = {
    "ci-gate": "a blocking automated gate (a tool returns pass/fail)",
    "auditor": "talus-auditor review-time judgment (a finding tied to a §)",
    "design": "caught at design time by talus-architect / talus-cartographer",
    "phase": "the talus-phase skill + Phase Guidelines process",
    "advisory": "a strong default with no named TALUS arm; justified per row",
}

HEADER = """\
# TALUS GATE COVERAGE — the self-conformance audit

> **Generated from `doctrine.toml` + `coverage.toml` by `scripts/gen-coverage.py` — do not edit by hand.**
> Regenerate with `python3 scripts/gen-coverage.py`; `--check` verifies it is current (a CI / pre-commit gate).
>
> Every must-gate in [`DOCTRINE.md`](DOCTRINE.md) (handles `[A1]`..`[PY9]`) mapped to the arm that catches a
> violation. This is what makes "enforced, not aspirational" checkable: the generator fails if any gate has
> no coverage, so a gate cannot quietly go unenforced. Catch levels, strongest first:
>
{legend}
>
> **Coverage:** {summary}.
> {framing}
"""

FOOTER = """\
---

Read a row with its gate in `DOCTRINE.md`: the handle ties them together. A `must` here is enforced by the
named arm; the lone advisory ({advisory_list}) is a strong default with no automated TALUS gate, justified in
its row. {n_gates} gates · {n_standards} standards.
"""


def gate_index(doctrine: dict) -> list[dict]:
    """The ordered gate list from doctrine.toml: one dict per gate with its handle, text, and standard meta.

    Handle assignment mirrors gen-doctrine.py exactly (id + 1-based position within the standard)."""
    index: list[dict] = []
    for std in doctrine.get("standard", []):
        sid = std["id"]
        for i, text in enumerate(std.get("gates", []), start=1):
            index.append(
                {"handle": f"{sid}{i}", "sid": sid, "title": std["title"], "file": std["file"], "text": text}
            )
    return index


def validate(index: list[dict], rows: list[dict]) -> dict[str, dict]:
    """Cross-check coverage rows against the doctrine gate index. Raises ValueError on any gap or drift.

    Returns a handle -> coverage-row map for rendering."""
    by_handle = {g["handle"] for g in index}
    seen: dict[str, dict] = {}
    errors: list[str] = []

    for row in rows:
        handle = row.get("gate", "")
        if handle not in by_handle:
            errors.append(f"coverage row '{handle}' references no gate in doctrine.toml")
            continue
        if handle in seen:
            errors.append(f"duplicate coverage row for gate '{handle}'")
            continue
        seen[handle] = row
        catch = row.get("catch", "")
        if catch not in CATCH_LEVELS:
            errors.append(f"gate '{handle}': catch '{catch}' is not one of {CATCH_LEVELS}")
        if not row.get("mechanism", "").strip():
            errors.append(f"gate '{handle}': empty mechanism")
        token = row.get("must", "")
        text = next(g["text"] for g in index if g["handle"] == handle)
        if not token or token not in text:
            errors.append(f"gate '{handle}': drift — must token {token!r} is not in the gate text {text!r}")

    missing = [g["handle"] for g in index if g["handle"] not in seen]
    if missing:
        errors.append(f"{len(missing)} gate(s) with no coverage row: {', '.join(missing)}")

    if errors:
        raise ValueError("; ".join(errors))
    return seen


def _cell(text: str) -> str:
    """Escape a value for a Markdown table cell."""
    return text.replace("|", "\\|").strip()


def render(doctrine: dict, coverage: dict) -> str:
    index = gate_index(doctrine)
    if not index:
        raise ValueError("doctrine.toml declares no gates")
    rows = coverage.get("coverage", [])
    by_handle = validate(index, rows)

    counts = {level: sum(1 for r in by_handle.values() if r["catch"] == level) for level in CATCH_LEVELS}
    n_gates = len(index)
    blocking = counts["ci-gate"]
    systematic = counts["auditor"] + counts["design"] + counts["phase"]
    advisory_handles = [h for h, r in by_handle.items() if r["catch"] == "advisory"]

    legend = "\n".join(f"> - **{lvl}** — {CATCH_BLURB[lvl]}" for lvl in CATCH_LEVELS)
    summary = " · ".join(f"{counts[lvl]} {lvl}" for lvl in CATCH_LEVELS) + f" ({n_gates} gates)"
    framing = (f"{blocking} caught by a blocking automated gate, {systematic} by a systematic review/design/"
               f"process arm, {len(advisory_handles)} advisory.")

    blocks = [HEADER.format(legend=legend, summary=summary, framing=framing).rstrip("\n")]

    # Group rows by standard, in doctrine order.
    seen_sids: list[str] = []
    for g in index:
        if g["sid"] not in seen_sids:
            seen_sids.append(g["sid"])
    for sid in seen_sids:
        gates = [g for g in index if g["sid"] == sid]
        title, file = gates[0]["title"], gates[0]["file"]
        lines = [f"## {sid} — {title} · `{file}`", "", "| Gate | Must | Catch | Mechanism |",
                 "|---|---|---|---|"]
        for g in gates:
            r = by_handle[g["handle"]]
            lines.append(f"| `[{g['handle']}]` | {_cell(r['must'])} | `{r['catch']}` | {_cell(r['mechanism'])} |")
        blocks.append("\n".join(lines))

    advisory_list = ", ".join(f"`[{h}]`" for h in advisory_handles) or "none"
    blocks.append(FOOTER.format(advisory_list=advisory_list, n_gates=n_gates,
                                n_standards=len(seen_sids)).rstrip("\n"))
    return "\n\n".join(blocks) + "\n"


def load(path: Path) -> dict:
    if not path.exists():
        print(f"Error: source data not found at {path}", file=sys.stderr)
        raise SystemExit(2)
    return tomllib.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate GATE_COVERAGE.md from doctrine.toml + coverage.toml.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="verify GATE_COVERAGE.md is current; exit 1 if stale (no write)")
    mode.add_argument("--stdout", action="store_true", help="print the rendered audit; write nothing")
    args = parser.parse_args(argv)

    try:
        rendered = render(load(DOCTRINE_DATA), load(COVERAGE_DATA))
    except (KeyError, ValueError) as exc:
        print(f"Error: gate coverage is incomplete or drifted — {exc}", file=sys.stderr)
        return 2

    if args.stdout:
        sys.stdout.write(rendered)
        return 0

    if args.check:
        current = OUT_PATH.read_text(encoding="utf-8") if OUT_PATH.exists() else ""
        if current == rendered:
            print("GATE_COVERAGE.md is current.")
            return 0
        print("GATE_COVERAGE.md is STALE — regenerate it with: python3 scripts/gen-coverage.py", file=sys.stderr)
        diff = difflib.unified_diff(
            current.splitlines(keepends=True), rendered.splitlines(keepends=True),
            fromfile="GATE_COVERAGE.md (on disk)", tofile="GATE_COVERAGE.md (expected)",
        )
        sys.stderr.writelines(diff)
        return 1

    OUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUT_PATH.relative_to(ROOT)} ({rendered.count(chr(10))} lines).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
