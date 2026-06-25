# TALUS Coding Standard: Reference

Exhaustive lookup reference for the TALUS standards suite. All flags, config keys, agents, skills, gates,
and file layouts. No narrative; for task recipes see [USER_GUIDE.md](USER_GUIDE.md), for an end-to-end
walkthrough see [TUTORIAL.md](TUTORIAL.md).

---

## Contents

1. [Standards index](#1-standards-index)
2. [Agents](#2-agents)
3. [Skills](#3-skills)
4. [Scripts](#4-scripts)
   - [install.sh](#41-installsh)
   - [run-gates.py](#42-run-gatespy)
   - [gen-doctrine.py](#43-gen-doctrinepy)
   - [gen-coverage.py](#44-gen-coveragepy)
   - [project-agents.py](#45-project-agentspy)
   - [sync-agents.sh](#46-sync-agentssh)
5. [Configuration files](#5-configuration-files)
   - [doctrine.toml](#51-doctrinetoml)
   - [coverage.toml](#52-coveragetoml)
   - [gates.toml](#53-gatestoml)
6. [Generated artifacts](#6-generated-artifacts)
7. [Gate manifest (Python)](#7-gate-manifest-python)
8. [Repository layout](#8-repository-layout)
9. [Exit codes](#9-exit-codes)

---

## 1. Standards index

All standards live in the repository root. Read `DOCTRINE.md` first; open the individual standard only for
the section you need.

| File | Code | Title | Version |
|---|---|---|---|
| `DOCTRINE.md` | (generated) | Flattened must-gate contract (generated; do not edit) | generated from doctrine.toml |
| `GATE_COVERAGE.md` | (generated) | Self-conformance gate-coverage audit (generated; do not edit) | generated from coverage.toml |
| `A_TALUS_Coding_Standard.md` | A | Language-agnostic umbrella | v1.3 |
| `B_AI_Coding_Phase_Guidelines.md` | B | How an AI builds in bounded, reviewable phases | v1.3 |
| `C_Documentation_and_Architecting_Standard.md` | C | Minimum design-spec set (the Architecture/ baseline) | v1.2.1 |
| `D_Visual_UX_UI_Standard.md` | D | CLI and web UX/UI | v1.0 |
| `E_API_and_Data_Contract_Standard.md` | E | Contract-first interfaces and the output envelope | v1.0 |
| `F_Security_and_OpSec_Standard.md` | F | Secure and opsec by construction | v1.0 |
| `G_Observability_and_Reliability_Standard.md` | G | Telemetry, SLOs, safe rollout | v1.0 |
| `H_Git_and_Release_Engineering_Standard.md` | H | Trunk-based flow, SemVer, gated releases | v1.2.1 |
| `I_Licensing_and_Editions_Standard.md` | I | Open-core community and pro editions | v1.0 |
| `J_LLM_AI_Integration_Standard.md` | J | LLMs inside products, safely (OWASP LLM Top 10 mapped) | v1.0 |
| `K_User_Documentation_Standard.md` | K | The four user-facing doc artifacts (README, GUIDE, RTFM, TUTORIAL) | v1.0 |
| `languages/Python_Coding_Standard.md` | PY | Python: Pyright strict, ruff, pytest, uv, Hatchling | v1.1 |

---

## 2. Agents

Seven agents live in `.claude/agents/` (the canonical source). Claude Code reads them directly. Other
harnesses derive from them via `project-agents.py`.

| Agent | Role | Model | Tools |
|---|---|---|---|
| `talus-researcher` | Cross-domain literature research; algorithm-to-problem mapping; annotated research brief with citations | opus | Read, Glob, Grep, WebSearch, WebFetch, Write |
| `talus-architect` | Design proposal: module decomposition, data model, algorithm selection, ADRs, integration contracts | opus | Read, Glob, Grep, WebSearch, WebFetch, Write |
| `talus-scribe` | Author Architecture/ doc suite to the gold standard; sense-aware doc edits | opus | Read, Glob, Grep, Write, Edit |
| `talus-cartographer` | Validate cross-component contracts; maintain the contract registry; detect naming drift | sonnet | Read, Glob, Grep, Write, Edit |
| `talus-auditor` | Code conformance review against the relevant standard; per-rule findings with file:line | sonnet | Read, Glob, Grep, Bash, Write |
| `talus-herald` | Author and review user-facing docs (README, GUIDE, RTFM, TUTORIAL) to the User Documentation Standard (K) | sonnet (upgradable to opus via --herald-opus) | Read, Glob, Grep, Bash, Write, Edit |
| `talus-chronicler` | Maintain `.talus/journal/`: write compacted-conversation records, refresh the rolling index | sonnet | Read, Glob, Grep, Bash, Write, Edit |

**Pipeline order (design):** researcher -> architect -> scribe -> cartographer.
**Cross-cutting review:** talus-auditor (code quality), talus-herald (user docs), talus-chronicler (journal upkeep).
**Dispatch protocol:** perform these roles inline in a warm session; dispatch an actual subagent for
research-heavy work, wide cross-component audits, or cold-context sessions.

---

## 3. Skills

Two skills live in `.claude/skills/`. Skills are model-invoked, short procedures (only name and description
are always loaded; the body loads on use).

| Skill | Directory | Role |
|---|---|---|
| `talus-phase` | `.claude/skills/talus-phase/SKILL.md` | Drive a build in bounded, reviewed phases: shape the phase template, do one phase, verify with evidence, stop for review. |
| `talus-gates` | `.claude/skills/talus-gates/SKILL.md` | Run the project's CI gates via `run-gates.py` and report pass/fail. No judgment; report only. |

---

## 4. Scripts

All scripts live in `Standards/scripts/` (vendored). Run them from the project root.

### 4.1 install.sh

Installs the standards into a target project.

```
bash Standards/scripts/install.sh <target-dir> [harness] [options]
```

| Argument / Flag | Type | Default | Effect |
|---|---|---|---|
| `<target-dir>` | positional, required | (required) | The project directory to install into. Must exist and be outside the Standards tree. |
| `[harness]` | positional, optional | `claude` | Agent harness to target. One of: `claude`, `roo`, `codex`, `chatgpt`, `generic`. A non-Claude harness is derived immediately via `project-agents.py`. |
| `--no-hook` | flag | off | Skip the per-turn reminder hook (`CLAUDE.md` directive is the only orientation layer). |
| `--no-precommit` | flag | off | Skip the pre-commit gate. |
| `--herald-opus` | flag | off | Install `talus-herald` on the `opus` model (higher quality, higher cost). Mutually exclusive with `--herald-sonnet`. |
| `--herald-sonnet` | flag | off | Explicitly select the `sonnet` model for `talus-herald` (suppresses the interactive prompt; useful in CI). |
| `-h`, `--help` | flag | (n/a) | Print usage and exit. |

**What install.sh does (in order):**

1. Vendors `Standards/` into `<target>/Standards/` (excludes `.git`, `.claude`, `.talus`).
2. Runs `sync-agents.sh --suite <target>` to install agents and `.talus/` context.
3. If `--herald-opus`: rewrites `talus-herald.md` frontmatter to `model: opus`.
4. Scaffolds `.talus/journal/STATUS.md` and `JOURNAL_INDEX.md` if absent.
5. Adds a `.gitignore` entry for `Standards/` (idempotent).
6. If harness is `roo`, `codex`, `chatgpt`, or `generic`: runs `project-agents.py <harness> --out <target>`.
7. Appends the standards directive to `CLAUDE.md` (and `AGENTS.md` for Codex). Append-only; never overwrites.
8. If `--hook` (default): writes the per-turn reminder hook to `.claude/settings.json` or `.codex/hooks.json`.
9. If `--precommit` (default) and target is a git repo: installs `.git/hooks/pre-commit`.

**Idempotency:** safe to re-run. The directive append checks for an existing marker; the `.gitignore` entry
checks for the marker comment; the pre-commit gate does not clobber an existing hook.

### 4.2 run-gates.py

Runs the CI gates a project's language standard declares. Reads `gates.toml`.

```
python3 Standards/scripts/run-gates.py [options] [TARGET]
```

| Argument / Flag | Type | Default | Effect |
|---|---|---|---|
| `TARGET` | positional, optional | `.` (cwd) | Project directory to check. |
| `--list` | flag | off | Show which gates would run without executing them. Output shows status `PLANNED`. |
| `--json` | flag | off | Emit machine-readable JSON output. The `evidence` field is included in the result. |
| `--fast` | flag | off | Skip gates marked `fast=false` in `gates.toml` (typically the full test run). Used by the pre-commit hook. |

**Output fields (human-readable):**

- `[pass]` / `[FAIL]` / `[skip]` / `[err ]` per gate.
- `evidence:` line: `gates: PASS|FAIL (language, N gate(s): P pass / F fail / S skip) · timestamp · run <hash>`.
  Paste this into `STATUS.md` as the phase verification record.

**Language detection:** `run-gates.py` scans the project for files listed in each language's `detect` array
in `gates.toml`. A project with none of those files gets a "judgment-only" result (no automated gates).

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | No gate failed (passes, skips, and judgment-only are all non-failing). |
| 1 | At least one gate `FAIL`. |
| 2 | Usage error or gate manifest not found. |

### 4.3 gen-doctrine.py

Generates `DOCTRINE.md` from `doctrine.toml`.

```
python3 Standards/scripts/gen-doctrine.py [--check | --stdout]
```

| Flag | Effect |
|---|---|
| (no flag) | Regenerate `DOCTRINE.md`. Exit 0 on success. |
| `--check` | Verify `DOCTRINE.md` is current with `doctrine.toml`. Exit 0 if current; exit 1 if stale. |
| `--stdout` | Print the rendered contract to stdout; write nothing. |

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Success (written, or `--check` found it current). |
| 1 | `--check`: `DOCTRINE.md` is stale. |
| 2 | Usage or data error (missing `doctrine.toml`, parse failure). |

### 4.4 gen-coverage.py

Generates `GATE_COVERAGE.md` from `doctrine.toml` + `coverage.toml`.

```
python3 Standards/scripts/gen-coverage.py [--check | --stdout]
```

| Flag | Effect |
|---|---|
| (no flag) | Regenerate `GATE_COVERAGE.md`. Exit 0 on success; exit 2 on validation failure. |
| `--check` | Verify `GATE_COVERAGE.md` is current. Exit 0 if current; exit 1 if stale; exit 2 on validation failure. |
| `--stdout` | Print to stdout; write nothing. |

**Validation (exits 2 if any fail):**

- Every gate handle in `doctrine.toml` has exactly one row in `coverage.toml`.
- No row in `coverage.toml` references a handle not in `doctrine.toml`.
- Each row's `must` token is still a substring of the gate's text (drift guard).
- Each row's `catch` is one of: `ci-gate`, `auditor`, `design`, `phase`, `advisory`.
- Each row's `mechanism` is non-empty.

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Success. |
| 1 | `--check`: `GATE_COVERAGE.md` is stale. |
| 2 | Validation failure or usage/data error. |

### 4.5 project-agents.py

Derives non-Claude agent definitions from the canonical `.claude/agents/` set.

```
python3 Standards/scripts/project-agents.py <harness> [--out DIR] [--suite | --generic]
```

| Argument / Flag | Type | Default | Effect |
|---|---|---|---|
| `<harness>` | positional, required | (required) | Target harness. One of: `roo`, `codex` (alias: `chatgpt`), `generic`. |
| `--out DIR` | option | cwd | Target directory to write derived artifacts into. |
| `--suite` | flag | default | Keep suite overlay fences in the output. |
| `--generic` | flag | off | Strip suite overlay fences from the output (the same fence-strip logic used for open-source releases). |

**Output per harness:**

| Harness | Output |
|---|---|
| `roo` | `<out>/.roomodes` (Roo Code custom modes JSON) |
| `codex` / `chatgpt` | `<out>/.agents/skills/<agent>/SKILL.md` (one SKILL.md per agent; OpenAI Codex CLI skill format) |
| `generic` | `<out>/AGENTS.md` (a plain bundle of all agents, load manually into any model) |

**Claude tool -> Roo group mapping:**

| Claude tool | Roo group |
|---|---|
| Read, Glob, Grep, LS, NotebookRead | read |
| Edit, Write, MultiEdit, NotebookEdit | edit |
| Bash, BashOutput, KillBash | command |
| WebSearch, WebFetch | browser |
| (others: Task, TodoWrite, etc.) | dropped |

### 4.6 sync-agents.sh

Installs agents from the canonical `.claude/agents/` into a target repo. Used internally by `install.sh`.

```
bash Standards/scripts/sync-agents.sh [--suite | --generic] <target-dir>
```

| Flag | Effect |
|---|---|
| `--suite` (default) | Copy agents verbatim (suite overlays intact) and install `.talus/` context. |
| `--generic` | Strip suite overlays from agents; do not install `.talus/`. |

The skills in `.claude/skills/` are copied in both modes. In `--generic` mode, each skill's markdown is
also stripped of any overlay fences.

---

## 5. Configuration files

### 5.1 doctrine.toml

Source of truth for `DOCTRINE.md`. Generated output; never edit `DOCTRINE.md` directly.

**Top-level keys:**

| Key | Type | Effect |
|---|---|---|
| `version` | string | The suite version this doctrine was generated for. Must match the umbrella's declared version. |

**`[[standard]]` block:**

| Key | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The handle prefix for this standard's gates (e.g. `"A"`, `"PY"`). Gates are numbered `[A1]`, `[A2]`, etc. |
| `file` | string | yes | The standard's filename relative to the repo root. |
| `title` | string | yes | Short human title shown in `DOCTRINE.md`. |
| `gates` | array of strings | yes | The distilled must-gate lines for this standard. Each must cite a `§`. Only true `must` rules; the standard carries the rationale. |

**Example:**

```toml
version = "1.3"

[[standard]]
id = "A"
file = "A_TALUS_Coding_Standard.md"
title = "Coding Standard (umbrella)"
gates = [
  "Determinism decides: behavior follows transparent, auditable, reproducible logic (§2, §8).",
  "Dependencies point inward: the domain core depends on nothing (§2, §4).",
]
```

### 5.2 coverage.toml

Source of truth for `GATE_COVERAGE.md`. Generated output; never edit `GATE_COVERAGE.md` directly.

**Top-level keys:**

| Key | Type | Effect |
|---|---|---|
| `version` | string | The suite version; must match `doctrine.toml`. |

**`[[coverage]]` block:**

| Key | Type | Required | Description |
|---|---|---|---|
| `gate` | string | yes | The gate handle (e.g. `"A1"`). Must match a handle in `doctrine.toml`. |
| `must` | string | yes | A leading substring of the gate's text (drift guard). The generator fails if this no longer matches the gate text. |
| `catch` | string | yes | The enforcement level. One of: `ci-gate`, `auditor`, `design`, `phase`, `advisory`. |
| `mechanism` | string | yes | The specific arm (non-empty). E.g. `"ruff check + ruff format --check"`, `"talus-auditor §A2"`. |
| `note` | string | no | Justification (required for `advisory` rows). |

**Catch levels (strongest to weakest):**

| Level | Meaning |
|---|---|
| `ci-gate` | A blocking automated gate: a `gates.toml` / `run-gates.py` tool or a CI check (gen-doctrine, gen-coverage, etc.). |
| `auditor` | `talus-auditor` review-time judgment: a finding tied to a standard and section. |
| `design` | Caught at design time by `talus-architect` or `talus-cartographer`. |
| `phase` | The `talus-phase` skill and AI Coding Phase Guidelines process (the phase template, stop-for-review gate, STATUS ledger). |
| `advisory` | A strong default with no named TALUS arm; caught downstream or by general judgment. Requires a `note`. |

### 5.3 gates.toml

Source of truth for `run-gates.py`'s gate manifest. One section per language.

**Per-language section:**

| Key | Type | Required | Description |
|---|---|---|---|
| `detect` | array of strings | yes | Filenames (relative to project root) whose presence marks this language. |
| `standard` | string | yes | The human standard this mirrors (cross-reference only; the standard is the rationale). |

**`[[<lang>.gates]]` block:**

| Key | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Short gate name (e.g. `"lint+format"`). Shown in output. |
| `command` | string | yes | The shell command to run from the project root. Exit 0 = PASS; exit 127 = SKIP (tool not installed); other = FAIL. |
| `fast` | bool | no (default: true) | If `false`, this gate is skipped by `run-gates.py --fast` (the pre-commit hook). Use for slow gates (e.g. the full test suite). |

---

## 6. Generated artifacts

| File | Source files | Regenerate | Verify (CI) |
|---|---|---|---|
| `DOCTRINE.md` | `doctrine.toml` | `python3 scripts/gen-doctrine.py` | `python3 scripts/gen-doctrine.py --check` |
| `GATE_COVERAGE.md` | `doctrine.toml` + `coverage.toml` | `python3 scripts/gen-coverage.py` | `python3 scripts/gen-coverage.py --check` |

Do not edit these files by hand. They carry a header warning. Any hand edit will be overwritten on the
next regeneration and will cause a `--check` failure in CI.

---

## 7. Gate manifest (Python)

The Python gate set, from `gates.toml`. Detected by presence of `pyproject.toml`, `setup.cfg`, or `setup.py`.

| Handle | Name | Command | Fast |
|---|---|---|---|
| `python/lint+format` | lint+format | `ruff check . && ruff format --check .` | yes |
| `python/type-check` | type-check | `pyright` | yes |
| `python/tests+coverage` | tests+coverage | `pytest -q` | **no** (skipped by `--fast`) |
| `python/imports` | imports | `lint-imports` | yes |
| `python/dep-audit` | dep-audit | `pip-audit` | yes |
| `python/secret-scan` | secret-scan | `gitleaks detect --no-banner --redact` | yes |

A gate whose tool is not installed reports `SKIP` (not `FAIL`). Install the tool to move it to `PASS`.

---

## 8. Repository layout

After `install.sh` runs against a project, the layout is:

```
<your-project>/
  Standards/                  vendored standards (git-ignored)
    A_TALUS_Coding_Standard.md
    B_AI_Coding_Phase_Guidelines.md
    C_Documentation_and_Architecting_Standard.md
    D_Visual_UX_UI_Standard.md
    E_API_and_Data_Contract_Standard.md
    F_Security_and_OpSec_Standard.md
    G_Observability_and_Reliability_Standard.md
    H_Git_and_Release_Engineering_Standard.md
    I_Licensing_and_Editions_Standard.md
    J_LLM_AI_Integration_Standard.md
    K_User_Documentation_Standard.md
    DOCTRINE.md               generated must-gate contract
    GATE_COVERAGE.md          generated gate-coverage audit
    CHANGELOG.md
    doctrine.toml             source for DOCTRINE.md
    coverage.toml             source for GATE_COVERAGE.md
    gates.toml                source for run-gates.py
    languages/
      Python_Coding_Standard.md
    scripts/
      install.sh
      run-gates.py
      gen-doctrine.py
      gen-coverage.py
      project-agents.py
      sync-agents.sh

  .claude/                    committed (shared build context)
    agents/
      talus-researcher.md
      talus-architect.md
      talus-scribe.md
      talus-cartographer.md
      talus-auditor.md
      talus-herald.md
      talus-chronicler.md
    skills/
      talus-phase/
        SKILL.md
      talus-gates/
        SKILL.md
    settings.json             per-turn reminder hook (if --hook)

  .talus/                     committed (shared build context)
    journal/
      STATUS.md               phase ledger
      JOURNAL_INDEX.md        rolling index

  CLAUDE.md                   standards directive (committed)
  .gitignore                  includes /Standards/ entry
  .git/hooks/pre-commit       pre-commit gate (if --precommit, not committed)
```

The **Standards/ source tree** (this repository) has a parallel layout, minus the `<your-project>/`
wrapper. The canonical agent source is `.claude/agents/` in the Standards tree; `install.sh` copies it
into the project.

---

## 9. Exit codes

| Script | Code | Meaning |
|---|---|---|
| `install.sh` | 0 | Install succeeded. |
| `install.sh` | 1 | Target directory does not exist or is invalid. |
| `install.sh` | 2 | Unknown option. |
| `run-gates.py` | 0 | No gate failed. |
| `run-gates.py` | 1 | At least one gate `FAIL`. |
| `run-gates.py` | 2 | Usage error or manifest not found. |
| `gen-doctrine.py` | 0 | Success (written, or `--check` current). |
| `gen-doctrine.py` | 1 | `--check`: stale. |
| `gen-doctrine.py` | 2 | Usage or data error. |
| `gen-coverage.py` | 0 | Success. |
| `gen-coverage.py` | 1 | `--check`: stale. |
| `gen-coverage.py` | 2 | Validation failure or data error. |
| `sync-agents.sh` | 0 | Sync succeeded. |
| `sync-agents.sh` | 1 | Target or source directory missing. |
| `sync-agents.sh` | 2 | Unknown option. |
| `project-agents.py` | 0 | Projection succeeded. |
| `project-agents.py` | non-zero | Usage error or source agents directory missing. |
