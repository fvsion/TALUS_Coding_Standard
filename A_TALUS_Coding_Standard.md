# TALUS Coding Standard — the umbrella

> **The language-agnostic foundation for how we build software.** This is the top of the standards
> hierarchy: it states the doctrine every project follows regardless of language, and every per-language
> standard (Python, and later C, TypeScript, …) is a faithful specialization of it. It is deliberately
> **high-level** — the binding, line-by-line rules live in the language standards. Where a language
> standard is silent, this document governs; where it speaks, it specializes this document and never
> contradicts it.
>
> **Mandatory and mechanically enforced.** Conformance is gated in CI and reviewed by a conformance agent.
> "Must" is a gate; "should" is a strong default requiring a logged justification to deviate; "may" is
> genuine latitude.
>
> Status: **Accepted, v1.3** (2026-06-26). This umbrella declares the **suite version** as a release marker:
> **Standards Suite v1.3** — locked together at **v1.0** (2026-06-25); **v1.1** added §-addressed reading;
> **v1.1.1** indexed the standards `A_–J_` and hardened them through review; **v1.2** adds directive durability
> + per-phase review, the generated `DOCTRINE.md` (the flattened must-gate contract), and `GATE_COVERAGE.md`
> (the self-conformance audit mapping every must-gate to the arm that enforces it); **v1.2.1** prescribes the
> `Research_and_Planning/` planning folder (`C` §3.1) and extends the dual-use posture to design-time artifacts
> (`H` §9); **v1.3** adds the **User Documentation Standard** (`K`) — README / GUIDE / RTFM / TUTORIAL as a
> first-class, gated deliverable written in an anti-AI-tell voice — and the `talus-herald` agent that authors
> and reviews it. The umbrella carries the suite marker; each companion standard keeps its own version and
> bumps only on a rule change. See `CHANGELOG.md`.
> Companion standards: `languages/Python_Coding_Standard.md` (the first language
> instance), `B_AI_Coding_Phase_Guidelines.md`, `C_Documentation_and_Architecting_Standard.md`,
> `D_Visual_UX_UI_Standard.md`, `E_API_and_Data_Contract_Standard.md`, `F_Security_and_OpSec_Standard.md`,
> `G_Observability_and_Reliability_Standard.md`, `H_Git_and_Release_Engineering_Standard.md`,
> `I_Licensing_and_Editions_Standard.md`, `J_LLM_AI_Integration_Standard.md`,
> `K_User_Documentation_Standard.md`.

---

## Contents

§1 Purpose & the Standards Hierarchy · §2 The Canonical Principles · §3 Distribution, Packaging &
Cross-Platform Reach · §4 Architecture Doctrine · §5 Implementation Doctrine · §6 Concurrency & Performance Doctrine
· §7 Quality, Testing & Tooling · §8 Security & OpSec by Construction · §9 Documentation & Architecture ·
§10 Visual & Interaction Design · §11 Governance · §12 Why This Is Right

---

## 1. Purpose & the Standards Hierarchy

### 1.1 Why this document exists

A team building many tools needs one shared definition of "good," above any single language. Implicit
convention drifts between projects, is invisible to a new contributor, and cannot be enforced. This
umbrella fixes the doctrine once; the language standards turn it into mechanical rules a linter and a
type checker can check.

### 1.2 The hierarchy

```
            ┌─────────────────────────────────────────────┐
            │   TALUS Coding Standard  (this document)     │   language-agnostic doctrine
            └───────────────────┬─────────────────────────┘
        ┌───────────────────────┼───────────────────────────┐
        ▼                       ▼                            ▼
  languages/Python        languages/C  (later)     languages/TypeScript (later)
   (binding rules)         (binding rules)            (binding rules)
        └───────────────────────┴───────────────────────────┘
                                │ every project also conforms to:
            ┌───────────────────┴───────────────────┐
            ▼                                        ▼
  Documentation_and_Architecting_Standard     Visual_UX_UI_Standard
```

- **This umbrella** owns cross-language doctrine: principles, architecture, security posture, quality
  bar, governance.
- **A language standard** owns the concrete rules for one language: its packaging, its type system, its
  toolchain and gates, its idioms. It *inherits* every principle here and may only tighten, never relax.
- **The Documentation & Architecting Standard** defines the minimum design specifications every project
  produces. **The Visual UX/UI Standard** defines how output and interfaces look and behave. Both apply
  across all languages.
- **The User Documentation Standard** defines the user-facing doc set every shipped tool produces — the
  README, GUIDE, RTFM, and TUTORIAL — as a first-class, gated deliverable in an anti-AI-tell voice (§9). It
  is the public-surface peer of the (internal) Documentation & Architecting Standard.
- **The AI Coding Phase Guidelines** define how an AI coding session executes a build in bounded,
  reviewable phases — the methodology that keeps quality constant across models (frontier to small local),
  applied to whatever the roadmap sequences.
- **The Licensing & Editions Standard** defines the open-core community/pro split — the edition seam, the
  build-time exclusion of `pro/`, and the licensing mechanics (§3.2).
- **The Security & OpSec Standard** defines secure-/opsec-by-construction in depth — threat modeling, the
  control baseline, secrets, audit, and operational security (§8).
- **The Git & Release Engineering Standard** defines version control and shipping — trunk-based flow,
  commits/PRs, SemVer/changelog/tagging, CI gate orchestration, and the dual-use git posture (§11).
- **The API & Data-Contract Standard** defines how interfaces are authored and evolved — contract-first,
  schema-as-source-of-truth, compatibility rules, the output envelope, and the contract registry
  (Principle 6).
- **The Observability & Reliability Standard** defines how software is *operated* — the three correlated
  signals (logs/metrics/traces), SLIs/SLOs, health/lifecycle, the reliability patterns, deploy safety &
  rollback, and operational readiness — sized to the tool's tier.
- **The LLM / AI Integration Standard** defines how an LLM is embedded *in a product* — at a named seam
  that decides nothing, with untrusted input/output, least privilege, and prompt/data protection
  (Principle 1).

### 1.3 Authority and precedence

1. A language standard governs the concrete rule for its language.
2. This umbrella governs anything the language standard does not address, and the doctrine all of them
   share.
3. The Documentation & Architecting and Visual UX/UI standards govern their domains across languages.
4. Deviations are explicit: a `must` is a gate (deviation needs a new ADR); a `should` may be deviated
   from with a logged, justified, ideally time-boxed exception.

### 1.4 Adding a language standard

Create `languages/<Language>_Coding_Standard.md`, mirror the section framework of the Python standard,
and for every principle in §2 state the language-specific mechanism that enforces it (the type checker,
the linter, the packaging system, the concurrency model). A language standard is not done until each
principle has a concrete, gated expression.

### 1.5 The canonical section framework

Every language standard mirrors **one** section framework, so a reader (and the `talus-auditor`) navigates
any language standard by the same map and reads **only the section the work touches** — never the whole file
(the standards are section-addressable by design; Documentation & Architecting Standard §6). The Python
standard is the worked realization; future languages keep the same Part/§ bands with the same concern in each:

| Part | §-band | Concern |
|---|---|---|
| I — Foundations & Doctrine | §1–§3 | purpose & authority · core principles · language baseline & version policy |
| II — Project Shape & Packaging | §4–§7 | packaging tiers · project layout · build backend · dependency policy |
| III — Architecture & Design | §8–§12 | layered architecture · SOLID · ports & adapters · configuration · domain modeling |
| IV — Implementation | §13–§19 | typing · naming & clean code · errors · logging · filesystem & I/O · terminal output & color · CLI |
| V — Concurrency & Performance | §20–§21 | concurrency model · performance & going-native |
| VI — Quality, Testing & Tooling | §22–§25 | testing · toolchain & CI gates · documentation · security & OpSec |
| VII — Governance | §26–§28 | adoption / exceptions / enforcement · decision summary · why this is right |
| Appendices | A–E | templates · tool configs · skeletons · flowcharts · glossary & references |

A language standard **may** add a section its language genuinely needs (record it in that standard's own ADR
log and preserve the band ordering), but it does not drop a concern or renumber the shared bands. This makes
"mirror the section framework of the Python standard" (§1.4) concrete, and it is what lets a constrained
session read any standard by section instead of loading it whole.

---

## 2. The Canonical Principles

These nine hold in every language. A language standard makes each one mechanical.

1. **Determinism decides; automation is principled, not improvised.** Behavior is driven by transparent,
   inspectable logic a human can audit and reproduce — not by opaque heuristics, and never by an LLM
   making a decision. Where a model is used at all, it is glue at a named boundary and decides nothing
   (§8); how an embedded LLM is contained at that boundary is the
   **LLM / AI Integration Standard**.

2. **Dependencies point inward; the core depends on nothing.** Business logic knows nothing of
   frameworks, I/O, terminals, or datastores. Everything volatile is an adapter at the edge. This is
   what makes a tool re-targetable without touching its core.

3. **Extend by addition, not modification.** New capability is a new unit implementing an existing
   interface (a plugin, a strategy, an adapter) — not a new branch in a growing conditional. This is the
   single most important property for software meant to grow.

4. **Everything a reasonable operator would change is a variable.** Thresholds, weights, limits, paths,
   and workflow shapes are named configuration with one definition site, never literals buried in logic.
   Anything that changes a recorded result is versioned.

5. **Secure and OpSec by construction.** Validate untrusted input at the boundary; parameterize every
   query; encode output; never embed secrets; scope-gate consequential actions; log to an immutable
   audit trail. Security is a design property, not a later pass.

6. **Composable: useful alone, multiplicative together.** Every component does one job well, stands
   alone, and speaks a public contract — never screen-scraping a sibling's human-readable output. The
   contract is the schema.

7. **Reproducibility is a property, not an aspiration.** The same inputs produce the same outputs.
   Determinism is testable; anything that alters a recorded result is versioned so the output records the
   configuration that produced it.

8. **Efficiency is a feature, achieved by design.** Performance comes from the right algorithm and an
   honest profile, not from premature micro-optimization or from throwing hardware at a bad design. We
   measure before we optimize, and we reach for rigorous methods over brute force.

9. **Cross-platform by default.** Tools are designed and tested to run on macOS, Linux, and Windows from
   the outset; platform-specific behavior is isolated behind a thin adapter, never scattered through the
   code. Cross-platform interoperability is the primary design ethos — a tool that is genuinely
   platform-bound *declares* its supported platforms and the reason, as a deliberate, documented exception
   rather than an accident (§3.1).

The rest of this document, and every language standard, is the disciplined application of these nine.

---

## 3. Distribution, Packaging & Cross-Platform Reach

Every artifact declares **what it is** and **where it runs**, because that determines its shape:

- **Library / installable component** — imported or installed; a public API others depend on; minimal
  dependency budget; ships its type information.
- **Standalone application** — run in place by an operator; one thin entry point dispatching to internal
  modules; no heavy install.
- **Platform / service** — long-running, with a backend and usually a frontend; deployed as containers;
  a layered package whose directory tree *is* the architecture.

Orthogonal to the above: **where it is deployed.** Code that runs on a host we do not control inherits
that host's constraints (the available runtime, the dependency budget) and states them explicitly. A
language standard defines the concrete tiers, layouts, build backends, and dependency policy.

**Composability invariant.** Independent of shape, every data-producing component emits its public
contract and is useful standalone; it never *requires* the rest of the system to be present.

### 3.1 Cross-platform reach

Cross-platform interoperability (Principle 9) is a first-order design constraint for libraries and
standalone applications: they target **macOS, Linux, and Windows** from day one, and that intent is
proven by running on all three, not assumed. The doctrine:

- **Declare supported platforms** the way a project declares its runtime floor — in the README and the
  build metadata — so "where this runs" is explicit, not folklore.
- **Isolate platform differences behind an adapter.** Per-OS branches (paths, scratch locations,
  executable resolution, signals, OS-only APIs) live in one small platform module or capability seam, not
  sprinkled through the codebase. Scattered `if windows / else` checks are the anti-pattern.
- **Test on every declared platform** — a CI matrix across the supported OSes, with platform-specific
  tests marked, not silently skipped.
- **Honest exceptions are fine.** Some work is genuinely platform-bound — a service that only deploys on
  Linux, a capability that only exists on one OS. That is acceptable *when declared with a reason*;
  cross-platform is the default, and a restriction is a deliberate, documented choice. (Long-running
  platforms/services, which ship as containers, set their own base-OS target and are exempt from the
  three-OS default.)

The binding, mechanical rules — path handling, encodings, signals, optional-module guards, terminal
differences — live in each language standard.

### 3.2 Editions & licensing (open-core)

A tool that has — or could ever have — a public **community** edition and a commercial **pro** edition is
designed **open-core, with the edition boundary as a clean architectural seam from the start**: pro
features attach to the community core through defined extension points and are *excluded from the community
build*, never forked into a divergent copy and never merely hidden behind a crackable runtime check. The
discipline is one line — **an edition is a seam, not a fork** — and it is the same "one source, mechanically
produce the public variant" philosophy this suite uses to fence proprietary docs, applied to code. Getting
the seam right up front makes a pro edition a build profile, not a recode. The full model (the seam, the
build-time split, the `pro/` convention, protection by absence, licensing/SPDX, per-tool requirements) is
the **Licensing & Editions Standard**.

---

## 4. Architecture Doctrine

- **Layered, with dependencies pointing inward.** Outer layers (interfaces, I/O, frameworks) depend on
  inner layers (use cases, then a framework-free domain). The domain depends on nothing. This holds for a
  platform (API → service → domain ← repository) and for a CLI (dispatch → use-case → domain ← adapters)
  — the same shape at different scales. Import boundaries are enforced mechanically, not just documented.
- **SOLID, applied.** Single responsibility per unit; open for extension, closed for modification; narrow
  interfaces; substitutable implementations; depend on abstractions. New variants arrive as new
  implementations, not as edits to a widening conditional.
- **Ports & adapters (hexagonal).** Volatile detail (a terminal, a web framework, a subprocess, a
  datastore, an external tool's output) lives behind a port the domain owns. Re-targeting — a CLI gaining
  a TUI or a web/JSON frontend, a new backend — is a new adapter, not a rewrite. An inbound
  anti-corruption adapter turns messy external input into typed domain events so noise never reaches the
  core.
- **Everything is a variable.** Configuration is data with one typed definition site; workflow shapes are
  data, not code; secrets are never configuration-in-code.
- **Model the domain explicitly.** Immutable value objects for data, closed enumerations for closed sets,
  interfaces for ports. Purity and immutability are the default; side effects live at the edges.

---

## 5. Implementation Doctrine

- **Fully typed, statically checked, strict.** Every public surface is typed and verified by a strict
  static checker in CI and in the editor. Escape hatches are reasoned and rare. (The language standard
  names the checker and its config.)
- **Clean code & honest naming.** Names say *what*, not *how*; units are small and single-purpose;
  comments explain *why*. Prose and docstrings are substantive, not ceremonial — see the AI-tell style
  (§5.1).
- **Errors are typed and specific.** Raise the most specific exception that fits; never swallow errors or
  catch over-broadly; clean up with scoped resource management; surface failures appropriately for the
  tier (a non-zero exit and a human-readable message for a CLI; a structured problem response at an API
  boundary).
- **Observability is two-stream.** The console is quiet and human; a per-run record is complete and
  timestamped. Sensitive data never travels through the logging system. How a tool is *operated* beyond
  logging — metrics, traces, SLIs/SLOs, health checks, the reliability patterns, deploy safety and
  rollback — is the **Observability & Reliability Standard**, sized to the tool's tier.
- **Output is disciplined.** User-facing rendering goes through the presentation port, never ad-hoc
  prints; styling/color is capability-gated and degrades to plain text for files and pipes; raw
  external-tool output is classified before it reaches the user. (Detail in the Visual UX/UI Standard.)

### 5.1 The "avoid AI tells" style

Write like an engineer who knows the codebase: direct and economical. No filler, no marketing adjectives,
no hedging throat-clearing, no restating the signature in the docstring. Em-dashes sparing; lists where
lists help and prose where prose helps. The standard practices what it preaches.

---

## 6. Concurrency & Performance Doctrine

- **Pick the primitive for the workload.** I/O-bound supervision of subprocesses, high-concurrency
  network I/O, and CPU-bound kernels each have a correct concurrency model; choosing wrongly (threads for
  CPU work, blocking calls on an event loop) is a defect. The language standard provides the workload→
  primitive matrix.
- **Subprocess invocation is safe by construction** — argument lists, never a shell string with untrusted
  input.
- **Performance is profiled, not guessed.** Optimize a measured bottleneck, not a suspected one.

---

## 7. Quality, Testing & Tooling

- **One canonical toolchain per language, with blocking gates.** Lint + format, strict type-check, tests
  with a coverage floor, import-boundary enforcement, and secret + dependency scans. Non-conforming code
  fails CI. The language standard pins exact tools and config.
- **The test pyramid.** Unit tests dominate and cover pure domain logic in isolation with fakes for I/O;
  integration tests cover the seams; property-based tests guard invariants of the core. Determinism is
  tested with golden files.
- **Reproducible builds.** A lockfile captures the resolved dependency set; nothing in the build reaches
  the network for an unpinned artifact.

---

## 8. Security & OpSec by Construction

Threat-model the component; enumerate its assets and adversaries; place the controls in the design.
Parameterized queries, boundary input validation, output encoding, an authorization chokepoint, secrets
out of source and out of logs, and an immutable audit trail are baseline, not features. Where a tool
operates in a sensitive context, operational security — what an observer can see, what reaches disk, what
is cleaned up — is part of the architecture. The full model — threat modeling, the control baseline,
secrets, authorization/scope, audit, OpSec, data/retention, crypto, and the CI gates — is the **Security &
OpSec Standard**.

---

## 9. Documentation & Architecture

Every non-trivial project carries an `Architecture/` documentation suite to the gold standard defined by
the **Documentation & Architecting Standard**: vision, technology-decision ADRs, data model, core
algorithms, integration contracts, security/OpSec, code standards (which *reference* the relevant
language standard rather than restating it), interfaces, and roadmap — plus the conditional concerns a tool
actually has (a frontend architecture, devops/observability, a public SDK). The spec set is **concern-driven
and sized to the tool**: strict on which concerns and their rigor, flexible on document count and numbering.
Design specifications precede implementation; decisions are traceable to a principle or an ADR.

That `Architecture/` suite is the *internal* design record, for builders. The *external*, user-facing doc set
— README, GUIDE, RTFM, and TUTORIAL — is governed by the **User Documentation Standard** (`K`): a sized,
accurate, gated deliverable in an anti-AI-tell voice, on a par with the design specs and the tests. A tool is
not done when it compiles and passes its gates; it is done when an operator can install, run, look up, and
learn it. The two standards split cleanly: `C` is what a builder reads to design the tool, `K` is what a user
reads to wield it. Design-time artifacts (`Architecture/`, `Research_and_Planning/`) are internal by default
(`H` §9); the `K` doc set is the public surface.

---

## 10. Visual & Interaction Design

How a tool presents itself — terminal output and graphical interfaces alike — follows the **Visual UX/UI
Standard**: semantic severity/status reservation, density and legibility discipline, accessibility
baselines, and the ports-&-adapters separation that lets one domain feed a CLI, a TUI, or a web frontend.
Visual polish is part of the quality bar, not an afterthought.

---

## 11. Governance

This document and every standard under it is **versioned** and changed through an ADR process
(`ADR-STD-NNN` for this umbrella; `ADR-<LANG>-NNN` for a language standard). A change is proposed,
reviewed, and on acceptance bumps the document version and is announced. A change that touches a
cross-component contract is registered with the contract owner. Standards are living contracts, changed
deliberately and traceably, never by silent drift.

Two enforcement arms: **mechanical gates** in CI (what a machine can check) and a **review-time
conformance agent** (the judgment a linter cannot make). A documented, accepted exception is not a
finding. *Code* (as opposed to these standards) is versioned, branched, reviewed, and released per the
**Git & Release Engineering Standard** — trunk-based flow, SemVer, and gated, repeatable releases.

---

## 12. Why This Is Right

A single, high-level doctrine plus thin per-language specializations gives a new developer one place to
learn how we build, makes "good" enforceable instead of cultural, and lets the suite grow — new
languages, new tools — without re-litigating first principles. The moat is not any one rule; it is that
the guiding stars are defined clearly enough that excellent work is the path of least resistance.

