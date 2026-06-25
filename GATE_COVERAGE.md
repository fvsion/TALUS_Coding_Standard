# TALUS GATE COVERAGE — the self-conformance audit

> **Generated from `doctrine.toml` + `coverage.toml` by `scripts/gen-coverage.py` — do not edit by hand.**
> Regenerate with `python3 scripts/gen-coverage.py`; `--check` verifies it is current (a CI / pre-commit gate).
>
> Every must-gate in [`DOCTRINE.md`](DOCTRINE.md) (handles `[A1]`..`[PY9]`) mapped to the arm that catches a
> violation. This is what makes "enforced, not aspirational" checkable: the generator fails if any gate has
> no coverage, so a gate cannot quietly go unenforced. Catch levels, strongest first:
>
> - **ci-gate** — a blocking automated gate (a tool returns pass/fail)
> - **auditor** — talus-auditor review-time judgment (a finding tied to a §)
> - **design** — caught at design time by talus-architect / talus-cartographer
> - **phase** — the talus-phase skill + Phase Guidelines process
> - **advisory** — a strong default with no named TALUS arm; justified per row
>
> **Coverage:** 22 ci-gate · 26 auditor · 16 design · 7 phase · 1 advisory (72 gates).
> 22 caught by a blocking automated gate, 49 by a systematic review/design/process arm, 1 advisory.

## A — Coding Standard (umbrella) · `A_TALUS_Coding_Standard.md`

| Gate | Must | Catch | Mechanism |
|---|---|---|---|
| `[A1]` | Determinism decides | `auditor` | talus-auditor: decomposable-decision and 'no LLM decides' judgment (cross-checks the J standard's seam rules); no linter can decide this. |
| `[A2]` | Dependencies point inward | `ci-gate` | import-linter (gates.toml `imports`, Python §23.3) fails a forbidden cross-layer import; talus-auditor confirms the domain is framework/I/O-free (§8). |
| `[A3]` | Extend by addition | `auditor` | talus-auditor §9 (SOLID): flags a widening if/match ladder where a strategy/registry belongs. |
| `[A4]` | Everything a reasonable operator | `auditor` | talus-auditor §11: flags magic literals in business logic and scattered os.environ reads. |
| `[A5]` | Secure and OpSec by construction | `ci-gate` | secret-scan + dep-audit + injection lint (gates.toml); talus-auditor §25 for boundary validation, output encoding, and the authorization chokepoint. |
| `[A6]` | Cross-platform by default | `auditor` | talus-auditor §17.4/§17.5: declared platforms (classifiers + README), per-OS code behind one adapter, guarded POSIX-only imports; the project's CI OS matrix is the blocking check. |
| `[A7]` | One canonical toolchain | `ci-gate` | this is the gate set itself: scripts/run-gates.py over gates.toml; non-conforming code fails CI. |
| `[A8]` | Every non-trivial project carries | `auditor` | talus-auditor flags a missing Architecture/ suite or README tier (§24); talus-architect/scribe produce it at design time (C standard). |

## B — AI Coding Phase Guidelines · `B_AI_Coding_Phase_Guidelines.md`

| Gate | Must | Catch | Mechanism |
|---|---|---|---|
| `[B1]` | Work in bounded phases | `phase` | talus-phase skill: the six-part phase template; an open-ended request fails the shape check before any code. |
| `[B2]` | Cardinal rule | `phase` | talus-phase skill + the stop-for-review gate (Phase Guidelines §3): the session stops at the boundary and yields. |
| `[B3]` | Size the phase to the model | `phase` | talus-phase skill step 2 (model-aware sizing, Phase Guidelines §4); the reviewer rejects a mis-sized phase at the stop. |
| `[B4]` | Verify with evidence | `phase` | talus-phase skill step 4: tests/run/green gates plus a diff-scoped talus-auditor pass at the boundary; the gate evidence line records a real run (run-gates.py). |
| `[B5]` | Record every stop | `phase` | talus-phase skill step 5 updates the STATUS ledger; talus-chronicler maintains the journal so the build is resumable. |
| `[B6]` | Keep the directive durable | `ci-gate` | install.sh installs the per-turn reminder hook and the default-on git pre-commit gate (run-gates.py --fast); the pre-commit + CI gate is the context-independent enforcement layer (Phase Guidelines §7.4). |

## C — Documentation & Architecting · `C_Documentation_and_Architecting_Standard.md`

| Gate | Must | Catch | Mechanism |
|---|---|---|---|
| `[C1]` | Design precedes code | `auditor` | talus-auditor flags missing design specs against C §3; talus-architect produces the design before build. |
| `[C2]` | Carry the mandatory minimum | `design` | talus-scribe authors the 00–08 Architecture/ baseline (C §4); talus-auditor flags its absence. |
| `[C3]` | Every material decision is an ADR | `design` | talus-architect authors ADRs (C §7); review flags an unexplained material decision with no ADR. |
| `[C4]` | Every cross-component contract | `design` | talus-cartographer owns the contract registry (C §9 / E §11) — a contract without a registered owner/version is flagged at design time. |
| `[C5]` | Maintain STATUS | `phase` | talus-phase updates STATUS at each stop; talus-chronicler maintains the roadmap/journal (C §11). |

## D — Visual UX/UI · `D_Visual_UX_UI_Standard.md`

| Gate | Must | Catch | Mechanism |
|---|---|---|---|
| `[D1]` | The domain emits semantic roles | `auditor` | talus-auditor §10/§18: the domain emits roles/view-models and the adapter renders; raw color/escape codes in the core are a finding. |
| `[D2]` | Severity color is reserved | `auditor` | talus-auditor §18 color discipline; a Visual-UX review confirms severity semantics (loud = important) hold. |
| `[D3]` | A fully plain rendering | `auditor` | talus-auditor §18: ANSI to a redirected file/pipe (color not gated on isatty / NO_COLOR) is a FAIL; the plain form is golden-file testable (§22.3). |
| `[D4]` | Meet the accessibility floor | `advisory` | no language-agnostic automated gate today: the adopting project runs accessibility tooling (e.g. axe/pa11y) and a Visual-UX review verifies D §7. The sole advisory residual — strong default, flagged honestly. |

## E — API & Data Contract · `E_API_and_Data_Contract_Standard.md`

| Gate | Must | Catch | Mechanism |
|---|---|---|---|
| `[E1]` | The contract is the schema | `design` | talus-architect/cartographer: integration is against a registered schema; talus-auditor flags code that screen-scrapes a sibling's human output. |
| `[E2]` | Contract-first | `design` | talus-architect designs and reviews the contract before either side is built (E §2). |
| `[E3]` | Evolve compatibly | `design` | talus-cartographer registers a breaking change (E §5); a schema-diff/compat check in the producer's CI is the recommended blocking gate. |
| `[E4]` | One contract, two consumers | `design` | talus-architect: the producer emits the same envelope standalone or integrated and never requires the rest of the system (E §6). |
| `[E5]` | Every contract has a known producer | `design` | talus-cartographer's registry is exactly this invariant: no contract without a documented producer and consumers (E §11). |
| `[E6]` | Validate every payload | `auditor` | talus-auditor §25: untrusted input validated at the boundary against its schema before it reaches the domain. |

## F — Security & OpSec · `F_Security_and_OpSec_Standard.md`

| Gate | Must | Catch | Mechanism |
|---|---|---|---|
| `[F1]` | Secure by construction | `ci-gate` | injection lint (raw-string SQL / non-parameterized Cypher fails CI, §23.1); talus-auditor §25 for boundary validation, output encoding, the authorization chokepoint. |
| `[F2]` | Least privilege and defense in depth | `auditor` | talus-auditor §25 judgment: over-broad scope/permissions, a single load-bearing control, default-allow on error. |
| `[F3]` | Secrets never touch source | `ci-gate` | secret-scan (gitleaks, gates.toml) fails a credential-shaped string in source; talus-auditor §16 flags secrets routed through logs. |
| `[F4]` | Consequential actions are recorded | `auditor` | talus-auditor / talus-architect: a consequential action without an immutable, attributable audit record is a finding (F §6). |
| `[F5]` | Where a tool acts in a sensitive | `auditor` | talus-auditor §25/§17: temp-artifact cleanup, on-disk residue, observable footprint for a tool in a sensitive environment (F §7). |
| `[F6]` | Security gates run in CI | `ci-gate` | secret-scan + dep-audit + injection lint run by run-gates.py over gates.toml (F §10). |

## G — Observability & Reliability · `G_Observability_and_Reliability_Standard.md`

| Gate | Must | Catch | Mechanism |
|---|---|---|---|
| `[G1]` | Observable by construction | `design` | talus-architect sizes telemetry to tier (G §3); talus-auditor §16 checks the two-stream logging discipline in code. |
| `[G2]` | Reliability is designed up front | `design` | talus-architect: timeouts/retries/idempotency/degradation are design choices (G §7); the production-readiness review (G §11) is the gate. |
| `[G3]` | Define SLIs/SLOs | `design` | the production-readiness review (G §11) requires declared SLIs/SLOs measured against; no code linter checks this. |
| `[G4]` | Every deploy is reversible | `design` | deploy-safety design + the production-readiness review (G §8/§11): a tested rollback is required before ship. |
| `[G5]` | Telemetry never carries secrets | `auditor` | talus-auditor §16 (sensitive data never travels through logging); secret-scan is a backstop over emitted telemetry. |
| `[G6]` | Scope is proportional to tier | `design` | talus-architect sizes the observability/reliability weight to the tool's tier (G §2); the PRR rejects theater or under-instrumentation. |

## H — Git & Release Engineering · `H_Git_and_Release_Engineering_Standard.md`

| Gate | Must | Catch | Mechanism |
|---|---|---|---|
| `[H1]` | Trunk is always releasable | `ci-gate` | branch-protection + the merge-blocking gate set (H §8): nothing that breaks a gate reaches main. |
| `[H2]` | Small, reviewable changes | `phase` | one phase is one branch and one PR (Phase Guidelines / H §4); PR review rejects a giant drop. |
| `[H3]` | Conventional Commits | `ci-gate` | a commit-message lint (e.g. commitlint) in CI rejects a non-conforming commit (H §3). |
| `[H4]` | SemVer plus a generated | `ci-gate` | the release tooling (tag-driven, changelog-from-history, deterministic build) is mechanical (H §5–§7). |
| `[H5]` | Merge and release are blocked | `ci-gate` | the CI gate orchestration blocks merge and publish (H §8) — the same run-gates set plus the per-standard gates. |
| `[H6]` | The dual-use git posture | `ci-gate` | the public release is produced mechanically (produce-the-public-tree, never push the working repo); a leak/visibility scan over the produced tree is the gate (strip-proprietary.sh --check here, or the project's equivalent), keeping the journal, .claude/, and design-time artifacts (Architecture/, Research_and_Planning/) out of public (H §9). |

## I — Licensing & Editions · `I_Licensing_and_Editions_Standard.md`

| Gate | Must | Catch | Mechanism |
|---|---|---|---|
| `[I1]` | An edition is a seam | `auditor` | talus-auditor reviews the pro/ seam as extension-by-addition (I §3): pro attaches through defined seams, never modifies core. |
| `[I2]` | The community edition builds | `ci-gate` | a community-edition build job (pro absent) that builds, runs, and tests green is the gate (I §5). |
| `[I3]` | The community build is produced | `ci-gate` | the build-time exclusion of pro/ plus a leak scan over the community artifact (the same one-source-strip-the-overlay pattern as strip-proprietary.sh) verifies no pro code ships (I §5/§6). |
| `[I4]` | Each shipped artifact declares | `ci-gate` | an SPDX/license-header check (e.g. reuse lint) over each artifact (I §7). |

## J — LLM / AI Integration · `J_LLM_AI_Integration_Standard.md`

| Gate | Must | Catch | Mechanism |
|---|---|---|---|
| `[J1]` | The model is glue at a named seam | `auditor` | talus-auditor: the LLM call site is a named, typed seam that gates no control flow and authorizes no action (J §2); an ambient model capability is a finding. |
| `[J2]` | All model input is untrusted | `auditor` | talus-auditor §25 + J §3: direct/indirect prompt-injection defense — external text reaching the model is treated as hostile. |
| `[J3]` | All model output is untrusted | `auditor` | talus-auditor §25 + J §4: model output is validated as data, never executed or obeyed unchecked. |
| `[J4]` | Least privilege for the model | `auditor` | talus-auditor: minimal tools/data/authority for the model; high-consequence actions stay behind a human and the deterministic core (J §5). |
| `[J5]` | Assume the context leaks | `auditor` | talus-auditor §25 + J §6: no secrets in prompts, data minimization; secret-scan is a backstop over prompt-building code. |
| `[J6]` | Isolate the non-deterministic seam | `design` | talus-architect places the model behind a port (umbrella Principle 2); an eval harness (J §7) is the evaluation gate. |

## K — User Documentation · `K_User_Documentation_Standard.md`

| Gate | Must | Catch | Mechanism |
|---|---|---|---|
| `[K1]` | Ship the artifacts the tool's tier requires | `ci-gate` | a docs-presence check (the tier-required artifacts from K §8 exist) plus an internal link-check (no broken cross-links, so the four jobs stay findable); talus-herald confirms each job is actually served. |
| `[K2]` | Each artifact holds its depth band | `design` | talus-herald (author + review) holds each artifact to its depth band and anti-scope (K §4–§8): a README growing into the manual, or a tutorial padded with reference, is a herald finding. |
| `[K3]` | User docs hold the voice | `auditor` | talus-herald review-time voice judgment — banned tells, show-don't-claim, honest caveats (K §9) — the judgment a linter cannot make; the no-dash sub-rule is mechanically backstopped by a grep gate (grep -nE '[–—]\| -- '). |
| `[K4]` | Docs match behavior | `ci-gate` | doc code blocks execute where a runner is feasible (K §11); talus-herald flags docs-behavior drift in review when no runner covers it. |
| `[K5]` | The CLI `--help`/man surface derives | `ci-gate` | a --help/man ↔ RTFM parity check where the tool has a CLI (K §6, §11): the help surface derives from the one reference, so a divergence fails the check. |
| `[K6]` | Every fact has one home | `design` | talus-herald: each fact has one home, linked from the others (K §2, §10); copy-paste duplication across the doc set is a finding. |

## PY — Python (language standard) · `languages/Python_Coding_Standard.md`

| Gate | Must | Catch | Mechanism |
|---|---|---|---|
| `[PY1]` | Pick the distribution tier | `auditor` | talus-auditor §4–6: tier, layout (src/ vs flat vs layered), build backend, and dependency budget fit the declared tier. |
| `[PY2]` | Honor the version floors | `auditor` | talus-auditor §3: pyproject requires-python vs README floor; ruff/pyright target-version pin the floor mechanically. |
| `[PY3]` | Fully typed | `ci-gate` | Pyright strict (gates.toml `type-check`, §13.2): a type error fails CI. |
| `[PY4]` | Layered architecture enforced by import-linter | `ci-gate` | import-linter (gates.toml `imports`, §23.3): a dependency arrow pointing the wrong way fails CI. |
| `[PY5]` | Volatile detail | `auditor` | talus-auditor §10: terminal/subprocess/datastore/external-tool output lives behind a port + adapter, not in the domain. |
| `[PY6]` | User output goes through the presentation port | `auditor` | talus-auditor §18: user output via the presentation port; color capability-gated (isatty / NO_COLOR), plain for files and pipes. |
| `[PY7]` | The canonical toolchain is the only path | `ci-gate` | the full gates.toml set via run-gates.py: ruff, Pyright strict, pytest+coverage, uv lock, import-linter, secret-scan, dep-audit, injection lint (§23.1). |
| `[PY8]` | Security coding | `ci-gate` | injection lint + secret-scan (gates.toml); talus-auditor §20/§25 for subprocess argument lists (never shell=True with untrusted input). |
| `[PY9]` | Cross-platform: declare supported OSes | `auditor` | talus-auditor §17.4: declared OSes, guarded POSIX-only imports with a fallback; the project's CI OS matrix across declared platforms is the blocking check. |

---

Read a row with its gate in `DOCTRINE.md`: the handle ties them together. A `must` here is enforced by the
named arm; the lone advisory (`[D4]`) is a strong default with no automated TALUS gate, justified in
its row. 72 gates · 12 standards.
