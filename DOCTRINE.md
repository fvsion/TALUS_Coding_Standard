# TALUS DOCTRINE — the must-gate contract

> **Generated from `doctrine.toml` by `scripts/gen-doctrine.py` — do not edit by hand.** Regenerate with
> `python3 scripts/gen-doctrine.py`; `--check` verifies it is current (a CI / pre-commit gate).
>
> The flattened, always-loadable contract: every standard's hardest **must**-gates on roughly one screen,
> each citing its standard + § so the full rule and its rationale are one lookup away. A `must` is a gate
> (deviating needs an ADR). Read this first; then open only the `§` you need, never a whole standard file.
> This is the distillation; the standards are the source of truth.
>
> Standards Suite v1.3.

## A — Coding Standard (umbrella) · `A_TALUS_Coding_Standard.md`

- **[A1]** Determinism decides: behavior follows transparent, auditable, reproducible logic; an LLM never makes a decision (§2, §8).
- **[A2]** Dependencies point inward: the domain core depends on nothing — no framework, I/O, terminal, or datastore (§2, §4).
- **[A3]** Extend by addition, not modification: a new variant is a new unit behind an existing interface, never a new branch in a widening conditional (§2, §4).
- **[A4]** Everything a reasonable operator would change is a named variable with one definition site; no magic literals in business logic (§2, §4).
- **[A5]** Secure and OpSec by construction: validate untrusted input at the boundary, parameterize queries, encode output, scope-gate consequential actions, log to an immutable audit trail (§2, §8).
- **[A6]** Cross-platform by default: target macOS, Linux, and Windows from day one and isolate per-OS code behind one adapter; a platform-bound tool declares the restriction with a reason (§2, §3.1).
- **[A7]** One canonical toolchain per language with blocking CI gates; non-conforming code fails CI (§7).
- **[A8]** Every non-trivial project carries an Architecture/ suite; design precedes code and traces to a principle or an ADR (§9, §11).

## B — AI Coding Phase Guidelines · `B_AI_Coding_Phase_Guidelines.md`

- **[B1]** Work in bounded phases: each declares entry, scope in and out, one objective, exit criteria, and a verification step (§2).
- **[B2]** Cardinal rule: do one phase, verify it, record it, then stop for review; never roll into the next phase unprompted (§3).
- **[B3]** Size the phase to the model, and budget the cost of verifying it, not just writing it (§4).
- **[B4]** Verify with evidence, never 'looks done': tests, a run, green gates — and for a code phase, a diff-scoped auditor pass at the boundary, not deferred to the end (§6).
- **[B5]** Record every stop in the phase ledger (STATUS.md) so the build is resumable across sessions and models (§7).
- **[B6]** Keep the directive durable: presence (loaded directive) + salience (per-turn reminder) + re-anchor (STATUS.md) + enforcement (gates); subagents do not inherit the directive (§7.4).

## C — Documentation & Architecting · `C_Documentation_and_Architecting_Standard.md`

- **[C1]** Design precedes code: a non-trivial project is not ready to build without its design-spec set (§1, §3).
- **[C2]** Carry the mandatory minimum design-spec set (the 00–08 Architecture/ baseline), concern-driven and sized to the tool (§4, §10).
- **[C3]** Every material decision is an ADR, traceable — not folklore (§7).
- **[C4]** Every cross-component contract is a first-class, owned, versioned artifact in the registry (§9).
- **[C5]** Maintain STATUS and the build roadmap; the roadmap defines which phases exist and in what order (§11).

## D — Visual UX/UI · `D_Visual_UX_UI_Standard.md`

- **[D1]** The domain emits semantic roles and view-models; the adapter renders color, escape codes, or DOM — never the core (§2, §3).
- **[D2]** Severity color is reserved for severity, never decorative; one loud thing per surface (§2).
- **[D3]** A fully plain rendering (no color, no motion) always exists and is the guaranteed form for files, pipes, and reduced environments (§2, §4).
- **[D4]** Meet the accessibility floor — it is a gate, not a preference (§7).

## E — API & Data Contract · `E_API_and_Data_Contract_Standard.md`

- **[E1]** The contract is the schema: integrate against a typed, machine-readable schema, never a sibling's human-readable output (§1, §3).
- **[E2]** Contract-first: define and review the contract before building either the producer or the consumer (§2).
- **[E3]** Evolve compatibly; a breaking change is versioned, announced, and registered — never silent (§4, §5).
- **[E4]** One contract, two consumers: a producer emits the same envelope standalone or integrated, and never requires the rest of the system to exist (§1, §6).
- **[E5]** Every contract has a known producer and known consumers in the registry (§11).
- **[E6]** Validate every payload at the boundary against its schema (§10).

## F — Security & OpSec · `F_Security_and_OpSec_Standard.md`

- **[F1]** Secure by construction: parameterized queries, boundary input validation, output encoding, an authorization chokepoint (§1, §3).
- **[F2]** Least privilege and defense in depth; fail closed — on error or ambiguity, deny (§1).
- **[F3]** Secrets never touch source or logs; they load from a manager or the environment and are redacted everywhere (§4).
- **[F4]** Consequential actions are recorded to an immutable audit trail with an attributable, approved trigger (§6).
- **[F5]** Where a tool acts in a sensitive environment, OpSec is by construction: minimize footprint and on-disk residue, and clean up (§7).
- **[F6]** Security gates run in CI: secret scan, dependency audit, and injection lint where applicable (§10).

## G — Observability & Reliability · `G_Observability_and_Reliability_Standard.md`

- **[G1]** Observable by construction: structured, correlated telemetry (logs, metrics, traces) built in as code is written, sized to tier (§1, §3).
- **[G2]** Reliability is designed up front: timeouts, retries, idempotency, and graceful degradation are architectural choices (§2, §7).
- **[G3]** Define SLIs/SLOs and measure against them — not by vibes (§5).
- **[G4]** Every deploy is reversible with a tested rollback; an irreversible deploy is a design defect (§4, §8).
- **[G5]** Telemetry never carries secrets or sensitive data and is separate from the audit trail (§1; Security & OpSec Standard §4).
- **[G6]** Scope is proportional to tier — enough to operate the thing, never theater (§2).

## H — Git & Release Engineering · `H_Git_and_Release_Engineering_Standard.md`

- **[H1]** Trunk is always releasable: main is green at every commit; nothing that breaks a gate merges (§1, §2).
- **[H2]** Small, reviewable changes: one phase is roughly one branch and one PR (§1, §4).
- **[H3]** Conventional Commits; history is an attributable record, not a scratchpad (§3).
- **[H4]** SemVer plus a generated-from-history changelog; a release is a tag and a deterministic build from it (§5, §6, §7).
- **[H5]** Merge and release are blocked by mechanical gates, not goodwill (§1, §8).
- **[H6]** The dual-use git posture keeps internal context — the journal (`.talus/`), `.claude/`, and design-time artifacts (`Architecture/`, `Research_and_Planning/`) — out of public releases unless deliberately published (§9).

## I — Licensing & Editions · `I_Licensing_and_Editions_Standard.md`

- **[I1]** An edition is a seam, not a fork: one codebase; pro is strictly additive through defined extension points (§2, §3).
- **[I2]** The community edition builds, runs, and tests with pro entirely absent and never depends on pro (§2, §5).
- **[I3]** The community build is produced by excluding pro at build time — never by copying, never by a crackable runtime check (§5, §6).
- **[I4]** Each shipped artifact declares its license (SPDX) and edition (§7).

## J — LLM / AI Integration · `J_LLM_AI_Integration_Standard.md`

- **[J1]** The model is glue at a named seam: it never gates control flow, authorizes an action, or decides what/when/who (§1, §2).
- **[J2]** All model input is untrusted — any external text may carry instructions; defend against direct and indirect prompt injection (§1, §3).
- **[J3]** All model output is untrusted: validate it as data; never execute or obey it unchecked (§1, §4).
- **[J4]** Least privilege for the model; high-consequence actions stay behind a human and the deterministic core (§1, §5).
- **[J5]** Assume the context leaks: no secrets in prompts, and minimize the data placed there (§1, §6).
- **[J6]** Isolate the non-deterministic seam behind a port and evaluate the feature; do not assume it works (§1, §7).

## K — User Documentation · `K_User_Documentation_Standard.md`

- **[K1]** Ship the artifacts the tool's tier requires; the four jobs (overview, tasks, reference, learning) are served and findable (§8, §3).
- **[K2]** Each artifact holds its depth band and anti-scope: no artifact absorbs another's job; the README routes out, never swallows the manual (§4, §8).
- **[K3]** User docs hold the voice: show-don't-claim, no banned tells, limits stated plainly, and no em/en dashes or double-hyphen substitutes (§9).
- **[K4]** Docs match behavior: examples run, and a behavior change updates its docs in the same change (§11).
- **[K5]** The CLI `--help`/man surface derives from the RTFM — one source of truth (§6, §11).
- **[K6]** Every fact has one home, linked from the others — no copy-paste duplication (§2, §10).

## PY — Python (language standard) · `languages/Python_Coding_Standard.md`

- **[PY1]** Pick the distribution tier (library / application / platform) and match its layout, build backend, and dependency budget (§4, §5, §6).
- **[PY2]** Honor the version floors: operator side 3.12+, deployed floor justified down to 3.9; adopt the highest the target reality allows (§3).
- **[PY3]** Fully typed; Pyright (strict) passes in CI; a `# type: ignore` is reasoned and rare (§13).
- **[PY4]** Layered architecture enforced by import-linter; the domain imports no framework or adapter (§8, §23.3).
- **[PY5]** Volatile detail (terminal, subprocess, datastore, external-tool output) lives behind a port and adapter (§10).
- **[PY6]** User output goes through the presentation port; color is capability-gated (isatty / NO_COLOR) and degrades to plain for files and pipes (§18).
- **[PY7]** The canonical toolchain is the only path CI permits: ruff (lint + format), Pyright strict, pytest + coverage, uv lock, import-linter, secret scan, dependency audit, injection lint (§23.1).
- **[PY8]** Security coding: parameterized queries, boundary validation, subprocess argument lists (never shell=True with untrusted input), secrets out of source and logs (§25).
- **[PY9]** Cross-platform: declare supported OSes, guard POSIX-only imports with a fallback, and run a CI OS matrix across the declared platforms (§17.4).

---

Each line above is a **must** — a gate, not a suggestion. The bracketed handle (for example `[A3]`, `[PY7]`)
identifies the gate; the `§` points to the full rule in the named standard. 12 standards · 72 gates.
