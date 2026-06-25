# User Documentation Standard

> **A tool is not finished when it works; it is finished when a stranger can install it, use it, look up its
> details, and learn it from the docs that ship with it.** User documentation is a first-class deliverable,
> built to the same bar as the code — not an afterthought, and not optional. Most of the industry, and the
> security industry in particular, has treated it as optional for decades; this standard does not. It defines
> four artifacts — the **README** (the front door), the **GUIDE** (how-to), the **RTFM** (the reference
> manual), and the **TUTORIAL** (the walkthrough) — their depth limits, and the voice they are written in.
>
> This governs the **external** docs a *user* reads. It is distinct from the **Documentation & Architecting
> Standard (`C`)**, which governs the **internal** `Architecture/` design specs a *builder* reads. Sits under
> the `A_TALUS_Coding_Standard.md` umbrella, a peer of `C`. Scope is **proportional to tier** (§8). **Mandatory**
> at the weight a tool's tier sets. "Must" is a gate; "should" is a strong default requiring a logged
> justification; "may" is latitude.
>
> Status: **Accepted, v1.0** (2026-06-26). Part of **Standards Suite v1.3**.

---

## Contents

§1 Purpose & Authority · §2 Principles · §3 The Four Artifacts & the Diátaxis Backbone · §4 The README ·
§5 The GUIDE · §6 The RTFM (Reference) · §7 The TUTORIAL · §8 Depth Limits & Tier Proportionality ·
§9 Voice & the Anti-AI-Tell Standard · §10 Structure, Layout & Cross-Linking · §11 Reference Accuracy &
Docs-Behavior Parity · §12 Per-Tool Requirements · §13 Verification & Gates · §14 Why This Is Right ·
Appendix A: annotated skeletons

---

## 1. Purpose & Authority

### 1.1 Why user docs are mandatory

Software that no one can install, operate, look up, or learn is unfinished, however good the code. The cost
of missing docs is paid by every user, repeatedly, forever: a tool that takes an hour to figure out instead
of five minutes has thrown away most of its own value. The security industry is the worst offender — powerful
tools shipped with a terse README and a shrug, their real capabilities locked behind tribal knowledge. This
standard treats the user-facing doc set as a gated deliverable, the same as tests or types.

### 1.2 What this governs

The four user-facing artifacts — **README, GUIDE, RTFM, TUTORIAL** — plus the **CLI `--help` / man-page
surface**, which is user documentation and derives from the RTFM (§6, §11). It governs *which* artifacts a
tool ships (by tier, §8), *what* each contains and how deep it goes (§4–§8), the *voice* they are written in
(§9), and how they stay *accurate* (§11).

### 1.3 Authority and the boundary with neighboring standards

Under the umbrella (§9 there). A peer of `C`, not a part of it. The line between the standards that touch
documentation:

| Standard | Owns | Audience |
|---|---|---|
| **`K`** (this) | README, GUIDE, RTFM, TUTORIAL, `--help`/man | the **user** |
| **`C`** Documentation & Architecting | the `Architecture/` design-spec suite, `Research_and_Planning/` | the **builder/maintainer** |
| **`D`** Visual UX/UI | how docs and output *look* (color, density, accessibility) | — |
| **`G`** Observability & Reliability | run-it-in-production runbooks | the **operator** |
| **`H`** Git & Release Engineering | `CHANGELOG.md`, release notes | the **consumer of a release** |
| **`F`** Security & OpSec | `SECURITY.md`, the disclosure policy | the **reporter/auditor** |

`K` links to a neighbor's artifact; it never duplicates it. A deviation from a `must` requires an ADR.

---

## 2. Principles

1. **Docs are a product.** They are designed, written to the gold standard, reviewed, and versioned like
   code — not generated once and abandoned.
2. **The reader is an operator under pressure.** Optimize for fast, trustworthy comprehension by someone who
   needs to get something done, not for completeness theater or marketing.
3. **Show, don't claim.** A benchmark table, a real command, real output, a cited source — these earn trust;
   adjectives do not. Replace every "fast/powerful/robust" with the number that proves it (§9).
4. **Honest over polished.** State limitations, caveats, and the cases where the tool is the wrong choice —
   plainly and early. A doc that hides the sharp edges costs the user more than one that names them.
5. **One source of truth per fact.** Each fact lives in exactly one artifact; the others link to it. Copy-paste
   is how docs rot — two copies drift, and the reader can't tell which is current.
6. **Right doc for the question.** The four artifacts answer four different questions (§3). Mixing them — a
   tutorial that stops to document every flag, a reference that editorializes — fails all of them.
7. **Docs match behavior.** A doc that lies is worse than no doc. Examples run as written; when behavior
   changes, the docs change in the same commit; drift is a defect (§11).
8. **Sized, not sprawling.** Every artifact has a depth band and an anti-scope (§8). The README is not the
   manual; the tutorial is not the reference. Discipline here is what keeps docs readable and maintainable.

---

## 3. The Four Artifacts & the Diátaxis Backbone

The set is built on **Diátaxis** (Procida's documentation framework), which separates docs by the reader's
purpose into four modes. Each maps to one artifact:

| Artifact | Diátaxis mode | The reader's question | The one job |
|---|---|---|---|
| **README** | overview / front door | "What is this, should I use it, how do I start *now*?" | Earn the next five minutes; route to the rest. |
| **GUIDE** | how-to (tasks) | "How do I install it and do *X*?" | Get a competent user through real tasks. |
| **RTFM** | reference (information) | "What *exactly* does this flag/key/API do?" | Be the exhaustive, authoritative lookup. |
| **TUTORIAL** | learning | "Teach me by doing." | Take a beginner end-to-end to a real result. |

**Do not mix the modes.** The single most common documentation failure is one artifact trying to do all four
jobs — a README that grows into a 2,000-line everything-doc, or a tutorial padded with every option. Keep each
artifact to its mode; link across them.

The fifth Diátaxis mode, **explanation** (understanding-oriented: "why is it built this way"), does not get
its own artifact by default. It lives as a short "How it works" section in the README and as strategy notes in
the GUIDE. A project with genuinely deep conceptual ground **may** add a dedicated explanation doc, but most
tools do not need one, and the design rationale belongs to `C` (the internal architecture docs), not here.

---

## 4. The README

**Job:** what this is, whether to use it, and how to start in sixty seconds. The README is the most-read file
in the project and usually the only one a hurried reader opens. It is technical and credibility-first — closer
to a strong security-tool README than to a marketing page — but with more named structure than most.

**Required structure** (a tool omits a part only when it does not apply):

1. **Name + a one-line statement** of what the tool is (the bold key term defined immediately).
2. **What and why**, in two or three sentences: the value, and why the approach matters.
3. **Credibility, front-loaded.** Proof the tool does what it claims: a benchmark table, real numbers, a
   worked result, provenance, or cited lineage. This is what converts a skeptical reader; it goes high, not
   buried at the bottom.
4. **(optional) A demo** — an asciinema cast, GIF, or screenshot, with **alt text** (§10).
5. **Install** — the shortest correct path, with the runtime floor and any prerequisites stated.
6. **Quickstart / Usage** — a few numbered, commented, copy-pasteable commands that produce a real result.
7. **Features** — a scannable list, or a **commands/options table** for a CLI.
8. **Configuration pointer** — where defaults live and how to override them (not the full key list; that is
   the RTFM).
9. **Security / OpSec note** — for a tool that touches sensitive context, what it reveals and leaves behind,
   and a link to `SECURITY.md` (`F`).
10. **Documentation** — links to the GUIDE, RTFM, TUTORIAL, and CHANGELOG.
11. **License.**

**Depth:** a **tier-banded target** (§8) — skimmable on one screen, roughly 150–250 lines for a Tier-2 tool.
This is a target enforced by judgment and the anti-scope, not a hard line cap; a legitimately rich front door
may run longer, a library's may be shorter. The test is "can a reader skim it in a minute and know whether to
proceed?"

**Anti-scope — the README must NOT:** be the manual (no exhaustive flag-by-flag listing — link to the RTFM);
be the tutorial (no long narrative walkthrough — link to the TUTORIAL); carry marketing fluff (§9).

---

## 5. The GUIDE

**Job:** get a competent user from installed to productive on real tasks. Conventionally `USER_GUIDE.md`.

**Required structure:**

- **Orientation** — a short "what this is and the mental model" (the campaign directory, the workspace, the
  core nouns) so later steps have context.
- **Prerequisites** — every dependency, version, and external tool, with how to obtain them and how to verify
  the install.
- **One section per real task**, each a **numbered, runnable recipe**: the goal, the command(s) with the
  flags that matter, the expected result. Tasks are ordered by the normal workflow.
- **Strategy / operational notes** — the judgment a reference can't give: when to use which option, the
  trade-offs, the gotchas.
- **Troubleshooting** — the failures users actually hit, and the fix.
- **A command reference pointer** — link to the RTFM for the exhaustive option list; the GUIDE shows the
  flags that matter for each task, not all of them.

**Depth:** grows with the number of real tasks, not with prose. Each recipe is bounded; a recipe that needs
a page of narrative is two recipes or belongs in the TUTORIAL.

**Anti-scope — the GUIDE must NOT:** become the reference (do not document every flag — link to the RTFM);
teach from zero (it assumes the reader did the README quickstart).

---

## 6. The RTFM (Reference)

**Job:** answer "what exactly does this do?" for every command, flag, key, and surface — completely and
authoritatively. Conventionally `REFERENCE.md`. This is the artifact the project's `--help` and man pages are
generated from or checked against (§11): **one source of truth, no drift.**

**Required structure** — exhaustive and lookup-shaped, not narrative:

- **Every command**, with **every flag**: name, type, default, and a one-line description.
- **Every configuration key**: name, type, default, effect, and the env var or CLI flag that overrides it.
- **Every environment variable** the tool reads.
- **Every exit code** and what it means.
- **The public API surface** (for a library): each function/class/endpoint, signature, parameters, return,
  and errors.
- Organized for lookup: tables, consistent ordering (alphabetical or grouped by command), one entry per item.

**Depth:** complete and flat. The RTFM has **no upper depth limit** — completeness beats brevity here; a
missing entry is a defect. It is the one artifact a reader scans, not reads.

**Anti-scope — the RTFM must NOT:** teach, narrate, or editorialize. "When should I use this?" is the GUIDE's
job. The RTFM states what the option *is*, not when to reach for it.

---

## 7. The TUTORIAL

**Job:** take a beginner end-to-end, by doing, to a real result they can see. Conventionally `TUTORIAL.md` or
`WALKTHROUGH.md`.

**Required structure:**

- **The scenario** — a concrete, realistic situation the reader is solving, with bundled **sample data** so
  they can follow exactly.
- **One coherent path**, in **numbered steps**, from a clean start to a finished result.
- **Real commands and real output** at each step — what the reader types and what they should actually see
  (not idealized or invented output).
- **A close** — "what you just did / what you learned," and where to go next (the GUIDE for more tasks, the
  RTFM for details).

**Depth:** exactly **one happy-path example**, bounded. It is allowed to be long if the path is long, but it
is one path.

**Anti-scope — the TUTORIAL must NOT:** be exhaustive (it shows *a* way, not every way); branch into every
option (that is the RTFM); turn into reference or strategy.

---

## 8. Depth Limits & Tier Proportionality

The doc set scales with the tool's distribution tier (the umbrella's tiers; mirrored in the language standards
and in `C`/`G`):

| Tier | README | GUIDE | RTFM | TUTORIAL |
|---|---|---|---|---|
| **Tier 1 — library** | **must** (rich) | should | **must** (API reference) | should |
| **Tier 2 — CLI / application** | **must** | **must** | **must** | **must** |
| **Tier 3 — platform / service** | **must** | **must** | **must** | **must** (heaviest; operator runbooks hand off to `G`) |

For a library, a thorough README quickstart **may** serve the TUTORIAL job, and the GUIDE **may** be a short
"common tasks" section — but the **RTFM (API reference) is mandatory**: a library nobody can look up is unusable.

**Small tools may merge files, never jobs.** A tiny CLI **may** fold the GUIDE into the README and run the
TUTORIAL as a README "Walkthrough" section. The **must** is that the four *jobs* are served and findable; the
*file layout* is proportional. A tool that merges states so in its README's Documentation section.

**The depth bands and anti-scopes (§4–§7) are the anti-sprawl discipline.** They exist because the default
failure mode of documentation is unbounded growth in the wrong place. Enforce them.

---

## 9. Voice & the Anti-AI-Tell Standard

User docs are the most-read prose a project ships and the most likely to read as machine-generated filler.
Slop erodes trust in the tool itself: a reader who senses the README was dashed off stops believing the
benchmark table. Write like an engineer who knows the tool and respects the reader's time. This specializes
the umbrella's "avoid AI tells" rule (§5.1 there) for documentation, and **`talus-herald` enforces it** on
every user-facing doc.

### 9.1 The principles

- **Lead with the substance.** Open with what the tool does and why it matters. No scene-setting, no "in
  today's fast-paced world," no throat-clearing.
- **Show, don't claim.** Replace every performance adjective with the measurement that earns it. "Fast"
  becomes "processes 1M rows/s on a laptop"; "scalable" becomes the number it scales to.
- **Be specific.** Real commands, real paths, real output, real numbers. Vagueness is the tell.
- **State the limits plainly, and early.** Name what the tool does badly, where it is the wrong choice, and
  the caveats. Honesty is the brand.
- **Active voice, the operator's vocabulary.** Name what the reader controls and recognizes.
- **Economy.** Cut filler. Do not restate the heading in the first sentence. Do not write a closing paragraph
  that re-summarizes what the reader just read.
- **No em or en dashes, and no dash substitutes, in user-facing docs (a hard rule).** The em dash is a leading
  AI tell, and so is the workaround for it: a spaced double hyphen (` -- `) reads exactly like one, and a spaced
  single hyphen (` - `) used to join two clauses does too. Banned in user docs: the em dash (—), the en dash
  (–), and the spaced double hyphen (` -- `); also avoid ` - ` as a clause connector. Use a colon, a comma,
  parentheses, or two sentences. This is mechanically checkable (§13) and applies to the README, GUIDE, RTFM,
  and TUTORIAL. Lists where lists help, prose where prose helps; the doc practices what it preaches.

### 9.2 The banned tells (illustrative, not exhaustive)

These read as machine-generated and are not permitted in user docs:

- **Filler adjectives/verbs:** *seamless / seamlessly, robust, powerful, cutting-edge, blazing(ly) fast,
  leverage (as a verb), elevate, unlock, supercharge, effortless, boasts*.
- **Throat-clearing:** *"In today's fast-paced world…", "It's worth noting that…", "Needless to say…",
  "At the end of the day…"*.
- **Cadence tells:** the rule-of-three padding (*"simple, powerful, and elegant"*), the *"It's not just X —
  it's Y"* construction, the summary paragraph that restates the intro, hedging stacks (*"might possibly
  perhaps"*), emoji used as bullet points.
- **Empty meta:** *"This section will discuss…", "As we can see…", "Let's dive in."*

The list is a smell test, not a denylist to game. The underlying rule is §9.1; a doc that avoids every banned
word but still says nothing concrete fails anyway.

### 9.3 Before / after

```
Before:  SyncTool is a powerful, cutting-edge solution that seamlessly streamlines your data
         workflows for maximum efficiency.
After:   SyncTool batches the API calls a sync would make one-at-a-time into a single request,
         so a 500-item sync drops from ~40s to ~3s.

Before:  In today's fast-paced environment, it's worth noting that our robust tool leverages
         advanced algorithms to deliver results.
After:   It ranks candidates by an order-n Markov model, so the most likely guesses come first.
         On a disjoint test set it cracks ~4x more than the next-best method at the same budget.

Before:  Installation is a breeze — simply run the command and you're good to go!
After:   Runtime is stdlib-only. Install with `pip install synctool`, or run `python -m synctool`
         from a clone without installing.
```

---

## 10. Structure, Layout & Cross-Linking

- **Root-level files.** `README.md`, `USER_GUIDE.md`, `REFERENCE.md` (the RTFM), and `TUTORIAL.md` live at the
  repository root so a host (GitHub, etc.) renders them and a reader finds them without hunting. A doc-heavy
  project **may** put the non-README files under `docs/`, but the README always stays at the root.
- **The README routes out.** Its Documentation section links the other three plus the CHANGELOG. Every artifact
  links back to the README and to the others it references.
- **One source of truth, then link.** A fact is documented once, in the artifact that owns it (a flag in the
  RTFM, a task in the GUIDE), and referenced elsewhere by link — never copy-pasted, which drifts.
- **`--help` / man derive from the RTFM** (§6, §11): one source, generated or checked, never independently
  hand-maintained.
- **Visual and accessibility defer to `D`.** Code blocks are runnable and copy-pasteable; tables carry
  reference data; every image, GIF, or cast has **alt text**; color and density follow the Visual UX/UI
  Standard. Docs meet the same accessibility floor as the product.

---

## 11. Reference Accuracy & Docs-Behavior Parity

A doc that lies is worse than no doc, because the reader trusts it and is led wrong.

- **Examples run as written.** Every command and code block is executable as shown, or is explicitly marked a
  fragment. Where feasible, CI executes the doc examples (a doctest-style runner) so a stale example fails the
  build.
- **Drift is a defect.** When behavior changes, its docs change in the **same commit/PR**. A behavior change
  that lands without its doc update is an incomplete change; `talus-herald` and `talus-auditor` flag it.
- **`--help` / man match the RTFM.** Generate them from a single source, or run a parity check that fails when
  they diverge.
- **Docs are versioned.** A doc states the version it describes; the docs for `vX` are not silently serving
  `vY`. Release docs track the release (`H`).

---

## 12. Per-Tool Requirements

Each tool documents, by its tier (§8):

- The **artifacts it ships** and where they live; if it merges files, the README's Documentation section says so.
- A **library** ships an API reference (the RTFM), generated from docstrings or hand-authored, kept in parity
  with the code.
- A **platform** ships operator docs that **hand off** to the Observability & Reliability Standard's runbooks
  (`G`) rather than duplicating them; `K` covers the user/operator-of-the-product surface, `G` covers
  run-it-in-production.
- A tool that deviates from its tier's doc set (e.g. an internal tool with no public README) records *why*,
  the same as any `must` deviation (§1.3).

---

## 13. Verification & Gates

Two enforcement arms, the same split the suite uses everywhere (the umbrella's governance): mechanical gates
for what a machine can check, and `talus-herald` review for the judgment a linter cannot make.

**Mechanical (ci-gate / mechanically checkable):**

- **Presence** — the tier-required artifacts exist (a docs-presence check against §8).
- **Links resolve** — no broken internal links across the doc set (a link-check).
- **No em/en dashes or double-hyphen** — the user docs contain no em (—) or en (–) dash and no spaced double
  hyphen (` -- `) (§9.1); a grep gate (`grep -nE '[–—]| -- '`). The ` - ` clause-separator is a voice-review
  check, not a grep, to avoid false positives on tables and numeric ranges.
- **Examples run** — doc code blocks execute where a runner is feasible (§11).
- **`--help` ↔ RTFM parity** — the CLI help/man match the reference (§11), where the tool has a CLI.

**Judgment (`talus-herald` review):**

- The four **jobs are served** for the tool's tier, and each artifact stays in its mode (§3) and its
  **depth band + anti-scope** (§4–§8).
- The README is **credibility-first** and routes out (§4).
- The **voice** holds — no AI tells, show-don't-claim, honest caveats (§9).
- **Docs match behavior** — no drift from the code as it stands (§11).

### 13.1 Must-gates (the `K` contract)

- A tool ships the **artifacts its tier requires** (§8); the four **jobs** are served and findable.
- Each artifact respects its **depth band and anti-scope** (§4–§8) — no artifact absorbs another's job.
- User docs hold the **voice** (§9): show-don't-claim, no banned tells, limits stated plainly, **and no em or
  en dashes or double-hyphen substitutes** (` -- `; avoid ` - ` clause connectors too) — the first three
  mechanically checked.
- **Docs match behavior**: examples run, and a behavior change updates its docs in the same change (§11).
- The **`--help` / man surface derives from the RTFM** — one source of truth (§6, §11).
- Every fact has **one home**, linked from the others — no copy-paste duplication (§2, §10).

---

## 14. Why This Is Right

Documentation is where the engineering finally meets the person it was built for, and it is the gap the
industry most reliably leaves open — a great tool that loses most of its value because no one can tell what it
does or how to drive it. Making the doc set a sized, voiced, accurate, **gated** deliverable closes that gap:
the four artifacts each answer one real question, the depth limits keep them readable and maintainable, the
voice keeps them trustworthy, and the parity rules keep them true. A tool documented this way is adopted
faster, trusted more, and supported less — and the security tool that ships docs this good stops being the
exception.

---

## Appendix A — Annotated skeletons

**README.md** (Tier 2; §4)
```
# <name>
<one line: what it is>

<2–3 sentences: what + why it matters>

## <Credibility>           # benchmark table / real numbers / provenance — high, not buried
## Install                 # shortest correct path + runtime floor
## Usage                   # numbered, commented, runnable quickstart
## Features | Commands      # scannable list, or a CLI options table
## Configuration           # where defaults live + how to override (pointer, not the full list)
## Security / OpSec        # what it reveals/leaves behind; link to SECURITY.md   (if applicable)
## Documentation           # links: GUIDE · RTFM · TUTORIAL · CHANGELOG
## License
```

**USER_GUIDE.md** (§5)
```
# <name> — User Guide
## What <name> is          # the mental model + core nouns
## Prerequisites           # deps, versions, external tools, how to verify
## <Task 1> … <Task N>     # one section per real task: a numbered runnable recipe
## Strategy / operations   # the judgment: when to use what, trade-offs, gotchas
## Troubleshooting         # the failures users hit + the fix
## Command reference       # pointer to REFERENCE.md
```

**REFERENCE.md** (the RTFM; §6)
```
# <name> — Reference
## Commands                # every command → every flag (name · type · default · effect)
## Configuration keys      # every key → type · default · effect · override
## Environment variables   # every var the tool reads
## Exit codes              # every code → meaning
## API                     # (library) each surface: signature · params · returns · errors
```

**TUTORIAL.md / WALKTHROUGH.md** (§7)
```
# <name> — Walkthrough
## The scenario            # concrete situation + bundled sample data
## 0 … N  <steps>          # one path, numbered; real commands + real output each step
## What you did / next     # recap + where to go (GUIDE, RTFM)
```
