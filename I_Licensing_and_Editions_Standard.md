# Licensing & Editions Standard

> **How a tool is split into a public (community) edition and a commercial (pro) edition — by design, from
> the first commit.** The guiding star: **an edition is a *seam*, not a *fork*.** Pro features attach to a
> community core through defined extension points and are excluded from the community build; they are never
> a divergent copy of the codebase. Getting this seam right up front is what lets a tool grow a pro edition
> later as a *packaging* change, not a *recode*.
>
> Language-agnostic; sits under the `A_TALUS_Coding_Standard.md` umbrella (§3.2). A tool that will *ever* have
> a pro edition designs the seam from the start; a tool that is single-edition still benefits from the same
> clean extension points. **Must** is a gate; **should** is a strong default.
>
> Status: **Accepted, v1.0** (2026-06-25). Part of **Standards Suite v1.0**.

---

## Contents

§1 Purpose & Scope · §2 The Edition Model (open-core) · §3 The Edition Seam · §4 Authoring & Marking Pro ·
§5 The Edition Build (build-time split) · §6 The Protection Model · §7 Licensing Mechanics · §8 Per-Tool
Requirements · §9 Governance & Evolution · §10 Why This Is Right · Appendix A: the `pro/` seam, worked

---

## 1. Purpose & Scope

A tool often has two audiences: an open community that gets a capable free edition, and paying customers
who get a pro edition with advanced features. The expensive mistake is to **discover this late** and bolt
it on — stripping a built tool into a "lite" copy, or hiding pro code behind a runtime check that anyone
can flip. Both produce a *fork* (two diverging codebases) or a *false lock* (the code is present and
crackable). This standard prevents both by making the edition boundary a **first-class architectural seam**
decided during design.

It governs: what distinguishes the editions, where pro code lives, how the community edition is *built* (by
excluding pro, not by copying), how the code is protected, and how each edition is licensed. It is the
same philosophy as this repo's own proprietary-doc fencing — *one source, mechanically produce the public
variant by removing the marked/bounded parts* — applied to code.

---

## 2. The Edition Model (open-core)

The model is **open-core**:

- **Community edition** — the open core. A genuinely useful, complete-in-itself tool, published under an
  OSS license. It never depends on pro code and builds/runs/tests with pro entirely absent.
- **Pro edition** — the community core **plus** pro features, under a commercial license. Pro is strictly
  *additive*: it extends the core through defined seams; it never modifies or replaces core code.

Rules:

1. **An edition is a seam, not a fork.** There is one codebase. The community edition is the core with pro
   excluded; the pro edition is the core with pro included. There is never a second, diverging copy.
2. **The core is whole.** The community edition must be a real product on its own — not crippled bait. What
   is pro is *additional* capability, not a removed essential.
3. **Pro is additive and isolated.** Pro code lives behind the seam (§3) and is the only thing that differs
   between editions.

---

## 3. The Edition Seam

The seam is a **load-bearing architectural boundary** (Documentation & Architecting Standard §8): designed
now, even if pro is built later, because retrofitting it is the recode this standard prevents.

- **The community core never references pro.** Dependencies point one way: pro → core, never core → pro.
  The core compiles, imports, runs, and passes its tests with all pro code removed. (This is the same rule
  as a doc fence: *what remains after the cut must stand on its own.*)
- **Pro attaches at defined extension points**, the same open-closed seams the architecture already uses:
  - a **plugin/strategy registry** the core exposes, into which pro registers extra implementations;
  - **optional adapters** behind a port the core owns (pro provides a richer adapter);
  - **feature-gated commands/capabilities** the core discovers if present (a pro subcommand, an extra
    analysis pass), absent otherwise.
- **No core branch says `if pro`.** The core does not know about pro; it discovers whatever has registered
  at its extension points. Adding pro is *registering more*, not *editing the core*.

If a tool already follows "extend by addition, not modification" (umbrella Principle 3), the edition seam
is nearly free — pro is just another set of registered extensions that the build can include or exclude.

---

## 4. Authoring & Marking Pro

You usually know a feature is pro *while you are writing it*. Mark it then, at the boundary that the build
can act on:

- **The primary unit is a bounded module/package: `pro/`.** Pro features live in a clearly-named `pro/`
  namespace (a `pro/` subpackage, or pro-tagged plugin files) that the community build excludes wholesale.
  This is the cleanest unit — easy to author, easy to exclude, and trivially **promotable to a separate
  closed package** later (§6) because the boundary already exists.
- **Inline gates are the exception, for small in-line pro paths.** Where a pro branch is too small to be
  its own module, fence it inline so the community build strips it:

  ```
  # PRO:BEGIN — advanced scoring (commercial edition)
  ...pro-only code...
  # PRO:END
  ```

  Use these sparingly; prefer a `pro/` module. An inline gate, like a doc fence, must leave the surrounding
  community code **valid and complete** once removed.
- **Author-time discipline:** when a feature is pro, put it behind the seam *as you write it* — never "I'll
  separate it later." Later is the fork.

---

## 5. The Edition Build (build-time split)

The community edition is **produced by excluding pro at build time**, not by copying the tree:

- **The community build omits `pro/`** (and strips any `# PRO` inline gates), yielding an artifact in which
  pro code is **genuinely absent**. The pro build includes everything.
- This is one source of truth with two build profiles — exactly the model this repo uses for docs
  (`strip-proprietary.sh` produces the public tree by removing fenced/excluded content). The code analogue:
  the packaging config excludes the `pro/` package for the community wheel/image; a small strip pass removes
  inline `# PRO` gates. (The language standard specifies the concrete mechanism — e.g. Hatchling package
  selection — see Appendix A.)
- **Reproducible & verified.** The community build is deterministic, and **CI builds *both* editions** and
  runs the community edition's tests **with `pro/` absent** — proving the seam is clean (the core never
  secretly depended on pro). A community build that fails without pro is a seam defect, not a test bug.

---

## 6. The Protection Model

What actually protects pro code is **absence**, not a check:

- **Do not rely on a runtime entitlement/license check to protect pro code.** If the pro code ships in the
  community artifact and is merely gated by an `if licensed:` test, it is trivially crackable — the code is
  already there. A license/activation check **may gate** a pro feature *within the pro edition* (to enforce
  seat counts, expiry, etc.), but it is **never the thing protecting the code**.
- **Protection = the community build does not contain pro code.** Because the build excludes `pro/`, there
  is nothing to crack in the community edition.
- **Maximum protection = a separate closed package.** For a crown-jewel pro module, publish it as a
  separate, closed-source package that the pro build depends on. Because the seam is already clean, this is
  a **packaging move, not a recode** — exactly the promotability the seam buys. Default to in-repo `pro/`
  (best dev ergonomics); escalate to a separate package only where the protection warrants the overhead.

---

## 7. Licensing Mechanics

- **Two licenses, declared explicitly.** The community edition is licensed under the project's chosen **OSS
  license**; the pro edition (and any separate pro package) under a **commercial license**. The choice of
  OSS license is recorded in the tool's technology ADRs.
- **`LICENSE` and `LICENSE-PRO`.** The repo carries the community `LICENSE` at root; pro carries a
  `LICENSE-PRO` (or lives in the closed package with its own). The README states which edition is which and
  what each license permits.
- **Per-file SPDX headers.** Every source file declares its license with an SPDX identifier so the boundary
  is machine-checkable and unambiguous:

  ```
  # SPDX-License-Identifier: <OSS-LICENSE>          ← community/core files
  # SPDX-License-Identifier: LicenseRef-<Org>-Commercial   ← pro files (under pro/)
  ```

  A CI check asserts that every file under `pro/` carries the commercial identifier and every core file
  carries the OSS one — drift here is a licensing defect.
- **Edition labeling.** The tool reports its edition (community/pro) and version so support and bug reports
  are unambiguous.

---

## 8. Per-Tool Requirements

Every tool that has — or could ever have — a pro edition states this in its design specs:

- **`00_VISION` declares the editions** (Documentation & Architecting Standard §4): what the community
  edition is (the whole, useful core) and what is pro (the additive capability), in one short table.
- **The architecture specifies the edition seam** as a load-bearing seam (Doc&Arch §8): the extension
  points pro uses, and the rule that the core never depends on pro.
- **The build documents both profiles** and the community-without-pro test run (§5).
- **Licensing is stated** (§7): the two licenses, the `LICENSE`/`LICENSE-PRO` files, the SPDX convention.
- **A single-edition tool still declares it** — "community-only, no pro edition planned" — so the absence
  is a decision, not an oversight; and it still uses clean extension points so a future pro edition is a
  seam, not a fork.

---

## 9. Governance & Evolution

- **Moving a feature across the seam** (community → pro, or pro → community) is a deliberate, recorded
  decision (an ADR), because it changes what users get and may have licensing/announcement consequences.
  Promoting a community feature *to* pro after release is especially sensitive — prefer adding new pro
  capability over taking community capability away.
- **The seam is maintained, not eroded.** A core change that quietly reaches into pro, or a pro feature
  that the core starts to assume, is drift — caught by the community-without-pro build (§5) and the SPDX
  check (§7).
- **Editions are versioned together** off one source; release notes state what changed per edition.

---

## 10. Why This Is Right

Designing the edition boundary as a clean seam from the start means a pro edition is always one build
profile away — never a fork to maintain, never a recode to retrofit, never crackable code shipped to
everyone. The community gets a whole, honest tool; the business gets defensible pro features; and
engineering maintains **one codebase** with the discipline (extend-by-addition, the clean seam, the
build-time split) it was already using. The boundary is decided once, in the open, and then it just holds.

---

## Appendix A — The `pro/` seam, worked

A Tier-2 tool with a pro edition, sketched:

```
mytool/
├── mytool.py                 # entry: dispatch only; discovers registered commands (core + pro if present)
├── modules/
│   ├── core/                 # the community core — depends on NOTHING in pro/
│   │   ├── registry.py       # the extension points: register_command(), register_adapter(), …
│   │   └── …                 # the whole, useful community feature set
│   └── pro/                  # PRO — excluded from the community build; commercial license
│       ├── __init__.py       # registers pro commands/adapters into core.registry on import
│       └── advanced_*.py
├── LICENSE                   # community OSS license
├── LICENSE-PRO               # commercial license (pro/)
└── pyproject.toml            # build selects packages; community profile excludes modules/pro
```

**Build-time exclusion (illustrative, Hatchling):**

```toml
# Community wheel: select packages, omitting pro.
[tool.hatch.build.targets.wheel]
packages = ["modules/core"]            # pro/ simply not selected → absent from the community artifact

# Pro build: a separate target/profile that also includes modules/pro (or depends on a closed pro package).
```

**SPDX headers:**

```python
# modules/core/registry.py
# SPDX-License-Identifier: <OSS-LICENSE>

# modules/pro/advanced_scoring.py
# SPDX-License-Identifier: LicenseRef-<Org>-Commercial
```

**The seam test (CI, community profile):** build with `modules/pro` excluded, then import the package and
run the community test suite. It must pass — proving the core never depended on pro. Build the pro profile
separately and run the full suite.
