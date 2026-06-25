# Talus ToolSuite — Python Coding Standard, Design & Implementation

> **The single source of truth for how Python is designed, written, packaged, and shipped across the
> Talus ToolSuite.** It binds every Python artifact in the suite: a `pip install` library (Tier 1), a
> standalone run-in-place CLI app (Tier 2), and a full platform or service (Tier 3). Where any other
> document states a general Python practice that conflicts with this one, **this document governs**;
> tool-specific design docs (e.g. an `Architecture/` suite) specialize it, they do not override it.
>
> This standard is **mandatory and mechanically enforced**. The opinionated rules here are backed by
> blocking CI gates (§23) and a review-time conformance agent, `talus-auditor` (§26). "Recommended,"
> "should," and "must" are used deliberately: **must** is a gate, **should** is a strong default that
> requires a logged justification to deviate from, **may** is genuine latitude.
>
> Status: **Accepted, v1.1** (2026-06-26). Part of **Standards Suite v1.1** (was v1.0, 2026-06-25).
> Supersedes the general (non-platform-specific) content of a
> prior platform code-standards document; reconciliations are logged in §26.

---

## Contents

**Part I — Foundations & Doctrine** — §1 Purpose, Scope & Authority · §2 Core Principles · §3 Language
Baseline & Version Policy
**Part II — Project Shape & Packaging Tiers** — §4 The Three Tiers · §5 Project Layout · §6 Packaging &
Build · §7 Dependency Policy
**Part III — Architecture & Design** — §8 Layered Architecture · §9 SOLID · §10 Ports & Adapters · §11
Configuration · §12 Domain Modeling
**Part IV — Implementation Standards** — §13 Typing · §14 Clean Code & Naming · §15 Errors & Exceptions
· §16 Logging · §17 Filesystem & I/O · §18 Terminal Output & Color · §19 CLI Conventions
**Part V — Concurrency & Performance** — §20 Concurrency Model · §21 Performance & Going Native
**Part VI — Quality, Testing & Tooling** — §22 Testing · §23 Toolchain & CI Gates · §24 Documentation ·
§25 Security & OpSec
**Part VII — Governance** — §26 Adoption, Exceptions & Enforcement · §27 Decision Summary · §28 Why This
Is Right
**Appendices** — A `pyproject.toml` templates · B tool configs · C ports-&-adapters skeleton · D
native-acceleration flowchart · E glossary & references

> **Reading this on a constrained context window:** this standard is **section-addressable** — read this
> Contents (or the umbrella's canonical section framework, §1.5 there) and then the specific `§` the work
> touches by its `## N.` heading, rather than loading the whole file. Every concern has a known home in the
> map, so reading by section loses nothing.

---

# Part I — Foundations & Doctrine

## 1. Purpose, Scope & Authority

### 1.1 Why this document exists

The suite is crossing the line from "scripts that work" to **a product family built and maintained by a
team**. At that scale, implicit convention is a liability: it drifts between tools, it is invisible to a
new contributor, and it cannot be enforced. The cost shows up concretely. Today some tools ship as
modern pip packages with `ruff`/type-checking/`pytest` configured, while others are run-in-place apps that carry no packaging, no tests, no
type-check gate, `os.path` string-handling throughout, and a single 4,800-line entry file. Both styles
"work." Neither is a standard. This document makes the practice explicit, opinionated, and enforced, so
that the path of least resistance is also the correct path.

### 1.2 What it governs

Everything written in Python anywhere in the suite: libraries, CLI tools, platform backends, analytical
cores, build scripts, and test code. It governs *design* (how the code is structured), *implementation*
(how it is written), *packaging* (how it is distributed), and *quality* (how it is verified). It is
deliberately broad because the suite spans the full distribution spectrum (§4), and a standard that only
covered web platforms would leave the majority of
the suite's Python ungoverned.

It does **not** govern non-Python code (TypeScript front-ends, the AGE/Cypher and SQL covered in
tool-specific docs, shell glue) except where a Python boundary touches them (e.g. the injection lint of
§25). It does not restate the suite's product taxonomy or integration contracts; those live in the project's
root orientation doc and contract registry and are referenced, not duplicated.

### 1.3 Authority and precedence

1. **This document is the canonical Python standard.** A tool's own `CLAUDE.md` points up to it.
2. **Tool-specific docs specialize, never contradict.** A platform's own code-standards doc remains valid
   as the platform-specific expression of these principles. Where it stated a *general* rule that this document now states
   differently — most notably the type checker (§13) — this document wins and §26 records the change.
3. **Deviations are explicit.** A `must` is a gate. To deviate from a `should`, record the reason in
   code (a comment citing the `§`) or in the tool's ADR log; an undocumented deviation is a defect the
   `talus-auditor` flags.

### 1.4 The standard practices what it preaches

This document is written in the style it mandates (§14.4): direct, economical, no filler, em-dashes used
sparingly rather than as a reflex. If the prose here reads as over-decorated, that is a bug in the
document.

---

## 2. Core Principles (canonical)

These are the non-negotiable commitments that every later rule serves. They are the suite's engineering
doctrine (`CLAUDE.md §4`), and they are the **nine canonical principles of the `A_TALUS_Coding_Standard.md`
umbrella (§2 there), in the same order**, specialized here to Python and binding on all tiers.

1. **Deterministic logic decides; the math is transparent.** Ordering, timing, scoring, and selection
   are made by explicit, auditable algorithms, never by opaque heuristics and never by an LLM. Every
   computed score is **decomposable**: each input's contribution is inspectable. Code that hides a
   decision behind an un-justified magic constant violates this (§11). **Where an LLM is used at all it is
   glue at a named boundary and decides nothing** — confined to the sanctioned places, never deciding what,
   when, or whom, with no new LLM decision point introduced without a suite-level ADR. Treat any LLM call
   as an untrusted, non-deterministic boundary: validate its output, never let it gate control flow (the
   full model is the **LLM / AI Integration Standard**).

2. **Dependencies point inward; the domain depends on nothing.** The business core has no knowledge of
   frameworks, I/O, terminals, or databases. Everything volatile (a web framework, an ANSI terminal, a
   subprocess, a datastore) is an *adapter* at the edge. This is what makes a tool re-targetable (a CLI
   app gaining a TUI or web API, §10) without touching its core. Detail in §8.

3. **Extend by addition, not modification (SOLID, especially Open/Closed).** New capability is a new
   class implementing an existing interface (a plugin, a strategy, an adapter), not a new branch in a
   growing conditional. This is the single most important property for software meant to grow. Detail in
   §9.

4. **Everything a reasonable operator would change is a variable.** Thresholds, weights, durations,
   limits, paths, and workflow shapes are named configuration with one definition site, never inline
   literals buried in logic. Tunables that affect a recorded output are versioned. Detail in §11.

5. **Secure and OpSec by construction.** Parameterized queries only; validate all untrusted input at the
   boundary; encode output; never embed secrets; scope-gate every action; log to an immutable audit
   trail. For offensive tools, operational security (what the target can observe, what reaches disk) is
   a design property, not a feature. Detail in §25.

6. **Composable: one contract, two consumers.** Every data-producing tool emits the public ingestion
   envelope and is independently useful standalone or live against the shared substrate. A
   tool never *requires* the substrate. The contract is the schema; never screen-scrape a sibling's
   human-readable output.

7. **Reproducibility is a property, not an aspiration.** The same inputs produce the same outputs.
   Determinism is testable (golden-file and property-based tests, §22), and anything that changes a
   recorded result is versioned so the output records the configuration that produced it.

8. **Efficiency is a feature, achieved by design.** Performance comes from the right algorithm and an
   honest profile, not from premature micro-optimization or from throwing hardware at a bad design.
   Measure before optimizing, and reach for a rigorous method over brute force; the native-acceleration
   ladder (better algorithm → vectorize → JIT → compiled extension) is climbed only on profiled evidence,
   each native artifact kept behind a pure fallback. Detail in §21.

9. **Cross-platform by default.** Tier 1 libraries and Tier 2 apps are designed and tested to run on
   macOS, Linux, and Windows from the outset; platform differences are isolated behind a thin adapter, not
   scattered. A genuinely platform-bound tool declares its supported platforms and why. Detail in §17.4.

The rest of this document is the disciplined application of these nine principles to the concrete
decisions a Python engineer makes daily.

---

## 3. Language Baseline & Version Policy

### 3.1 The two floors

The suite runs Python in two structurally different places, and they get two different floors. This is
not laxity; it reflects a real constraint, and conflating them is a recurring mistake.

| Class | What it is | Floor | Target |
|---|---|---|---|
| **Operator-side** | Anything that runs on the practitioner's machine or the suite's own infrastructure: platforms, orchestrators, and operator-run CLI tools. | **3.12+** | Track the current stable; adopt new minors deliberately. |
| **Target-deployed** | Code that runs **on a client or target host** the practitioner does not control, where the available interpreter is whatever shipped with the OS (e.g. an agent dropped on a box). | **3.9 absolute floor** | **Justify anything below 3.11**; adopt the highest floor the target reality permits. 3.9 is the floor, not the goal. |

**Rule.** A project declares its class and floor in its `pyproject.toml` `requires-python` (§6) and in
its README. Operator-side code that has no reason to run on an old interpreter targets **3.12+** and uses
the modern language freely. Target-deployed code states *why* its floor is what it is (a specific
distro's system Python), and an engineer who sets a floor below 3.11 records the target that forces it.

> #### ADR-PY-001 — Split Python version floors (operator-side 3.12+, target-deployed 3.9)
> **Status:** Accepted.
> **Context.** The suite's tools split cleanly into code that runs on the operator's controlled
> environment and code that must run on an arbitrary target host. A single modern floor (3.12+
> everywhere) would break tools that must run under an old system Python (RHEL/Ubuntu LTS ship 3.6–3.11
> depending on vintage); a single conservative floor (3.9 everywhere) would tax every operator-side
> tool with a decade-old language for no benefit.
> **Decision.** Two floors, declared per project: **3.12+** operator-side, **3.9** absolute floor
> target-deployed, with a standing mandate to push the target floor as high as the deployment reality
> allows and to justify any floor below 3.11.
> **Alternatives considered.** *3.12+ everywhere* — rejected, breaks on-target tools. *3.11+ everywhere*
> — rejected, still too high for some LTS targets and needlessly conservative for operator-side.
> **Consequences.** Each project's CI matrix tests against its declared floor (§23). Shared libraries
> consumed by both classes target the **lower** floor or ship version-gated code paths. Syntax/stdlib
> availability is governed by the project's floor, not by what the author's laptop runs.

### 3.2 What the floor permits

Language and stdlib features are gated by the project's declared floor, verified by the type checker's
`pythonVersion` setting (§13) and `ruff`'s `target-version` (§23), which flag use of newer constructs.

- **Operator-side (3.12+).** Use modern syntax freely: PEP 604 unions (`int | None`), PEP 585 builtin
  generics (`list[str]`), `match` statements, the `tomllib` stdlib reader, PEP 695 type-parameter syntax
  where it clarifies. Prefer them; they are the house style.
- **Target-deployed (3.9–3.10).** PEP 585 builtin generics and PEP 604 unions in annotations are
  available under `from __future__ import annotations` (below); `match` (3.10) and `tomllib` (3.11) are
  not. Code that must run at the floor uses the constructs the floor supports and is tested there.

### 3.3 `from __future__ import annotations`

**Rule.** Every module **should** begin with `from __future__ import annotations`. It makes all
annotations strings (PEP 563), which (a) lets target-deployed code at the 3.9 floor write `list[str]`
and `X | None` in annotation position, (b) removes import-time cost of annotations, and (c) eases forward
references. The one caveat: code that reads annotations at runtime (Pydantic models, some dataclass
tricks, `typing.get_type_hints`) must account for stringized annotations; at trust boundaries that use
Pydantic (§12), follow that library's guidance. This is the only blanket exception.

**Forward note (3.14+).** Python 3.14's PEP 649/PEP 749 make annotations **lazily evaluated** by default
(via a descriptor), which natively solves the same forward-reference and import-cost concerns *without* the
future import and with friendlier runtime introspection. Until a project's floor reaches 3.14, the
`from __future__ import annotations` rule above remains the portable default; when the floor is 3.14+, rely
on the built-in lazy evaluation instead and use `annotationlib` for any runtime annotation access.

### 3.4 End-of-life and upgrades

Track the CPython release calendar. Do not run production operator-side code on an interpreter past its
upstream EOL. Adopting a new minor is a deliberate, tested change (a CI matrix addition and a green run),
not an automatic float — mirroring the suite's version-pinning discipline for its data stores. Free-
threaded builds are a special case governed by §20.4.

# Part II — Project Shape & Packaging Tiers

The suite spans the full Python distribution spectrum. A password-modeling library is `pip install`-ed
into other tools; a hash-recovery orchestrator is run in place by an operator; a reporting platform is a
containerized service. One file layout and one packaging recipe cannot serve all three, and pretending
otherwise is how a run-in-place app ends up un-packaged and untested while a sibling library stays clean.
This part defines **three tiers**, a decision procedure for which tier a tool belongs to, and the
canonical shape and packaging for each.

## 4. The Three Distribution Tiers

### 4.1 The tiers

| | **Tier 1 — Library / installable CLI** | **Tier 2 — Standalone app** | **Tier 3 — Platform / service** |
|---|---|---|---|
| **Definition** | Imported by other code and/or installed as a command; distributed as a wheel. | Run in place by an operator from a checkout; one entry script + internal modules. | A long-running service with a backend (and usually a front-end), deployed as containers. |
| **Examples** | a zero-dep library | a run-in-place orchestrator | a platform / substrate |
| **Distribution** | wheel/sdist (`pip install`); console-script entry point | git checkout; symlink the entry script onto `PATH` | Docker image(s) + compose/Helm |
| **Packaging** | `pyproject.toml`, `src/` layout, `py.typed` | `pyproject.toml` (for tooling + optional install), flat `modules/` layout | `pyproject.toml` per service, layered package |
| **Reuse surface** | high — a public API others depend on | low — the operator is the only consumer | the API is the contract; internals are private |
| **Dependency budget** | minimal; zero where feasible | minimal; vendoring acceptable | full framework stack as warranted |

### 4.2 Choosing a tier (decision procedure)

Apply in order; the first match wins.

```
Is it a long-running service with an API and/or persistent store (DB, queue, graph)?
   └─ yes → TIER 3 (platform/service)
   └─ no ↓
Will other Python code import it, OR should it install as a reusable command on many machines?
   └─ yes → TIER 1 (library / installable CLI)
   └─ no ↓
Is it operated as a single tool by a practitioner, orchestrating external binaries / files?
   └─ yes → TIER 2 (standalone app)
```

Two refinements that resolve the common ambiguities:

- **"Runs on a target host" forces a low dependency budget and the target-deployed floor (§3.1),
  regardless of tier.** A scanner can be a Tier 1 package *and* target-deployed: installable, yet
  designed to run dependency-free under an old system Python on a box the operator does not control.
  Tier and deployment-class are independent axes; declare both.
- **A Tier 2 app that grows a real reusable core should promote that core to a Tier 1 package** rather
  than letting siblings copy files. Recurring duplication across sibling apps is the signature of a missing Tier 1 library. Promotion
  is the sanctioned fix (§26.3).

### 4.3 The composability invariant (all tiers)

Independent of tier, every data-producing tool **emits the public ingestion envelope** and runs
standalone (Principle 6). A Tier 2 app is not exempt because it lacks a package boundary: its emit path
is a domain concern that targets the consolidation store directly, or the live substrate when present. The envelope is the same
either way; the substrate is never required.

---

## 5. Canonical Project Layout

### 5.1 Tier 1 — `src/` layout

Tier 1 uses the **`src/` layout**. The package lives under `src/<package>/`, which prevents the classic
defect of accidentally importing the in-tree source instead of the installed wheel during tests, and
forces tests to exercise the package as installed.

```
mylib/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── mylib/
│       ├── __init__.py
│       ├── py.typed              # ships type information (PEP 561)
│       ├── cli.py                # console-script entry: mylib = "mylib.cli:main"
│       ├── model.py  enumerate.py  …   # the public API + internals
│       └── _internal/            # underscore package = private, not part of the API
├── native/                       # optional compiled accelerator, built separately (§21)
│   └── mylib_accel.c
└── tests/                        # mirrors src/mylib/ one-to-one
    ├── test_model.py
    └── test_enumerate.py
```

Public vs private is expressed in the layout: a leading-underscore module or subpackage (`_internal`) is
not API and carries no stability promise; everything else is. `py.typed` is mandatory for a Tier 1
package (§13).

### 5.2 Tier 2 — flat `modules/` layout

Tier 2 uses a **single entry script plus a flat `modules/` package**. This is the run-in-place shape, and
it is correct for a run-in-place tool: no install step, runs from a checkout, symlinks onto `PATH`.

```
myapp/
├── myapp.py                      # entry: CLI dispatch ONLY (thin; see §5.4)
├── pyproject.toml                # present for tooling (ruff/pyright/pytest) + optional pipx install
├── README.md
├── modules/
│   ├── __init__.py               # install-root constants (single source of truth)
│   ├── campaign.py  runner.py  phases.py  speed.py  analyzer.py  reporter.py  tools.py
│   └── presentation/             # a ports-&-adapters subpackage (§10) — the model to follow
│       ├── model.py  console.py  theme.py  hashcat.py
├── config/   rules/   samples/
└── tests/                        # mirrors modules/ — REQUIRED going forward (§22)
```

Two standing rules for Tier 2, both mandated going forward:

- **The entry script is dispatch only.** A multi-thousand-line entry script is the named anti-pattern (§14.5):
  command bodies belong in `modules/`, not in the entry file. The entry script parses arguments, wires
  the renderer/config, and dispatches to a command function that lives in a module.
- **A `tests/` directory exists and mirrors `modules/`.** "No tests" is not a property of Tier 2; it is
  a gap (§22.6).

### 5.3 Tier 3 — layered package

Tier 3 uses the layered structure detailed in §8:
`api/` · `services/` · `domain/` · `repositories/` · plus a framework-independent analytical-core
package (`<tool>_core/`) as a sibling. The directory tree *is* the architecture; the layering is visible
in the filesystem, not merely asserted. Tests mirror the package.

### 5.4 Universal layout rules

- **`tests/` mirrors the package** one module to one test module, every tier.
- **One responsibility per module.** A module is named for the one concept it owns. When it accretes a
  second, it splits (§14).
- **Config, sample data, and generated artifacts are separate top-level directories** (`config/`,
  `samples/`, and a git-ignored output/cache root), never intermixed with source.
- **Install-root and path constants have one definition site** (e.g. `modules/__init__.py`), resolved
  via `pathlib` (§17), never recomputed ad hoc.

---

## 6. Packaging & Build

### 6.1 `pyproject.toml` is the only project config

**Rule (must).** Every project — all three tiers — has a `pyproject.toml`, and it is the single
configuration surface: build metadata (PEP 621), dependencies and dependency groups (PEP 735), and tool
configuration (`ruff`, `pyright`, `pytest`). No `setup.py`, no `setup.cfg`, no standalone `requirements.txt`
as the source of truth, no scattered tool dotfiles. `pyproject.toml` is the settled, PEP-backed standard
(PEP 517/518 for the build interface, 621 for metadata, 735 for dependency groups) and the ecosystem has
consolidated on it.

Tier 2 is **not exempt.** A run-in-place app still has a `pyproject.toml` so that `ruff`, `pyright`, and
`pytest` have a config home and the gates of §23 apply uniformly. The `[project]` table makes it
`pipx`-installable as a bonus; the build backend is still declared.

### 6.2 Build backend

| Situation | Backend | Why |
|---|---|---|
| Pure-Python (the default, all tiers) | **Hatchling** | Modern, fast, minimal config; the house default for new projects. |
| Ships a compiled extension (Cython/C/Rust, §21) | **setuptools** (or maturin for Rust/PyO3) | Mature support for building and shipping binary extensions; the newer backends do not handle this as well. |

**Rule.** New pure-Python projects use **Hatchling**. Reach for **setuptools** only when the project
actually builds a compiled extension — and that decision is itself gated by §21 (profile first). Note
that an *optional* native accelerator built out-of-band does **not** force
setuptools; it is the *integrated* compiled extension that does.

### 6.3 The `[project]` table and metadata

Required metadata on every package: `name`, `version`, `description`, `readme`, `requires-python` (the
declared floor, §3), `license`, `authors`, and meaningful `classifiers`. Versioning is **SemVer**: a
breaking change to a Tier 1 public API is a major bump and a logged event (§26), because siblings depend
on it.

### 6.4 Dependencies and dependency groups

- **Runtime dependencies** go in `[project.dependencies]`, kept to the minimum the tool genuinely needs
  (§7).
- **Development and optional extras** use **PEP 735 dependency groups** (`[dependency-groups]`) and/or
  `[project.optional-dependencies]`: a `dev` group (`pytest`, `pyright`, `ruff`), and feature extras
  (e.g. a `benchmark` extra for graphing tools) that keep the runtime lean.
- **Pin for applications, range for libraries.** A Tier 3 service pins a reproducible set via a lockfile;
  a Tier 1 library expresses compatible ranges so it composes with its consumers. Detail in §7.

### 6.5 Workflow tool: `uv`

**Rule (should).** Use **`uv`** for environment creation, dependency resolution, locking, and running.
It is fast, it produces a reproducible `uv.lock`, and it understands `pyproject.toml`/PEP 735 natively.
`uv` is the house workflow tool across tiers; it does not change the build backend (Hatchling/setuptools
still build the wheel), it manages the environment and lock around it. Target-deployed tools still must
*run* under a stock interpreter with no `uv` present, so their runtime must not assume it.

### 6.6 Entry points

A Tier 1 CLI exposes a **console-script entry point** (`[project.scripts]`, e.g. `mylib = "mylib.cli:main"`)
so `pip install` puts a command on `PATH`. A Tier 2 app is invoked as `python3 <entry>.py` or via a
symlink; if it also declares `[project.scripts]` it becomes `pipx`-installable, which is encouraged but
not required.

### 6.7 Reproducible builds

Builds are deterministic: a lockfile (`uv.lock`) captures the resolved set, the Tier 3 container image
bakes an exact, validated dependency set (mirroring the suite's data-store pinning discipline), and
nothing in the build reaches the network for an unpinned artifact. Reproducibility of *builds* is the
packaging-level expression of Principle 7.

Worked `pyproject.toml` templates for Tier 1 and Tier 3 are in **Appendix A**; the canonical tool-config
block (`ruff` + `pyright` + `pytest`) is in **Appendix B**.

### 6.8 Editions: the `pro/` seam and build-time split

A tool with a community and a pro edition follows the **Licensing & Editions Standard** (open-core; an
edition is a *seam*, not a *fork*). The Python expression:

- **Pro code lives in a bounded `pro/` package** (e.g. `modules/pro/` for Tier 2, `src/<pkg>/pro/` for
  Tier 1) that the **community core never imports**. The core exposes extension points (a plugin/strategy
  registry, optional adapters); `pro/` registers into them on import. No core module branches on `if pro`.
- **The community build excludes `pro/`** via package selection, so pro code is genuinely *absent* from the
  community artifact (not gated by a crackable runtime check):

  ```toml
  [tool.hatch.build.targets.wheel]
  packages = ["src/<pkg>"]            # community profile: select the core; do NOT list src/<pkg>/pro
  # exclude = ["src/<pkg>/pro"]       # or exclude explicitly; the pro build adds it back
  ```

  Small in-line pro paths use `# PRO:BEGIN` / `# PRO:END` fences stripped from the community build, and
  must leave the surrounding community code valid once removed.
- **Verify the seam in CI:** build the community profile with `pro/` excluded, then `import` the package and
  run the community test suite — it must pass with pro absent (proving the core never depended on it).
  Per-file **SPDX headers** mark each file's edition/license. Full model, protection rationale, and
  promotion-to-separate-package: the Licensing & Editions Standard.

---

## 7. Dependency Policy

### 7.1 Stdlib-first

**Rule.** Prefer the standard library. A third-party runtime dependency is added only when it provides
capability the stdlib genuinely lacks, and the choice is justified in the project's ADR log or README.
This is not asceticism: a deliberate zero-dependency posture is precisely what lets a scanner run on an
arbitrary target host and a library embed anywhere without dragging a tree behind it.

Each added dependency is weighed on: maintenance health, transitive footprint, security surface, license
compatibility, and whether it raises the effective Python floor. A dependency that pulls twenty
transitive packages to save ten lines of stdlib code is a net loss.

### 7.2 The target-host rule

**Rule (must).** Target-deployed code (§3.1) minimizes dependencies aggressively and prefers
**zero**. Every dependency is something that must already exist, or be installed, on a host the operator
does not control — often impossible in an air-gapped or locked-down environment. When a capability is
unavoidable, prefer vendoring a small, license-compatible, audited module over requiring a `pip install`
on the target.

### 7.3 Pinning and supply chain

- **Applications (Tier 2/3) pin**; **libraries (Tier 1) range.** A service commits a lockfile for a
  reproducible deploy; a library declares compatible version ranges so it does not over-constrain its
  consumers.
- **Verify integrity.** Locks carry hashes; CI installs from the lock. Dependency vulnerability scanning
  is part of the gate set (§23/§25).
- **No unpinned network fetches at build or runtime** for anything that affects a recorded output.

### 7.4 Vendoring

Vendoring (copying a small dependency into the tree) is acceptable for target-deployed code and for
avoiding a heavy transitive tree, provided the vendored code is license-compatible, clearly marked with
its source and version in a header, and updated deliberately. Vendoring a large, fast-moving library to
dodge a version constraint is not; that is a maintenance trap.

# Part III — Architecture & Design

This part is the load-bearing center of the standard. It defines *how the code is shaped* so that the
domain stays stable while the volatile edges (frameworks, terminals, datastores, external binaries)
churn — and so that a tool can be re-targeted (a CLI gaining a TUI or web API) without rewriting its
core. The principles are constant across tiers; their concrete expression scales from a small library to
a platform.

## 8. Layered Clean Architecture

### 8.1 The golden rule

**Dependencies point inward; the domain depends on nothing.** The business core knows nothing of
FastAPI, SQLAlchemy, argparse, ANSI, `subprocess`, or Redis. Everything that talks to the outside world
is an adapter at the edge, depended upon through an interface the domain owns. This is Dependency
Inversion applied at architecture scale, and it is the precondition for testability, for storage/UI
reversibility, and for growth by addition.

### 8.2 The platform shape (Tier 3)

For a service, the layering is the four-tier stack:

```
┌──────────────────────────────────────────────────────────────┐
│  API layer        HTTP only: routing, (de)serialize, status   │ → depends on Service
├──────────────────────────────────────────────────────────────┤
│  Service layer    use cases; the authorization chokepoint;    │ → depends on Domain + Repo interfaces
│                   calls the analytical core; enqueues work     │
├──────────────────────────────────────────────────────────────┤
│  Domain layer     entities, value objects, domain services;   │ → depends on NOTHING
│                   pure business concepts; no framework, no I/O │
├──────────────────────────────────────────────────────────────┤
│  Repository layer the ONLY code that touches the datastore     │ → implements domain interfaces
└──────────────────────────────────────────────────────────────┘
   Analytical core (<tool>_core) — sibling package, also depends on NOTHING (pure transforms)
```

Layer rules (enforced by import-linting, §23): the API layer is thin and holds no business logic or data
access; services orchestrate and own authorization; the domain is pure; repositories are the sole
database-touching code so a storage swap stays contained; the analytical core (the cross-domain math
that is the product's moat) is a framework-independent package taking plain data in and out, reusable
from services, workers, and CLI tools alike.

### 8.3 The CLI/standalone shape (Tier 2), and why it is the same shape

A standalone tool has the *same* inward-pointing dependency structure, renamed:

```
┌──────────────────────────────────────────────────────────────┐
│  CLI layer        argparse dispatch; wire config + renderer    │ → depends on use cases
├──────────────────────────────────────────────────────────────┤
│  Use-case layer   command bodies: "init", "run", "report"      │ → depends on Domain + adapter ports
├──────────────────────────────────────────────────────────────┤
│  Domain layer     campaign/phase model, scheduling, analysis   │ → depends on NOTHING
├──────────────────────────────────────────────────────────────┤
│  Adapters         subprocess runner, filesystem, the renderer   │ → implement domain-owned ports
│                   port (§10), the ingestion-envelope emitter     │
└──────────────────────────────────────────────────────────────┘
```

The mapping is exact: the API layer becomes the CLI dispatch, services become command/use-case
functions, repositories become adapters (the `subprocess` runner that drives `hashcat`, the filesystem,
the presentation renderer). The lesson a monolithic entry script teaches by counterexample is that when command bodies
live *in the entry script* instead of a use-case layer, the architecture is asserted but not real. Put
the bodies in `modules/`, behind the dispatch.

### 8.4 Dependency injection

Dependencies are **injected, not constructed in place.** A use case or service receives its adapters
(repository interface, renderer port, runner) through its constructor or parameters; the composition root
(the API wiring, or the CLI `main`) selects and wires the concrete implementations. Consequence: the core
is unit-testable with fakes (an in-memory repository, a recording renderer), and swapping an
implementation is a wiring change, not a code change. Never reach for a global singleton or import a
concrete adapter from inside the domain; that is the dependency arrow pointing the wrong way.

---

## 9. SOLID, Applied

SOLID is not invoked here as a slogan; each letter has a concrete, enforced expression.

- **Single Responsibility.** A class has one reason to change. A service orchestrates one domain area; a
  repository persists one aggregate; a connector parses one tool's output; a renderer targets one
  backend; a phase-strategy builds one kind of attack. A module that needs "and" to describe what it does
  is two modules.
- **Open/Closed — the most important property for software meant to grow.** Extend by **addition**: a new
  engagement type is a new plugin, a new import format is a new connector implementing the interface, a
  new output backend is a new renderer adapter, a new enrichment source implements `EnrichmentSource`, a
  new attack tactic is a new strategy registered in a table. Adding capability is a new class, never a
  new `elif` in a widening conditional. When you find yourself editing a `match`/`if` ladder to add a
  case, that ladder wants to be a registry of strategies.
- **Liskov Substitution.** Every implementation of an interface is genuinely substitutable and is tested
  against the interface's contract, not its own internals. Any `Renderer` (§10) honors the renderer
  contract; the domain cannot tell which one it holds.
- **Interface Segregation.** Ports are narrow and purpose-specific. A consumer depends only on the
  methods it uses. The renderer port (§10) is split into one-shot surfaces, inline text, and a streaming
  `LiveRegion` so a caller that only prints a table does not depend on live-region semantics.
- **Dependency Inversion.** High-level policy depends on abstractions; the whole of §8 is this principle
  at scale. Services depend on repository *interfaces*; the domain depends on the *port*, not the ANSI
  adapter.

**The strategy/plugin test.** If adding the next variant of something requires touching existing code
that already handles the previous variants, the design is closed where it should be open. Refactor to a
registry of strategies before adding the case. This is the single most common architectural finding the
`talus-auditor` will raise.

### 9.1 The registry/decorator idiom

The concrete way "extend by addition" is wired: a registry maps a key to an implementation, and a
**decorator registers each implementation at definition site**, so adding a variant is writing a new class
— never editing a dispatch ladder.

```python
from __future__ import annotations
from typing import Callable

_STRATEGIES: dict[str, type[Strategy]] = {}

def register(name: str) -> Callable[[type[Strategy]], type[Strategy]]:
    """Register a Strategy under `name`. Duplicate names are a programming error."""
    def deco(cls: type[Strategy]) -> type[Strategy]:
        if name in _STRATEGIES:
            raise ValueError(f"duplicate strategy {name!r}")
        _STRATEGIES[name] = cls
        return cls
    return deco

def get_strategy(name: str) -> Strategy:
    try:
        return _STRATEGIES[name]()
    except KeyError:
        raise UnknownStrategyError(name) from None   # fail closed on an unknown key

@register("dictionary")
class DictionaryStrategy:        # conforms to the Strategy Protocol structurally (§10.2/§12.2)
    ...
```

- **Lookup fails closed** (§15) on an unknown key — never a silent default.
- **The registry is populated by import**: the composition root imports the package whose modules carry the
  `@register` calls (a plugin discovers itself by being imported); the core never enumerates concrete
  classes. This is the same seam the **edition split** rides — a `pro/` module simply registers more on
  import (Licensing & Editions Standard §3), absent from the community build.
- Prefer a registry over an `Enum`-keyed `match` when the set is **open** (plugins, strategies, adapters);
  keep the `Enum` + `match` for a genuinely **closed** set (§12.2).

---

## 10. Ports & Adapters (Hexagonal)

This is the pattern that makes the suite's "bring any part, re-target anything" promise real, and it is
worth a worked example because it is where a CLI tool earns a future TUI or web/JSON frontend **for free**.
The exemplar is a presentation package that isolates rendering behind a port, the model every tool's output and
external-tool integration should follow.

### 10.1 The shape

A **port** is an interface the domain owns and depends on. An **adapter** implements that port for a
specific backend. The domain speaks only the port's vocabulary; it never knows which adapter is wired.
Two directions:

- **Outbound (driven) port** — the domain *calls out* through it. The presentation `Renderer` is outbound:
  the domain says "render this table"; an adapter decides whether that means ANSI, a TUI widget, or JSON.
- **Inbound (anti-corruption) adapter** — the domain *receives* through it. An external-tool output classifier
  is inbound: it turns raw, messy `hashcat` stdout into typed `HashcatEvent`s so noise never reaches the
  domain or the renderer. This is the fix for "raw tool spew leaking into output."

### 10.2 The port is plain data + an interface, and imports nothing volatile

The port module defines *view-models* (what to show) and *events* (what happened) as frozen dataclasses,
plus the interface as a `typing.Protocol`. The rule that keeps the seam honest, quoted from the real
port:

> **Nothing in this module imports `theme` or emits an escape code. Colour is an adapter concern.**

The interface, abbreviated from `modules/presentation/model.py`:

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Sequence, Tuple, Optional, runtime_checkable

@dataclass(frozen=True)
class KeyValues:
    """Aligned `label value` rows; `dim` selects the muted diagnostic tier."""
    pairs: Sequence[Tuple[str, str]]
    title: Optional[str] = None
    dim: bool = False
    indent: int = 0

@runtime_checkable
class Renderer(Protocol):
    """The presentation port. Adapters implement this; the domain depends only on it.
    No method may change program behaviour, and text destined for a file/log must be plain."""
    @property
    def color(self) -> bool: ...
    def section(self, title: str = "") -> None: ...
    def key_values(self, kv: KeyValues) -> None: ...
    def table(self, table: Table) -> None: ...
    def detail(self, text: str) -> None: ...      # the dim diagnostic tier
    def live(self) -> LiveRegion: ...              # streaming, in-place updates
```

Why `Protocol` rather than an abstract base class: structural typing means an adapter (or a test double)
satisfies the port by *shape*, with no inheritance coupling, and `@runtime_checkable` allows a cheap
isinstance guard at the composition root. Prefer `Protocol` for ports; reserve ABCs for cases that need
shared implementation (§12.3).

### 10.3 Adapters are where the volatile detail lives

- **The CLI/ANSI adapter** (`console.py`) paints view-models with color, does ANSI-aware width math, and
  manages the in-place live region. It is the only place that knows about terminals.
- **The colour model** (`theme.py`) is adapter-private: truecolor→256→16→plain degradation lives here and
  nowhere else (§18).
- **The inbound classifier** (`hashcat.py`) imports only the port's `model`, never the console or theme;
  it turns raw lines into `HashcatEvent`s and drops noise.

### 10.4 The payoff: re-targeting is a new adapter, not a rewrite

Because the domain calls `renderer.table(...)` and `renderer.key_values(...)`, adding a frontend is
adding one class:

- a **TUI** adapter renders view-models into curses/Textual widgets;
- a **web/JSON** adapter serializes view-models to JSON for an HTTP or WebSocket frontend;
- a **test** adapter records calls for assertions.

None of these touch a single line of `phases`, `runner`, `campaign`, or `analyzer`. That is the concrete
meaning of "the port + console adaptable to a TUI or API later." Build the port now, even when only one
adapter exists, and the optionality is free. Conversely, output written with bare `print()` and inline
escape codes throws this optionality away and is a defect (§18).

### 10.5 When to apply it

Use a port-and-adapter seam wherever the domain meets something volatile or replaceable: presentation
(every tool with terminal output), external-binary integration (a `subprocess`-driven tool like
`hashcat`/`nmap`), persistence (the repository pattern is ports-and-adapters for storage), and the
ingestion-envelope emit path. Do not over-apply it to stable, internal collaborators; a port earns its
keep only at a boundary that is genuinely volatile or genuinely needs a second implementation.

### 10.6 Reporters as context managers, and composing many

A **reporter** is an output adapter that owns a sink with a lifecycle (a file, a stream, a socket). Author
it as a **context manager** so its lifecycle is guaranteed — opened on entry, header written, and
**flushed and closed on every exit path including an exception** (the §15.3 cleanup rule, made the adapter's
own responsibility rather than the caller's):

```python
class FileReporter:
    """A Renderer (§10.2) that writes plain view-models to a file sink."""
    def __init__(self, path: Path) -> None:
        self._path, self._fh = path, None

    def __enter__(self) -> "FileReporter":
        self._fh = self._path.open("w", encoding="utf-8", newline="\n")  # explicit (§17.2)
        return self

    def __exit__(self, *exc: object) -> None:
        if self._fh:
            self._fh.flush()
            self._fh.close()   # runs on success AND on error — no leaked/half-written report
```

**Compose many reporters** when one run must emit to several sinks at once (console + a `.txt` report + a
JSON envelope) without the domain knowing how many there are. A composite *is itself* a reporter (Liskov,
§9) that fans each call out to its children and manages all their lifecycles together with
`contextlib.ExitStack`:

```python
class MultiReporter:
    def __init__(self, reporters: Sequence[Renderer]) -> None:
        self._reporters, self._stack = reporters, ExitStack()

    def __enter__(self) -> "MultiReporter":
        for r in self._reporters:
            self._stack.enter_context(r)   # each child entered; all unwound on exit, even on error
        return self

    def __exit__(self, *exc: object) -> None:
        self._stack.close()

    def table(self, table: Table) -> None:
        for r in self._reporters:
            r.table(table)                 # fan-out; the domain calls one renderer, N sinks receive it
```

The domain still calls a single `renderer.table(...)` (§10.4); whether that reaches one terminal or three
sinks is a composition-root decision. `ExitStack` guarantees that if the third reporter's `__enter__`
fails, the first two are still closed.

---

## 11. Configuration & the "Everything Is a Variable" Standard

### 11.1 The rule

**Any value a reasonable operator would want to change is named configuration with a single definition
site, never an inline literal buried in logic.** Thresholds, weights, ε-values, limits, retry counts,
durations, timeouts, page sizes, priority bands, file paths, and charset sizes are parameters. The test:
if a sensible practitioner would ask "can we change X without shipping new code?", X is a variable.

This is a maintainability *and* a doctrine requirement: Principle 1 demands every decision be transparent
and decomposable, and a magic constant hidden in a branch is the opposite of transparent.

### 11.2 Workflow shapes are data, not code

Where a tool encodes a *process* — phase priority bands, status enumerations, attack-tactic ordering,
report section layouts, notification routing — that shape is configuration the tool reads, so it can be
retuned without a fork. The shipped values are a default *seed*, not a hardcoded ceiling.

### 11.3 One typed settings layer

Configuration is loaded once, through **one typed settings object**, validated at startup, and never read
ad hoc from `os.environ` scattered through the code. Precedence is explicit and uniform (§19.4):
command-line flags override environment variables override the config file override built-in defaults.
For Tier 3, this is a Pydantic `BaseSettings`-style object; for Tier 2, a small typed dataclass loaded
from a JSON/TOML config plus env is sufficient. Either way: one site, typed, validated.

### 11.4 Versioned tunables

Anything that changes a *recorded* output (a scoring weight, a speed model, a priority formula) is
**versioned**, so the output records the configuration that produced it (Principle 7). Changeability never
costs reproducibility.

### 11.5 Secrets are never configuration-in-code

Secrets come from the environment or a secret store, never from source, never from a committed config
file. This is restated and enforced in §25.

---

## 12. Domain Modeling

### 12.1 Dataclasses for data

Model domain data as **dataclasses**, not hand-written `__init__` boilerplate. Use `@dataclass(frozen=True)`
for **value objects and view-models** (immutable, hashable, safe to share — the presentation view-models
and the `HashcatEvent` are the model), and a plain mutable `@dataclass` only where a single instance is
deliberately updated in place (the live `RunState` the runner ticks). Default to frozen; reach for mutable
with a reason. A frozen dataclass is **hashable**, so a `set` (or a `dict` key) deduplicates value objects
for free — the idiomatic way to dedupe findings, observations, or events without a hand-written key.

### 12.2 `Protocol` for ports, `Enum` for closed sets

- **`Protocol`** (structural) for ports and pluggable seams (§10): adapters and test doubles conform by
  shape, with no inheritance coupling.
- **`Enum`** for every closed set of named constants (status, level, kind, mode). A bare string literal
  standing in for a member is a defect (§11.1). The presentation `Level`, `Align`, and `HashcatLineKind`
  enums are the pattern.

### 12.3 Dataclass vs class vs Pydantic — the boundary rule

- **`@dataclass`** for internal domain data and value objects (the default).
- **A plain class** when behavior dominates and identity matters (a service, an adapter, a strategy).
- **An abstract base class** only when implementations share real code; otherwise prefer `Protocol`.
- **Pydantic only at trust boundaries** — request/response schemas, ingestion-envelope validation,
  settings — where untrusted input must be parsed and validated. Pydantic does not belong in the pure
  domain or analytical core; those take and return plain data (Principle 2). Keeping validation at the
  edge keeps the core framework-free and fast.

### 12.4 Immutability and purity defaults

Prefer immutable data and pure functions; push side effects (I/O, mutation, time, randomness) to the
edges. Pure code is testable code, and the analytical core is pure by mandate. A function that both
computes and prints is two functions; the compute half belongs in the domain, the print half goes through
the renderer port.

# Part IV — Implementation Standards

The line-level discipline. These rules are the most frequently checked, by `ruff`, by Pyright, and by the
`talus-auditor`. They are deliberately concrete.

## 13. Typing Discipline

### 13.1 Fully typed, no exceptions

**Rule (must).** All Python is fully type-annotated: every function signature (parameters and return),
every dataclass field, every public attribute. Types are documentation that cannot go stale and the
substrate the analytical guarantees rest on. Untyped code does not pass the gate (§23).

### 13.2 Pyright (strict) is the canonical type checker

**Rule (must).** **Pyright in strict mode** is the suite's type checker, run in CI as a blocking gate.

> #### ADR-PY-002 — Standardize on Pyright (strict), superseding `mypy --strict`
> **Status:** Accepted. Supersedes any prior `mypy --strict` mandate.
> **Context.** The suite previously mandated `mypy --strict`. By 2026 the type-checker landscape has
> moved: Pyright offers a markedly better speed-to-correctness ratio with very high spec conformance and
> first-class editor integration, and Astral's `ty` (Rust, same vendor as `ruff`/`uv`) is fast but still
> beta. The suite already standardizes on `ruff`; a single, fast, strict checker reduces friction.
> **Decision.** Pyright (`strict`) is the canonical checker, in CI and in the editor. Set
> `pythonVersion` to the project's declared floor (§3) so version-inappropriate constructs are flagged.
> **Alternatives considered.** *Keep mypy* — established and library-friendly, but slower and weaker
> editor story; rejected as the default for new work (a project with a specific reason may run mypy
> additionally, never instead). *Adopt `ty` now* — promising and fast, but beta; revisit when stable.
> **Consequences.** One checker config across the suite (Appendix B). Existing `[tool.mypy]` blocks are migrated to `[tool.pyright]`; a project keeping mypy too must keep both green.

### 13.3 `py.typed` for libraries

**Rule (must for Tier 1).** A distributed library ships a `py.typed` marker (PEP 561) so its consumers
get its types. A library without `py.typed` is opaque to every downstream checker; this is a packaging
defect.

### 13.4 No silent escape hatches

`Any` is not a substitute for thinking. `# type: ignore` and `# pyright: ignore` are permitted only with
a specific code and a short reason (`# pyright: ignore[reportGeneralTypeIssues] — third-party stub gap`),
and they are reviewed. A bare, reasonless ignore is a defect. Prefer fixing the type over silencing the
checker.

### 13.5 Modern typing, gated by floor

Use the modern spellings the project's floor permits (§3.2): builtin generics (`list[str]`), PEP 604
unions (`X | None`), `Protocol` over `ABC` for structural ports, `typing.Self`, `Final` for constants,
`Literal` for closed string sets that are not full enums, and PEP 695 type parameters where they clarify.
Under `from __future__ import annotations`, the modern annotation spellings are available even at the 3.9
target-deployed floor.

---

## 14. Clean Code & Naming

### 14.1 Names say what, not how

Domain vocabulary in domain code (`recover`, `compute_blast_radius`, `Campaign`, `Phase`), not
implementation jargon. Functions are verbs, classes are nouns, booleans read as predicates
(`is_complete`, `has_cracked`). A name that needs a comment to explain what it refers to is the wrong
name.

### 14.2 Small, focused units

A function does one thing. A function that needs a paragraph to explain what it does, or that spans more
than roughly a screen, is doing too much and is split. A class that grows past a single responsibility is
split (§9). This is a guideline enforced by judgment, not a hard line count, but the `talus-auditor`
flags outliers.

### 14.3 Comments explain *why*, not *what*

The code says what it does; comments capture the reasoning, the trade-off, the non-obvious choice, the
citation for a borrowed algorithm. A comment that restates the code is noise. ADRs are the macro form of
this discipline. The cross-domain math that is the suite's moat is commented with its source.

### 14.4 The "avoid AI tells" style

Code and prose are **direct and economical.** No filler, no boilerplate-for-its-own-sake, no decorative
hedging, and em-dashes used sparingly in prose rather than as a reflex. Naming is precise rather than
verbose. Docstrings are substantive (what, why, contract), not ceremonial. The code should read as
written by a deliberate engineer, not generated from a template. This is an operator preference with
teeth: the `talus-auditor` flags AI-tell patterns, and this document is held to the same bar.

### 14.5 Module and file size

A module owns one concept; an entry script dispatches and nothing more. **A 4,800-line entry script is
the named anti-pattern**: command bodies, phase logic, and dispatch crammed into one file. The standard
going forward: the entry script is thin (§5.2), command bodies live in `modules/`, and a module that
crosses into a second responsibility is split. Size is a smell, not a crime; the underlying defect is
mixed responsibility, and that is what gets fixed.

### 14.6 Purity and side-effect placement

Prefer pure functions; push I/O, mutation, clock reads, and randomness to the edges (§12.4). A function
that computes *and* renders is split: the computation is testable domain code, the rendering goes through
the port.

---

## 15. Error Handling & Exceptions

### 15.1 Typed, specific exceptions

Domain errors are **typed exceptions** with clear semantics, organized under a small per-tool base
(`class MyToolError(Exception)`), so callers catch precisely. Raise the most specific exception that
fits; never raise bare `Exception` for a domain condition.

### 15.2 No bare except, no swallowed errors

**Rule (must).** No bare `except:` and no `except Exception: pass` that silently discards a failure. Catch
the specific exceptions you can handle; let the rest propagate. The one sanctioned narrow exception is a
genuinely optional, non-critical side effect (e.g. a best-effort cache write) — and even then it is
`except <SpecificError>:` with a logged `debug`/`warning`, never a bare swallow. The `talus-auditor`
flags bare and over-broad handlers.

### 15.3 Clean up with context managers

Resources (files, subprocesses, sockets, temp files, locks) are released deterministically via `with`
context managers or `try/finally`, including on the error and cancellation paths. A leaked subprocess or
temp file is a defect, especially for offensive tools where a left-behind artifact is an OpSec failure
(§25).

### 15.4 How errors surface, by tier

- **CLI (Tier 1/2):** an unhandled domain error becomes a clean message through the renderer (not a raw
  traceback) and a **non-zero exit code** (§19.3); `--debug` may surface the traceback. The error text is
  for a human operator.
- **Platform (Tier 3):** domain errors map to RFC 9457 problem-detail responses at the API boundary;
  internals never leak stack traces to a client.

### 15.5 Graceful cancellation

Long-running work (a cracking run, a scan) handles interruption deterministically: a signal handler sets
a stop flag, in-flight subprocesses are terminated gracefully (SIGTERM on POSIX, the console-ctrl event
on Windows), checkpoints are written, and resources are released.
Cancellation is a designed path, not an afterthought; it is tested.

---

## 16. Logging & Observability

Logging is the *first* of the three observability signals. Metrics, traces, SLIs/SLOs, health checks, and
the reliability patterns (for a Tier-2 service or a Tier-3 platform) are the **Observability & Reliability
Standard**; this section is the Python logging discipline its telemetry builds on, plus the audit-trail
rule that stays distinct from telemetry (§16.5). Sensitive captured values never travel through logging at
all — they go to the reporters under the differential-reveal rule (§25.3).

### 16.1 The two-stream configuration

**Rule.** Configure `logging` so the **console is quiet and the file is complete.** The console handler
is **WARNING and above** with a clean, timestamp-free format; a **per-run file handler** captures
**INFO** (and below as needed) with timestamps for the full record. it is the house pattern:

```python
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(logging.Formatter("  %(levelname)s: %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[console])
# then, per run/campaign, attach a FileHandler at INFO to <run>/<tool>.log (timestamped)
```

The full diagnostic detail (e.g. the exact external command, with arguments, for reproducibility) goes to
the **file**, not the console. The operator's screen stays signal; the disk record stays complete.

### 16.2 Named loggers, never the root in library code

Each module uses `logger = logging.getLogger(__name__)`. Libraries (Tier 1) **never** call `basicConfig`
or attach handlers to the root logger; configuration is the *application's* job. A library that configures
logging hijacks its host. Tier 2/3 applications own the configuration at their entry point.

### 16.3 Diagnostics go through the renderer, not `print()`

User-facing output is a presentation concern and goes through the port (§18), not `print()` and not the
logging console. `logging` is for the diagnostic record; the renderer is for what the operator sees. Mixing
them is what produced the "raw `HH:MM:SS INFO CMD:` line bleeding into styled output" defect that the
two-stream config and the renderer's dim "command" line fixed.

### 16.4 Never leak raw external-tool output

Raw stdout/stderr from an external binary (`hashcat`, `nmap`) is classified through an inbound adapter
(§10.1) into typed events before it reaches the operator; unrecognized lines are dropped as noise, not
echoed. An allow-list of "interesting" raw lines is the inferior pattern (it leaks the unexpected); the
classifier is the standard.

### 16.5 Audit logging is immutable (OpSec)

For tools that take consequential actions, the **audit trail is append-only and tamper-evident** (§25):
who/what/when/scope for every approved action. This is a security-doctrine requirement, separate from
diagnostic logging, and it is never routed through the same mutable file.

---

## 17. Filesystem & I/O

### 17.1 `pathlib` is the default

**Rule (should, strongly).** New code uses `pathlib.Path` for path construction, joining, and queries,
not `os.path` string manipulation. Paths are `Path` objects through the code and stringified only at the
boundary that demands a string. `os.path` is legacy; it is permitted only with a specific justification
(the most common legitimate one being symlink-resolution edge cases or a hot loop where the `Path`
overhead is measured to matter), and that justification is noted. Legacy `os.path` is acceptable in place but not the model for new code or new modules.

### 17.2 Encodings are explicit

**Rule (must).** Every text `open()` / `Path.read_text()` / `write_text()` specifies `encoding=` (almost
always `"utf-8"`). Relying on the platform default encoding is a cross-platform defect. Binary data uses
binary mode explicitly.

### 17.3 Temp-file and artifact hygiene

Temporary files and FIFOs are created via `tempfile`, scoped with context managers, and removed on every
exit path including errors and cancellation (§15.3). For offensive tools, a leaked artifact on disk is an
OpSec failure; cleanup is mandatory and tested. Generated outputs and caches live under a single,
git-ignored root, never intermixed with source (§5.4).

### 17.4 Cross-platform interoperability

This is the Python expression of the umbrella's **Cross-platform by default** principle (TALUS §3.1):
**Tier 1 libraries and Tier 2 standalone apps target macOS, Linux, and Windows from the outset**, and
prove it by running on all three. (Tier 3 platforms ship as containers and set their own base-OS target;
they are exempt from the three-OS default.) A genuinely platform-bound tool is allowed, but it **declares**
its supported platforms and the reason in its `pyproject.toml` (classifiers) and README — a restriction is
a documented decision, never an accident.

**Isolate platform differences behind a thin adapter.** Per-OS behavior lives in *one* place — a small
`platform`/`paths` module (or a ports-&-adapters seam, §10) — never scattered as `sys.platform` /
`os.name` branches through the codebase. Scattered platform checks across a large module are the
anti-pattern: they make every OS a separate, untested reality.

### 17.5 The platform-difference rules

The concrete differences a portable Python tool handles, all behind the §17.4 adapter:

- **Paths & scratch locations.** `pathlib` for all path work (§17.1); `os.sep`/`os.pathsep` awareness;
  never hard-code separators or drive letters. Per-OS application and scratch locations are resolved, not
  assumed: app data (`%LOCALAPPDATA%` on Windows, `$XDG_*`/`~/.config`/`~/.cache` on Linux, `~/Library` on
  macOS) and fast scratch (`/dev/shm` on Linux, a temp dir or RAM-disk path on Windows). Each has one
  definition site (§5.4).
- **Executable & tool resolution.** Resolve external binaries with `shutil.which` (it honors `PATHEXT` on
  Windows); account for `.exe`/`.bat` vs an extensionless or `.bin` name. Never assume a POSIX path layout.
- **POSIX-only module guards.** `fcntl`, `termios`, `pwd`, `grp`, `os.fork`, and friends do not exist on
  Windows. Guard the import (`try: import fcntl / except ImportError:`) and provide a Windows fallback, or
  gate the code path on the platform behind the adapter.
- **Subprocess & signals.** Signal handling differs: `SIGTERM`/`SIGINT` on POSIX vs `CTRL_BREAK_EVENT`
  with `CREATE_NEW_PROCESS_GROUP` (and the lack of most POSIX signals) on Windows. Graceful cancellation
  (§15.5) and subprocess supervision (§20) account for both; subprocess args are always lists, never a
  shell string (§20).
- **Encodings & newlines.** `encoding=` is always explicit (§17.2). For format-sensitive text files,
  control line endings with `newline=` rather than assuming `\n`; do not let the platform default rewrite
  bytes.
- **Terminal differences.** Color-capability detection and the plain-text fallback (§18) already cover
  Windows terminal differences (VT processing, `NO_COLOR`/TTY); rendering stays in the adapter.

**Testing (§22).** A project that declares multiple platforms runs its test suite on each via a CI OS
matrix; platform-specific tests are explicitly marked/skipped (e.g. `@pytest.mark.skipif(sys.platform ==
"win32", …)`), never silently absent. "It works on my machine" is not cross-platform support.

---

## 18. Terminal Output & Color Discipline

Terminal output is a presentation concern routed entirely through the renderer port (§10). This section is
the color-and-rendering law; it codifies a presentation subsystem as the standard.

### 18.1 All output goes through the port

**Rule (must).** Domain and use-case code never calls `print()` for user-facing output and never emits an
escape code; it calls the renderer (`renderer.section(...)`, `.table(...)`, `.detail(...)`, the live
region). `print()` survives only inside the console adapter itself. This is what makes a TUI/web frontend
a drop-in (§10.4) and what guarantees the file-safety below.

### 18.2 Graceful color degradation

The adapter detects terminal capability and degrades **truecolor → 256-color → 16-color → plain**, so the
same view-models render correctly on a 24-bit terminal, a basic TTY, and a dumb pipe. Color logic
(palettes, gradients, RGB down-conversion) lives only in the adapter's theme module; it never appears in
the domain or the port.

### 18.3 Color is gated; files and pipes are always plain

**Rule (must).** Color is emitted only to an interactive terminal. The gate honors, in order: an explicit
`--color {auto,always,never}` flag, the `NO_COLOR` and `FORCE_COLOR` environment conventions, and TTY
detection (`isatty`). When output is redirected to a file or pipe, or `--color never` is set, **zero ANSI
is emitted** — reports, logs, and piped output are byte-for-byte plain. This is verifiable. A report file with color codes in it is a
defect.

### 18.4 Layout math is ANSI-aware

Width, alignment, and truncation are computed on the **visible** length of a string (escape codes
stripped), and painting is applied after layout, never sliced through. Truncating a string mid-escape (the
`name…[0m` leak) is the classic bug; measure plain, paint whole.

### 18.5 The live region

In-place streaming status (a progress block that redraws each tick) is a `LiveRegion` off the port: the
domain pushes a `RunState` view-model and one-off classified events; the adapter handles cursor control
and redraw. The domain makes no cursor calls and no rendering decisions.

---

## 19. CLI Conventions

### 19.1 Structure

CLI tools use `argparse` with subcommands, one function per command, command bodies in modules (§5.2/§8.3).
Group related subcommands in help output so a multi-command
tool stays navigable.

### 19.2 Consistent global flags

Every CLI offers a consistent core: `--color {auto,always,never}` (§18.3), `--version`, `--help`, and
where applicable `--dry-run` (print the planned action, take none) and `--debug` (surface tracebacks /
verbose diagnostics). Flags are uniform across tools so muscle memory transfers.

### 19.3 Exit codes

**Rule.** `0` on success, non-zero on failure, with documented, distinct codes for distinct failure
classes where a caller would branch on them. A CLI is a composable Unix citizen; a tool that exits `0` on
failure breaks every script that wraps it.

### 19.4 Configuration precedence

Resolution is uniform and explicit: **command-line flag > environment variable > config file > built-in
default** (§11.3). Config is loaded once into the typed settings object; the precedence is implemented in
one place, not rediscovered per option.

### 19.5 Output is for humans and machines

Human output goes through the renderer (§18). Where a command is meant to feed a pipeline, it offers a
machine-readable mode (e.g. `--json`) that emits the same view-models through a JSON adapter (§10.4) — not
a separately-maintained print path. The ingestion-envelope emit (Principle 6) is the canonical
machine-output contract for data-producing tools.

### 19.6 The parser is a testable function

Build the argument parser in a **pure function that returns it**, separate from `main`, and have `main`
accept `argv`. Then parsing is unit-tested without running a command or touching the world:

```python
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mytool")
    p.add_argument("--color", choices=("auto", "always", "never"), default="auto")
    sub = p.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan")
    scan.add_argument("target")
    return p

def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)      # argv=None → sys.argv; a list in tests
    ...
    return 0
```

```python
def test_scan_requires_target() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["scan"])     # parsing asserted; no command runs

def test_color_default() -> None:
    assert build_parser().parse_args(["scan", "h"]).color == "auto"
```

Defaults, choices, mutually-exclusive groups, and subcommand wiring are covered as cheap, fast unit tests
(§22); `main(argv)` taking an explicit list is what makes an end-to-end CLI test possible without
subprocessing. A parser built inline inside `main` cannot be tested this way and is the anti-pattern.

# Part V — Concurrency & Performance

Two questions engineers get wrong by reflex: "which concurrency primitive?" and "should I drop to C?".
Both have disciplined answers. The first is a decision matrix keyed to the *kind* of work; the second is
a profile-first ladder where native code is the last rung, not the first.

## 20. Concurrency Model

### 20.1 Pick the primitive by the kind of work

| Workload | Primitive | When | Suite example |
|---|---|---|---|
| **I/O-bound, modest concurrency; supervising subprocesses** | **`threading`** (+ `queue`, `subprocess`) | Driving and monitoring external binaries, bounded producer/consumer feeds, blocking I/O where a handful of threads suffice. | A subprocess-driver: a producer thread fills a bounded queue of candidates, a consumer spools them to an external binary, a status thread polls — coordinated by `Event`/`Queue`. |
| **I/O-bound, high concurrency; network services** | **`asyncio`** | Thousands of concurrent connections, async web frameworks, fan-out network calls. No blocking calls on the event loop; CPU work is offloaded. | a web service's FastAPI request path; async DB driver. |
| **CPU-bound parallelism (today)** | **`multiprocessing`** / `concurrent.futures.ProcessPoolExecutor` | Saturating multiple cores for pure-Python compute while the GIL still binds threads. | Heavy analytical-core batch compute offloaded to workers. |
| **CPU-bound, single hot kernel** | **native acceleration** (§21) | One measured hot loop dominates; parallelism alone is insufficient. | a Markov-enumeration hot loop. |

**Rule.** Choose the primitive from this table, deliberately, and record the reason in a comment at the
concurrency seam. Do not default to threads for CPU work (the GIL serializes them); do not reach for
`asyncio` for a tool that supervises one subprocess (threads are simpler and correct there). Mixing models
(async + threads + processes) is sometimes right but always justified explicitly.

### 20.2 Subprocess standards

Most Ashwood tools orchestrate external binaries; this is where concurrency bugs and OpSec failures live.

- **Arguments are always a list, never a shell string.** `subprocess.run([bin, "-m", str(mode), ...])`,
  never `shell=True` with interpolated input. `shell=True` with any untrusted or constructed value is a
  command-injection defect (§25) and is gated.
- **Every external call has a timeout** and a defined behavior on timeout.
- **Cancellation is graceful** (§15.5): terminate the child cleanly (SIGTERM / console-ctrl event), let it
  checkpoint where it supports it, then reap it; never leak a child process.
- **Capture is classified, not echoed** (§16.4): stdout/stderr go through an inbound adapter into typed
  events.

### 20.3 Thread-safety discipline

Shared mutable state across threads is guarded (locks, or better, confined to a single owner thread and
communicated via `queue.Queue`). Prefer message-passing over shared memory: the producer/consumer-over-a-
bounded-queue pattern is the house model precisely because it confines mutation. Module-level mutable
globals used for cross-thread coordination (a stop flag, a runner reference) are the documented exception,
kept minimal and clearly marked.

### 20.4 The GIL and free-threading: architect for it, do not depend on it yet

The GIL serializes Python bytecode across threads, which is why CPU-bound parallelism uses processes
today. Free-threaded CPython (PEP 703) changes this, and its status as of 2026 is specific:

> #### ADR-PY-003 — Free-threading posture: architect-for, do not depend on (yet)
> **Status:** Accepted (revisit per trigger).
> **Context.** PEP 703 introduced a free-threaded (no-GIL) CPython build. Timeline: **3.13** (Oct 2024)
> shipped it as **experimental**; **3.14**, via **PEP 779**, moved it to **officially supported but still
> optional and not the default build**; the project's own roadmap targets making it non-experimental and
> eventually default across subsequent releases (the 2026–2027 window). Real caveats remain: a single-
> threaded performance penalty (roughly 5–10%), and many C extensions still need updates to run correctly
> under the free-threaded build.
> **Decision.** **Do not require the free-threaded build** for any suite tool now. **Do** write
> thread-safe, share-nothing concurrency (§20.3) so the suite benefits automatically as free-threading
> matures: confine mutation, pass messages, avoid relying on the GIL as an implicit lock. Treat "the GIL
> makes this atomic" as a latent bug, not a guarantee.
> **Alternatives considered.** *Adopt free-threaded builds now for CPU parallelism* — rejected: optional/
> non-default build, ecosystem (C-extension) gaps, single-thread penalty. *Ignore it* — rejected: writing
> GIL-dependent code now creates a migration debt exactly when the platform shifts.
> **Consequences.** CPU parallelism uses `multiprocessing` today (§20.1). Code is written to be correct
> *without* the GIL's implicit serialization. **Trigger to revisit:** the free-threaded build becomes the
> default/non-experimental and the suite's C-dependency set supports it; at that point threads become a
> viable CPU-parallelism option and this ADR is superseded.

---

## 21. Performance & When to Go Native

### 21.1 Profile first — always

**Rule (must).** No optimization without a measurement. Before changing code for speed, profile
(`cProfile` for call-level, `py-spy` for a sampling view of a running process, `scalene` for CPU+memory
with line granularity) and identify the actual hot path. "I think this is slow" is not a license to
complicate code; a profile is. Most perceived slowness is an algorithm or an accidental O(n²), not a
language-speed problem, and is fixed at the top of the ladder below for free.

### 21.2 The optimization ladder

Climb from the top. Each rung is more powerful and more costly (in complexity, build, and the cost of
crossing the Python↔native boundary). Stop at the first rung that meets the measured target.

```
1. Better algorithm / data structure        ← almost always the real win; no new deps, no new risk
2. Idiomatic Python + stdlib                 ← comprehensions, generators, sets/dicts, itertools,
                                                functools.lru_cache, the right builtin
3. Vectorize with NumPy                      ← array/numeric batch work; move the loop into C-backed ops
4. JIT with Numba (@njit)                    ← numeric hot loops on arrays; minimal code change,
                                                first-call compile cost; great for self-contained kernels
5. Compile typed Python with mypyc           ← compile existing type-annotated pure-Python modules to a
                                                C extension; little/no code change; still maturing
6. Cython                                    ← hand-optimized C-level loops, fine control, C/C++ interop;
                                                a build step and a new language surface
7. C / C++ / Rust extension                  ← cffi (wrap C), pybind11 / nanobind (C++), PyO3/maturin
   (the last resort)                           (Rust); maximum control and speed, maximum build + maintenance cost
```

### 21.3 Choosing a native rung

| Tool | Use when | Avoid when | Notes |
|---|---|---|---|
| **NumPy** | The hot work is numeric/array batch math. | The data is irregular/object-shaped (copy cost dominates). | Often the whole answer; no compiler. |
| **Numba** | A self-contained numeric loop over arrays; you want a quick win with minimal change. | The hot path touches rich Python objects or arbitrary stdlib; you need a shippable wheel with no JIT warmup. | First-call compile cost; pin the version. |
| **mypyc** | You already have strictly typed pure-Python modules and want a transparent C-extension speedup. | You rely on dynamic features mypyc does not support; the toolchain's maturity is a project risk you cannot accept. | Pairs naturally with this standard's full-typing mandate. |
| **Cython** | A recursive/complex kernel needs hand C-level control, or you must integrate with C. | NumPy/Numba already meet the target; the build complexity is not justified. | Mature; the right tool for serious, structured speedups. |
| **C / C++ / Rust** | A single hot kernel dominates and nothing above suffices; or you must bind an existing native library. | You have not exhausted the rungs above; the maintenance and build-matrix cost outweighs the gain. | cffi for C, pybind11/nanobind for C++, PyO3/maturin for Rust. |

The recurring tax at every native rung is **the boundary-crossing cost**: marshalling data between Python
objects and native structures has real overhead, so a native kernel pays off only when the work *inside*
the boundary dominates the cost of crossing it. A "fast" C function called a million times in a Python
loop can be slower than staying in NumPy.

### 21.4 Keep native code behind a clean, optional seam

When a native rung is justified, isolate it:

- **Behind a Python interface**, so callers depend on the function, not its implementation (ports &
  adapters again). The pure-Python fallback stays available and is what tests target by default.
- **Optional where possible.** The model is a **pure-Python, zero-dependency** runtime wheel with a
  *separate, optional* native accelerator for the one hot loop. The tool is fully functional without it; the native build accelerates a measured
  bottleneck for those who build it. This keeps Tier 1 installability and the target-host dependency budget
  (§7.2) intact while still offering the speedup.
- **Build it correctly:** an *integrated* compiled extension moves the project to the setuptools/maturin
  backend (§6.2) and adds a build matrix; weigh that cost in the decision.

### 21.5 The standalone-tool default

Tier 2 and target-deployed tools stay **pure Python unless a profile justifies otherwise.** Their value
is portability and a zero/low dependency budget; trading that for speed is a decision made against a
measurement, not a hunch. The native-acceleration decision flowchart is in **Appendix D**.

# Part VI — Quality, Testing & Tooling

Standards that are not mechanically enforced decay into reviewer memory and then into nothing. This part
makes the standard real: a test discipline, a single canonical toolchain, and **blocking CI gates** so the
conforming path is the only path CI permits.

## 22. Testing Strategy

### 22.1 pytest, mirroring the package

**Rule (must).** Tests use **pytest**, live in `tests/`, and mirror the package one test module per source
module (§5.4). Every tier has tests; "no tests" is a gap closed
going forward (§22.6), not a property of standalone tools.

### 22.2 The test pyramid

- **Unit tests** dominate: pure domain logic and the analytical core, tested in isolation with **fakes for
  the ports** (an in-memory repository, a recording renderer, a stub runner). The ports-and-adapters seam
  (§10) and dependency injection (§8.4) are what make this fast and database-free.
- **Integration tests** exercise the adapters against the real edge (a real DB in a container for Tier 3; a
  real, sandboxed external binary or a recorded fixture for a subprocess-driven tool).
- **End-to-end tests** cover the critical user paths sparingly.

### 22.3 Golden-file / byte-stability tests for reproducible outputs

Anything that must be reproducible (a rendered report, a generated `pyproject`, an ingestion envelope) has
a **golden-file test asserting byte-stability** for fixed inputs (Principle 7). This is how reproducibility
stops being an aspiration. The presentation file-safety checks (no ANSI in piped/`report` output, §18.3)
are golden-style assertions and are required.

### 22.4 Property-based tests for the analytical core

The cross-domain math (the moat) is **deterministic and pure**, which makes it ideal for property-based
testing with **Hypothesis**: assert invariants (a score stays in range, a transform round-trips, an
ordering is total) across generated inputs, not just hand-picked cases. The analytical core carries the
highest test bar in the suite.

### 22.5 Coverage gates, weighted by layer

Coverage is a **blocking gate** (§23) with the bar set highest where risk is highest: the **analytical core
and the service/use-case layer** carry the strictest thresholds; thin glue (adapters, CLI dispatch) is
held to a lower but real bar. Coverage is a floor, not a goal — 100% coverage of trivial code is not
quality — but an untested service method does not merge.

### 22.6 Fixtures and sample data

Realistic fixtures live under `samples/` / `tests/fixtures/` so integration tests run against representative input. Sensitive sample data is synthetic or
sanitized; never commit real client material.

---

## 23. Canonical Toolchain & Quality Gates

This section defines the Python gate *tools*; *when* they run (PR vs merge vs release) and how releases are
cut is the **Git & Release Engineering Standard**.

### 23.1 The one toolchain

**Rule (must).** Every project uses this toolchain, configured in `pyproject.toml`, run identically
locally (pre-commit) and in CI:

| Concern | Tool | Gate |
|---|---|---|
| Lint + format | **`ruff`** (lint and formatter) | non-conforming code fails CI |
| Type check | **Pyright (strict)** (§13.2) | type errors fail CI |
| Tests + coverage | **`pytest`** (+ coverage) | failing tests or sub-threshold coverage fails CI |
| Env / deps / lock | **`uv`** | reproducible install from lock |
| Architecture conformance | **import-linter** | a forbidden cross-layer import fails CI |
| Secret scanning | a secret scanner (e.g. `gitleaks`/`detect-secrets`) | a credential-shaped string fails CI |
| Dependency vulnerabilities | an audit tool (e.g. `pip-audit`) | known-vulnerable deps flagged |
| Injection lint (where SQL/Cypher present) | the project's injection rule | raw-string SQL / non-parameterized Cypher fails CI |

There is one canonical config block (Appendix B); a project copies it and adjusts only `requires-python`/
`target-version` to its floor. The mechanical message of this table: **the secure, typed, formatted,
architecturally-conformant path is the only path CI permits.**

The machine-readable mirror of this gate set is **`gates.toml`** (at the standards root), executed by the
data-driven **`scripts/run-gates.py`**, which runs exactly the gates a project's language standard declares
(no hardcoded toolchain), so the review and CI run the same set. This table is the rationale; the manifest is
the executable form. Keep the two in sync (a future enhancement may generate one from the other).

### 23.2 `ruff` configuration

`ruff` is both linter and formatter (no separate `black`/`isort`/`flake8`). A sensible default rule set —
`E`, `F`, `I` (import sorting), `B` (bugbear), `UP` (pyupgrade), `SIM`, `RUF`,
with `line-length` and `target-version` set to the project's floor. The formatter is authoritative;
formatting is never argued in review.

### 23.3 Architecture is enforced, not just documented

**import-linter** encodes the layer rules of §8: the API/CLI layer may not import a repository
implementation, the domain may not import a framework or an adapter, the analytical core imports nothing
of the application. A dependency arrow pointing the wrong way (§8.1) is caught by a tool, not left to a
reviewer's vigilance.

### 23.4 pre-commit and CI parity

The same checks run in a **pre-commit** hook locally and in the CI pipeline, so failures are caught before
push and the pipeline holds the line. CI runs the matrix against the project's declared floor(s) (§3.1).
No green-locally/red-in-CI drift: the configs are shared.

### 23.5 Gates are blocking

Per the operator's chosen posture, these are **blocking** gates: a failing gate blocks merge. The
migration path for existing non-conforming tools is incremental adoption with a
documented, time-boxed runway (§26.3), not a permanent exemption.

---

## 24. Documentation & Comments

### 24.1 Docstrings

**Rule.** Every public module, class, and function has a **Google-style docstring** stating what it does,
its contract (args, returns, raised exceptions), and any non-obvious *why*. Docstrings are
substantive, not ceremonial (§14.4); a docstring that restates the signature adds nothing.

### 24.2 The per-tool `Architecture/` suite

Each non-trivial tool carries an `Architecture/` documentation suite to the gold standard set by the
**Documentation & Architecting Standard** (its baseline `00`–`08`): vision, technology-decision ADRs, data model, algorithm core, integration
contracts, security/OpSec, code standards (which *reference this document* rather than restating it), and
roadmap. `talus-scribe` authors these; this coding standard is the upstream they inherit.

### 24.3 ADRs for significant decisions

Significant technology and design choices are recorded as **ADRs** (Status / Context / Decision /
Alternatives / Consequences), immutable once accepted, superseded by new ADRs rather than edited. This
document uses that format for its own contested calls (ADR-PY-001/002/003) and is the model.

### 24.4 READMEs

Every project has a README that states what the tool is, its tier and Python floor (§3/§4), how to install/
run it, and how to develop against it (the toolchain of §23). A new contributor becomes productive from
the README plus this standard.

---

## 25. Security & OpSec Coding Standards

Security and operational security are design properties (Principle 5), enforced in code and CI. The full,
language-agnostic model is the **Security & OpSec Standard**; this section is its Python expression.

### 25.1 Input, queries, and output

- **Parameterized queries only.** No string-built SQL; no non-parameterized AGE/Cypher. Dynamic
  identifiers are allow-list-validated. The injection lint (§23.1) enforces this.
- **Validate untrusted input at the boundary.** Everything crossing into the system (HTTP requests,
  ingested envelopes, file contents, external-tool output, CLI arguments) is validated/parsed at the edge
  (Pydantic at trust boundaries, §12.3) before reaching the domain.
- **Encode output** for its sink (HTML/terminal/file) to close injection and rendering attacks.

### 25.2 Subprocess and command safety

No `shell=True` with constructed or untrusted input; arguments are lists (§20.2). External-binary
invocation is the most common injection surface in the orchestrator tools and is reviewed and gated.

### 25.3 Secrets

**Secrets never appear in source or committed config.** They come from the environment or a secret store,
loaded through the typed settings layer (§11.3/§11.5). The secret scanner (§23.1) blocks credential-shaped
strings at commit and in CI.

**Differential reveal — and captured secrets never traverse logging.** For a tool that *handles* sensitive
values (captured credentials, tokens, secret material), the default representation is **masked**; the full
value is revealed only to a deliberate, secured sink — a `0600` file, an explicit `--reveal` flag — never
the console or a shared log by default. Captured secrets do **not** go through the logging system at all:
logging is for diagnostics (§16), and a value object carrying a secret routes to the **reporters** (§10.6),
which mask unless explicitly told to reveal:

```python
@dataclass(frozen=True)
class Credential:
    user: str
    _secret: str
    def summary(self, *, reveal: bool = False) -> str:
        return f"{self.user}:{self._secret if reveal else '********'}"   # masked by default
```

So reconfiguring or silencing logging can never leak — or lose — a secret. This is the Python expression of
the **Security & OpSec Standard §4** differential-reveal rule.

### 25.4 Scope gating, action approval, immutable audit

For tools that take consequential action (the offensive sub-suite):

- **Scope gating** — an action against an out-of-scope target is refused by construction, not by operator
  discipline.
- **Action approval** — nothing is autonomous; the math decides *order and timing*, a human approves each
  action (suite doctrine §0).
- **Immutable audit** — every approved action is recorded append-only and tamper-evident (§16.5):
  who, what, when, against what scope.

### 25.5 OpSec hygiene in code

- **No artifact left behind.** Temp files, FIFOs, and caches are cleaned on every exit path (§17.3); a
  leaked artifact on a target is an OpSec failure.
- **Mind what reaches disk and the wire.** Diagnostic detail goes to the operator's controlled log, not to
  anything observable on the target.
- **Supply-chain hygiene** — pinned, hash-verified, vulnerability-scanned dependencies (§7.3); the tool's
  own integrity is part of its OpSec.

### 25.6 Authorized use

These tools are built for sanctioned engagements under written scope and rules of engagement. The code's
guardrails (scope gating, approval, audit) encode that authorization model; weakening them to "make
testing easier" is never an acceptable trade.

# Part VII — Governance

A standard needs a clear story for how new code adopts it, how existing code migrates to it, how
exceptions are granted, and how it itself evolves. Without that, it is either ignored or applied with a
rigidity that breaks shipping.

## 26. Adoption, Exceptions & Enforcement

### 26.1 New code adopts in full

Any new project, and any new module in an existing project, conforms to this standard from the first
commit: `pyproject.toml`, the toolchain (§23), full typing (§13), tests (§22), the architectural shape for
its tier (§8). There is no runway for greenfield code; the conforming path is the cheap path.

### 26.2 Two enforcement arms

The standard is enforced by two complementary mechanisms:

- **Blocking CI gates (mechanical, §23)** catch what is mechanically checkable: formatting, lint, types,
  coverage, layer-import violations, secrets, vulnerable deps.
- **The `talus-auditor` agent (judgment, §26.5)** catches what a linter cannot: tier-appropriateness,
  layering and ports-and-adapters conformance, SOLID/extension-by-addition, "everything is a variable,"
  concurrency-primitive choice, native-acceleration justification, error/logging/color discipline,
  docstring substance, and the AI-tell style.

Mechanical where possible, judgment where necessary; together they make the standard real rather than
aspirational.

### 26.3 Existing tools migrate incrementally

A tool that is non-conforming today may lack packaging and tests, run a monolithic entry with `os.path`,
and have no type gate. Such tools migrate on a **documented, time-boxed runway**, not in a single rewrite and not via a
permanent exemption. The recommended order, lowest-risk first:

1. Add `pyproject.toml` with the toolchain config (§23) and the project's floor; get `ruff format` clean.
2. Stand up `tests/` mirroring `modules/`; cover the domain (analyzer, speed, phases) first.
3. Turn on Pyright; annotate to strict incrementally, module by module.
4. Extract command bodies from the entry script into `modules/` use-case functions (§5.2/§14.5).
5. New modules use `pathlib`; convert `os.path` opportunistically, not in a risky big-bang.
6. Promote genuinely shared code across sibling apps to a Tier 1 library (§4.2) to end file-copy reuse.

The runway is tracked per tool (its `Architecture/08`/README), and the `talus-auditor` reports remaining
gaps so progress is visible.

### 26.4 Exceptions

A `must` is a gate; deviating from it requires a suite-level decision (a new ADR). A `should` may be
deviated from with a **logged, justified, ideally time-boxed** exception: a comment at the site citing the
`§` and the reason, or an entry in the tool's ADR log. An undocumented deviation is a defect. Legitimate
exceptions exist (a measured `os.path` hot path, a target-host floor below 3.11, a second type checker for
library compatibility); they are *recorded*, not hidden.

### 26.5 The `talus-auditor` agent

This standard ships with a review-time conformance agent, `talus-auditor` (a Talus project subagent
alongside `researcher`/`architect`/`scribe`/`cartographer`/`chronicler`). It reads this document as its
source of truth, consumes the mechanical gate verdict (run by the `talus-gates` skill or CI), applies the
judgment checks of §26.2, and emits a
**decomposable conformance report**: per-`§` pass / warn / fail, each finding with a `file:line` citation,
the `§` it violates, and a prioritized remediation. It is **advisory and recommend-only** — it never edits
code; the practitioner approves and applies fixes (suite doctrine §0). It is design-complementary to
`talus-architect` (design-time) and distinct from `talus-cartographer` (cross-tool *contracts*, not
per-tool code).

### 26.6 Evolution of the standard

This document is **versioned**. A change is proposed as an ADR (the `ADR-PY-NNN` series), reviewed at suite
level, and on acceptance bumps the document version and is announced to every tool. Breaking changes to a
Tier 1 public API contract or to a cross-tool contract are registered with `talus-cartographer`. The
standard is a living contract, changed deliberately and traceably, never by silent drift.

---

## 27. Decision Summary Table

| Decision | Choice | Key rejected alternative |
|---|---|---|
| Document location/scope | Suite-wide `Standards/` doc; single source of truth | Per-tool standards (drift); a platform-only code-standards doc (too narrow) |
| Enforcement posture | Mandates + **blocking** CI gates + judgment agent | Advisory gates; guidance-only |
| Python floors (ADR-PY-001) | Operator-side **3.12+**; target-deployed **3.9** floor (justify < 3.11) | 3.12+ everywhere (breaks targets); 3.9 everywhere (taxes operator-side) |
| Type checker (ADR-PY-002) | **Pyright (strict)** | `mypy --strict` (slower); `ty` (beta) |
| Lint + format | **`ruff`** (lint + format) | black + isort + flake8 (three tools) |
| Tests | **pytest** + coverage; Hypothesis for the core | unittest; no tests (the current gap) |
| Packaging config | **`pyproject.toml`** only (PEP 621/735) | setup.py / setup.cfg / requirements.txt as truth |
| Build backend | **Hatchling** default; **setuptools** for compiled extensions | Poetry/PDM backends as default |
| Workflow tool | **`uv`** (env/lock/run) | pip + venv + pip-tools by hand |
| Distribution tiers | Library / Standalone app / Platform, chosen by §4.2 | One-size packaging |
| Project layout | Tier 1 `src/`; Tier 2 flat `modules/`; Tier 3 layered | Monolithic entry script |
| Architecture | Layered, dependencies inward; ports & adapters | Logic in the entry script / framework-coupled domain |
| Type modeling | dataclasses; `Protocol` ports; Pydantic only at boundaries | Pydantic everywhere; hand-written `__init__` |
| Paths | **`pathlib`** default | `os.path` strings (legacy) |
| Output | Renderer port; color gated; never ANSI to files | bare `print()` + inline escape codes |
| Concurrency | Primitive by workload (threads/asyncio/processes) | Threads for CPU work; asyncio for one subprocess |
| Free-threading (ADR-PY-003) | Architect-for, do not depend on yet | Require no-GIL build now; ignore it |
| Going native | Profile first; climb the ladder; native last, behind a seam | Reaching for C before measuring |

---

## 28. Why This Standard Is Right

A suite that intends to be built and maintained by a team, across a decade-long naming theme and an
open-ended roster of tools, lives or dies on two properties: **maintainability** and **growth by
addition.** Every rule here serves one or both.

The layered architecture and ports-and-adapters seam keep the domain stable while the volatile edges churn,
which is what lets a CLI tool grow a TUI or a web API without a rewrite and lets a platform swap a datastore
without touching its services. SOLID — especially open/closed — means the suite grows by adding plugins,
connectors, renderers, strategies, and analytical modules rather than by editing an ever-branching core,
which is exactly the growth the Tier-2-open-set thesis requires. Full typing, the repository pattern, and
dependency injection make the system testable without its heavy edges, and the test discipline makes the
determinism and reproducibility the suite promises actually checkable. The packaging tiers let a password-
modeling library, a run-in-place orchestrator, and a reporting platform each be shipped correctly for what
it is, instead of forcing one shape on all three. The profile-first performance ladder keeps the code
simple until a measurement says otherwise, and keeps native code optional and contained when a measurement
does. The security and OpSec rules encode the authorization model these tools exist to honor.

And the mechanical gates plus the conformance agent make the whole thing real: the secure path, the typed
path, the architecturally-conformant path, and the well-shipped path are the only paths the suite permits.
Clean code here is not an aesthetic preference. It is the precondition for the suite shipping, growing, and
surviving the people who did not write it.

# Appendices

## Appendix A — `pyproject.toml` templates

### A.1 Tier 1 — library / installable CLI (`src/` layout, Hatchling)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "example-tool"
version = "0.1.0"                       # SemVer (§6.3); a public-API break is a major bump
description = "One-line description of the tool."
readme = "README.md"
requires-python = ">=3.12"              # operator-side floor (§3.1); a target-deployed lib uses ">=3.9"
license = { file = "LICENSE" }
authors = [{ name = "Talus" }]
keywords = ["security"]
classifiers = [
    "Programming Language :: Python :: 3",
    "Topic :: Security",
    "Intended Audience :: Information Technology",
    "Typing :: Typed",                 # ships py.typed (§13.3)
]
dependencies = []                       # stdlib-first (§7.1); add only what is justified

[project.optional-dependencies]
benchmark = ["matplotlib>=3.7"]         # feature extra keeps the runtime lean (§6.4)

[project.scripts]
example = "example.cli:main"            # console-script entry point (§6.6)

[dependency-groups]                     # PEP 735 dev tooling — NOT shipped in the wheel
dev = ["pytest>=8", "pyright>=1.1.390", "ruff>=0.6", "hypothesis>=6", "pip-audit>=2", "import-linter>=2"]

[tool.hatch.build.targets.wheel]
packages = ["src/example"]              # src-layout; py.typed inside the package is included automatically

# Tool configuration: see Appendix B (the shared canonical block).
```

### A.2 Tier 3 — platform / service (layered package + analytical core)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "myservice"
version = "0.1.0"
description = "Reporting & consolidation platform."
readme = "README.md"
requires-python = ">=3.12"
license = { file = "LICENSE" }
dependencies = [                        # applications PIN for a reproducible deploy (§7.3)
    "fastapi>=0.111,<0.112",
    "sqlalchemy[asyncio]>=2.0,<2.1",
    "pydantic>=2.7,<3",
    "celery>=5.4,<6",
]

[dependency-groups]
dev = ["pytest>=8", "pyright>=1.1.390", "ruff>=0.6", "hypothesis>=6", "pip-audit>=2", "import-linter>=2"]

[tool.hatch.build.targets.wheel]
packages = ["src/myservice"]
# The analytical core (myservice_core) is a sibling package with its own pyproject and
# `dependencies = []` (ADR-007): it depends on nothing and is testable in isolation.

# Tool configuration: see Appendix B. The container image bakes an exact, validated
# dependency set from uv.lock (§6.7).
```

---

## Appendix B — Canonical tool-config block

Copy verbatim into any project's `pyproject.toml`; adjust only `target-version` / `pythonVersion` to the
project's declared floor (§3) and `fail_under` per layer (§22.5).

```toml
[tool.ruff]
line-length = 100
target-version = "py312"                # = the project's floor
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "RUF"]   # incl. I (import sort), B (bugbear), UP (pyupgrade)

# ruff format is authoritative; formatting is never argued in review (§23.2).

[tool.pyright]
pythonVersion = "3.12"                  # = the project's floor; flags version-inappropriate constructs
typeCheckingMode = "strict"             # ADR-PY-002
include = ["src", "tests"]
reportMissingTypeStubs = "warning"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--strict-markers --strict-config"

[tool.coverage.run]
branch = true
source = ["src"]

[tool.coverage.report]
show_missing = true
# fail_under is set per project, highest for the analytical core / service layer (§22.5).

[tool.importlinter]
root_package = "example"

[[tool.importlinter.contracts]]
name = "Domain depends on nothing internal"
type = "forbidden"
source_modules = ["example.domain"]
forbidden_modules = ["example.api", "example.services", "example.adapters", "example.repositories"]

[[tool.importlinter.contracts]]
name = "Domain imports no framework"
type = "forbidden"
source_modules = ["example.domain"]
forbidden_modules = ["fastapi", "sqlalchemy", "argparse"]
```

A pre-commit hook (§23.4) runs `ruff check`, `ruff format --check`, `pyright`, `pytest`, `lint-imports`,
the secret scanner, and `pip-audit`; CI runs the same set against the project's floor matrix.

---

## Appendix C — Ports & adapters skeleton (generic)

The minimal shape of §10, independent of the presentation example. The domain depends on the port; the
composition root wires a concrete adapter.

```python
# domain/ports.py — the PORT: depends on nothing volatile (no I/O, no framework, no ANSI)
from __future__ import annotations
from typing import Protocol, runtime_checkable
from .model import Finding            # a frozen dataclass value object (§12.1)

@runtime_checkable
class ResultSink(Protocol):
    """Outbound port: the domain emits results; an adapter decides where they go."""
    def emit(self, finding: Finding) -> None: ...

# domain/use_case.py — depends on the PORT, never on an adapter (§8.4)
class RecoverUseCase:
    def __init__(self, sink: ResultSink) -> None:
        self._sink = sink

    def run(self, target: str) -> None:
        finding = self._recover(target)      # pure domain work
        self._sink.emit(finding)             # emit through the port

# adapters/json_sink.py — one ADAPTER (the volatile detail lives here)
import json
class JsonSink:                              # structurally satisfies ResultSink — no inheritance needed
    def emit(self, finding: Finding) -> None:
        print(json.dumps(finding.as_envelope()))   # the public IngestionEnvelope (Principle 6)

# main.py — the COMPOSITION ROOT wires the concrete adapter; swapping it is a one-line change
def main() -> int:
    use_case = RecoverUseCase(sink=JsonSink())     # ← a TUI/HTTP/test sink drops in here unchanged
    use_case.run("…")
    return 0
```

Adding a TUI, a web/JSON API, or a recording test double is a new `*Sink` class plus one line at the
composition root. No domain code changes (§10.4).

---

## Appendix D — Native-acceleration decision flowchart

```
              ┌──────────────────────────────────┐
              │ Is it actually too slow?          │
              │ (measured against a real target)  │
              └───────────────┬──────────────────┘
                        no    │    yes
            ┌─────────────────┘    └──────────────────┐
            ▼                                          ▼
   stop — do not optimize            ┌──────────────────────────────────┐
   (§21.1)                           │ PROFILE: cProfile / py-spy /      │
                                     │ scalene → find the hot path        │
                                     └───────────────┬──────────────────┘
                                                     ▼
                          Better algorithm / data structure?  ──yes──▶ do it, re-measure
                                                     │ no
                                                     ▼
                          Idiomatic Python + stdlib enough?    ──yes──▶ do it, re-measure
                                                     │ no
                                                     ▼
                          Numeric / array batch work?          ──yes──▶ NumPy → still hot? Numba
                                                     │ no
                                                     ▼
                          Typed pure-Python module?            ──yes──▶ mypyc
                                                     │ no
                                                     ▼
                          Need C-level control / C interop?    ──yes──▶ Cython
                                                     │ no
                                                     ▼
                          One dominant kernel, nothing above fits? ──▶ C / C++ / Rust extension
                                                     │                  (cffi · pybind11/nanobind · PyO3)
                                                     ▼
                          Keep it behind a Python seam + OPTIONAL (§21.4); re-measure.
```

---

## Appendix E — Glossary & References

### E.1 Glossary

- **Tier 1 / 2 / 3** — library/installable CLI · standalone run-in-place app · platform/service (§4).
- **Operator-side / target-deployed** — code on the practitioner's controlled environment (floor 3.12+)
  vs code that runs on a host the operator does not control (floor 3.9) (§3.1).
- **Port / adapter** — an interface the domain owns (port) and a backend-specific implementation of it
  (adapter); **inbound/anti-corruption** adapters translate messy external input into typed domain events,
  **outbound** adapters carry domain output to a backend (§10).
- **View-model** — a plain-data description of *what to show*, free of formatting/color (§10.2).
- **Analytical core** — the framework-independent, pure package holding the cross-domain math; depends on
  nothing (§8.2).
- **IngestionEnvelope** — the public contract every data-producing tool emits, to the consolidation store or the live substrate
  (Principle 6).
- **The ladder** — the profile-first optimization sequence ending in native code as the last rung (§21.2).
- **Gate** — a blocking CI check; a `must` is backed by a gate (§23).

### E.2 References

**Packaging & metadata** — [Python Packaging User Guide: writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
· [pyproject.toml specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
· [PEP 517](https://peps.python.org/pep-0517/) · [PEP 518](https://peps.python.org/pep-0518/)
· [PEP 621](https://peps.python.org/pep-0621/) · [PEP 735 (dependency groups)](https://peps.python.org/pep-0735/)
· [PEP 561 (py.typed)](https://peps.python.org/pep-0561/).

**Language & typing** — [PEP 8](https://peps.python.org/pep-0008/) · [PEP 563 (postponed annotations)](https://peps.python.org/pep-0563/)
· [PEP 585 (builtin generics)](https://peps.python.org/pep-0585/) · [PEP 604 (union types)](https://peps.python.org/pep-0604/)
· [PEP 695 (type parameters)](https://peps.python.org/pep-0695/) · [Pyright](https://microsoft.github.io/pyright/).

**Tooling** — [ruff](https://docs.astral.sh/ruff/) · [uv](https://docs.astral.sh/uv/)
· [ty (Astral type checker)](https://astral.sh/blog/ty) · [import-linter](https://import-linter.readthedocs.io/)
· [Hypothesis](https://hypothesis.readthedocs.io/) · [pytest](https://docs.pytest.org/).

**Concurrency & the GIL** — [Python free-threading HOWTO](https://docs.python.org/3/howto/free-threading-python.html)
· [Python Free-Threading Guide](https://py-free-threading.github.io/) · [PEP 703 (making the GIL optional)](https://peps.python.org/pep-0703/)
· [PEP 779 (supported free-threaded status)](https://peps.python.org/pep-0779/).

**Native acceleration** — [Cython](https://cython.readthedocs.io/) · [Numba](https://numba.readthedocs.io/)
· [mypyc](https://mypyc.readthedocs.io/) · [cffi](https://cffi.readthedocs.io/)
· [pybind11](https://pybind11.readthedocs.io/) · [nanobind](https://nanobind.readthedocs.io/)
· [PyO3](https://pyo3.rs/) · [maturin](https://www.maturin.rs/)
· [Cython, Rust, and more: choosing a language for Python extensions (pythonspeed)](https://pythonspeed.com/articles/rust-cython-python-extensions/).

---

*End of standard. Changes follow the `ADR-PY-NNN` process of §26.6.*

