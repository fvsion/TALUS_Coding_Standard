---
name: talus-phase
description: >-
  Use when starting or continuing a non-trivial build: plan the work into bounded phases, do exactly one
  phase, verify it with evidence, then stop for review. Invoke whenever a request is larger than a quick
  throwaway, when resuming a build across sessions or models, or whenever you are tempted to one-shot a
  feature. It enforces the cardinal rule (one phase, then stop) and keeps the project resumable. For the
  full doctrine see Standards/B_AI_Coding_Phase_Guidelines.md; this skill is the actionable procedure.
---

# Skill: Phase a build

Drive a build in bounded, reviewable phases so the work stays correct, reviewable, and resumable no matter
which model is at the keyboard. This skill is the short procedure. The reasoning behind it lives in
`Standards/B_AI_Coding_Phase_Guidelines.md` — read it when you need the why; do not duplicate it here.

## The cardinal rule

**Do one phase, verify it, record it, stop.** Stopping at a clean phase boundary with a green verification
and a clear "next" is success, not incompleteness. Do not roll into the next phase on your own initiative.
A capable model may bundle a few tightly-related phases **only if it declares the set up front** and still
stops at the end of the set. A quick throwaway may be one-shotted — say so explicitly when you do.

## Steps

1. **Shape the phase before writing code.** State it in the template below. If any part is missing it is not
   a phase, it is an open-ended request — split or sharpen it. If the objective needs the word "and," it is
   probably two phases. If unsure whether it fits in one pass, it does not: split it.

   ```
   PHASE: <id> — <short title>
     Entry:     <preconditions; prior phase verified>
     Scope in:  <what this phase does>
     Scope out: <what it deliberately does not touch>
     Objective: <the one reviewable outcome>
     Exit:      <concrete, checkable conditions>
     Verify by: <the evidence that will prove exit — tests / run / gate>
   ```

2. **Size it to the model.** Frontier model: a coherent subsystem, lighter gates. Mid: one module with its
   tests. Small or local model: one file or function-cluster, verify before every stop. Account for the cost
   of *verifying*, not just writing — a phase you can write but not check is mis-sized.

3. **Do the phase, in dependency order.** Substrate and contracts before consumers; design before build;
   foundations before features. Build only on what already exists and is verified.

4. **Verify with evidence — never "it looks done."** Run the checks the phase calls for: tests pass (new
   behavior has new tests), the thing runs, and the language standard's CI gates are green (run the
   `talus-gates` skill). **For a code phase, also run the `talus-auditor` diff-scoped to this phase's changes
   — here, at the boundary, not deferred to the end** (a whole-repo auditor pass is for a milestone). Report
   the result with the actual output. If verification fails, fix within the phase or stop and report the
   failure honestly — never paper over it.

5. **Record completely, then stop.** Update the phase ledger `.talus/journal/STATUS.md` at every stop — the
   full entry: what the phase delivered, what verified it (with the evidence), and the next action. Keep the
   ledger **bounded**: when an effort finishes, demote its detail to a one-liner in `JOURNAL_INDEX.md` and
   invoke `talus-chronicler` to write the compacted record. A skipped or half-written ledger update means the
   phase is not done. Then report at the gate — what was done, the verification evidence, what is next, any
   decision the reviewer should weigh — and yield.

   ```
   ── on completion ──────────────────────────────────────────────
     Result:    <what was done>
     Evidence:  <verification output / gate result>
     Next:      <the next phase, per the roadmap>
     STOP for review.
   ```

## Boundary

This skill governs *how a session is run*, not what the code looks like. It pairs with the design agents
(`talus-architect`, `talus-scribe`) for the work inside a phase, the `talus-gates` skill for the mechanical
verification, and the `talus-auditor` subagent for the conformance judgment. The project's `08_ROADMAP`
defines *which* phases exist and in what order; this skill is *how to execute one safely*.
