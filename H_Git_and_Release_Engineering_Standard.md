# Git & Release Engineering Standard

> **How we use version control and ship releases — so the main branch is always releasable, every change is
> small, reviewed, and gated, and a release is a repeatable, auditable event.** Trunk-based development with
> short-lived branches; Conventional Commits; SemVer; a generated-from-history changelog; CI gates that
> block merge and publish; and the dual-use git posture that keeps internal build context out of public
> releases.
>
> Language-agnostic; under the `A_TALUS_Coding_Standard.md` umbrella (§11 Governance). **Mandatory.** "Must"
> is a gate; "should" is a strong default.
>
> Status: **Accepted, v1.2.1** (2026-06-26). Part of **Standards Suite v1.2.1** (was v1.0). v1.2.1 extends the
> dual-use posture (§9) to design-time artifacts (`Architecture/`, `Research_and_Planning/`).

---

## Contents

§1 Purpose & Principles · §2 Branching Model · §3 Commits · §4 Pull Requests & Review · §5 Versioning
(SemVer) · §6 Changelog · §7 Tagging & Releases · §8 CI/CD Gate Orchestration · §9 The Dual-Use Git Posture
· §10 Per-Tool Requirements · §11 Why This Is Right · Appendix A: commit / PR / release checklists

---

## 1. Purpose & Principles

A team — and a fleet of AI coding sessions — needs one shared discipline for how work enters the codebase
and how it ships. Without it, history is noise, the main branch is sometimes broken, and a release is a
nervous manual ritual. This standard makes the main branch **always releasable**, every change **small and
reviewed**, and every release **repeatable**.

Principles:

1. **Trunk is always releasable.** `main` is green and shippable at every commit; nothing merges that
   breaks a gate (§8).
2. **Small, reviewable changes.** Work lands in focused units — one phase, one feature, one fix — not giant
   drops. (This maps cleanly onto the AI Coding Phase Guidelines: one phase ≈ one branch ≈ one PR.)
3. **Everything is gated.** Merge and release are blocked by mechanical gates, not by goodwill.
4. **History is a record.** Commits and tags are a durable, attributable account of what changed and why —
   not a scratchpad.
5. **Releases are repeatable and auditable.** A version is a tag; a release is a deterministic build from
   that tag; the changelog says what changed.

---

## 2. Branching Model

**Trunk-based development** with short-lived branches:

- **`main` is the trunk** — protected, always green, the single source of releasable truth.
- **Short-lived branches** off `main` for each unit of work (`feat/...`, `fix/...`, `docs/...`,
  `chore/...`). They live hours-to-days, not weeks; they merge back via PR and are deleted.
- **No long-lived divergent branches.** Avoid GitFlow-style permanent `develop`/`release` branches and
  long feature forks — they accumulate merge debt. A long-running effort is *sequenced into phases that
  each land on trunk* (Phase Guidelines), behind a feature flag if a partial feature must not yet be
  active.
- **Release branches only when needed** — a maintenance branch (`release/1.x`) is created only to backport
  fixes to an older supported major; it is the exception, not the default flow.
- **Never commit directly to `main`** for non-trivial work; go through a branch + PR so the gates run.

---

## 3. Commits

- **Conventional Commits.** `type(scope): summary` — `feat`, `fix`, `docs`, `refactor`, `test`, `perf`,
  `build`, `ci`, `chore`. A breaking change is marked `type(scope)!:` or a `BREAKING CHANGE:` footer (this
  drives SemVer, §5).
- **Imperative summary**, ≤ ~72 chars, no trailing period: "add UCB scheduler", not "added"/"adds".
- **The body explains *why*** — the motivation and any non-obvious trade-off — not a restatement of the
  diff. Reference issues/ADRs.
- **Atomic commits.** One logical change per commit; don't mix a refactor with a feature. Keep the working
  tree green at each commit where practical.
- **Attribute AI-assisted work.** Commits produced with an AI agent carry an attribution trailer (e.g. a
  `Co-Authored-By:` line for the agent) so authorship is honest and history is auditable.
- **Never commit** secrets, credentials, or client/target data (Security & OpSec Standard §4/§8) — the
  secret-scan gate (§8) enforces this.

---

## 4. Pull Requests & Review

- **Every non-trivial change is a PR** against `main`, small enough to review well (a phase-sized unit, §1).
- **Green before review.** All CI gates (§8) pass before a human spends time; a red PR is the author's to
  fix.
- **Human review is required** — at least one reviewer who is not the author. The PR describes *what* and
  *why*, and how it was verified (the phase's verification evidence, Phase Guidelines §6).
- **The conformance agent assists, not replaces.** The review-time auditor runs the judgment checks a
  linter cannot and posts findings; a human still approves. Recommend-only — nothing auto-merges
  unreviewed.
- **Merge policy:** prefer **squash-merge** for a clean, linear trunk history (one logical change = one
  trunk commit with a Conventional-Commit title); keep merge commits only where preserving a branch's
  internal history matters. No merge with failing gates, ever.

---

## 5. Versioning (SemVer)

- **Semantic Versioning** `MAJOR.MINOR.PATCH`: **MAJOR** for a breaking change to a public contract,
  **MINOR** for backward-compatible capability, **PATCH** for backward-compatible fixes.
- **A breaking change to a public API/contract is a MAJOR bump and a logged event** — because consumers
  (sibling tools, clients) depend on it. The Conventional-Commit `!`/`BREAKING CHANGE` drives this.
- **Pre-1.0 (`0.y.z`)** signals "API still settling"; even so, document breaking changes. Cut `1.0.0` when
  the public surface is committed-to.
- **Editions version together** (Licensing & Editions Standard): community and pro ship the same version
  off one source; release notes call out what differs per edition.

---

## 6. Changelog

- **Keep a Changelog** format: a human-readable `CHANGELOG.md`, newest first, grouped by *Added / Changed /
  Deprecated / Removed / Fixed / Security*, with an **`[Unreleased]`** section that accrues during
  development.
- **Driven by Conventional Commits** but human-curated for the reader — the changelog is for *users*, not a
  raw commit dump.
- **Every release has an entry** with its version and date; **`Security`** changes are always called out.
- Breaking changes are prominent, with migration notes.

---

## 7. Tagging & Releases

- **A release is an annotated tag** `v<MAJOR.MINOR.PATCH>` on `main` (or a maintenance branch), matching
  the package/project version exactly.
- **The release procedure** (repeatable, ideally automated):
  1. Land all changes on `main` (green).
  2. Bump the version; finalize the `CHANGELOG.md` entry (move `[Unreleased]` → the version).
  3. Tag `v<version>` (annotated).
  4. **Build the deliverables deterministically from the tag** — both editions where applicable (Licensing
     & Editions Standard): the community artifact (with `pro/` excluded) and the pro artifact.
  5. **Generate supply-chain attestations** for each artifact (Security & OpSec Standard §3.1): an SBOM
     (CycloneDX/SPDX), a cryptographic signature (Sigstore/cosign), and signed build provenance (SLSA L2).
  6. Run the **release gates** (§8) — including **verifying** each artifact's signature + provenance;
     publish only if green — a wheel/sdist to the index (Tier 1), a container image (Tier 3), or a tagged
     checkout (Tier 2). The SBOM, signature, and provenance are published alongside each artifact.
  7. Publish the changelog / release notes.
- **Releases are immutable.** Never move a tag or re-publish a version; a mistake is a new patch.

---

## 8. CI/CD Gate Orchestration

The gates from the language and other standards run mechanically; the orchestration is **when** they run
and **what they block**.

- **On every PR (block merge):** lint + format, strict type-check, tests + coverage floor, import-boundary
  enforcement (language standard); secret scan + dependency/SCA scan + injection/SAST (Security & OpSec
  Standard §10); the **edition seam test** — a community build with `pro/` excluded that still passes
  (Licensing & Editions Standard §5); and for a docs/standards repo, the proprietary-fence/leak check.
  **Where the tool has them:** the **reliability tests** (timeouts/retries/idempotency/graceful shutdown —
  Observability & Reliability Standard §12), and — for a tool with an LLM seam — the LLM **adversarial/
  red-team eval**, **output-validation tests**, and **secret-in-prompt scan** (LLM / AI Integration
  Standard §8).
- **On merge to `main`:** the full suite again on trunk (catch interaction effects); main stays green.
- **On a release tag (block publish):** all of the above **plus** a clean deterministic build of every
  edition/artifact; **SBOM generation, artifact signing, and signed build provenance** for each artifact,
  with the gate **verifying** signature + provenance (SLSA L2 target; Security & OpSec Standard §3.1); the
  pre-release **security review** sign-off for high-risk tools (Security & OpSec Standard §10); and **for a
  Tier-3 service**, the **production-readiness review** and a **tested rollback** (Observability &
  Reliability Standard §11/§12), plus the **agency review** for any LLM seam (LLM / AI Integration
  Standard §8).
- **A missing gate is a finding.** No publish path skips the gates; no "force-merge" of a red PR without a
  recorded, risk-accepted exception.

---

## 9. The Dual-Use Git Posture

A repo serves two audiences, and what is committed differs by intent (the deployment model the standards
ship with):

- **Internal (team / solo dev) — what's committed.** The working-context home `.talus/` (doctrine + the
  `journal/`: phase ledger, build records, decision log) **and** `.claude/agents` are committed — they are
  the shared, attributable build history. A *vendored* copy of the standards (under `Standards/`) is
  **git-ignored** (re-pullable, pinned by reference), not committed.
- **Public post — what's stripped.** `.talus/` and `.claude/` are **internal and may be sensitive** (the
  journal especially); a public release is produced mechanically and contains **neither** — plus the
  proprietary-fence strip and (for code) the `pro/` exclusion. **Design-time artifacts are internal by
  default, too:** the `Architecture/` spec suite and the `Research_and_Planning/` design trail (briefs +
  design proposal, Documentation & Architecting Standard §3.1) are excluded from a public release unless a
  project *deliberately* chooses to publish its design (an open-source project may; the default is not to).
  Publishing is *producing the public tree*, never just pushing the working repo.
- **Never in any repo:** secrets, credentials, client/target data (Security & OpSec Standard). The
  secret-scan gate (§8) is the backstop.
- **`.gitignore` is deliberate:** generated artifacts, caches, local env, and the vendored standards are
  ignored; the working-context journal is *not* (internally) — it is the record.

---

## 10. Per-Tool Requirements

Each tool documents, in its `08_ROADMAP`/`09_DEVOPS` (Documentation & Architecting Standard): its branching
expectations (trunk-based by default), its versioning line and current version, its `CHANGELOG.md`, its
release procedure and where it publishes, and its CI gate set. A tool that deviates (e.g. a different
release cadence) records *why*.

---

## 11. Why This Is Right

Trunk-based flow with small, gated, reviewed changes keeps the main branch shippable and the history
honest; SemVer + a curated changelog tell consumers exactly what changed; tagged, deterministic, gated
releases make shipping a non-event instead of a gamble; and the dual-use posture means the team keeps a
rich, attributable build record while a public release carries none of it. The discipline is mechanical, so
it holds whether a frontier model, a local model, or a human is at the keyboard.

---

## Appendix A — Checklists

**Commit**

- [ ] Conventional-Commit `type(scope): summary`, imperative, ≤ ~72 chars.
- [ ] Body explains *why*; breaking change marked `!` / `BREAKING CHANGE:`.
- [ ] Atomic; AI-assisted work attributed; no secrets/client data.

**Pull request**

- [ ] Small/phase-sized; description = what + why + verification evidence.
- [ ] All CI gates green; conformance-agent findings addressed; ≥1 non-author reviewer approved.
- [ ] Squash-merge to a linear `main`; branch deleted.

**Release**

- [ ] `main` green; version bumped; `CHANGELOG.md` finalized (`[Unreleased]` → version).
- [ ] Annotated tag `v<semver>`; deterministic build of every edition from the tag.
- [ ] SBOM, signature, and signed build provenance generated **and verified** for each artifact (SLSA L2).
- [ ] Release gates green (incl. edition seam test + security sign-off where required); published; notes out.
- [ ] Tag/version immutable — fixes go in a new version.
