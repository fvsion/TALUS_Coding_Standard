---
name: talus-gates
description: >-
  Use to run a project's CI gates and report whether it passes: lint, format, type-check, tests, import
  boundaries, dependency and secret scans. Runs exactly the gates the project's language standard declares,
  via the data-driven gate-runner. Invoke before calling code done, on a pre-merge check, or whenever someone
  asks "does this pass the gates / checks." It runs gates only and makes no judgments; for the conformance
  review a linter cannot do, hand off to the talus-auditor subagent.
---

# Skill: Gate check

Run the project's declared CI gates and report the result. This is the cheap, mechanical check. You make
**no judgments** here. You run the gates, report pass/fail, then hand off the judgment review.

## Steps

1. Run the data-driven gate-runner against the project. It reads `gates.toml` and runs the gates the
   project's language standard declares; it hardcodes no toolchain.

   ```sh
   python3 Standards/scripts/run-gates.py --json .
   ```

   Use the path to `run-gates.py` in this repo (the standards are vendored under `Standards/`). The default
   target is the current directory; pass a path to check elsewhere.

2. Read the JSON result and report, per gate: `PASS`, `FAIL`, or `SKIP` (the tool is not installed). List
   any `FAIL` with its command so the practitioner can reproduce it. Do not fix anything; report only.

3. **Record the evidence line.** The JSON carries an `evidence` field — a one-line verdict + gate counts + a
   content hash. When a phase is being marked verified in `.talus/journal/STATUS.md`, paste that line into the
   phase entry, so a phase is *verified* only against a real recorded green run, not a bare assertion.

4. Interpret the outcome:
   - **All pass** (or pass + skip): the mechanical bar is met. Recommend a `talus-auditor` review for the
     judgment checks a linter cannot make.
   - **Any fail**: report them plainly; the code is not done.
   - **judgment-only** (the runner found no manifest for the language): there are no gates for this language
     yet. Hand off to the `talus-auditor` subagent, which reviews by reasoning from the umbrella standards.

## Boundary

This skill runs gates only. The conformance **judgment** (layered architecture, ports-and-adapters, SOLID,
security-by-construction, cross-platform, naming, and the anti-AI-tell style) is the **talus-auditor**
subagent's job, and an unstandardized language is reviewed there too. Always hand off for the judgment.
