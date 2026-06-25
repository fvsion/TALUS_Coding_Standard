# TALUS Coding Standard: Tutorial

One end-to-end walkthrough: a fresh Python project, TALUS installed, one bounded phase built and verified,
the gates run, and a clean public-release tree produced. Follow the steps in order; each one builds on the
last.

For the exhaustive flag reference, see [REFERENCE.md](REFERENCE.md). For task recipes, see
[USER_GUIDE.md](USER_GUIDE.md).

---

## The scenario

You have a small Python CLI called `tidyup` that reformats JSON files. It has a `pyproject.toml` but no
standards enforced yet. You want to install TALUS, add one feature (a `--dry-run` flag) in a single
reviewed phase, verify the gates pass, and then produce a clean tree to share.

Directory layout before we start:

```
~/Dev/
  tidyup/               your project
    pyproject.toml
    src/
      tidyup/
        __init__.py
        cli.py
    tests/
      test_cli.py
    CLAUDE.md             (does not exist yet)
```

---

## Step 1: Clone TALUS beside your project

TALUS installs by copying files in; you never run it from inside your project.

```sh
cd ~/Dev
git clone https://github.com/fvsion/TALUS_Coding_Standard.git
```

Expected output (abbreviated):

```
Cloning into 'TALUS_Coding_Standard'...
remote: Enumerating objects: 312, done.
Resolving deltas: 100% (189/189), done.
```

---

## Step 2: Run the installer

```sh
bash ~/Dev/TALUS_Coding_Standard/scripts/install.sh ~/Dev/tidyup
```

The installer asks whether to upgrade the documentation agent to `opus` (the higher-quality model). For
this walkthrough, type `n` to keep the default `sonnet`:

```
Use the higher-quality "opus" model for the documentation agent (talus-herald)? Costs more per run. [y/N] n
```

Then it runs and reports what it installed:

```
Installed standards into: /Users/you/Dev/tidyup
  Standards/        vendored docs + tooling (git-ignored)
  .claude/agents/   design/review agents
  CLAUDE.md         standards directive for your coding agent (appended, never overwritten)
  .talus/           journal/ (phase ledger, build records)
  per-turn hook     re-states the core rule every turn (--no-hook to skip)
  pre-commit gate   runs the CI gates on commit, blocks a FAIL (--no-precommit to skip)
  docs agent        talus-herald model: sonnet (--herald-opus for higher quality at higher cost)

Restart your coding-agent app so CLAUDE.md and the agents load.
Commit .claude/ and .talus/ (shared build context); the vendored /Standards/ is ignored.
Another harness? From the repo root:  python3 Standards/scripts/project-agents.py roo | codex | generic
```

Check what was created:

```sh
ls ~/Dev/tidyup/.claude/agents/
```

```
talus-architect.md  talus-auditor.md  talus-cartographer.md
talus-chronicler.md talus-herald.md   talus-researcher.md   talus-scribe.md
```

```sh
ls ~/Dev/tidyup/.talus/journal/
```

```
JOURNAL_INDEX.md  STATUS.md
```

---

## Step 3: Commit the installed artifacts

The vendored `Standards/` is git-ignored. Commit the agents, skills, directive, and journal:

```sh
cd ~/Dev/tidyup
git add .claude .talus CLAUDE.md .gitignore
git status
```

```
On branch main
Changes to be committed:
  new file:   .claude/agents/talus-architect.md
  new file:   .claude/agents/talus-auditor.md
  new file:   .claude/agents/talus-cartographer.md
  new file:   .claude/agents/talus-chronicler.md
  new file:   .claude/agents/talus-herald.md
  new file:   .claude/agents/talus-researcher.md
  new file:   .claude/agents/talus-scribe.md
  new file:   .claude/skills/talus-gates/SKILL.md
  new file:   .claude/skills/talus-phase/SKILL.md
  new file:   .talus/journal/JOURNAL_INDEX.md
  new file:   .talus/journal/STATUS.md
  modified:   .gitignore
  modified:   CLAUDE.md
```

```sh
git commit -m "chore: install TALUS engineering standards v1.3"
```

---

## Step 4: Restart your agent and prime it

Restart Claude Code (or your agent app) so the agents and `CLAUDE.md` load. Then open a session in
`~/Dev/tidyup` and send:

> Read `Standards/DOCTRINE.md` and `Standards/A_TALUS_Coding_Standard.md`, and follow the TALUS standards
> for this project. Work in bounded phases. Resume context lives in `.talus/journal/STATUS.md`.

The agent reads the files and confirms:

```
I've read DOCTRINE.md (66 must-gates across 12 standards) and the umbrella coding standard.
I'll follow the TALUS standards and work in bounded phases. STATUS.md is ready for the first entry.
```

---

## Step 5: Shape a phase before writing code

You want to add `--dry-run` to `tidyup`. Instead of asking the agent to "add the flag," invoke the phase
skill:

> Use the talus-phase skill to shape the work for adding --dry-run to tidyup.

The agent fills in the six-part template:

```
Entry:         src/tidyup/cli.py exists; tests/test_cli.py covers the basic reformat path.
Scope in:      add --dry-run flag to the CLI; print a summary of changes without writing files.
Scope out:     no changes to the core reformatter logic; no changes to the output format.
Objective:     --dry-run exits 0 and prints "Would reformat N file(s)" without writing.
Exit criteria: `pytest -q` passes; `ruff check . && ruff format --check .` passes;
               `pyright` passes; the flag appears in `--help`.
Verify by:     run the gates via `python3 Standards/scripts/run-gates.py .`
```

You review the shape and approve:

> That looks right. Do Phase 1.

---

## Step 6: The agent does the phase

The agent adds `--dry-run` to `cli.py` and updates `test_cli.py`. It then stops and reports:

```
Phase 1 done. Changes:
  src/tidyup/cli.py       +18 lines (--dry-run flag, summary print)
  tests/test_cli.py       +12 lines (dry-run test cases)

Ready to verify. Run the gates.
```

The agent stops here. It does not roll into another phase.

---

## Step 7: Run the gates

```sh
python3 Standards/scripts/run-gates.py .
```

```
Gate run for /Users/you/Dev/tidyup
  languages detected: python
  [pass] python/lint+format: ruff check . && ruff format --check .
  [pass] python/type-check: pyright
  [pass] python/tests+coverage: pytest -q
  [skip] python/imports: lint-imports
  [skip] python/dep-audit: pip-audit
  [skip] python/secret-scan: gitleaks detect --no-banner --redact
  evidence: gates: PASS (python, 6 gate(s): 3 pass / 0 fail / 3 skip) · 2026-06-26T10:14Z · run 4e7f9a1b2c
```

Three gates are `SKIP` because the tools are not installed (`lint-imports`, `pip-audit`, `gitleaks`). That
is not a failure; the gates run when the tools are present. Install them to move those to `PASS`:

```sh
pip install import-linter pip-audit
brew install gitleaks     # macOS; or: https://github.com/gitleaks/gitleaks#installing
```

---

## Step 8: Run a conformance review

Ask `talus-auditor` to review the phase's changes:

> Use talus-auditor, scoped to the changes in this phase, and report any findings.

The agent reviews the diff and responds:

```
[PASS] A§2   src/tidyup/cli.py   domain-layer clean; no framework imports in business logic.
[PASS] PY§4  src/tidyup/cli.py   types annotated; click types used correctly.
[PASS] PY§8  tests/test_cli.py   uses pytest fixtures; no unittest.TestCase.
No FAIL or WARN findings for this phase.
```

---

## Step 9: Update the phase ledger

Copy the evidence line from the gate run and update `.talus/journal/STATUS.md`:

```markdown
## Where we are now

- Phase 1 done: added --dry-run flag to tidyup CLI. Gates passing.

## Active effort: dry-run flag

- [x] **Phase 1: add --dry-run.** Added flag and tests. All 3 installed gates PASS.
  evidence: gates: PASS (python, 6 gate(s): 3 pass / 0 fail / 3 skip) · 2026-06-26T10:14Z · run 4e7f9a1b2c
  next: Phase 2 (if any), or call the build done and merge.

## Next

- (no further phases planned for this effort)
```

Commit the changes:

```sh
git add src tests .talus/journal/STATUS.md
git commit -m "feat: add --dry-run flag to tidyup CLI"
```

The pre-commit gate runs automatically. It runs `run-gates.py --fast` (skipping `tests+coverage` for
speed) and blocks the commit if any fast gate fails. Since the gates pass, the commit proceeds:

```
Pre-commit gate: [pass] lint+format | [pass] type-check | [skip] imports | [skip] dep-audit | [skip] secret-scan
[main 3f4a9b1] feat: add --dry-run flag to tidyup CLI
```

---

## Step 10: Share the work

The feature is done, reviewed, and committed. To share the project with a colleague, push the branch or
send a tarball of the repo. The committed `.claude/` agents and `.talus/` journal travel with it, so
the recipient gets the same agent setup and phase ledger you used.

If your project follows a dual-use git posture (an internal branch and a published release that excludes
design-time artifacts and internal configuration), that release process is described in the Git and Release
Engineering Standard (`H`, its dual-use section) and the Licensing and Editions Standard (`I`). Read those
standards when you are ready to set up a formal release pipeline. The general principle: design-time
artifacts (`Architecture/`, `Research_and_Planning/`) are internal by default and should be excluded from
the published tree; your project's own release step handles that exclusion.

---

## What you just did

Starting from a plain Python project, you:

1. Installed TALUS: vendored standards, 7 agents, 2 skills, a CLAUDE.md directive, a per-turn hook, a
   pre-commit gate, and a scaffolded phase ledger.
2. Shaped and executed one bounded phase with the 6-part template before writing code.
3. Ran the CI gates and confirmed the gate evidence: 3 tools passing, 3 skipped (not installed).
4. Ran a diff-scoped conformance review with `talus-auditor` and got clean results.
5. Updated `STATUS.md` with the phase record and evidence, then committed with the pre-commit gate running.
6. Reviewed the options for sharing and releasing the work, with pointers to the standards that govern dual-use and edition posture.

---

## Where to go next

- **More tasks:** [USER_GUIDE.md](USER_GUIDE.md) covers the release posture (dual-use and edition), adding a
  language standard, using the design agents, and maintaining the journal.
- **Exhaustive reference:** [REFERENCE.md](REFERENCE.md) has every flag, config key, and agent specification.
- **Standards:** start with `Standards/DOCTRINE.md` (one screen, 66 gates), then open only the `§` you need.
- **Drift:** when behavior changes, update the docs in the same commit. `talus-herald` runs drift checks.
