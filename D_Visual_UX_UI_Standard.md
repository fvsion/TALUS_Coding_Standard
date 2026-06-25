# Visual UX/UI Standard

> **How our tools look and behave — terminal and graphical alike.** A single, language-agnostic standard
> for visual and interaction design across both media: a CLI's terminal output and a web/desktop frontend
> share one set of principles, then specialize. The thesis: an interface is a **forensic instrument**, not
> a marketing surface — quiet, dense where it must be, every element load-bearing. Visual quality is part
> of the bar, not a finishing coat.
>
> Sits under the `A_TALUS_Coding_Standard.md` umbrella (§10). **Should** is a strong default; **must** is a
> gate (notably the accessibility and plain-text-fallback rules).
>
> Status: **Accepted, v1.0** (2026-06-25). Part of **Standards Suite v1.0**.

---

## Contents

§1 Purpose & Scope · §2 Shared Principles (medium-independent) · §3 The Output Port (separation of domain
from rendering) · §4 Terminal / CLI Medium · §5 Web / GUI Medium · §6 Cross-Medium Consistency · §7
Accessibility (the floor) · §8 Maturity & Honest Gaps · §9 Why This Is Right

---

## 1. Purpose & Scope

Tools present results an operator must read under pressure and trust. This standard governs the *visual
language* (color, type, density, structure) and the *interaction language* (status, progress, navigation,
copy) for both the terminal and the browser. It is deliberately one document: the **principles are shared**
and only the **mechanics differ** by medium. It does not govern component-library implementation details
(those live with the frontend code) or a language's rendering API (that lives in the language standard);
it governs the *decisions* those implementations must honor.

---

## 2. Shared Principles (medium-independent)

1. **Severity color is reserved for severity.** Saturated red/orange/amber carry *meaning* (risk,
   failure, warning) and are never decorative. An operator must be able to trust that loud = important,
   everywhere, always.
2. **One loud thing.** A surface has a single locus of emphasis (the risk, the error, the active state).
   Everything else is quiet so the loud thing reads instantly.
3. **The domain emits semantic intent; the adapter renders it.** Business logic produces *roles*
   (`success`, `warning`, `header`, `muted`) and *view-models* (a table, a status row) — never colors or
   escape codes or DOM. Rendering is an adapter (§3). This is the rule that lets one core drive a CLI, a
   TUI, and a web frontend.
4. **Density discipline.** Dense where the operator *scans* (lists, tables, dashboards); generous where
   the operator *reads* (prose, reports, long-form). Structure with hairline separators, not heavy chrome.
5. **Legibility over decoration.** Mid-tone colors on a dark ground; monospace for all data-bearing text
   (IDs, hashes, vectors, command output) so columns align and technical strings are scannable; restraint
   over flourish.
6. **Reproducible, with a plain fallback that always works.** The same inputs produce the same visual
   output (not animated, not random). A fully plain rendering (no color, no motion) is always available
   and is the *guaranteed* form for files, pipes, and reduced environments.
7. **Copy is in the operator's vocabulary.** Name what the operator controls and recognizes; active voice;
   errors explain *what went wrong and how to fix it* (never vague, never apologetic); empty states direct
   the next action.
8. **Accessibility is a floor, not a feature** (§7).

---

## 3. The Output Port (separation of domain from rendering)

A **presentation port** is the seam that makes every other rule enforceable and every retarget free:

- The domain depends on a renderer *interface* and speaks only **view-models** (what to show) and **events**
  (what happened) plus **semantic roles** (how important). It never imports color, escape codes, a terminal
  library, or a UI framework.
- An **adapter** implements the port for a medium: an ANSI terminal, a TUI, a web client, or a structured
  JSON/headless sink. Adding a target is a new adapter, **not** a rewrite of the domain.
- An **inbound (anti-corruption) adapter** classifies messy external input (another tool's raw stdout)
  into typed events so noise never reaches the domain or the renderer.

> **Hard rule:** no domain module imports the theme, the color logic, or the rendering backend. Color and
> layout are computed only in the adapter. (This is the §10/§18 contract in the Python standard, expressed
> visually.)

---

## 4. Terminal / CLI Medium

### 4.1 Color capability detection & graceful degradation

Detect the terminal's capability and **degrade automatically**: truecolor (24-bit) → 256 → 16 → plain.
Honor the conventions: `NO_COLOR` and `FORCE_COLOR`/`CLICOLOR_FORCE`, `COLORTERM`/`TERM`, and TTY
detection (`isatty`). **When output is not a TTY (a pipe or a file) or color is disabled, emit zero escape
codes** — byte-for-byte plain. This is a `must`: a report file or piped stream with color codes in it is a
defect.

### 4.2 The semantic role palette

Define a small, closed palette of **roles**, not colors, chosen as mid-tones legible on both light and
dark terminals: `ok` / `error` / `warn` / `info` / `header` / `value` / `accent` / `muted` / `note` /
`border` (and severity roles where risk is shown). The domain emits a role; the adapter paints it and
down-converts per capability. `muted` uses the terminal's *dim* attribute so it adapts to the user's theme.

### 4.3 View-models

Render structured surfaces from plain data, not ad-hoc prints: a **banner** (run identity), **section**
(header + separator), **key/values** (aligned rows), **bullet list** (with an `… +N more` tail),
**checklist** (`✓ / ✗ / ·` + label + note), **table** (column-aligned, width-aware), **panel** (bordered
box), and a mutable **run-state** (phase, percent, speed, ETA) for live updates.

### 4.4 Layout mechanics

- **Box drawing:** a heavy set reserved for the top banner; a rounded set for in-app panels. Consistent,
  not mixed arbitrarily.
- **ANSI-aware width & truncation:** measure visible length ignoring escape sequences; truncate on the
  plain text and add an ellipsis; never slice through a color code. Layout is computed *before* paint;
  painted strings are atomic.
- **Live region:** in-place updates via cursor positioning, with color adding *no* newlines so the cursor
  math holds. Progress bars interpolate the role gradient per character and degrade with capability.
- **Status badges:** normalize a status enumeration (`pending`/`running`/`completed`/`failed`/`skipped`/…)
  to fixed-width tags with semantic roles, so columns of status read cleanly.

### 4.5 The plain-text guarantee

A plain renderer (zero ANSI) is a first-class adapter, not an afterthought — it is what produces report
files and piped output. Verify it: piped output and any `*.txt` report contain no escape codes.

---

## 5. Web / GUI Medium

### 5.1 Design tokens

A disciplined token system: a **neutral ground** (a near-black slate scale for background, raised
surfaces, hairline borders, primary and muted text), a **single signal accent** (one restrained brand
hue), and **severity colors as the only saturated palette** — reserved for risk, never decorative (Shared
Principle 1). Every color is a token; no ad-hoc hexes in components.

### 5.2 Typography

Three tiers: a **display/heading** geometric sans used with restraint, a **body/UI** neutral sans legible
at small sizes and high density, and a **data/mono** face for all data-bearing surfaces (tables, vectors,
hashes, IDs, logs). Monospace-for-data is the same rule as the CLI.

### 5.3 Layout & components

- Dense where scanning, generous where reading; hairline structure; restrained, intentional corners (no
  gratuitous radius).
- Build on **headless primitives** and own the visual layer through tokens; forms validate against the
  same schemas the backend enforces.
- An optional **ambient/signature element** (e.g. a subtle, risk-reactive perimeter cue) may give a
  pre-cognitive read on state — but it is ambient, never distracting, and respects reduced-motion.

### 5.4 Interaction

- **Keyboard-first.** A command palette for fuzzy navigation/actions; full keyboard navigability of the
  primary surfaces; discoverable shortcuts.
- **Frictionless capture** for the highest-frequency action (paste/drag), optimistic but durable-or-
  explicit on failure.
- **Copy & IA** per Shared Principle 7: the operator's vocabulary, actionable errors, directive empty
  states.

---

## 6. Cross-Medium Consistency

One domain feeds every surface, so the *language* stays constant across media: severity means the same
thing in a terminal badge and a web table; status enumerations map to the same semantics; the operator's
vocabulary is identical in a CLI help string and a web tooltip; monospace carries data in both. A finding
that is "critical" looks critical — and only critical things look that way — whether the operator is in a
pipe, a TUI, or a browser. The shared port (§3) is what makes this hold without duplicated logic.

---

## 7. Accessibility (the floor)

Non-negotiable, both media:

- **Contrast** clears WCAG AA (the dark, mid-tone palette is chosen to pass).
- **Keyboard** access to every interactive surface, with a **visible focus** indicator.
- **Motion** respects `prefers-reduced-motion` (web) and is absent from non-interactive output; nothing
  essential is conveyed by motion alone.
- **Color is never the only channel** — pair it with a glyph, label, or position (so color-blind operators
  and `NO_COLOR`/plain renderings lose no meaning).
- **Honor environment**: `prefers-color-scheme` (web), `NO_COLOR`/`FORCE_COLOR`/TTY (CLI).

---

## 8. Maturity & Honest Gaps

Per the standard's own candor rule, the current state:

- **CLI presentation is mature** (a real ports-&-adapters implementation exists and is the model). **Web
  design is specified but not yet built** — tokens, typography, components, and affordances are designed;
  the implementation is pending, which is the moment to lock this standard before it diverges.
- **Only an ANSI/CLI adapter exists today**; TUI/web/headless adapters are architected, not built.
- **No formal icon/glyph or motion system** yet (basic Unicode symbols are used in the CLI).
- **Accessibility is specified (WCAG AA, keyboard, reduced-motion) but not yet audited** end-to-end.

These are named, not hidden; they are the near-term work.

---

## 9. Why This Is Right

One visual language across media, anchored on a domain/renderer seam, means an operator learns the
interface once and trusts it everywhere: loud always means important, data is always scannable, and the
plain rendering always works. Designing the tokens and the port *before* the web build is what keeps the
terminal and the browser speaking the same language instead of drifting into two products.
