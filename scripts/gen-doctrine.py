#!/usr/bin/env python3
"""gen-doctrine.py — generate DOCTRINE.md, the flattened must-gate contract, from doctrine.toml.

DOCTRINE.md is the distilled, always-loadable contract: every standard's hardest **must**-gates on roughly
one screen, each citing its standard + § so the full rule is one lookup away. The source of truth is the
curated data file `doctrine.toml` (the standards themselves remain the source of truth for the full rule);
this script is the renderer. It mirrors the gates.toml / run-gates.py pattern — a .toml data file plus a
Python tool that consumes it — so adding or sharpening a gate is editing the data, never the script.

Usage:
  gen-doctrine.py            regenerate DOCTRINE.md from doctrine.toml (writes the file)
  gen-doctrine.py --check    verify DOCTRINE.md is current with doctrine.toml; exit 1 if stale (for CI / pre-commit)
  gen-doctrine.py --stdout   print the rendered contract to stdout; write nothing

Exit code: 0 on success (written, or --check current); 1 if --check finds DOCTRINE.md stale; 2 on a usage or
data error.
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # tomllib is stdlib on 3.11+; the operator floor is 3.12 (ADR-PY-001).
    print("gen-doctrine.py needs Python 3.11+ (stdlib tomllib) to read doctrine.toml.", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "doctrine.toml"
DOCTRINE_PATH = ROOT / "DOCTRINE.md"

HEADER = """\
# TALUS DOCTRINE — the must-gate contract

> **Generated from `doctrine.toml` by `scripts/gen-doctrine.py` — do not edit by hand.** Regenerate with
> `python3 scripts/gen-doctrine.py`; `--check` verifies it is current (a CI / pre-commit gate).
>
> The flattened, always-loadable contract: every standard's hardest **must**-gates on roughly one screen,
> each citing its standard + § so the full rule and its rationale are one lookup away. A `must` is a gate
> (deviating needs an ADR). Read this first; then open only the `§` you need, never a whole standard file.
> This is the distillation; the standards are the source of truth.
>
> Standards Suite v{version}.
"""

FOOTER = """\
---

Each line above is a **must** — a gate, not a suggestion. The bracketed handle (for example `[A3]`, `[PY7]`)
identifies the gate; the `§` points to the full rule in the named standard. {n_standards} standards · {n_gates} gates.
"""


def render(data: dict) -> str:
    """Render the full DOCTRINE.md text from the parsed doctrine.toml data.

    Each block (header, one per standard, footer) is built without surrounding blank lines; the blocks are
    joined with exactly one blank line between them, so spacing is uniform regardless of the data."""
    standards = data.get("standard", [])
    if not standards:
        raise ValueError("doctrine.toml declares no [[standard]] entries")
    version = str(data.get("version", "")).strip() or "0.0"

    blocks: list[str] = [HEADER.format(version=version).rstrip("\n")]
    n_gates = 0
    for std in standards:
        sid = std["id"]
        gates = std.get("gates", [])
        if not gates:
            raise ValueError(f"standard {sid} ({std['file']}) declares no gates")
        lines = [f"## {sid} — {std['title']} · `{std['file']}`", ""]
        for i, gate in enumerate(gates, start=1):
            lines.append(f"- **[{sid}{i}]** {gate}")
            n_gates += 1
        blocks.append("\n".join(lines))

    blocks.append(FOOTER.format(n_standards=len(standards), n_gates=n_gates).rstrip("\n"))
    return "\n\n".join(blocks) + "\n"


def load_data() -> dict:
    if not DATA_PATH.exists():
        print(f"Error: source data not found at {DATA_PATH}", file=sys.stderr)
        raise SystemExit(2)
    return tomllib.loads(DATA_PATH.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate DOCTRINE.md from doctrine.toml.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="verify DOCTRINE.md is current with doctrine.toml; exit 1 if stale (no write)")
    mode.add_argument("--stdout", action="store_true", help="print the rendered contract; write nothing")
    args = parser.parse_args(argv)

    try:
        rendered = render(load_data())
    except (KeyError, ValueError) as exc:
        print(f"Error: malformed doctrine.toml — {exc}", file=sys.stderr)
        return 2

    if args.stdout:
        sys.stdout.write(rendered)
        return 0

    if args.check:
        current = DOCTRINE_PATH.read_text(encoding="utf-8") if DOCTRINE_PATH.exists() else ""
        if current == rendered:
            print("DOCTRINE.md is current.")
            return 0
        print("DOCTRINE.md is STALE — regenerate it with: python3 scripts/gen-doctrine.py", file=sys.stderr)
        diff = difflib.unified_diff(
            current.splitlines(keepends=True), rendered.splitlines(keepends=True),
            fromfile="DOCTRINE.md (on disk)", tofile="DOCTRINE.md (expected)",
        )
        sys.stderr.writelines(diff)
        return 1

    DOCTRINE_PATH.write_text(rendered, encoding="utf-8")
    print(f"Wrote {DOCTRINE_PATH.relative_to(ROOT)} ({rendered.count(chr(10))} lines).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
