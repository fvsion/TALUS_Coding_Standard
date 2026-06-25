# TALUS Coding Standard: User Guide

This guide gets you from zero to productive on real tasks: installing into a project, driving a build in
phases, running the gates, using the agents, and producing a public-release tree. It assumes you have read
the README quickstart. For the exhaustive flag and config reference, see [REFERENCE.md](REFERENCE.md).

---

## What TALUS is (the mental model)

TALUS installs three things into a project:

1. **Standards** (`Standards/`, vendored and git-ignored): the markdown files a model reads to know the
   rules.
2. **Agents and skills** (`.claude/agents/`, `.claude/skills/`): named roles the model activates on
   demand (a researcher, an architect, a scribe, an auditor, a documentation author, a cartographer,
   and a chronicler), plus two skills that encode the phase procedure and gate run as short procedures.
3. **Durability layers**: a `CLAUDE.md` directive (always loaded), a per-turn reminder hook (salience), a
   `.talus/journal/STATUS.md` phase ledger (re-anchor across sessions), and a pre-commit gate (enforcement).

A model that forgets the rules mid-session still hits the gate at commit time. A session that dies mid-build
can be resumed from `STATUS.md` without re-explaining context. The layers are independent so each one is a
backstop for the ones above it.

The **core nouns**:

- **Phase**: a bounded unit of work with a six-part shape (entry, scope in, scope out, one objective, exit
  criteria, verify-by). The model does one, verifies it, records it, then stops.
- **Gate**: a CI check the language standard declares (lint, type-check, tests, import boundaries, secret and
  dependency scans). Blocking on commit; runnable on demand.
- **Agent**: a named subagent with a role, a tool set, and a model. Activated by asking for it by name.
- **Skill**: a short, model-invoked procedure. `talus-phase` walks the phase template; `talus-gates` runs
  the gate check.
- **Ledger**: `.talus/journal/STATUS.md`: the single document that says where the build is, what the last
  phase delivered, and what comes next.

---

## Prerequisites

- **Shell**: bash 3.2+ (macOS ships this; Linux has it; Windows: WSL or Git Bash).
- **Python 3.11+**: for `run-gates.py`, `gen-doctrine.py`, `gen-coverage.py`, and `project-agents.py`.
  Check with `python3 --version`. Python 3.11 ships `tomllib` in stdlib; the scripts require it.
- **Git**: for the pre-commit gate and the `--check` validators.
- **A target project directory**: an existing directory (does not need to be a git repo, though the
  pre-commit gate is skipped if it is not).
- **Claude Code** (recommended) or another supported agent harness (Codex, Roo, generic).

Verify your Python version:

```sh
python3 --version    # must be 3.11 or higher
```

---

## Task 1: Install into a project

**Goal:** vendor the standards, install agents and the directive, and set up the durability layers.

1. Clone TALUS beside your project (not inside it):

   ```sh
   cd ~/Dev
   git clone https://github.com/fvsion/TALUS_Coding_Standard.git
   ```

2. Run the installer against your project:

   ```sh
   bash ~/Dev/TALUS_Coding_Standard/scripts/install.sh /path/to/your-project
   ```

   The installer will ask whether to use the `opus` model for `talus-herald` (the documentation agent).
   Opus produces higher-quality output; sonnet is the default and costs less. Choose based on your usage.

3. Restart your coding-agent app. The `CLAUDE.md` directive and the agents load on startup.

4. Commit the installed artifacts (`.claude/`, `.talus/`) into your project. The vendored `Standards/`
   folder is git-ignored by the installer (it is re-pullable, not committed):

   ```sh
   git add .claude .talus CLAUDE.md .gitignore
   git commit -m "chore: install TALUS engineering standards"
   ```

**What was installed:**

```
your-project/
  Standards/              vendored standards docs + tooling (git-ignored)
  .claude/agents/         7 design/review/doc agents
  .claude/skills/         2 skills (talus-phase, talus-gates)
  CLAUDE.md               standards directive, appended
  .talus/journal/
    STATUS.md             phase ledger (scaffolded blank)
    JOURNAL_INDEX.md      rolling index (scaffolded blank)
  .git/hooks/pre-commit   blocks a commit if any gate fails (if git repo)
```

**Flags that change default behavior:**

- `--no-hook`: skip the per-turn reminder hook (`.claude/settings.json`). Use this if you already have a
  settings file with custom hooks and want to add the hook manually.
- `--no-precommit`: skip the pre-commit gate. Use in a non-git project or if you manage hooks separately.
- `--herald-opus`: install `talus-herald` on the `opus` model instead of `sonnet`.
- `--herald-sonnet`: explicitly select sonnet (suppresses the interactive prompt in CI).
- Second argument sets the harness: `claude` (default), `roo`, `codex`, `chatgpt`, `generic`.

**Example: install for Roo Code without the pre-commit gate:**

```sh
bash scripts/install.sh /path/to/your-project roo --no-precommit
```

---

## Task 2: Prime the agent after install

**Goal:** confirm the agent has loaded the standards and knows the workflow.

After restarting your agent app, send this message:

> Read `Standards/DOCTRINE.md` (the must-gate contract) and `Standards/A_TALUS_Coding_Standard.md`, and
> follow the TALUS standards for this project. For non-trivial work, use the design agents
> (`talus-architect`, `talus-scribe`, `talus-cartographer`), write the user docs with `talus-herald`, and
> run `talus-auditor` (diff-scoped) at each phase, not just at the end. Work in small reviewed phases, do
> not one-shot. Resume context lives in `.talus/journal/STATUS.md`.

**Tight context or local model:** use this leaner primer instead:

> Follow the TALUS standards in `Standards/`. Read `Standards/DOCTRINE.md` first (one screen), then open
> only the `§` it cites that your task needs. Do one tiny phase, verify it, then stop. Resume context lives
> in `.talus/journal/STATUS.md`.

The `CLAUDE.md` directive loads automatically in Claude Code, so a fresh session may not need the explicit
primer. Send it if the model is not referencing the standards.

---

## Task 3: Work in bounded phases

**Goal:** drive a non-trivial build one reviewed phase at a time, using the `talus-phase` skill.

The phase discipline is the cardinal rule of TALUS: do one phase, verify it, record it, then stop for
review. A phase that the model rolls through without stopping is not a phase; it is a one-shot, and
one-shots break the quality bar.

1. Tell the agent to invoke the `talus-phase` skill (or just say "use the phase skill"):

   > Use the talus-phase skill to plan the next phase of this build.

2. The skill will prompt you to fill in the six-part phase template before writing any code:

   ```
   Entry:          what must be true before this phase starts
   Scope in:       what this phase does
   Scope out:      what this phase does not touch
   Objective:      the one reviewable outcome
   Exit criteria:  the checkable conditions that mean it is done
   Verify by:      how you will check it (tests, a run, gate output)
   ```

   If any part is missing, it is not a phase yet. Split or sharpen it.

3. The agent does the work for that phase only, then stops and reports the outcome.

4. Verify the phase: run the gates (Task 4), review the diff with `talus-auditor` (Task 6), and confirm
   the outcome matches the exit criteria.

5. Update `STATUS.md` to record what the phase delivered, the verification evidence, and the next step:

   ```
   ## Active effort: <name>
   - [x] Phase 1: <title>. <what it delivered> · evidence: gates: PASS (python, 6 gate(s): 6 pass / 0 fail / 0 skip) · next: Phase 2
   ```

6. Approve the next phase. The agent does not roll forward without your approval.

**When to one-shot:** quick throwaway work (a rename, a docstring fix, a config tweak) does not need a
formal phase. The model should say so explicitly when it one-shots. If a request is larger than "a few
lines in one file," shape a phase.

---

## Task 4: Run the CI gates

**Goal:** check whether the project passes its declared CI gates.

The `talus-gates` skill runs the gates mechanically (no judgment, just pass/fail). The language standard
declares which tools to run; `run-gates.py` reads `gates.toml` and executes them.

1. Tell the agent to run the gates:

   > Run the talus-gates skill.

   Or run them directly:

   ```sh
   python3 Standards/scripts/run-gates.py .
   ```

2. The output shows each gate's status:

   ```
   Gate run for /path/to/your-project
     languages detected: python
     [pass] python/lint+format: ruff check . && ruff format --check .
     [pass] python/type-check: pyright
     [skip] python/tests+coverage: pytest -q        (tool not installed)
     [FAIL] python/imports: lint-imports
           ...first line of lint-imports output...
     evidence: gates: FAIL (python, 4 gate(s): 2 pass / 1 fail / 1 skip) · 2026-06-26T10:00Z · run a1b2c3d4e5
   ```

   `SKIP` means the tool is not installed, not a code defect, but note it.
   `FAIL` blocks the commit and must be fixed.

3. Copy the `evidence:` line into your `STATUS.md` phase record. It is a compact, reproducible receipt of
   the run (verdict, counts, a content hash, and a timestamp).

**Flags:**

- `--list`: show which gates would run without executing them.
- `--fast`: skip slow gates (those marked `fast=false`, typically the full test run). The pre-commit gate
  uses this automatically.
- `--json`: machine-readable output; useful for an agent or CI pipeline consuming the result.

**No language detected:** if the project has no `pyproject.toml`, `setup.cfg`, or other language marker
in `gates.toml`, the run reports "judgment-only": no automated gates exist yet for that language, and the
`talus-auditor` agent reasons from the umbrella standards instead.

---

## Task 5: Use the design agents

**Goal:** run the design pipeline for a new or evolving feature.

The four design agents follow a pipeline order: researcher, architect, scribe, cartographer.

1. **Research** (before designing anything new): invoke `talus-researcher` to pull cross-domain literature
   and produce an annotated research brief with citations and applicability notes.

   > Use talus-researcher to research [the problem]. Write findings to Research_and_Planning/.

2. **Architect** (after research, before writing specs): invoke `talus-architect` to produce a design
   proposal: module decomposition, data model, algorithm selection, ADRs, and integration contracts.

   > Use talus-architect to design [the component] based on the research brief.

3. **Scribe** (after design, before code): invoke `talus-scribe` to author the `Architecture/` doc suite
   to the Documentation and Architecting Standard.

   > Use talus-scribe to write the Architecture/ docs for [the component] from the design proposal.

4. **Cartographer** (after any contract change): invoke `talus-cartographer` to validate that all cross-
   component contracts are consistent and register any new ones.

   > Use talus-cartographer to check the contracts after this design change.

**When to skip research:** if the design is straightforward or the domain is well-understood, start at
architect. Reserve researcher for genuinely novel algorithm choices or unfamiliar problem domains.

**Dispatch vs. inline:** in a warm session with full context, the model can perform these roles inline
(cheaper, no cold start). Dispatch an actual subagent for research-heavy work, wide cross-component audits,
or when the session context is cold.

---

## Task 6: Run a code-conformance review

**Goal:** check that new or changed code conforms to the relevant TALUS standards.

`talus-auditor` performs the judgment checks a linter cannot: layered architecture conformance, SOLID
discipline, typing, error and logging conventions, and the AI-tell style.

Run it diff-scoped at each phase boundary, not only at the end:

> Use talus-auditor, scoped to the changes in this phase (the diff from main), and report any FAIL or WARN
> findings with file:line, the rule cited, and a remediation.

Run a whole-repo pass before calling a build done or merging a pull request:

> Use talus-auditor for a full repo conformance review.

The auditor emits findings in the form:

```
[FAIL] PY§4  src/module.py:42  bare `except:` catches everything; too broad.
       -> narrow to the specific exception type; log and re-raise others.
[WARN] A§2   src/service.py:15  domain class imports `requests` directly.
       -> route through a repository interface; the domain should not own I/O.
```

Fix FAILs before marking the phase done. WARNs are strong defaults; if you deviate, log the justification.

---

## Task 7: Author or update user documentation

**Goal:** write or audit the user-facing doc set (README, GUIDE, RTFM, TUTORIAL) to the User Documentation
Standard (`K`).

`talus-herald` authors and reviews the doc set. It is the owner of all four user-facing artifacts.

To author a fresh doc set for a project (after a build is done enough to document):

> Use talus-herald to author the user documentation for this project. Treat it as a Tier 2 CLI tool.

To review an existing doc set for drift or quality issues:

> Use talus-herald to review the user docs against the User Documentation Standard (K). Report findings
> with file:line evidence and a fix for each.

The agent produces a findings report for review mode, or writes the files for author mode, then lists any
placeholders that require a human to fill (benchmark numbers, real sample output).

---

## Task 8: Produce a public-release tree

**Goal:** produce a version of a project's standards tree suitable for sharing or open-sourcing, with
internal-only content removed.

If your project uses a dual-use git posture (an internal development branch plus a published release) or
carries a pro edition that separates community from commercial content, the release process is governed by
two standards:

- **Git and Release Engineering Standard (`H`)**: its dual-use section describes the general posture of
  keeping internal artifacts out of the published tree. Design-time artifacts (`Architecture/`,
  `Research_and_Planning/`) are internal by default.
- **Licensing and Editions Standard (`I`)**: covers the edition seam for open-core projects and what each
  tier of release should include.

Read those two standards for the approach that fits your project's release model. They are the source of
truth; a project's own release tooling implements their posture.

---

## Task 9: Regenerate DOCTRINE.md and GATE_COVERAGE.md

**Goal:** after changing a must-gate in any standard, regenerate the two contract artifacts.

These files are generated from data, never hand-edited. If you edit `doctrine.toml` or `coverage.toml`,
regenerate both:

```sh
python3 Standards/scripts/gen-doctrine.py          # rewrites DOCTRINE.md
python3 Standards/scripts/gen-coverage.py          # rewrites GATE_COVERAGE.md
```

To verify they are current with their source files (for CI or pre-commit):

```sh
python3 Standards/scripts/gen-doctrine.py --check  # exits 1 if stale
python3 Standards/scripts/gen-coverage.py --check  # exits 1 if stale
```

`gen-coverage.py` fails if any gate in `doctrine.toml` lacks a `coverage.toml` row. This is by design:
a gate cannot ship unenforced. When you add a new gate to `doctrine.toml`, add its coverage row to
`coverage.toml` before regenerating.

---

## Task 10: Add a language standard

**Goal:** extend TALUS with a new language standard and wire it into the gate runner.

1. Write the standard following the umbrella's structure (`A_TALUS_Coding_Standard.md`) and the
   Documentation and Architecting Standard (`C`). Place it in `languages/`.

2. Add a section to `gates.toml` for the new language:

   ```toml
   [typescript]
   detect = ["package.json", "tsconfig.json"]
   standard = "languages/TypeScript_Coding_Standard.md §X"

   [[typescript.gates]]
   name = "lint+format"
   command = "eslint . && prettier --check ."

   [[typescript.gates]]
   name = "type-check"
   command = "tsc --noEmit"
   ```

3. Add the new standard's must-gates to `doctrine.toml` with a new `[[standard]]` block.

4. Add coverage rows to `coverage.toml` for each new gate handle.

5. Regenerate both artifacts and verify:

   ```sh
   python3 Standards/scripts/gen-doctrine.py
   python3 Standards/scripts/gen-coverage.py
   python3 Standards/scripts/gen-doctrine.py --check
   python3 Standards/scripts/gen-coverage.py --check
   ```

6. Update `README.md` to list the new standard.

---

## Strategy and operational notes

**When to use agents vs. inline work.** The model can perform researcher, architect, and scribe roles inline
in a warm session (cheaper, preserves context). Dispatch a named subagent when the work is research-heavy
(deep literature pulls), cross-component (the cartographer auditing a contract change across multiple specs),
or when you want an isolated context for a review pass.

**Keeping the ledger bounded.** `STATUS.md` is the session's working memory. When it grows past a few active
efforts, demote finished efforts to a one-liner in `JOURNAL_INDEX.md`. Use `talus-chronicler` to write the
compacted record for a finished effort and refresh the index. A bloated ledger defeats its own purpose.

**The pre-commit gate runs `--fast`.** It skips gates marked `fast=false` (typically the full test suite)
because a commit hook needs to be fast. The full gate set runs in CI. Run `python3 Standards/scripts/run-gates.py .`
without `--fast` before a merge to catch what the pre-commit gate skipped.

**A project with no manifest language** gets a "judgment-only" gate run: `run-gates.py` reports no automated
gates and the `talus-auditor` agent reasons from the umbrella. This is correct behavior, not an error.

---

## Troubleshooting

**The agent does not follow the standards after install.**
Restart the app so `CLAUDE.md` loads. If it still does not, send the prime message from Task 2. Check that
`.claude/agents/` exists in the project root (not inside `Standards/`).

**The pre-commit gate blocks my commit with `gates: FAIL`.**
Run `python3 Standards/scripts/run-gates.py .` to see which gate failed and why. Fix the issue, then commit
again. To bypass once (not as a habit): `git commit --no-verify`.

**`run-gates.py` errors with "gate manifest not found."**
The script expects `gates.toml` to be two directories up from itself (`Standards/gates.toml`). Run it from
the project root, not from inside `Standards/`: `python3 Standards/scripts/run-gates.py .`

**`gen-doctrine.py` or `gen-coverage.py` exits 2.**
This is a data error: either a gate handle in `coverage.toml` does not match one in `doctrine.toml`, or the
`must` drift-guard token no longer matches the gate text. Read the error output; it names the mismatched
handle. Update `coverage.toml` to match the current gate text, then regenerate.

**The `--herald-opus` flag is not recognized.**
You are running an older copy of `install.sh`. Pull the latest version:
`cd ~/Dev/TALUS_Coding_Standard && git pull`

---

## Command reference

For the exhaustive flag list, config key schemas, agent specifications, and gate manifests, see
[REFERENCE.md](REFERENCE.md).
