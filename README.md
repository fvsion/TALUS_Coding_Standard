# TALUS Coding Standard

Portable engineering standards: one baseline for how software is designed, written, secured, shipped,
documented, and built with AI. Install it into any project so the output holds the same quality bar no
matter who, or what, wrote it.

## Why this exists

Most AI-assisted codebases converge on one of two failure modes: no standards at all (the model does
whatever it learned from the open internet), or standards as a suggestion file that a long session forgets.
TALUS treats standards as a gated deliverable. Every must-rule is backed by either a blocking CI gate or a
review agent that produces a per-rule finding; conformance is checkable, not asserted.

The approach also addresses the skill-marketplace supply-chain risk: a poisoned agent skill from a registry
leaves no CVE or SBOM trace. TALUS ships flat markdown and opt-in shell scripts that you read before you
run; nothing fetches from a registry, executes on install, or phones home.

## Install

Recommended: let your AI coding agent do it. Manual works too. Do not clone this inside your project; the
installer vendors a copy in for you.

### Option 1: tell your AI agent (recommended)

From inside your project, tell your coding agent:

> [!IMPORTANT]
> **Prompt to give your coding agent:**
>
> Install the TALUS coding standard from https://github.com/fvsion/TALUS_Coding_Standard into this project.
> Clone it outside the project first, then run its installer.

- The installer is additive and idempotent. The agent confirms before writing.
- The documentation agent (`talus-herald`) installs on the `sonnet` model by default. Your agent should ask
  whether to upgrade it to the higher-quality `opus` model (higher cost per run); say so up front, or have it
  pass `--herald-opus`.
- Restart the agent app afterward so the agents load.

### Option 2: manual

1. Clone it into your dev folder, beside your projects (not inside one):

```sh
cd ~/Dev
git clone https://github.com/fvsion/TALUS_Coding_Standard.git
cd TALUS_Coding_Standard
```

2. Run the installer against your project. It is a shell script, so run it with `bash`:

```sh
bash scripts/install.sh /path/to/your-project
```

3. Restart your coding-agent app.

### What it installs (into your project)

- `Standards/`: the standards, vendored (git-ignored, re-pullable).
- `.claude/agents/`: the design, documentation, and review agents.
- `.claude/skills/`: model-invoked skills (`talus-phase` runs a build in reviewed phases; `talus-gates` runs the CI gates).
- `CLAUDE.md`: a directive that points your coding agent at the standards. Appended, never overwritten.
- `.talus/journal/`: the phase ledger and build journal (the project's working memory).
- A per-turn reminder hook (default on) that re-states the core rule every turn so it survives compaction (Claude `.claude/settings.json`; Codex `.codex/hooks.json`). Opt out with `--no-hook`.
- A git pre-commit gate (default on) that runs the CI gates and blocks a failing commit. Opt out with `--no-precommit`.
- The documentation agent (`talus-herald`) on the `sonnet` model by default; pass `--herald-opus` for the higher-quality `opus` model at higher cost. Run interactively without the flag and the installer asks.
- A `.gitignore` entry for the vendored copy.

### After install: prime your agent

Restart the agent app so `CLAUDE.md` and the agents load. The `CLAUDE.md` directive already points the agent
at the standards, so a Claude Code session is primed on load. If it does not pick it up, or you are on
another tool, send this as your first message:

> [!IMPORTANT]
> **Prompt to prime your agent (send as the first message):**
>
> Read `Standards/DOCTRINE.md` (the must-gate contract) and `Standards/A_TALUS_Coding_Standard.md`, and follow
> the TALUS standards for this project. For non-trivial work, use the design agents (`talus-architect`,
> `talus-scribe`, `talus-cartographer`), write the user docs with `talus-herald`, and run `talus-auditor`
> (diff-scoped) at each phase, not just at the end. Work in small reviewed phases, do not one-shot. Resume
> context lives in `.talus/journal/STATUS.md`.

**Small or local model (tight context):** if you are running a smaller or local model, use this leaner prompt
instead, so it never loads a whole large standard:

> [!IMPORTANT]
> **Prompt for a small or local model:**
>
> Follow the TALUS standards in `Standards/`. Read `Standards/DOCTRINE.md` first (the whole must-gate contract,
> one screen), then open only the specific `§` it cites that your task needs, never a whole standard file. Do
> one tiny phase, verify it, then stop. Resume context lives in `.talus/journal/STATUS.md`.

**Durability.** The install layers four defenses so the directive is not lost in a long or compacted session:
the always-loaded `CLAUDE.md` (presence), the per-turn reminder hook (salience, default on), the
`.talus/journal/STATUS.md` ledger (re-anchor), and the pre-commit + CI gates (enforcement, default on). Opt out
of the hook or the gate with `--no-hook` / `--no-precommit`.

### Other coding agents

Claude Code reads `.claude/agents/` directly. For another agent, pass it as a second argument:

- `bash scripts/install.sh <project> codex`: OpenAI Codex / ChatGPT (skills under `.agents/skills/`).
- `bash scripts/install.sh <project> roo`: Roo Code (for example, a local model in VS Code).
- `bash scripts/install.sh <project> generic`: a plain `AGENTS.md` bundle.

## The standards

- `DOCTRINE.md`: the flattened must-gate contract, every standard's hardest gates on one screen. Read it first.
- `A_TALUS_Coding_Standard.md`: the language-agnostic umbrella.
- `languages/Python_Coding_Standard.md`: the Python standard (more languages later).
- `B_AI_Coding_Phase_Guidelines.md`: how an AI builds in bounded, reviewable phases.
- `C_Documentation_and_Architecting_Standard.md`: the minimum design-spec set.
- `D_Visual_UX_UI_Standard.md`: CLI and web UX/UI.
- `E_API_and_Data_Contract_Standard.md`: contract-first interfaces.
- `F_Security_and_OpSec_Standard.md`: secure and opsec by construction.
- `G_Observability_and_Reliability_Standard.md`: telemetry, SLOs, safe rollout.
- `H_Git_and_Release_Engineering_Standard.md`: trunk-based flow, SemVer, gated releases.
- `I_Licensing_and_Editions_Standard.md`: open-core community and pro editions.
- `J_LLM_AI_Integration_Standard.md`: LLMs inside products, safely.
- `K_User_Documentation_Standard.md`: the four user-facing doc artifacts (README, GUIDE, RTFM, TUTORIAL).

## Using the standards

- Start with `DOCTRINE.md`: the one-screen must-gate contract distilled from every standard, each gate citing
  its standard and section. It fits in any context window, so load it first, then open only the sections it
  cites that your task needs. It is generated from `doctrine.toml`; do not edit it by hand.
- Read order: the umbrella, then your language standard, then Documentation & Architecting, then Visual UX/UI.
- On a tight context window, read a large standard by section: its Contents (or the umbrella's section map),
  then the section you need. Do not load the whole file.
- Build with the AI Coding Phase Guidelines: one phase, verify, stop for review. The `talus-phase` skill walks
  the agent through it.
- Enforcement: mandatory and CI-gated (lint and format, strict type-check, tests and coverage, import
  boundaries, secret and dependency scans). Non-conforming code fails CI. The `talus-gates` skill runs them on
  demand; the `talus-auditor` agent reviews what a linter cannot.

## How TALUS compares

TALUS is **horizontal**: it standardizes how you engineer *anything*, organized by concern (design, security,
releasing, operating), rather than by framework, feature, or lifecycle phase. It complements the per-stack and
spec-driven tools more than it competes with them.

| Suite | Organized by | Scope | Delivery | Enforcement | Maturity |
|---|---|---|---|---|---|
| **TALUS** (this) | Engineering concern (horizontal) | 12 standards across the SDLC: design, architecture, a language, security, observability, contracts, release, licensing, LLM-in-product, UX, user docs | `git clone` + `bash`, flat markdown; no registry, runtime, or telemetry | Blocking CI gates + a review agent | New (v1.3) |
| [agent-skills-standard](https://github.com/HoangNguyen0403/agent-skills-standard) | Framework / language (vertical) | Hundreds of per-stack coding-standard skills | CLI-synced from a registry | Skill descriptions; eval tests | Established |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Lifecycle phase (Define to Ship) | ~20 skills, slash commands, 3 agent personas | Claude Code plugin marketplace | Per-skill TDD, step gates | Rising |
| [GitHub Spec Kit](https://github.com/github/spec-kit) | Per-feature spec | Spec, Plan, Tasks, Implement workflow | `specify` CLI | The spec is the checkpoint | Large (GitHub) |
| [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | Per-feature, agent role | Multi-agent agile: PRD, architecture, sharded stories | CLI + agent bundles | Role-gated artifacts | Large community |

Where TALUS is deliberately different:

- **Offline and dependency-free.** It installs by copying flat markdown; nothing fetches from a registry, runs
  a daemon, or phones home, so you read it before you trust it. This matters in 2026: independent audits of
  agent-skill marketplaces found a meaningful share of published skills carried vulnerabilities such as prompt
  injection, malware, and exposed secrets ([Snyk](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/),
  [Orca](https://orca.security/resources/blog/ai-agent-skill-supply-chain-security/)), and a poisoned skill
  leaves no CVE or SBOM trace. TALUS ships documents and opt-in scripts, not auto-running code.
- **Enforced, not advisory.** Every standard is backed by a blocking CI gate or a review agent; non-conforming
  code fails CI rather than relying on the model's goodwill. `GATE_COVERAGE.md` is the receipt: every must-gate
  mapped to the arm that catches a violation, generated from data so a gate cannot quietly go unenforced.
- **Concern-complete.** Security, observability, API contracts, release engineering, licensing, and
  LLM-in-product are first-class standards, not a single "best practices" file.

Honest trade-offs: TALUS is **new**, with no adoption yet, and it is **restrictively licensed**
(CC BY-NC-ND: use and share as-is, noncommercial, no derivatives) where most alternatives are MIT or Apache.

## Documentation

- [USER_GUIDE.md](USER_GUIDE.md): install into a project, work in phases, run the gates, use the agents.
- [REFERENCE.md](REFERENCE.md): every script flag, agent, skill, config key, and gate. The lookup reference.
- [TUTORIAL.md](TUTORIAL.md): one end-to-end walkthrough from a fresh project to a passing gate run.
- [CHANGELOG.md](CHANGELOG.md): version history.

## Version

Standards Suite v1.3 (2026-06-26). Locked at v1.0 (2026-06-25); v1.1 added section-addressed reading; v1.1.1
indexed the standards `A_` to `J_`; v1.2 adds directive durability and per-phase review, plus two generated
contracts: `DOCTRINE.md` (the must-gate distillation) and `GATE_COVERAGE.md` (the enforcement map); v1.2.1
prescribes the `Research_and_Planning/` planning folder and marks design-time artifacts internal by default;
v1.3 adds the User Documentation Standard (`K`) and the `talus-herald` agent that writes and reviews the
user-facing doc set. Standards version independently after the v1.0 lock. See [CHANGELOG.md](CHANGELOG.md).

## License

Licensed **CC BY-NC-ND 4.0** (Creative Commons Attribution-NonCommercial-NoDerivatives). You may use and
share these standards as-is, for noncommercial purposes, with attribution. You may not modify, rebrand, or
redistribute modified versions. The bundled scripts are provided under the same terms. See [LICENSE](LICENSE).
