# Documentation & Architecting Standard

> **How we design before we build, and the minimum set of design specifications every non-trivial project
> produces.** Architecture is decided and written down *before* implementation, to a consistent gold
> standard, so any engineer — or any AI coding session — can build from the spec with minimal ambiguity
> and so decisions are traceable. This standard is language- and domain-agnostic; it sits under the
> `A_TALUS_Coding_Standard.md` umbrella and applies to every project alongside the relevant language
> standard.
>
> **Mandatory.** A non-trivial project without its design-spec set is not ready to build. "Must" is a
> gate; "should" is a strong default requiring a logged justification; "may" is latitude.
>
> Status: **Accepted, v1.2.1** (2026-06-26). Part of **Standards Suite v1.2.1** (was v1.1). v1.2.1 prescribes
> the `Research_and_Planning/` planning folder (§3.1) and marks design-time artifacts internal by default.

---

## Contents

§1 Purpose & Authority · §2 Principles of Good Design Documentation · §3 The Artifact Lifecycle
(Planning → Architecture → Build) · §4 The Mandatory Minimum Design-Spec Set (00–08) · §5 Conditional &
Supplementary Documents · §6 The Gold-Standard Format · §7 ADRs · §8 Seams · §9 Contracts & Integration ·
§10 Tailoring (baseline, not quota) · §11 Maintenance, Status & the Build Roadmap · §12 Why This Is Right
· Appendix A: the `Architecture/` skeleton & authoring checklist

---

## 1. Purpose & Authority

### 1.1 Why design precedes code

Code written without a design drifts, duplicates, and encodes decisions nobody can later explain. A
written architecture is the cheapest place to be wrong: a schema is corrected in a paragraph, not a
migration; a contract is aligned in a sentence, not a cross-team refactor. The specification is also what
makes the work *parallelizable and resumable* — a second engineer, or a fresh AI session, picks it up
without re-deriving the reasoning. The bar is **implementable**: a competent builder produces the system
from the spec with minimal guesswork.

### 1.2 What this governs

Every non-trivial project carries an `Architecture/` documentation suite built to this standard. "Non-
trivial" means anything another person or tool will depend on, extend, or operate — i.e. nearly everything
beyond a throwaway script. This standard governs *which* documents exist, *what* each must contain, the
*format* they share, and the *planning artifacts* that precede them. It does not restate language rules
(those live in the language standard, which the code-standards document *references*).

### 1.3 Authority

Under the `A_TALUS_Coding_Standard.md` umbrella (§9 there). A project's own code-standards document
specializes the relevant language standard and never contradicts it. Cross-component contracts are owned
by the contract registry (§9). Deviations from a `must` require an ADR.

---

## 2. Principles of Good Design Documentation

1. **Implementable, not aspirational.** Complete schemas, enumerated APIs, worked numeric examples. If a
   builder would have to guess, the spec is unfinished.
2. **Traceable.** Every non-obvious decision links to a principle or an ADR. The reader can always answer
   "why is it this way?"
3. **Decomposable.** A composite — a score, a pipeline, a workflow — is presented as its parts, each
   visible. No black boxes (mirrors the umbrella's decomposability principle).
4. **Candid.** State what is *out of scope*, what is a deferred *seam* (§8), and the known limitations.
   A spec that hides its gaps is worse than one that names them.
5. **Cross-referenced precisely.** Refer to other docs and sections by number (`see 02 §2.2`) and keep
   the references valid. The suite of docs reads as one coherent work.
6. **Cited.** Borrowed algorithms and external standards carry a citation (author, year, venue / RFC).
7. **The document practices the standard.** Direct, economical prose; no filler; diagrams where a diagram
   is clearer than a paragraph.

---

## 3. The Artifact Lifecycle (Planning → Architecture → Build)

Three stages, three kinds of artifact. Architecture assumes planning is complete; build assumes
architecture is complete.

```
   PLANNING                         ARCHITECTURE                      BUILD
   (working context)                (the locked spec)                 (code + tests)
   ──────────────                   ───────────────                   ──────────────
   research briefs        ─────►    Architecture/00..08      ─────►   implementation,
   decision log                     (+ conditional 09..)              gated by the language
   contract registry                supporting evaluations            standard, sequenced by
   status ledger                    Architecture/README               the 08 roadmap (→ Phase Guidelines)
```

### 3.1 Planning artifacts (precede the architecture)

- **Research briefs** — when a project borrows non-obvious (often cross-domain) methods, the formal
  problem statement, candidate techniques with worked micro-examples, and an honest recommendation
  precede the algorithm spec. (Authored by `talus-researcher`.)
- **Design proposal** — the module decomposition, data model, algorithm selection with trade-offs, and the
  integration contract, proposed before the prose spec is written. (Authored by `talus-architect`.)
- **Decision log** — an append-only narrative of the consequential choices and *why*, with open threads
  and a resume pointer. Distinct from ADRs: the log is the story; ADRs are the formal records.
- **Contract registry** — the single source of truth for cross-component contracts (§9).
- **Status ledger** — per-project/per-document state so any session knows what is done and what is next
  (§11).

These are working context, not deliverables; they may be terse. The Architecture suite is the deliverable.
They have **two canonical homes**, both kept out of the working root and **internal by default — excluded from
a public release unless the project deliberately publishes its design** (Git & Release Engineering Standard §9):

- **`Research_and_Planning/`** — a project-root folder beside `Architecture/`, the **pre-architecture design
  trail**: the research briefs and the design proposal, where `talus-researcher` and `talus-architect` write
  (`Research_and_Planning/<topic>_research_brief.md`, `Research_and_Planning/<tool>_design_proposal.md`). The
  deliberate "research → design" work the locked spec is built from.
- **`.talus/`** — the framework-controlled working-context folder (AI Coding Phase Guidelines §7): the
  **running journal** — the decision log, the status ledger, and the per-phase build records. A local mirror
  of the contract registry (§9) may live here too.

### 3.2 The Architecture suite

The locked specification — the subject of §4–§9. Authored by `talus-architect` (design proposal) then
`talus-scribe` (the prose suite), validated by `talus-cartographer` (contracts). It is what the build
follows.

---

## 4. The Mandatory Minimum Design-Spec Set (00–08)

Every non-trivial project's `Architecture/` carries these nine concerns. **The concerns and the intent of
each are mandatory; the canonical numbering below is the default** a typical tool follows as-is, and
**slots 03 and 04 carry a domain-appropriate title** (a tool's core differs). This is a *baseline, not a
quota* (§10): a small tool may merge slots, and a complex platform may split the core and give heavy
concerns their own later-numbered documents (§10) — but never silently drop a concern, and map any
renumbering in the `Architecture/README`.

| # | Slot (canonical title) | Mandate — what it must contain |
|---|---|---|
| **00** | `VISION_AND_ARCHITECTURE` | The one-sentence mandate; what the tool *is* and **is not**; the design principles (non-negotiable, numbered); the gap it fills / why it exists; a high-level architecture sketch (ASCII); **its editions** — community vs pro, or "single-edition" stated as a decision (Licensing & Editions Standard). The entry point — read first. |
| **01** | `TECHNOLOGY_DECISIONS_ADR` | Every significant technology choice as an ADR (§7): status, context, decision, alternatives *named and rejected with reasons*, consequences. Includes triggers for revisiting a choice. |
| **02** | `DATA_MODEL_AND_PERSISTENCE` | The canonical entities (Field / Type / Notes tables), an ER diagram (ASCII), identity and key strategy, storage lifecycle (audit, soft-delete, retention), and field-level constraints. Worked instantiation examples. |
| **03** | *core domain* — `ALGORITHM_CORE` **or** `DOMAIN_MODEL`/`<domain>_MODULARITY` | The tool's reason to exist: its core algorithms (with formulation, worked numeric examples, cited lineage) **or** its domain/plugin model. Deterministic and independently testable; every composite decomposable. |
| **04** | *integration* — `INTEGRATION` / substrate contract | What the tool reads/writes/publishes/subscribes on the shared substrate, the events it emits, and its public ingestion profile. First-class; must match the contract registry exactly (§9). A tool's **frontend** is a *separate* concern, not a retitling of this slot (§5). |
| **05** | `SECURITY_AND_OPSEC` | Per the **Security & OpSec Standard**: threat model (assets, sensitivity, adversaries); the secure-by-construction control matrix (parameterized queries, boundary validation, output encoding, authorization chokepoint, secrets handling, audit log); authorization/scope, data handling/retention, and operational-security properties where relevant. |
| **06** | `CODE_STANDARDS_AND_STRUCTURE` | The project tree (the layering *visible* in the filesystem), module/naming conventions, import boundaries, and the layered/ports-&-adapters shape. **References the language standard** rather than restating it. |
| **07** | `INTERFACES_AND_CLI` | The public surface: API contract (endpoints, verbs, auth scopes, versioning) and/or CLI conventions, with examples. For a producing tool, the `ingest/<tool>` profile lives here or in 04. |
| **08** | `ROADMAP_AND_MILESTONES` | The phased build plan: sequencing philosophy, phases with goal / build / **exit criteria**, and the load-bearing seams (§8) architected now but built later. This is the input to the AI Coding Phase Guidelines (§11). |

A tool whose core is analytical titles **03** `ALGORITHM_CORE`; a tool whose core is a plugin/domain model
titles it `DOMAIN_MODEL` or `<domain>_MODULARITY`. Slot **04** is always the integration/substrate-contract
document. A tool with a substantial UI documents its frontend in a **dedicated `FRONTEND_ARCHITECTURE`
document** (§5) — a *separate* concern from integration, not a retitling of 04 (a real UI-led platform needs
*both*). The intent of each slot is fixed; the title serves the domain.

---

## 5. Conditional & Supplementary Documents

Beyond the mandatory 00–08 concerns, a tool documents the **conditional concerns it actually has** — each
as its own document when substantial, never padded to hit a count. Some are *primary* and sit early in the
numbering (a UI-led tool's frontend); others are platform add-ons at 09+.

- **`FRONTEND_ARCHITECTURE`** — **required when the tool has a substantial UI.** The frontend's *software
  architecture*: the stack, the component/feature structure, client–server state, the typed API client, the
  key views, and the build. It **binds the Visual UX/UI Standard** — the two are complementary: this document
  is *how the frontend is built*; the Visual standard is *how it looks and behaves*. For a UI-led tool this
  is a **primary** document placed **early** in the numbering (not a peripheral 09+), and **separate from**
  the integration document (04).
- **09+ conditional core** (a platform or deployed/extensible system):
  - `DEVOPS_TOOLING_PIPELINES` — containerization, CI/CD stages, test strategy, rendering pipeline,
    backup/restore, the **release process** (per the Git & Release Engineering Standard), and the
    **observability & operational-readiness** content — telemetry (logs/metrics/traces), SLIs/SLOs, health
    checks, the reliability patterns, deploy/rollback safety, runbooks, on-call/ownership, and the
    production-readiness review (per the **Observability & Reliability Standard**). Required when the tool
    is deployed or orchestrated.
  - `INTEGRATION_AND_SDK` — a public plugin SDK / connector model. Required when third parties extend it.
- **Supporting evaluations** (recommended for hard trade-offs, novel math, or a final sweep) — named for
  what they do: a `TECHNIQUES_DEEPDIVE` (cross-domain candidate techniques scored by fit / lineage /
  candor), a `GAPS_REVIEW` (operational gaps scored in-arc / seam / decline with retrofit cost), a
  `PERSPECTIVES_REVIEW` (a final cross-lens sweep). These are where tough calls are reasoned in the open.
- **`Architecture/README.md`** — **required.** A brief inventory: every doc in the suite, each one's
  status (seed / partial / spec-complete), a pointer to the relevant planning artifacts, and any setup
  notes. It is the map to the suite.

Rule of thumb: **00–08 are mandatory; 09+ exist iff the tool is deployable/orchestrated or publicly
extensible; supporting evaluations exist iff a decision was hard enough to deserve a written verdict.**

---

## 6. The Gold-Standard Format

Every document shares the format that makes the suite implementable and navigable:

- **A header preamble** — the document's position, what to read first, and the vocabulary it carries
  forward.
- **A one-sentence mandate** up top, and an explicit **"what it is not."**
- **Numbered sections** at consistent depth (`§1`, `§2.1`, …) under a navigable **Contents / section map** at
  the top — precisely referenceable and **section-addressable**: a reader grabs one `§` by its stable `## N.`
  heading without scanning the whole file. A large document is read **Contents → the relevant `§`**, never
  whole-file, when context is tight (for the language standards, the umbrella's canonical section framework,
  §1.5 there).
- **ASCII diagrams** for architecture, schema (ER), data flow, and layering. A diagram beats a paragraph
  for structure.
- **Worked numeric examples** for any formula, score, or non-trivial transform — the calculation done with
  real numbers, not just described.
- **Field/Type/Notes tables** for entities; **enumerated** endpoints/commands for interfaces; **complete**
  schemas, not sketches.
- **ADR blocks** (§7) for decisions; **decision tables** for comparative choices.
- **Precise cross-references** and **citations** for borrowed methods.
- **Candor blocks** — explicit in-scope / seam / out-of-scope and known limitations.

Exemplar to emulate:
.

---

## 7. ADRs (Architecture Decision Records)

A significant decision — a technology choice, a structural commitment, a rejected alternative worth
remembering — is recorded as an ADR with a fixed shape:

```
#### ADR-<NS>-NNN — <short imperative title>
**Status:** Proposed | Accepted | Superseded by ADR-<NS>-MMM
**Context.** The forces at play; what makes this a real decision.
**Decision.** What we are doing.
**Alternatives considered.** Each option named and *rejected with a reason* (not a strawman).
**Consequences.** What this makes easy, what it makes hard, and any revisit trigger.
```

- **Namespace per project** (`ADR-<TOOL>-NNN`) to avoid cross-tool numbering collisions; reference a
  foreign ADR by its full id. Standards use their own series (`ADR-STD-NNN`, `ADR-<LANG>-NNN`).
- ADRs are **append-only**: a reversed decision is *superseded*, never edited away — the history is the
  point.
- Live mainly in `01_TECHNOLOGY_DECISIONS_ADR`, but any document may carry an ADR for a decision in its
  scope.

---

## 8. Seams

A **seam** is an architectural boundary **architected now but built later**, because retrofitting it would
be expensive. Naming seams is how a spec stays honest about scope without painting the future into a
corner.

- Mark a seam explicitly where it lives (a reserved field in `02`, an unimplemented interface in `06`, a
  `[seam]` milestone in `08`).
- A seam states *what* is reserved, *why* it is deferred, and *what it would cost* to add later if not
  reserved now.
- The roadmap (`08`) lists the load-bearing seams — the ones whose absence later would force a painful
  migration (a stable identifier, a signature/hash field, an event-emission point, a cross-framework
  crosswalk, **the edition seam** that lets a pro edition be a build profile rather than a fork — Licensing
  & Editions Standard §3).

Seams are the disciplined alternative to either over-building now or being trapped later.

---

## 9. Contracts & Integration

> **The contract is the schema. Never screen-scrape a sibling's human-readable output.**

How contracts are *authored, schema-defined, versioned, and evolved* is the **API & Data-Contract
Standard**; this section is the documentation requirement. Every cross-component interaction is specified,
not improvised:

- The producing and consuming sides are written down: what is read, written, published, subscribed; the
  event names and payload schemas; the public ingestion/output profile.
- A cross-component contract is **registered in the contract registry** and validated by
  `talus-cartographer`; a change finds every affected producer/consumer before it lands.
- The integration document (`04`, or `07` for a public API) must match the registry **exactly** — a doc
  that claims an event no one consumes, or reads a structure no one produces, is drift and is a finding.

---

## 10. Tailoring: Baseline, Not Quota

The standard is **strict on *which* concerns must be documented and to what *format rigor*, and flexible on
*how many* documents and their *numbering*** — documentation grows to fit the tool, not the tool to fit a
fixed document count. The 00–08 set is a *baseline*. Apply judgment:

- **Merge** slots when a tool is small (a simple CLI may fold `07` into `00`/`06`); **split** a slot when
  a concern is heavy (a data-heavy substrate tool may split `02` across several documents).
- **A complex platform may expand and renumber.** When the core is large enough to warrant it, split it
  into more than one numbered document and give heavy concerns their own later number — the *concerns* are
  what is mandatory (§4), not the exact slot integers. The canonical 00–08 is the default a typical tool
  keeps as-is; a platform that diverges maps its layout in the `Architecture/README` so the concerns are
  still locatable at a glance.
- **Scale depth to complexity.** A standalone CLI typically needs a lean 00–08. A platform adds 09–11 and
  supporting evaluations. A seed-stage tool may legitimately carry only a `00_VISION` with the rest marked
  *deferred* in its `Architecture/README` — as long as the deferral is explicit.
- **Never pad, never silently cut.** Padding to hit a number and dropping a concern that matters are equal
  failures. If a slot is genuinely N/A, say so in one line rather than omitting it.

---

## 11. Maintenance, Status & the Build Roadmap

- **Status ledger.** Each project (and the program over it) keeps a status ledger: per-document state
  (`not-started` / `researching` / `in-design` / `spec-complete` / `building`) and the next action. A
  fresh session reads it to know exactly where things stand.
- **Docs track the system.** When the build diverges from the spec, the spec is updated (or an ADR records
  the change) — the `Architecture/` suite is kept true, not abandoned after kickoff.
- **The roadmap drives the build, the Phase Guidelines drive the AI.** The `08_ROADMAP` defines *what* to
  build and *in what order* (phases, exit criteria, seams). The **AI Coding Phase Guidelines**
  (`B_AI_Coding_Phase_Guidelines.md`) define *how* an AI session executes a phase safely — one phase, then
  stop for review. The two are complementary: roadmap = the route; phase guidelines = how to drive it.

---

## 12. Why This Is Right

A fixed minimum spec set, a shared format, and explicit planning artifacts mean every project is
designed before it is built, to the same implementable bar, with its decisions traceable and its contracts
registered. That is what lets the work be parallelized across people, resumed cold across sessions and
models, and grown without re-litigating first principles — and it is what makes a system feel coherent
rather than accreted.

---

## Appendix A — The `Architecture/` skeleton & authoring checklist

```
<Tool>/
├── Architecture/
│   ├── README.md                       # inventory + per-doc status + planning pointers
│   ├── 00_VISION_AND_ARCHITECTURE.md
│   ├── 01_TECHNOLOGY_DECISIONS_ADR.md
│   ├── 02_DATA_MODEL_AND_PERSISTENCE.md
│   ├── 03_<ALGORITHM_CORE | DOMAIN_MODEL>.md
│   ├── 04_<INTEGRATION | FRONTEND_ARCHITECTURE>.md
│   ├── 05_SECURITY_AND_OPSEC.md
│   ├── 06_CODE_STANDARDS_AND_STRUCTURE.md
│   ├── 07_INTERFACES_AND_CLI.md
│   ├── 08_ROADMAP_AND_MILESTONES.md
│   ├── 09_DEVOPS_TOOLING_PIPELINES.md          # conditional (deployed/orchestrated)
│   ├── 10_INTEGRATION_AND_SDK.md               # conditional (publicly extensible)
│   └── <TECHNIQUES_DEEPDIVE | GAPS_REVIEW | PERSPECTIVES_REVIEW>.md   # supporting, as warranted
└── Research_and_Planning/                # pre-architecture design trail: briefs + design proposal (internal)
```

**Before a project is "ready to build", confirm:**

- [ ] 00–08 present (or explicitly deferred in `Architecture/README` with a reason).
- [ ] Every significant tech choice is an ADR with named, rejected alternatives.
- [ ] The data model has complete Field/Type/Notes tables and an ER diagram.
- [ ] The core (03) has worked numeric examples and cited lineage; every composite is decomposable.
- [ ] Every cross-component contract (04/07) matches the registry and is validated.
- [ ] Security (05) has a threat model and a control matrix, not just intentions.
- [ ] 06 references the language standard rather than restating it.
- [ ] 08 has phases with **exit criteria** and the load-bearing seams marked.
- [ ] Format: numbered sections, ASCII diagrams, precise cross-refs, candor on scope/seams.
