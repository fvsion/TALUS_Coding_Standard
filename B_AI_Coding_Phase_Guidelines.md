# AI Coding Phase Guidelines

> **How to drive an AI coding agent through a build in bounded, gated phases — so the work is correct,
> reviewable, and resumable regardless of which model is at the keyboard.** Large builds exceed any
> model's reliable context and attention; phasing is how we keep quality constant from a frontier model
> down to a small local one. This is methodology, not code style: it governs *how a session is run*, not
> what the code looks like.
>
> Language- and tool-agnostic; sits under the `A_TALUS_Coding_Standard.md` umbrella. It pairs with the
> **Documentation & Architecting Standard** (a project's `08_ROADMAP` defines the phases; this defines how
> an agent executes one). **Must** is a gate; **should** is a strong default.
>
> Status: **Accepted, v1.3** (2026-06-26). Part of **Standards Suite v1.3** (was v1.2). v1.2 added the
> per-phase conformance review (§6) and the directive-durability model (§7.4); **v1.3** adds the build-loop
> discipline — shape-first + record-completely musts (§3) and the chronicler-cadence rule (§7.1).

---

## Contents

§1 Why Phase-Gate AI Builds · §2 Anatomy of a Phase · §3 The Cardinal Rule: One Phase, Then Stop · §4
Model-Aware Phase Sizing · §5 Dependency-Ordered Sequencing · §6 Verification Gates · §7 Phase Records
(Resumability) · §8 Relationship to the Build Roadmap · §9 Anti-Patterns · §10 Why This Is Right ·
Appendix A: the phase template

---

## 1. Why Phase-Gate AI Builds

An AI coding agent has three hard limits a human supervisor must design around: a **finite context
window** (it cannot hold a whole large project), **degrading attention** over a long generation (quality
drops as a single turn sprawls), and **no durable memory** between sessions (each start is cold). Left
unmanaged, these produce the familiar failure: an agent runs far past where it should have stopped,
compounds an early wrong assumption across thousands of lines, and leaves work no one can review or
resume.

**Phasing is the control system.** A phase bounds *what one session does* to a unit the model can hold,
execute, and verify reliably — then hands control back. This does three things at once: it keeps each unit
within the model's competence, it creates a review gate before errors compound, and it produces a durable
record so the next session (or a different model) resumes cleanly. The discipline matters *more*, not
less, as the model gets weaker: a frontier model may self-pace tolerably; a small local model
(`qwen3-27b`-class) will not, and relies on these rules being explicit and mechanical.

---

## 2. Anatomy of a Phase

A phase is a bounded unit of work with six declared parts. If any is missing, it is not a phase — it is
an open-ended request, which is the thing this standard exists to prevent.

1. **Entry state / preconditions** — what must be true to start (prior phase complete and verified,
   contracts available, design locked).
2. **Scope — explicitly in *and* out.** A short statement of what this phase will do, and a short list of
   what it deliberately will *not* (so the agent does not drift into adjacent work).
3. **A single coherent objective** — one outcome a reviewer can evaluate as done-or-not. "Lay the
   foundation," not "improve the project."
4. **Exit criteria** — the concrete, checkable conditions that mean the phase is finished.
5. **A verification step** (§6) — the evidence that the exit criteria are met (tests pass, the gate is
   green, the app runs).
6. **A stop-for-review gate** (§3) — the agent stops and reports; a human reviews before the next phase.

---

## 3. The Cardinal Rule: One Phase, Then Stop

**An agent executes one phase — or a small, explicitly declared set of phases — then stops and reports for
human review before proceeding.** This is a `must`, and it is stated mechanically because weaker models
will not infer it:

- **Shape the phase first (§2).** Before writing code, state the phase in the six-part template — Entry,
  Scope in, Scope out, Objective (one), Exit, Verify-by. A phase you cannot shape is an open-ended request,
  the exact failure this standard exists to prevent; split it until you can. This is a `must`, not a
  formality: an unshaped phase is the first domino of an unreviewable build.
- **Do the phase. Verify it. Record it. Stop.** Do not roll into the next phase on your own initiative.
- **Record completely (§7).** At the stop, update the phase ledger with what the phase delivered, the
  verification evidence, and the next action — *and* demote any now-finished effort's detail to the rolling
  index so the ledger stays bounded (§7.1). A skipped or half-written ledger update is an unfinished phase.
- **Stopping is success, not incompleteness.** A clean stop at a phase boundary with a green verification
  and a clear "next" is the desired end state of a session, not a failure to finish.
- **Report at the gate:** what was done, the verification result (with evidence), what is next, and any
  decision the reviewer should weigh. Then yield.
- **Bundling is allowed but bounded.** A capable model may execute several tightly-related phases in one
  session *if it declares the set up front* and still stops at the end of the set for review — never an
  open-ended "keep going."

---

## 4. Model-Aware Phase Sizing

The right phase size is **the most a given model can hold in context, execute coherently, and verify in a
single pass — and no more.** That ceiling moves with the model, so phase sizing is explicitly capability-
aware:

| Model capability | Phase size | Gating density | Verification |
|---|---|---|---|
| **Frontier** (large context, strong attention) | Larger — a coherent subsystem or several related units | Lighter — stop at meaningful subsystem boundaries | Self-directed but still evidence-backed |
| **Mid** | Moderate — one module/feature with its tests | Stop at each module boundary | Explicit gate each phase |
| **Small / local** (`qwen3-27b`-class) | Small — one file or one function-cluster, tightly scoped | Tight — stop frequently, re-orient often | Spelled-out, step-by-step; verify before every stop |

Sizing heuristics (all models):

- **If you are unsure whether a phase fits, it does not — split it.** Two verified small phases beat one
  unverifiable large one.
- **Scope to one reviewable outcome.** If the phase needs the word "and" to describe its objective, it is
  probably two phases.
- **Smaller models get more explicit everything**: narrower scope, more numbered steps, more frequent
  stops, and verification described concretely rather than assumed. The guidelines do the planning the
  model cannot.
- **Account for verification cost in the budget**, not just the writing — a phase the model can write but
  not check is mis-sized.

### 4.1 Operating under a constrained context window

Context budget is itself a model-capability axis — a small local model has far less working room than a
frontier one, and even a large window costs per token and degrades as it fills. Operate to keep the *working
set* small, not just the phase:

- **Read by section, not whole-file.** Pull the part of a standard or spec the work touches — its Contents /
  section map, then the relevant `§` — rather than loading the whole document. A single large standard read
  in full can dominate a small window; the same answer usually lives in one section. (The standards are
  section-addressable by design — Documentation & Architecting Standard §6; the umbrella's canonical section
  framework names which `§` owns which concern.)
- **Route a heavy read into an isolated subagent.** When a task genuinely needs a large document or a
  whole-repo pass (e.g. a conformance review), run it in a subagent whose separate context absorbs the big
  read and returns only the digest — the main thread never pays for it.
- **Keep stale context out.** Abandoned approaches and resolved errors charge every later turn; shed them at
  the phase boundary (§3), which is the natural place to drop them.

---

## 5. Dependency-Ordered Sequencing

Phases are ordered so each builds only on what already exists and is verified — the order that minimizes
rework:

- **Substrate and contracts before consumers.** Build the shared state/contract a thing depends on before
  the thing. A consumer built against an unwritten contract is rework waiting to happen.
- **Design before build.** A project's architecture (its `Architecture/` suite) is complete before its
  implementation phases begin; an algorithm's research brief precedes its implementation.
- **Foundations before features.** Project scaffolding, the typed config layer, the domain core, and the
  ports come before the features that ride on them.
- **Define the order once, in the roadmap** (§8), and follow it; do not re-derive sequencing per session.

---

## 6. Verification Gates

**No phase is complete without evidence.** "It looks done" is not a verification. Every phase ends by
demonstrating its exit criteria with a concrete check appropriate to the work:

- Tests pass (and new behavior has new tests); the language standard's CI gates are green.
- The thing runs — the app starts, the command produces the expected output, the build succeeds.
- For a code phase, run the **conformance review a linter cannot do** — the review agent (e.g. `talus-auditor`),
  **scoped to this phase's diff** — *at this boundary*, not deferred to the end. The mechanical gates and the
  diff-scoped review are *both* part of per-phase verification; a build that defers all review to the final
  phase has compounded whatever it got wrong. (A whole-repo review belongs at a milestone or before "done.")
- A documentation/spec phase passes its own mechanical check (e.g. links resolve, a required structure is
  present, a packaging/strip gate is clean).
- The verification result is **reported with the evidence**, not merely asserted.

If verification fails, the phase is not done: fix within the phase, or stop and report the failure
honestly (with the output) — never paper over it to reach the gate.

---

## 7. Phase Records & Working-Context Artifacts (Resumability)

Because the next session may be a different model — or the same model with no memory — the **project itself**
must carry everything needed to resume: a durable record of where the build is and how it got there. The
chat history is not the source of truth; the repo is.

### 7.1 The working-context artifact set

A well-run build maintains a small, named set of **working-context artifacts** — the "do it right"
continuity kit — alongside the code and the `Architecture/` suite. Each is updated as part of finishing a
phase (§6); the record is a phase deliverable, not an afterthought.

- **The orientation file** — the auto-loaded `CLAUDE.md` (or the coding agent's equivalent project-entry
  doc). It says what the project is and **points into** the rest of the kit. It stays *lean*: a map, not a
  dumping ground. Critically, it does more than describe: it **directs** the session. Installed standards and
  available agents do nothing on their own, so the orientation file is where the model is told which
  standards to consult, when to use the design and review agents, and to work in reviewed phases rather than
  one-shotting. A project that adopts these standards extends this file with that directive, append-only, so
  it never clobbers existing content.
- **The phase ledger** (the status/next-steps ledger) — the canonical record of where the build stands:
  every phase's state, what it delivered, what verified it, and the next action (the Documentation &
  Architecting Standard's status ledger, §11 there). One per project, named consistently (e.g. `STATUS.md`).
  Updated at **every phase stop** — it is *where phases are tracked*. It stays **bounded**: keep the current
  state, the next action, and a short window of recent phases inline, and roll older phase detail into the
  compacted records + rolling index (below), read only when the history is needed. An unbounded ledger
  becomes a context cost on every resume — the very thing this kit exists to avoid.
- **Compacted-conversation records** — durable, human-written narratives of how the project was built and
  why (distinct from a model's automatic context compaction). Use **both** granularities: a **sub-compact
  per effort** (`COMPACTED_<effort>.md`), plus a **rolling index** (`JOURNAL_INDEX.md`) that gives the
  one-paragraph "where are we" and links the sub-compacts and the phase ledger.
  **Cadence (a `should`, and a `must` when a weaker model drives):** write the sub-compact at **every effort
  boundary**, not only at large milestones — and whenever the ledger's inline recent window grows past a few
  efforts (that growth is the signal to demote and record). The **`talus-chronicler` agent** writes these from
  the artifacts (git history, the ledger, the files produced); invoke it at each effort boundary. The
  **driving session owns the tick-by-tick `STATUS.md`** at each phase stop; the chronicler owns the narrative
  and the index — keep the two roles distinct so neither is skipped. Sparse, milestone-only records are the
  anti-pattern: they lose the *why* and let the phase discipline drift unobserved.
- **The decision log** — an append-only narrative of consequential choices and their *why*. Formal ADRs
  live in the `Architecture/` suite (Doc&Arch Standard §7); the decision log is the running story around
  them.
- **Archived plans** — the per-task plan files, kept so a decision's rationale and scope survive the
  session that produced them.

### 7.2 Where they live: `.talus/`

These artifacts have **one canonical home: `.talus/`** — a framework-controlled dotfolder that is part of
the TALUS SDLC the way `.git/` belongs to git or `.github/` belongs to GitHub. Adopting these standards
*means* using `.talus/`; the name is fixed, so every project looks the same and the shipped agents can rely
on a known path. It is chosen so working context neither clutters the working root nor squats in a
directory another tool owns:

- **Not the working root.** The root holds deliverables, the lean orientation file, and the standard tool
  dotfolders — not a pile of session notes.
- **Not `.claude/`.** That directory is reserved for the coding agent's own files (subagents, settings,
  commands, hooks); do not repurpose it for project notes. (Root and nested `CLAUDE.md` files are the
  exception — the agent auto-loads them, so they stay where it expects, kept lean and pointing into `.talus/`.)
- **`.talus/` is ours.** Everything that is *how we work on this project* — and not a deliverable or the
  coding agent's own config — lives here.

Rule of thumb: if a file is *how we work on this project* rather than *the project itself* or *the coding
agent's configuration*, it lives in `.talus/journal/` — not the root, not `.claude/`.

### 7.3 `.talus/` structure and lifecycle

- **Top level** — project-wide context every session should see (e.g. a doctrine/orientation overlay or a
  shared contract registry an adopter installs once).
- **`journal/`** — the per-project working artifacts: the phase ledger (`STATUS.md`), the compacted-convo
  records + the rolling `JOURNAL_INDEX.md`, the decision log, and archived plans.
- **Privacy (it's internal).** The `.talus/` *convention* is public — it is named in this standard and the
  shipped agents use it. A given project's `.talus/` *contents* are not: they are committed for team/solo
  dev (the shared build history) but **removed entirely for a public release** (the journal especially is
  sensitive). The folder is standard; what a project puts in it is private.

### 7.4 Keeping the directive effective (durability)

The orientation file (§7.1) only works if the model actually *attends* to it. An auto-loaded directive is
durable against deletion but not against **decay**: in a long or compacted session it is still present but
low-salience (the "lost in the middle" effect), so a model can drift back to one-shotting even with good
guidance loaded. Defend the core directives in **four layers**, weakest to strongest:

- **Presence — the orientation file**, kept *lean*. It is re-injected each session and after compaction; a
  short directive re-weights far better than a long one. This is the floor, not the ceiling.
- **Salience — a per-turn hook.** A `UserPromptSubmit` hook (Claude `.claude/settings.json`; Codex
  `.codex/hooks.json` — both inject the hook's stdout as context) re-states the core rule at the *most recent*
  position in context **every turn**, where attention is highest, so it survives window-fill and compaction.
  This is the real durability lever; ship it **on by default**.
- **Re-anchor — the phase ledger.** The build state lives in `STATUS.md`, not the chat (§7); re-reading it at
  each phase boundary recovers "where am I / what's next" even after a summary blurs the conversation.
- **Enforcement — a mechanical gate.** A git pre-commit hook and CI run the gates **regardless of what the
  model remembers** — the only context-independent guarantee. Reserve it for the non-negotiables.

One caveat the layering does not fix: a **spawned subagent does not inherit the parent's orientation file or
hook** — it sees only its own prompt and the files it reads. So an agent meant to enforce a standard must
*read that standard itself* (the `talus-auditor` does), never assume the directive reached it.

This is what makes the build portable across models and sessions — the project, not the chat history, is
the source of truth.

---

## 8. Relationship to the Build Roadmap

These guidelines and a project's roadmap are complementary, and the boundary is clean:

- **The roadmap (`08_ROADMAP_AND_MILESTONES`, Documentation & Architecting Standard §4)** defines *what* to
  build and *in what order* — the phases, their exit criteria, and the load-bearing seams. It is
  project-specific and authored during design.
- **These guidelines** define *how an AI session executes a phase safely* — sizing, the stop gate,
  verification, and the record. They are project-agnostic and constant.

Roadmap = the route; these guidelines = how to drive it. An agent reads the roadmap to know which phase is
next, and reads these guidelines to know how to run it and when to stop.

---

## 9. Anti-Patterns

- **The runaway session.** Executing phase after phase with no stop, compounding an early error. The
  cardinal rule (§3) exists to prevent exactly this.
- **The fuzzy phase.** No explicit scope or exit criteria, so "done" is unknowable and the agent drifts.
- **Building on an unwritten contract.** A consumer ahead of its substrate/contract — guaranteed rework
  (§5).
- **Skipping verification.** Declaring done without evidence; or worse, trimming scope silently to reach a
  green gate.
- **Phase too big for the model.** Sized to what the model can *write* but not *hold or verify* — split it
  (§4).
- **Amnesiac handoff.** Stopping without updating the record, so the next session re-derives context and
  repeats work (§7).

---

## 10. Why This Is Right

Bounded, verified, recorded phases turn an unbounded generative process into an auditable, resumable
build. The same project can be advanced by a frontier model in large strides or a small local model in
careful steps, and the output holds the same quality bar either way — because the discipline lives in the
*method*, not in any one model's judgment. That is what lets these standards be used by whoever, or
whatever, is doing the building.

---

## Appendix A — The phase template

A session should be able to state its phase in this shape before starting work, and fill the result before
stopping:

```
PHASE: <id> — <short title>
  Entry:     <preconditions; prior phase verified>
  Scope in:  <what this phase does>
  Scope out: <what it deliberately does not touch>
  Scale:     <expected input size / growth — for an algorithmic or data-path phase; else n/a>
  Budget:    <permissible time/space complexity class — for such a phase; else n/a>
  Objective: <the one reviewable outcome>
  Exit:      <concrete, checkable conditions>
  Verify by: <the evidence that will prove exit — tests / run / gate>
  ── on completion ──────────────────────────────────────────────
  Result:    <what was done>
  Evidence:  <verification output / gate result>
  Next:      <the next phase, per the roadmap>
  STOP for review.
```

**`Scale:` / `Budget:` are conditional.** Fill them for any phase that writes algorithmic or data-path code:
state the expected input size and the permissible time/space complexity class *before* writing it, so the
design is chosen against a budget rather than rationalized after. A docs/config/wiring phase marks them
`n/a`. This is generic engineering discipline — it makes Principle 8 (efficiency by design; measure before
you optimize) mechanical at the phase boundary.
