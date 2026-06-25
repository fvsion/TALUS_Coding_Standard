#!/usr/bin/env bash
#
# sync-agents.sh — install the Talus subagents into a target repo's .claude/agents/ so a
# dedicated single-repo session inherits them. The Standards/ folder is the agents' canonical
# home; project subagents resolve from the target repo root, so run this at repo-init time
# (and again after the agents change) to keep a repo in sync.
#
# Two flavours from one maintained source. Each agent is a generic base body plus a trailing
# PROPRIETARY-fenced "suite overlay" (substrate / contract-registry / canonical-name
# specifics):
#
#   --suite   <repo>   Install agents verbatim (overlay intact) AND drop the .talus/ suite
#                      context, so the overlay's matrix-reads resolve. Default. Use this for
#                      developing the Talus suite.
#   --generic <repo>   Install agents with the suite overlays stripped, and NO .talus/.
#                      Portable, suite-agnostic — use this for a fresh/unrelated project.
#
# Usage:
#   scripts/sync-agents.sh [--suite|--generic] <target-repo-dir>
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_SRC="$ROOT/.claude/agents"
SKILLS_SRC="$ROOT/.claude/skills"
TALUS_SRC="$ROOT/.talus"

# Reuse the canonical fence-strip (strip_md) when it is present. strip-proprietary.sh is NOT shipped in a
# stripped/public tree — where the agents are already overlay-free — so fall back to a no-op there, keeping
# --generic functional without it.
if [[ -f "$ROOT/scripts/strip-proprietary.sh" ]]; then
  # shellcheck source=/dev/null
  source "$ROOT/scripts/strip-proprietary.sh"
else
  strip_md() { :; }
fi

MODE="suite"
TARGET=""
for arg in "$@"; do
  case "$arg" in
    --suite)   MODE="suite" ;;
    --generic) MODE="generic" ;;
    -h|--help) sed -n '2,/^set -euo/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//; s/^#//'; exit 0 ;;
    -*)        echo "Error: unknown option '$arg'." >&2; exit 2 ;;
    *)         TARGET="$arg" ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 [--suite|--generic] <target-repo-dir>" >&2; exit 1
fi
if [[ ! -d "$TARGET" ]]; then
  echo "Error: target '$TARGET' is not a directory." >&2; exit 1
fi
if [[ ! -d "$AGENTS_SRC" ]]; then
  echo "Error: agents source missing: $AGENTS_SRC" >&2; exit 1
fi

mkdir -p "$TARGET/.claude/agents"
count=0

if [[ "$MODE" == "generic" ]]; then
  for f in "$AGENTS_SRC"/*.md; do
    dest="$TARGET/.claude/agents/$(basename "$f")"
    cp "$f" "$dest"
    strip_md "$dest"
    count=$((count + 1))
  done
  echo "Synced $count generic agents (suite overlays stripped) into: $TARGET/.claude/agents/"
  echo "No .talus/ context installed (generic mode). Restart the app to activate."
else
  cp "$AGENTS_SRC"/*.md "$TARGET/.claude/agents/"
  count="$(find "$AGENTS_SRC" -maxdepth 1 -name '*.md' | grep -c '')"
  if [[ -d "$TALUS_SRC" ]]; then
    mkdir -p "$TARGET/.talus"
    cp "$TALUS_SRC"/*.md "$TARGET/.talus/"
    echo "Synced $count suite agents + .talus/ context into: $TARGET"
    echo "  .claude/agents/                  ($count agents — restart the app to activate)"
    echo "  .talus/                          (suite orientation + contract registry)"
  else
    echo "Synced $count suite agents into: $TARGET/.claude/agents/"
    echo "Note: no .talus/ found at $TALUS_SRC; suite-overlay matrix reads will be unresolved."
  fi
  echo
  echo "Reminder: the repo's own CLAUDE.md should reference .talus/ for suite doctrine + contracts."
fi

# Skill-first roles (.claude/skills/<name>/SKILL.md) — copied the same way in both flavors; stripped in
# generic mode like the agents. Claude Code reads them directly; Codex gets them via project-agents.py.
if [[ -d "$SKILLS_SRC" ]]; then
  mkdir -p "$TARGET/.claude/skills"
  cp -R "$SKILLS_SRC"/. "$TARGET/.claude/skills/"
  if [[ "$MODE" == "generic" ]]; then
    while IFS= read -r -d '' f; do strip_md "$f"; done < <(find "$TARGET/.claude/skills" -type f -name '*.md' -print0)
  fi
  echo "  .claude/skills/                  ($(find "$SKILLS_SRC" -name 'SKILL.md' | grep -c '') skill(s))"
fi
