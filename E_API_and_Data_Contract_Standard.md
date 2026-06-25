# API & Data-Contract Standard

> **The contract is the schema.** Components talk to each other — and to clients — through explicit,
> typed, versioned contracts, never by screen-scraping a sibling's human-readable output. A contract is
> designed before its implementations, defined as a machine-readable schema, evolved under strict
> compatibility rules, and registered so every producer and consumer of it is known. This is the deep
> treatment of the umbrella's Principle 6 ("composable: one contract, two consumers") and of the
> integration sections each tool's `Architecture/` carries.
>
> Language-agnostic; under the `A_TALUS_Coding_Standard.md` umbrella. **Mandatory** for any cross-component
> or public interface. "Must" is a gate; "should" is a strong default.
>
> Status: **Accepted, v1.0** (2026-06-25). Part of **Standards Suite v1.0**.

---

## Contents

§1 Purpose & Principles · §2 Contract-First Design · §3 Schema as the Source of Truth · §4 Versioning &
Evolution · §5 Compatibility Rules · §6 The Public Output Envelope · §7 Events · §8 HTTP / REST Conventions
· §9 Data Contracts & Persistence · §10 Validation · §11 The Contract Registry & Governance · §12 Per-Tool
Requirements · §13 Why This Is Right · Appendix A: compatibility quick-reference

---

## 1. Purpose & Principles

When components integrate through whatever output happened to be convenient — parsing a log line, reading
a CLI's pretty table — every change to that output silently breaks a consumer. Contracts make the
interface **explicit and stable**: a typed schema both sides agree on, changed only deliberately.

Principles:

1. **The contract is the schema.** Integration is against a defined, machine-readable schema — never
   against human-readable output, which is for humans and free to change.
2. **Contract-first.** The contract is designed and agreed *before* the producer or consumer is built;
   both code to it.
3. **One contract, two consumers.** A producer emits the *same* contract whether a consumer reads it
   standalone or as part of a larger system; the component is independently useful and never *requires* the
   rest to exist (umbrella Principle 6).
4. **Evolve compatibly; break deliberately.** Contracts change under strict compatibility rules (§5); a
   breaking change is a versioned, announced, registered event — never silent.
5. **Every contract has a known producer and known consumers** (the registry, §11). Nothing reads a
   contract that nobody is documented to produce, and nothing publishes one nobody consumes.

---

## 2. Contract-First Design

- **Define the contract before the implementations.** Write the schema (and an example payload) first;
  review it; *then* build the producer and consumer against it. This catches integration mismatches in a
  paragraph, not a cross-team refactor.
- **The contract is owned, not incidental.** It is a first-class artifact in the architecture
  (Documentation & Architecting Standard §9), with a name, an owner, and a version — not an accident of an
  implementation detail.
- **Examples are part of the contract.** Every schema ships at least one worked example payload (a real
  instance), so a consumer can build and test against it.

---

## 3. Schema as the Source of Truth

- **Machine-readable, typed schemas — not prose.** The canonical forms:
  - **HTTP APIs → OpenAPI.** The OpenAPI document is the source of truth for endpoints, request/response
    shapes, status codes, and auth; clients and server models are generated from or validated against it.
  - **Data, events, and envelopes → JSON Schema** (or an equivalent typed schema). Payloads validate
    against it on both sides.
- **The schema is versioned and stored in the repo** (and registered, §11) — a reviewed artifact under
  version control, diffable in a PR like code.
- **Generated, not hand-copied.** Where possible, types on both sides are generated from the schema so the
  code cannot drift from the contract (e.g. request/response models, the client). A hand-maintained copy is
  a drift source.

---

## 4. Versioning & Evolution

- **Contracts are versioned** (SemVer applied to the contract): a backward-compatible addition is a MINOR
  bump; a breaking change is a MAJOR bump and a registered, announced event (Git & Release Engineering
  Standard).
- **Expand → migrate → contract.** To make a breaking change without a flag-day: *add* the new shape
  alongside the old (expand), move producers/consumers over (migrate), then *remove* the old once nothing
  uses it (contract). Never remove-and-replace in one step.
- **Deprecate with a window.** A field/endpoint slated for removal is marked deprecated, announced, and
  kept for a stated window so consumers can move.
- **For HTTP, version the surface** (`/v1/…`, or a version header) so a MAJOR change can run beside the old
  version during migration.

---

## 5. Compatibility Rules

What is safe vs breaking (the asymmetry: relaxing what you *accept* and adding to what you *emit* is safe;
tightening or removing is breaking):

- **Backward-compatible (MINOR):** add an *optional* request field; add a field to a response; add a new
  endpoint/event/enum-value-in-a-response; widen what the producer accepts; relax a constraint on input.
- **Breaking (MAJOR):** remove or rename a field/endpoint/event; change a field's type or semantics; make
  an optional request field required; remove an enum value a consumer may send; tighten validation on
  existing input; change an error's meaning.
- **Consumers must tolerate the unknown:** ignore unrecognized fields rather than failing, so a producer's
  additive change never breaks them (be liberal in what you accept).

---

## 6. The Public Output Envelope

Every data-producing component emits its results as a **versioned, schema-defined envelope** — the public
output contract — rather than expecting consumers to parse its internals or its display:

- **One envelope, two consumers.** The same envelope is valid whether consumed standalone (written to a
  store) or live (published to a shared substrate). The producer never needs to know which.
- **The envelope carries its schema version**, the producer/source, a timestamp, and the typed payload, so
  a consumer can route and validate it.
- **It is the only sanctioned output for integration** — a sibling integrates with the envelope, never
  with the tool's logs or CLI rendering.

---

## 7. Events

Events on a bus/signal channel are contracts too:

- Each event has a **stable name**, a **typed payload schema**, a documented **publisher**, and documented
  **subscribers** — the *event catalog*.
- Events follow the same versioning and compatibility rules (§4–§5): additive payload changes are safe;
  renames/retypes are breaking and versioned.
- A publisher does not assume who is listening; a subscriber validates the payload and tolerates additive
  changes. An event with no registered subscriber, or a subscriber for an unpublished event, is **drift**
  (§11).

---

## 8. HTTP / REST Conventions

For HTTP APIs (the OpenAPI document is authoritative, §3):

- **Resources & verbs.** Nouns for resources; `GET` (safe), `POST` (create/action), `PUT`/`PATCH`
  (replace/modify), `DELETE`. Correct, specific **status codes** (201 create, 204 no-content, 400/422
  validation, 401/403 authz, 404, 409 conflict, 429 rate-limit).
- **Errors are structured** — **RFC 9457 problem-details** (`type`, `title`, `status`, `detail`,
  `instance`), never an HTML page or an ad-hoc blob; they explain what went wrong without leaking internals
  or secrets (Security & OpSec Standard §4).
- **Auth is scoped.** Endpoints declare the scope/permission they require; authorization is checked at the
  chokepoint (Security & OpSec Standard §5).
- **Pagination, filtering, idempotency.** List endpoints paginate deterministically; mutating endpoints
  that may be retried are **idempotent** (an idempotency key or natural upsert) so a retry is safe.
- **Versioned** (`/v1/…` or header), per §4.

---

## 9. Data Contracts & Persistence

- **Entities are typed contracts** — Field / Type / Notes, with constraints — defined in the data model
  (Documentation & Architecting Standard `02`).
- **Stable identifiers.** Use stable, non-reassigned IDs (e.g. UUIDs) for anything referenced across a
  boundary; never expose a volatile internal key as a contract.
- **The persistence schema is a contract**; **migrations are contract changes** — versioned, reversible
  where feasible, and following expand→migrate→contract (§4). A migration that drops/renames a column is a
  breaking change to anything reading it.

---

## 10. Validation

- **Validate at the boundary against the schema.** Untrusted input is parsed into the typed model and
  rejected if it doesn't conform (Security & OpSec Standard §3) — *fail closed* on a contract mismatch.
- **Both sides validate:** a producer validates the output it emits against the contract; a consumer
  validates the input it receives. A payload that fails its schema is an error, not something to
  best-effort interpret.
- **Schemas are shared, not re-derived.** Producer and consumer validate against the *same* schema artifact
  (§3), so "valid" means the same thing on both ends.

---

## 11. The Contract Registry & Governance

> **The contract is the schema; never screen-scrape a sibling's output** — and every contract is registered.

- **Single source of truth.** A contract registry records each contract: its schema, version, **producer**,
  and **consumers** (a producer/consumer matrix), plus the event catalog and any public profiles.
- **Every change is registered and impact-analyzed.** Changing a contract finds every affected producer and
  consumer *before* it lands; a breaking change is announced and versioned (§4). This is the cross-component
  guardrail the conformance/contract agent enforces.
- **Drift is a finding.** An integration doc that claims to emit a field nobody consumes, consume one nobody
  produces, or contradicts the registry, is drift — caught in review.

---

## 12. Per-Tool Requirements

Each tool's integration docs (`04`/`07`, Documentation & Architecting Standard) specify: the contracts it
**produces** (output envelope, events, API) and **consumes**, each with its schema, version, and an example;
its public output-envelope profile; and an entry in the contract registry (§11). The schemas live in the
repo under version control; the validation (§10) is tested.

---

## 13. Why This Is Right

Explicit, schema-defined, versioned, registered contracts mean a component can change its insides freely
while its interface stays stable; a consumer can build against a real schema and example instead of reverse-
engineering output; and a breaking change is impossible to ship by accident because the registry names
everyone it touches. That is what lets the system be assembled from independently-built parts that
nonetheless fit — "more than the sum of its parts" without becoming a tangle.

---

## Appendix A — Compatibility quick-reference

| Change | Compatibility |
|---|---|
| Add an *optional* request field / new endpoint / new event | **MINOR** (safe) |
| Add a field to a response / new enum value in a response | **MINOR** (safe) — consumers ignore unknowns |
| Relax input validation; widen what the producer accepts | **MINOR** (safe) |
| Remove / rename a field, endpoint, or event | **MAJOR** (breaking) |
| Change a field's type or meaning | **MAJOR** (breaking) |
| Make an optional request field required; tighten input validation | **MAJOR** (breaking) |
| Change an error's status/meaning | **MAJOR** (breaking) |

Breaking changes follow **expand → migrate → contract**, are versioned and announced, and are registered
with impact analysis before they land.
