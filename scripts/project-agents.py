#!/usr/bin/env python3
"""project-agents.py — derive non-Claude agent definitions from the canonical Claude Code agents.

Talus is **claude-first**: the agents are authored once, in Claude Code's native format, under
`.claude/agents/*.md` (full `tools:` / `model:`, including MCP and other Claude-specific tools). Claude
Code reads that single canonical set directly — there is no projection for the primary harness. This tool
projects the same set *down* into other harnesses (best-effort; coarser permission models):

  roo       -> <out>/.roomodes                        (Roo Code custom modes; e.g. a local model in VS Code)
  codex     -> <out>/.agents/skills/<agent>/SKILL.md  (OpenAI Codex CLI / ChatGPT; alias: chatgpt)
  generic   -> <out>/AGENTS.md                        (a plain bundle to load by hand into any model)

Claude `tools:` map to each harness's tool/permission model. For Codex, each agent becomes a **skill**
(custom prompts are deprecated); the skill's `description` is Codex's implicit-invocation trigger, and
explicit invocation is `/skills` or `$<name>`. Suite-overlay fences are kept by default (`--suite`) and
removed by `--generic` (the same strip used for an open-source release).

Usage:
  scripts/project-agents.py roo     [--out DIR] [--suite | --generic]   # DIR defaults to the .claude/ root
  scripts/project-agents.py codex   [--out DIR] [--suite | --generic]   # (or: chatgpt)
  scripts/project-agents.py generic [--out DIR] [--suite | --generic]
"""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path


def _find_root() -> Path:
    """The project root that owns `.claude/agents` — walk up from CWD (works inside a consumer repo),
    falling back to this script's own repo."""
    for base in (Path.cwd(), *Path.cwd().parents):
        if (base / ".claude" / "agents").is_dir():
            return base
    return Path(__file__).resolve().parent.parent


ROOT = _find_root()
SRC = ROOT / ".claude" / "agents"
SKILLS_SRC = ROOT / ".claude" / "skills"  # skill-first roles (talus-gates, …): same SKILL.md format as Codex

# Claude tool name -> Roo Code tool group (coarser). Unmapped tools (Task, TodoWrite, …) are dropped.
_TOOL_GROUP: dict[str, str] = {
    "Read": "read", "Glob": "read", "Grep": "read", "LS": "read", "NotebookRead": "read",
    "Edit": "edit", "Write": "edit", "MultiEdit": "edit", "NotebookEdit": "edit",
    "Bash": "command", "BashOutput": "command", "KillBash": "command",
    "WebSearch": "browser", "WebFetch": "browser",
}
_GROUP_ORDER = ["read", "edit", "command", "browser", "mcp"]

_MARK = "PROPRIETARY"  # built from a token so this (shipped) file holds no literal block-fence marker.
_BLOCK_BEGIN = re.compile(rf"^\s*<!-- {_MARK}:BEGIN")
_BLOCK_END = re.compile(rf"^\s*<!-- {_MARK}:END")
_TAG = "prop"  # built from a token so this (shipped) file holds no literal inline-fence string.
_INLINE = re.compile(rf"<!-- {_TAG} -->.*?<!-- /{_TAG} -->")


@dataclass(frozen=True)
class Agent:
    name: str
    description: str
    tools: list[str]
    model: str
    body: str


def strip_overlays(text: str) -> str:
    """Remove PROPRIETARY-fenced content (block + inline), matching strip-proprietary.sh."""
    out: list[str] = []
    skip = False
    for line in text.splitlines():
        if _BLOCK_BEGIN.search(line):
            skip = True
            continue
        if _BLOCK_END.search(line):
            skip = False
            continue
        if not skip:
            out.append(_INLINE.sub("", line))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip("\n") + "\n"


def parse_agent(path: Path) -> Agent:
    """Parse a Claude Code agent spec (`.claude/agents/*.md`): front matter + body."""
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise ValueError(f"{path.name}: missing front matter")
    _, fm, body = raw.split("---", 2)

    fields: dict[str, str] = {}
    lines = fm.strip("\n").splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">-", ">", "|", "|-", ""):  # folded/block scalar -> gather indented continuation
            chunk: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or lines[i].strip() == ""):
                chunk.append(lines[i].strip())
                i += 1
            val = " ".join(s for s in chunk if s)
        else:
            i += 1
        fields[key] = val

    tools = [t.strip() for t in fields.get("tools", "").split(",") if t.strip()]
    return Agent(
        name=fields["name"],
        description=re.sub(r"\s+", " ", fields.get("description", "")).strip(),
        tools=tools,
        model=fields.get("model", "").strip(),
        body=body.strip("\n") + "\n",
    )


def load_agents(generic: bool) -> list[Agent]:
    agents: list[Agent] = []
    for path in sorted(SRC.glob("*.md")):
        a = parse_agent(path)
        if generic:
            a = Agent(a.name, a.description, a.tools, a.model, strip_overlays(a.body))
        agents.append(a)
    return agents


def _roo_groups(tools: list[str]) -> list[str]:
    found = {"mcp" if t.startswith("mcp__") else _TOOL_GROUP.get(t) for t in tools}
    return [g for g in _GROUP_ORDER if g in found]


def _wrap(text: str, indent: str, width: int = 108) -> str:
    return "\n".join(textwrap.wrap(text, width=width, initial_indent=indent, subsequent_indent=indent))


def emit_roo(agents: list[Agent], out: Path) -> list[Path]:
    def block(text: str) -> str:
        return "\n".join(("      " + line) if line else "" for line in text.rstrip("\n").splitlines())

    parts = ["customModes:\n"]
    for a in agents:
        display = a.name.replace("talus-", "Talus ").title().replace("Talus Talus", "Talus")
        groups = "\n".join(f"      - {g}" for g in _roo_groups(a.tools))
        parts.append(
            f"  - slug: {a.name}\n"
            f"    name: {display}\n"
            f"    roleDefinition: |-\n{block(a.body)}\n"
            f"    whenToUse: >-\n{_wrap(a.description, '      ')}\n"
            f"    groups:\n{groups}\n"
            f"    # preferred model tier (set in Roo's model config): {a.model}\n"
        )
    path = out / ".roomodes"
    path.write_text("".join(parts), encoding="utf-8")
    return [path]


def emit_generic(agents: list[Agent], out: Path) -> list[Path]:
    parts = [
        "# Agents (portable bundle)\n",
        "\nDerived from the canonical Claude Code agents (`.claude/agents/`). Load a role's prompt into any "
        "model that lacks a native agent system; grant it the listed tools/capabilities.\n",
    ]
    for a in agents:
        parts.append(
            f"\n---\n\n## {a.name}\n\n"
            f"**When to use:** {a.description}\n\n"
            f"**Tools:** {', '.join(a.tools) or '—'}  ·  **Model:** {a.model or '—'}\n\n"
            f"**Role prompt:**\n\n{a.body}"
        )
    path = out / "AGENTS.md"
    path.write_text("".join(parts), encoding="utf-8")
    return [path]


def _codex_caps(tools: list[str]) -> tuple[list[str], str]:
    """Coarse capability set + suggested Codex sandbox mode, from the Claude tools.

    Codex has no per-agent tool grants (the sandbox/approval model is global), so the per-agent tools
    project to a capability hint and a suggested `sandbox_mode` the operator can reflect in Codex config.
    """
    caps: set[str] = set()
    for t in tools:
        if t.startswith("mcp__"):
            caps.add("mcp")
        else:
            group = _TOOL_GROUP.get(t)
            if group:
                caps.add("web" if group == "browser" else group)
    order = ["read", "edit", "command", "web", "mcp"]
    ordered = [c for c in order if c in caps]
    sandbox = "workspace-write" if caps & {"edit", "command"} else "read-only"
    return ordered, sandbox


def _display_name(name: str) -> str:
    """`talus-auditor` -> `Talus Auditor` (the harness-facing label)."""
    return name.replace("talus-", "Talus ").title().replace("Talus Talus", "Talus")


# Agents that should be invoked *deliberately*, never auto-selected by Codex on a description match:
# the review-time auditor (you run it for a review, not mid-edit). The design pipeline + chronicler may
# implicit-trigger.
_EXPLICIT_ONLY = {"talus-auditor"}


def emit_codex(agents: list[Agent], out: Path) -> list[Path]:
    """OpenAI Codex CLI (a.k.a. the ChatGPT coding agent): one **skill** per agent under
    `<out>/.agents/skills/<name>/` — a `SKILL.md` (frontmatter `name` + `description`, body) plus an
    `agents/openai.yaml` (display name + implicit-invocation policy). The `description` is what Codex
    pattern-matches for implicit invocation; explicit invocation is `/skills` or `$<name>`. (Codex custom
    prompts are deprecated in favor of skills.)
    """
    written: list[Path] = []
    for a in agents:
        caps, sandbox = _codex_caps(a.tools)
        skill_dir = out / ".agents" / "skills" / a.name
        skill_dir.mkdir(parents=True, exist_ok=True)

        content = (
            "---\n"
            f"name: {a.name}\n"
            "description: >-\n"
            f"{_wrap(a.description, '  ')}\n"
            "---\n\n"
            f"**Capabilities:** {', '.join(caps) or '—'}  ·  "
            f"**Suggested Codex sandbox:** `{sandbox}`  ·  **Model tier:** {a.model or '—'}\n\n"
            f"{a.body}"
        )
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text(content, encoding="utf-8")
        written.append(skill_path)

        meta_dir = skill_dir / "agents"
        meta_dir.mkdir(parents=True, exist_ok=True)
        implicit = "false" if a.name in _EXPLICIT_ONLY else "true"
        meta = (
            "# Codex skill metadata (UI + invocation policy).\n"
            "interface:\n"
            f'  display_name: "{_display_name(a.name)}"\n'
            "policy:\n"
            f"  allow_implicit_invocation: {implicit}\n"
        )
        meta_path = meta_dir / "openai.yaml"
        meta_path.write_text(meta, encoding="utf-8")
        written.append(meta_path)
    return written


def copy_skill_first(out: Path, *, generic: bool) -> list[Path]:
    """Carry skill-first roles (`.claude/skills/<name>/SKILL.md`) verbatim into the Codex skill tree. The
    SKILL.md format is shared between Claude Code and Codex, so this is a copy, not a lossy projection;
    `--generic` strips any suite overlay."""
    written: list[Path] = []
    if not SKILLS_SRC.is_dir():
        return written
    for skill_md in sorted(SKILLS_SRC.glob("*/SKILL.md")):
        dest_dir = out / ".agents" / "skills" / skill_md.parent.name
        dest_dir.mkdir(parents=True, exist_ok=True)
        text = skill_md.read_text(encoding="utf-8")
        (dest_dir / "SKILL.md").write_text(strip_overlays(text) if generic else text, encoding="utf-8")
        written.append(dest_dir / "SKILL.md")
    return written


EMITTERS = {"roo": emit_roo, "codex": emit_codex, "generic": emit_generic}
_ALIASES = {"chatgpt": "codex"}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Derive non-Claude agents from the canonical .claude/agents/.")
    parser.add_argument("harness", choices=sorted(set(EMITTERS) | set(_ALIASES)))
    parser.add_argument("--out", type=Path, default=None, help="target repo root (default: the .claude/ root)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--suite", action="store_true", help="keep suite overlays (default)")
    mode.add_argument("--generic", action="store_true", help="strip suite overlays")
    args = parser.parse_args(argv)

    if not SRC.is_dir():
        print(f"Error: canonical agents not found at {SRC}", file=sys.stderr)
        return 1
    out = args.out or ROOT
    if not out.is_dir():
        print(f"Error: --out '{out}' is not a directory", file=sys.stderr)
        return 1

    harness = _ALIASES.get(args.harness, args.harness)
    agents = load_agents(generic=args.generic)
    written = EMITTERS[harness](agents, out)
    if harness == "codex":  # carry skill-first roles (talus-gates, …) verbatim alongside the derived skills
        written += copy_skill_first(out, generic=args.generic)
    flavor = "generic" if args.generic else "suite"
    print(f"Derived {len(agents)} agents ({flavor}) from .claude/agents/ -> {harness}:")
    for path in written:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
