# Changelog

All notable changes to the TALUS engineering standards are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The **suite version** is declared by the umbrella
(`A_TALUS_Coding_Standard.md`) as a release marker; individual standards version independently after the v1.0
lock (Git & Release Engineering Standard §5–§6).

## [1.3] - 2026-06-26

The User Documentation Standard. End-user documentation becomes a first-class, gated deliverable — a peer of
the Documentation & Architecting Standard — closing the gap the security industry most reliably leaves open.

### Added
- **User Documentation Standard (`K`) → v1.0:** a new standard defining the four user-facing artifacts
  (README, GUIDE, RTFM/REFERENCE, TUTORIAL) on a Diátaxis backbone, with tier-proportional depth limits,
  per-artifact anti-scope, and an anti-AI-tell voice standard (§9) — including a hard rule that user docs carry
  no em or en dashes and no ` -- ` substitute. Wired into the umbrella, `DOCTRINE.md` (six gates `[K1]`–`[K6]`),
  and `GATE_COVERAGE.md`. The suite now spans **twelve standards · 72 gates**.
- **`talus-herald` (the seventh agent):** authors and reviews the user-doc set to `K` (author + review modes),
  defaulting to the `sonnet` model with an install-time `--herald-opus` opt-in (a TTY prompt when interactive;
  `sonnet` without blocking under AI/CI). Projected into the Roo / Codex / generic harness targets.
- **The suite's own user docs**, authored to `K` as a dogfood: `USER_GUIDE.md`, `REFERENCE.md`, `TUTORIAL.md`,
  and a refreshed `README.md`.

### Changed
- **AI Coding Phase Guidelines → v1.3:** the build-loop discipline is hardened — §3 gains shape-first and
  record-completely `must`s, §7.1 a chronicler-cadence rule (write the sub-compact at every effort boundary).
  Reinforced across the installed directive, the per-turn reminder hook, the seeded `STATUS.md` scaffold, and
  the `talus-phase` / `talus-chronicler` cadence.
- **Umbrella → Standards Suite v1.3:** declares the suite version; adds `K` to the hierarchy (§1.2) and a §9
  pointer (internal design specs `C` vs the external doc set `K`).

## [1.2.1] - 2026-06-26

A doctrine-consistency patch. Two design-time-artifact rules are clarified and aligned across the standards,
the agents, and the generated contracts; no new capability.

### Changed
- **Documentation & Architecting Standard → v1.2.1:** §3.1 now **prescribes `Research_and_Planning/`** (a
  project-root folder beside `Architecture/`) as the canonical home for the pre-architecture design trail
  (research briefs + design proposal), resolving a contradiction where the prose routed briefs to `.talus/`
  while the Appendix A tree and the `talus-researcher` / `talus-architect` agents already wrote to
  `Research_and_Planning/`. The running journal (decision log, status ledger, phase records) stays in `.talus/`.
- **Git & Release Engineering Standard → v1.2.1:** §9 (the dual-use git posture) now states that **design-time
  artifacts (`Architecture/`, `Research_and_Planning/`) are internal by default and excluded from a public
  release** unless a project deliberately publishes its design. The `[H6]` must-gate and its `GATE_COVERAGE.md`
  row are extended to name them, so the rule is enforced — a project keeps them private through its own
  produce-the-public-tree release step, not through this repo's `.oss-exclude` (which is not installed into
  adopting projects).

## [1.2] - 2026-06-26

A durability + self-conformance release. The directive now survives long and compacted sessions, conformance
review runs at every phase boundary (not just at the end), and the suite's own must-gates are distilled into
one contract and their enforcement audited. The AI Coding Phase Guidelines bump to v1.2 (new rules in §6 and
§7.4); other companion standards are unchanged.

### Added
- **`DOCTRINE.md`** — the flattened must-gate contract: every standard's hardest gates on roughly one screen,
  each with a stable handle (`[A1]`..`[PY9]`) and a `§` pointer. Generated from `doctrine.toml` by
  `scripts/gen-doctrine.py`; `--check` is a sync gate.
- **`GATE_COVERAGE.md`** — the self-conformance audit: every must-gate mapped to the arm that catches a
  violation (`ci-gate` / `auditor` / `design` / `phase` / `advisory`). Generated from `coverage.toml` by
  `scripts/gen-coverage.py`, which fails unless every gate has a catch row, so a gate cannot ship unenforced.
- **Per-turn reminder hook, default on** (opt out with `--no-hook`), on both Claude (`.claude/settings.json`)
  and Codex (`.codex/hooks.json`): re-states the core rule every turn so it survives compaction.
- **Git pre-commit gate, default on** (opt out with `--no-precommit`): runs the CI gates
  (`run-gates.py --fast`) and blocks a failing commit. A new `--fast` flag skips slow gates (the full test run)
  so commits stay quick; CI still runs the full set.

### Changed
- **Per-phase review is now doctrine.** The installed directive, AI Coding Phase Guidelines §6, the
  `talus-phase` skill, and the `talus-auditor` agent all require a diff-scoped conformance review at each phase
  boundary, with a whole-repo pass before a build is called done — review is no longer deferred to the end.
- **AI Coding Phase Guidelines → v1.2:** new §6 per-phase review rule and new §7.4 "Directive durability" (the
  presence / salience / re-anchor / enforcement model; subagents do not inherit the directive).

## [1.1.1] - 2026-06-26

An indexing + review-hardening release. No rule changed; the standards were re-indexed for stable sort and
hardened through three review rounds. Companion standards keep their versions (the fixes were editorial).

### Changed
- **Indexed the standards `A_` to `J_`** (letter prefixes) so they always sort in read order. Letters, not
  numbers: `00_`–`09_` would collide visually with a tool's numeric Architecture-suite slots (`02_DATA_MODEL`,
  `08_ROADMAP`, `09_DEVOPS`). The umbrella is `A_`, the AI Coding Phase Guidelines `B_`, and so on; the Python
  language standard stays `languages/Python_Coding_Standard.md`.
- **Multi-round review fixes** (Full / Python-deep / Consistency): removed two internal build-compartment ids
  that had leaked into the Documentation & Architecting Standard; corrected the Python standard's reviewer
  description (agent count, and "consumes the gate verdict" rather than "runs the gates"); fixed a grammar slip
  and two cross-reference imprecisions in the Observability and LLM standards. Every cross-standard reference
  was verified to resolve.

### Added
- A **"How TALUS compares"** table in the README (horizontal/concern-oriented vs per-stack, spec-driven, and
  lifecycle suites), with honest trade-offs.

## [1.1] - 2026-06-26

The first efficiency release: read large standards **by section**, not whole-file, so the suite stays cheap on
a small context window. No rule was removed or changed in a breaking way.

### Added
- Umbrella **§1.5 — the canonical language-standard section framework**: an enumerated, language-agnostic
  section map (Parts I–VII / §1–§28 / Appendices A–E) that every language standard mirrors, so a reader (and
  the `talus-auditor`) navigates any standard by the same map and reads only the relevant `§` — and no concern
  is ever lost in a section read.
- AI Coding Phase Guidelines **§4.1 — operating under a constrained context window**: read by section; route a
  heavy/large-doc read into an isolated subagent; keep the working set lean.
- AI Coding Phase Guidelines **Appendix A** — conditional `Scale:` / `Budget:` phase-template fields (state the
  expected input size and the permissible time/space complexity class before writing data-path code).
- A gate-run **evidence line** in `scripts/run-gates.py` (verdict + gate counts + a content hash), surfaced by
  the `talus-gates` skill and pasted into the phase ledger so a "verified" phase references a real recorded
  green run rather than a bare assertion.
- This `CHANGELOG.md`.

### Changed
- Documentation & Architecting Standard **§6** — documents are **section-addressable**: a navigable
  Contents/section map, read *Contents → the relevant `§`* and never whole-file when context is tight.
- AI Coding Phase Guidelines **§7.1** — the phase ledger is kept **bounded** (current state + next + a short
  recent window inline; older detail rolls into the rolling index and the compacted records).
- The installer directive (`scripts/install.sh`) now tells the agent to read a standard by section, not
  whole-file (both the `CLAUDE.md` and codex `AGENTS.md` directives).
- `talus-auditor` now reads the standard **by section** and **defaults to reviewing the phase diff** (the
  changed files/hunks), reserving a whole-repo pass for a milestone or pre-release audit.
- Python Coding Standard — a section-addressable reading note under its Contents.

## [1.0] - 2026-06-25

- Initial locked release: the umbrella **TALUS Coding Standard** + the **Python Coding Standard** + nine
  cross-cutting standards (Documentation & Architecting, Visual UX/UI, AI Coding Phase Guidelines, Licensing &
  Editions, Security & OpSec, Git & Release Engineering, API & Data-Contract, Observability & Reliability,
  LLM/AI Integration), the portable "first-ingest" tooling, the proprietary/OSS split, and the claude-first
  agents + skills. All standards were reviewed end-to-end and locked together at v1.0.
