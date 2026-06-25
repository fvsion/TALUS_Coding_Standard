#!/usr/bin/env bash
#
# install.sh — set up a target repo to use these standards, with the correct topology.
#
# Topology (see README "Deployment & Portability"):
#   <repo>/Standards/        ← the vendored standards docs + tooling (re-pullable; git-ignored)
#   <repo>/.claude/agents/   ← the design/review agents AT THE REPO ROOT (Claude Code resolves them here)
#   <repo>/.talus/           ← suite doctrine overlay (top) + .talus/journal/ working artifacts
#
# Dual-use git (the install sets up the "internal dev" mode):
#   - the vendored /Standards/ is git-ignored (re-pullable, not committed)
#   - .claude/agents + .talus/ (incl. journal) are committed as the team's shared build context
#   For a PUBLIC post, do NOT use git state — run `strip-proprietary.sh --public` to emit a tree with
#   .claude/ and .talus/ removed.
#
# Usage:
#   scripts/install.sh <target-repo-dir> [harness] [--no-hook] [--no-precommit] [--herald-opus]
#     harness (optional): claude (default; agents used natively) | roo | codex | chatgpt | generic
#       A non-Claude harness is derived immediately via project-agents.py (skills/.roomodes/AGENTS.md).
#   By DEFAULT the installer adds two durability layers (opt out per below):
#     - a per-turn reminder hook (Claude .claude/settings.json or Codex .codex/hooks.json UserPromptSubmit)
#       that re-states the core rule every turn, so it survives compaction.     opt out: --no-hook
#     - a git pre-commit gate that runs the language-detected CI gates and blocks a FAIL.  opt out: --no-precommit
#   The documentation agent (talus-herald) defaults to the 'sonnet' model. Pass --herald-opus for the
#   higher-quality 'opus' model (higher cost per run). Run interactively without the flag and the installer
#   asks; non-interactively (an AI/CI driving the install) it defaults to sonnet without blocking.
#
#   The installer also writes/extends the repo's root CLAUDE.md (and AGENTS.md for codex) with a directive
#   that points the coding agent at the standards. It is APPEND-ONLY and never overwrites an existing file.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TARGET=""
HARNESS=""
HOOK=1          # per-turn reminder hook: default-ON (opt out with --no-hook)
PRECOMMIT=1     # git pre-commit gate: default-ON (opt out with --no-precommit)
HERALD_MODEL="" # docs agent (talus-herald) model: ""=decide later (prompt if TTY, else sonnet); else sonnet|opus
for arg in "$@"; do
  case "$arg" in
    --hook)         HOOK=1 ;;          # explicit on (back-compat; it is the default)
    --no-hook)      HOOK=0 ;;
    --no-precommit) PRECOMMIT=0 ;;
    --herald-opus)   HERALD_MODEL="opus" ;;    # upgrade the docs agent (higher quality, higher cost)
    --herald-sonnet) HERALD_MODEL="sonnet" ;;  # explicit default (suppresses the prompt)
    -h|--help) sed -n '2,/^set -euo/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//; s/^#//'; exit 0 ;;
    -*)        echo "Error: unknown option '$arg'." >&2; exit 2 ;;
    *)         if [[ -z "$TARGET" ]]; then TARGET="$arg"; elif [[ -z "$HARNESS" ]]; then HARNESS="$arg"; fi ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  sed -n '2,/^set -euo/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//; s/^#//'; exit 0
fi
if [[ ! -d "$TARGET" ]]; then
  echo "Error: target '$TARGET' is not a directory." >&2; exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"
case "$TARGET" in
  "$ROOT"|"$ROOT"/*|"$(dirname "$ROOT")") echo "Error: target must be a separate repo, not the Standards tree itself." >&2; exit 1;;
esac

# Resolve the documentation agent (talus-herald) model. Default is sonnet; opus is a higher-quality, higher-cost
# upgrade. If neither flag was given AND we are interactive (a human at a TTY), ask. Non-interactively (an AI or
# CI driving the install) we never block on input — default sonnet, and the README's AI-install instructions
# tell the installing agent to offer the --herald-opus upgrade in chat instead.
if [[ -z "$HERALD_MODEL" ]]; then
  if [[ -t 0 ]]; then
    printf 'Use the higher-quality "opus" model for the documentation agent (talus-herald)? Costs more per run. [y/N] '
    read -r _ans || _ans=""
    case "$_ans" in [Yy]*) HERALD_MODEL="opus" ;; *) HERALD_MODEL="sonnet" ;; esac
  else
    HERALD_MODEL="sonnet"
  fi
fi

# append_directive FILE — add the standards directive once, APPEND-ONLY. Never overwrites: if FILE exists
# and already carries the marker, it is left untouched; otherwise the block is appended (>> creates FILE if
# absent). This is the auto-loaded orientation that actually points the coding agent at the standards.
append_directive() {
  local f="$1"
  if [[ -f "$f" ]] && grep -q 'talus-standards' "$f"; then return 0; fi
  { [[ -s "$f" ]] && echo; cat <<'EOF'
<!-- >>> talus-standards (added by install.sh; safe to edit, keep the markers) >>> -->
## Engineering standards

This project follows the **TALUS engineering standards** (vendored in `Standards/`). They are mandatory.

**Read by section.** Start at `Standards/DOCTRINE.md` (the one-screen must-gate contract) and `Standards/A_TALUS_Coding_Standard.md`; language rules live in `Standards/languages/`. Open only the `§` you need; never load a whole large standard.

**Work in bounded phases. This is the cardinal rule** (AI Coding Phase Guidelines; run the `talus-phase` skill):

- **Shape every phase with the 6-part template BEFORE writing code:** Entry, Scope in, Scope out, Objective (one), Exit criteria, Verify-by. If you cannot fill all six, it is not a phase: split it.
- **Do ONE phase, then STOP for review.** Never roll into the next phase on your own. Never one-shot a non-trivial build. (A quick throwaway may be one-shotted; say so explicitly.)
- **Verify with evidence at every boundary, not just at the end:** run the `talus-gates` skill (CI gates) and a `talus-auditor` subagent **diff-scoped to that phase's changes**. Run a whole-repo `talus-auditor` before calling the build done.
- **Update `.talus/journal/STATUS.md` COMPLETELY at every stop:** the phase, what it delivered, the verification evidence, and the next action. Keep it bounded: when an effort finishes, demote its detail to a one-liner in `.talus/journal/JOURNAL_INDEX.md` and keep only the current state, the active effort, and a short recent window inline.
- **Invoke `talus-chronicler` at every effort boundary** to write the compacted record and refresh the index (essential when a smaller or local model is driving).

**Agents:** design with `talus-researcher` then `talus-architect` then `talus-scribe` (validate contracts via `talus-cartographer`); author user docs with `talus-herald`.

Resume context for any session: `.talus/journal/STATUS.md`.
<!-- <<< talus-standards <<< -->
EOF
  } >> "$f"
}

# 1) Vendor the standards docs + tooling under <repo>/Standards/ (minus the root-bound dotfolders).
mkdir -p "$TARGET/Standards"
( cd "$ROOT" && tar --exclude='./.git' --exclude='./.claude' --exclude='./.talus' -cf - . ) \
  | ( cd "$TARGET/Standards" && tar -xf - )

# 2) Install the canonical Claude agents + suite doctrine at the repo ROOT (reuses the canonical sync).
#    Other harnesses derive from these via `project-agents.py` (see below).
"$ROOT/scripts/sync-agents.sh" --suite "$TARGET" >/dev/null

# 2b) Documentation agent model: default sonnet; rewrite to opus on request (before any projection in step 5,
#     so a derived harness inherits the same choice). Touches only the talus-herald agent's frontmatter.
if [[ "$HERALD_MODEL" == "opus" && -f "$TARGET/.claude/agents/talus-herald.md" ]]; then
  python3 - "$TARGET/.claude/agents/talus-herald.md" <<'PY'
import re, sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(re.sub(r'(?m)^model:[ \t]*sonnet[ \t]*$', 'model: opus', t, count=1))
PY
fi

# 3) Scaffold the working-context journal if absent (per the AI Coding Phase Guidelines §7).
mkdir -p "$TARGET/.talus/journal"
if [[ ! -f "$TARGET/.talus/journal/STATUS.md" ]]; then
  cat > "$TARGET/.talus/journal/STATUS.md" <<'EOF'
# STATUS — project phase ledger

**The canonical phase ledger** (AI Coding Phase Guidelines §7), maintained by the driving session. Kept
**bounded**: the current state + the active effort + a short recent window inline; older detail demotes to
`JOURNAL_INDEX.md`. Update **completely** at every phase stop (what delivered, evidence, next).

## Where we are now

- (one line: what is built, what is in progress)

## Active effort — <name>

- [ ] **Phase 1 — <title>.** <what it delivered> · evidence: <gate/test/run result> · next: <next phase>

<!-- Shape EVERY phase with the 6-part template BEFORE coding (AI Coding Phase Guidelines §2):
       Entry: <preconditions>   Scope in: <what it does>   Scope out: <what it does not touch>
       Objective: <the one reviewable outcome>   Exit: <checkable conditions>   Verify by: <tests/run/gate>
     If you cannot fill all six, it is not a phase: split it. Do one phase, then STOP for review. -->

## Next

- (the next phase, shaped with the 6-part template above)

## Recent (history: one line per finished effort; full detail in JOURNAL_INDEX.md)

- (when an effort completes, demote it here as a one-liner, then prune to the index)
EOF
fi
if [[ ! -f "$TARGET/.talus/journal/JOURNAL_INDEX.md" ]]; then
  cat > "$TARGET/.talus/journal/JOURNAL_INDEX.md" <<'EOF'
# Journal Index

Rolling "where are we" + links (AI Coding Phase Guidelines §7).

## Where we are (current)

- (one paragraph)

## Artifacts

- Phase ledger: [STATUS.md](STATUS.md)
- Sub-compacts: *(add COMPACTED_<effort>.md per major effort and link here)*
EOF
fi

# 4) Mark the vendored standards as git-ignored (internal-dev mode), idempotently.
GI="$TARGET/.gitignore"
if ! grep -q 'talus-standards (vendored' "$GI" 2>/dev/null; then
  {
    echo ''
    echo '# >>> talus-standards (vendored; re-pullable, not committed) >>>'
    echo '/Standards/'
    echo '# <<< talus-standards <<<'
  } >> "$GI"
fi

# 5) Optionally derive a non-Claude harness's agents now (Claude reads .claude/agents directly).
case "$HARNESS" in
  ""|claude) ;;  # nothing to derive
  roo|codex|chatgpt|generic)
    echo "Deriving '$HARNESS' agents from .claude/agents/ ..."
    python3 "$ROOT/scripts/project-agents.py" "$HARNESS" --out "$TARGET"
    ;;
  *)
    echo "Warning: unknown harness '$HARNESS' (use: claude|roo|codex|chatgpt|generic); skipping." >&2
    ;;
esac

# 6) Write/extend the auto-loaded orientation file so the coding agent is actually DIRECTED to the standards
#    (this is what makes installed standards take effect instead of sitting inert). Append-only.
append_directive "$TARGET/CLAUDE.md"
case "$HARNESS" in
  codex|chatgpt) append_directive "$TARGET/AGENTS.md" ;;  # Codex auto-reads AGENTS.md
esac

# 7) Per-turn reminder hook (default-ON; opt out --no-hook). Re-states the core rule EVERY turn — the salience
#    layer that survives compaction and a full window. Both harnesses expose a UserPromptSubmit hook with the
#    same JSON shape (stdout is injected as context): Claude → .claude/settings.json; Codex → .codex/hooks.json.
if [[ "$HOOK" == "1" ]]; then
  case "$HARNESS" in
    codex|chatgpt) HOOK_FILE="$TARGET/.codex/hooks.json" ;;
    ""|claude)     HOOK_FILE="$TARGET/.claude/settings.json" ;;
    *)             HOOK_FILE="" ;;  # roo/generic: no per-turn hook mechanism — the directive is the layer
  esac
  if [[ -n "$HOOK_FILE" ]]; then
    python3 - "$HOOK_FILE" <<'PY'
import json, os, sys
path = sys.argv[1]
reminder = ("TALUS: follow Standards/ (read by section). Shape each phase with the 6-part template "
            "(entry/scope-in/scope-out/objective/exit/verify) BEFORE coding; do ONE phase then STOP. At each "
            "boundary run talus-gates + a diff-scoped talus-auditor, then update STATUS.md completely "
            "(what/evidence/next) and demote finished detail to JOURNAL_INDEX.md. Invoke talus-chronicler at "
            "effort boundaries. Design agents / talus-herald for non-trivial work. Do not one-shot.")
cmd = "echo " + json.dumps(reminder)
data = {}
if os.path.exists(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        data = {}
hooks = data.setdefault("hooks", {})
ups = hooks.setdefault("UserPromptSubmit", [])
present = any("TALUS:" in h.get("command", "") for grp in ups for h in grp.get("hooks", []))
if not present:
    ups.append({"hooks": [{"type": "command", "command": cmd}]})
os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
with open(path, "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2)
    fh.write("\n")
print("Per-turn reminder hook:", path)
PY
  else
    echo "Note: no per-turn hook mechanism for harness '$HARNESS'; the CLAUDE.md/AGENTS.md directive is the orientation layer." >&2
  fi
fi

# 8) Pre-commit gate (default-ON; opt out --no-precommit). The context-independent backstop: runs the
#    language-detected gates on every commit and blocks on a FAIL, regardless of what the model remembers.
#    Non-destructive — never clobbers an existing pre-commit. Bypass once with `git commit --no-verify`.
if [[ "$PRECOMMIT" == "1" ]]; then
  if [[ -d "$TARGET/.git" ]]; then
    HOOKF="$TARGET/.git/hooks/pre-commit"
    if [[ -e "$HOOKF" ]]; then
      echo "Note: a pre-commit hook already exists; left untouched. Add 'python3 Standards/scripts/run-gates.py --fast .' to it for the TALUS gate." >&2
    else
      mkdir -p "$TARGET/.git/hooks"
      cat > "$HOOKF" <<'HOOK'
#!/usr/bin/env bash
# >>> talus-standards pre-commit gate (added by install.sh; bypass once with: git commit --no-verify) >>>
if [[ -f Standards/scripts/run-gates.py ]]; then
  python3 Standards/scripts/run-gates.py --fast . || {
    echo "talus-gates: a gate FAILED — commit blocked (bypass once: git commit --no-verify)." >&2
    exit 1
  }
fi
# <<< talus-standards <<<
HOOK
      chmod +x "$HOOKF"
      echo "Pre-commit gate installed: $HOOKF"
    fi
  else
    echo "Note: '$TARGET' is not a git repo; skipped the pre-commit gate (--no-precommit to silence)." >&2
  fi
fi

echo "Installed standards into: $TARGET"
echo "  Standards/        vendored docs + tooling (git-ignored)"
echo "  .claude/agents/   design/review agents"
echo "  CLAUDE.md         standards directive for your coding agent (appended, never overwritten)"
echo "  .talus/           journal/ (phase ledger, build records)"
[[ "$HOOK" == "1" ]]      && echo "  per-turn hook     re-states the core rule every turn (--no-hook to skip)"
[[ "$PRECOMMIT" == "1" ]] && echo "  pre-commit gate   runs the CI gates on commit, blocks a FAIL (--no-precommit to skip)"
echo "  docs agent        talus-herald model: $HERALD_MODEL (--herald-opus for higher quality at higher cost)"
echo
echo "Restart your coding-agent app so CLAUDE.md and the agents load."
echo "Commit .claude/ and .talus/ (shared build context); the vendored /Standards/ is ignored."
echo "Another harness? From the repo root:  python3 Standards/scripts/project-agents.py roo | codex | generic"
echo "  (codex/chatgpt -> .agents/skills/<agent>/SKILL.md for the OpenAI Codex CLI)"
# The release-machinery hint is only meaningful where that machinery is present (not in a stripped tree).
if [[ -f "$ROOT/scripts/strip-proprietary.sh" ]]; then
  echo "Public post: run  Standards/scripts/strip-proprietary.sh --public <out>  (drops .claude/ + .talus/)."
fi
