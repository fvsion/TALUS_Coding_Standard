# Observability & Reliability Standard

> **A tool is not done when it works on the developer's machine — it is done when it can be *operated*: seen
> into when it misbehaves, depended on under load, deployed and rolled back safely, and recovered from an
> incident.** This standard makes observability and operational readiness design properties: structured,
> correlated telemetry (logs, metrics, traces); explicit reliability targets and the patterns that meet
> them; safe deploys and tested rollback; and the human-facing operations discipline (runbooks, on-call,
> blameless postmortems) that turns an outage into a bounded event.
>
> Language-agnostic; under the `A_TALUS_Coding_Standard.md` umbrella. Scope is **proportional to tier** (§2):
> heaviest for a long-running Tier-3 platform, a deliberate subset for a Tier-1 library or a Tier-2 CLI.
> **Mandatory** at the weight a tool's tier sets. "Must" is a gate; a documented, risk-accepted exception
> is not a finding.
>
> Status: **Accepted, v1.0** (2026-06-25). Part of **Standards Suite v1.0**.

---

## Contents

§1 Purpose & Principles · §2 Proportionality by Tier · §3 The Three Signals · §4 Instrumentation: What to
Measure · §5 SLIs, SLOs & Error Budgets · §6 Health, Readiness & Graceful Lifecycle · §7 Reliability
Patterns · §8 Deploy Safety & Rollback · §9 Capacity & Performance · §10 Operational Readiness · §11 The
Production-Readiness Review · §12 Verification & Gates · §13 Per-Tool Requirements · §14 Why This Is Right ·
Appendix A: production-readiness checklist

---

## 1. Purpose & Principles

Software that runs unattended fails in ways the test suite never saw: a dependency slows down, load spikes,
a deploy goes bad at 2am. Whether that is a shrug or a crisis is decided *at design time* — by whether the
system can be seen into, whether it degrades instead of collapsing, and whether a human has a tested way
back. This standard makes that capability a requirement, not an afterthought bolted on after the first
outage.

Principles:

1. **Observable by construction.** Instrumentation is built in as code is written, not retrofitted after an
   incident. A running tool emits enough structured signal to answer "is it healthy, and if not, where?"
   without attaching a debugger to production.
2. **Reliability is designed, not hoped for.** Timeouts, retries, idempotency, and graceful degradation are
   architectural choices made up front (§7); "it usually works" is not a reliability posture.
3. **Define the target, then measure against it.** A service states what "healthy" means as explicit SLIs/
   SLOs (§5) and measures itself against them — not by vibes.
4. **Every deploy is reversible.** Shipping a change always includes a tested way to undo it (§8). An
   irreversible deploy is a design defect.
5. **Telemetry is for operating; the audit trail is for accountability.** They are separate concerns with
   separate stores. **Telemetry never carries secrets or sensitive data** (Security & OpSec Standard §4/§8);
   the immutable audit trail (Security §6) is not a substitute for metrics, and vice versa.
6. **Proportional, not performative.** A library does not ship a tracing backend; a platform does not skip
   one. The weight matches the tier (§2) — enough to operate the thing, never theater.

---

## 2. Proportionality by Tier

What this standard *requires* scales with how the software runs. The tier model is the umbrella's; the
observability weight per tier:

| Tier | What it is | Observability & reliability weight |
|---|---|---|
| **Tier 1 — library** | Imported by others | Structured logging via the host's logger (no logging config imposed on importers); no global state; documented failure modes, timeouts, and thread-safety. It emits signal; it does not own a telemetry stack. |
| **Tier 2 — CLI / standalone** | Run by a human or a job | Structured logs (human + machine-readable); meaningful exit codes; progress/feedback for long work; deterministic, inspectable failures; optional metrics for batch/automated runs. Graceful cancellation (§6). |
| **Tier 3 — service / platform** | Long-running, multi-user | The full standard: all three signals correlated (§3), SLIs/SLOs + error budgets (§5), health/readiness endpoints + graceful lifecycle (§6), the reliability patterns (§7), deploy safety + rollback (§8), capacity testing (§9), runbooks + on-call + postmortems (§10), and a production-readiness review before launch (§11). |

A tool states its tier and therefore which sections bind it. A tool that runs in an unusual mode (a CLI run
as a long-lived daemon, a library with a network side) adopts the weight of the **heaviest** mode it
supports.

---

## 3. The Three Signals

An operable system emits three **correlated** signals. The discipline that makes them useful is correlation:
a request's trace ID appears in its logs and its metrics' exemplars, so an operator pivots from "error rate
spiked" to the exact traces to the exact log lines without guessing.

- **Logs** — structured, timestamped, leveled records of discrete events. **Structured (key-value / JSON),
  never f-string prose** that has to be regex-scraped (this is the language standard's logging rule, e.g.
  Python §16). Each log line carries correlation context (trace/span/request IDs) where one exists.
- **Metrics** — cheap, aggregatable numeric time-series for rates, counts, durations, and saturation. The
  basis for dashboards and alerts (§5). Metrics are low-cardinality by design; high-cardinality identifiers
  belong in traces/logs, not metric labels.
- **Traces** — the causal path of a request across components, as spans with timing and attributes. Traces
  answer "where did the latency go?" and "what did this request touch?" across process boundaries.

**Vendor-neutral by default.** Instrumentation targets the **OpenTelemetry** (OTel) data model and APIs —
an open, vendor-neutral standard — so the *backend* (where signals are stored and viewed) is a swappable
adapter, not a coupling baked through the code. Emitting OTel keeps the choice of collector/backend a
deployment decision (umbrella Principle 2: volatile concerns are adapters at the edge).

**Context propagation** crosses boundaries: the trace context travels with a request (HTTP headers, message
metadata) so a distributed operation is one trace, not N disconnected ones.

---

## 4. Instrumentation: What to Measure

Instrument for the questions an operator actually asks, using a standard frame rather than ad-hoc gauges:

- **RED, for request-driven services:** **R**ate (requests/sec), **E**rrors (failed requests/sec), and
  **D**uration (latency distribution, as histograms — p50/p95/p99, not just a mean). These three answer
  "are users being served, and how well?"
- **USE, for resources:** **U**tilization, **S**aturation, and **E**rrors of each constrained resource
  (CPU, memory, connection pools, queues, disk). These answer "is the system starved?"
- **Work/queue depth** for pipelines and batch tools: items processed, in-flight, failed, retried, and the
  age of the oldest unprocessed item (the real backlog signal).
- **Business/domain signals** the tool is *for* — measured, not assumed: things produced, jobs completed,
  the saturation of any bounded internal queue.

Latency is a **distribution** (histogram/percentiles), never an average — an average hides the tail where
users actually suffer. Every signal has an owner who knows what action a change in it should trigger; a
metric nobody would act on is noise, not observability.

---

## 5. SLIs, SLOs & Error Budgets

A Tier-3 service defines what "healthy" means and holds itself to it:

- **SLI (Service Level Indicator)** — a precise measurement of one aspect of health: request success rate,
  p99 latency under a threshold, freshness of a pipeline's output. Defined in terms a user feels.
- **SLO (Service Level Objective)** — the target for an SLI over a window (e.g. "99.9% of requests succeed
  over 30 days"). Realistic, not aspirational-to-the-point-of-meaningless.
- **Error budget** — the allowed shortfall (the complement of the SLO). It is a *budget*: spend it on change
  velocity while it lasts; when it is exhausted, the response is to slow down and stabilize. This makes the
  reliability-vs-velocity trade-off explicit and data-driven instead of an argument.
- **Alert on symptoms and burn, not causes.** Page a human when users are affected or the error budget is
  burning too fast — not on every transient CPU blip. **Every page is actionable**; an alert that fires
  without a human action to take is noise and gets fixed or deleted. Alert fatigue is an outage waiting to
  happen.

Dashboards present the SLIs and the RED/USE signals (§4) so the state of the system is legible at a glance,
to an on-call engineer who did not write the code.

---

## 6. Health, Readiness & Graceful Lifecycle

A service makes its state inspectable and its transitions clean:

- **Liveness** — "is the process alive / should it be restarted?" — and **readiness** — "can it serve
  traffic *right now* (dependencies reachable, warm-up done)?" are **separate** checks. A readiness check
  that goes red sheds the instance from rotation without killing it; conflating the two causes restart
  storms.
- **Graceful startup.** Don't accept traffic until dependencies are reachable and initialization is
  complete; fail fast and loudly on a misconfiguration rather than half-starting.
- **Graceful shutdown.** On a termination signal, stop taking new work, drain in-flight work within a
  bounded deadline, flush telemetry, release resources, and exit cleanly. This is the operational face of
  the language standard's lifecycle/signal-handling and scoped-resource rules (e.g. Python §15.5 cooperative
  cancellation; §17 resource cleanup) — and it ties to the OpSec rule that artifacts are removed on **every**
  exit path (Security & OpSec Standard §7).
- **Graceful cancellation (Tier 2).** A long-running CLI handles interruption (Ctrl-C / SIGINT) by cleaning
  up and reporting partial state, never by corrupting output or leaving residue.

---

## 7. Reliability Patterns

Calls across a boundary (network, subprocess, external service) **will** fail and stall; the design assumes
it. The standard patterns, applied where a boundary warrants:

- **Timeouts on everything.** No unbounded wait on any I/O or external call — ever. A missing timeout is the
  most common cause of a cascading hang. Timeouts are configured values (umbrella "everything is a
  variable"), not magic numbers.
- **Retries with backoff + jitter — only for idempotent operations.** Retry transient failures with
  exponential backoff and jitter to avoid synchronized retry storms; cap attempts. Never blindly retry a
  non-idempotent operation (see the idempotency rule below, and the API & Data-Contract Standard).
- **Circuit breakers.** When a dependency is failing, stop hammering it: trip open, fail fast, and probe for
  recovery — so one sick dependency doesn't exhaust the caller's resources and spread the outage.
- **Idempotency.** Operations that may be retried are designed to be safely repeatable (idempotency keys,
  dedup) so a retry can't double-charge / double-write. This is the same property the API & Data-Contract
  Standard requires of mutating endpoints.
- **Graceful degradation & bulkheads.** Shed load and serve a reduced experience under pressure rather than
  collapsing wholesale; isolate resources (separate pools/queues) so a failure in one path can't starve the
  others. Back-pressure over unbounded buffering.
- **Sensible defaults, fail closed on safety.** A reliability fallback never silently widens access or
  emits wrong data; where safety and availability conflict, fail closed (Security & OpSec Standard §1).

Each pattern a tool relies on is recorded in its design docs with its configured parameters (timeout
values, retry caps, breaker thresholds), so they are reviewable and tunable, not buried.

---

## 8. Deploy Safety & Rollback

Shipping is the riskiest routine operation; make it boring (this is the operational complement to the Git &
Release Engineering Standard §7):

- **Every deploy is reversible.** There is always a tested way back — redeploy the previous version, or roll
  forward a fix — and the rollback procedure is *exercised*, not assumed. An irreversible migration is
  re-shaped into reversible steps (the API standard's **expand → migrate → contract**: additive schema
  change, backfill, switch, then remove — each step independently reversible).
- **Progressive delivery for higher-risk changes.** Roll out gradually — canary / staged / blue-green — and
  watch the SLIs (§5) before widening; automatically halt or roll back on a regression. The blast radius of
  a bad deploy is bounded by design.
- **Feature flags** decouple deploy from release: ship code dark, enable it for a cohort, and kill it
  instantly without a redeploy. A long-running phased feature lands behind a flag (Git & Release §2;
  AI Coding Phase Guidelines).
- **Backward/forward compatibility during a deploy.** In a rolling deploy, old and new run **simultaneously**;
  changes (especially to schemas and contracts) are compatible across the overlap window — never a breaking
  change shipped in a single irreversible step.
- **Configuration and data migrations** are versioned, reversible where possible, and tested on
  production-like data before they run for real.

---

## 9. Capacity & Performance

Know the system's limits before production finds them for you:

- **Load & stress testing** for Tier-3 services: establish the throughput/latency envelope, find the
  saturation point, and confirm behavior *past* it is graceful degradation (§7), not collapse.
- **Capacity planning.** Size against expected load with headroom; know which resource saturates first (the
  USE signals, §4) and what the scaling lever is.
- **Performance budgets** for latency-sensitive paths, asserted in CI where feasible so a regression is
  caught at merge, not in production. (The umbrella's efficiency doctrine governs *how* to make code fast;
  this governs *proving* it meets its operational budget.)
- **Soak tests** for long-running services to surface leaks and slow degradation that a short test misses.

---

## 10. Operational Readiness

The human side of running software — without it, the best telemetry just tells you you're on fire:

- **Runbooks.** Each significant alert and failure mode has a written runbook: what it means, how to
  diagnose, how to mitigate, when to escalate. Written for the on-call engineer at 3am who did not write the
  code — concrete steps, not "investigate the issue."
- **Incident response.** A defined process: detect → triage by severity → mitigate (stop the bleeding before
  root-causing) → communicate → resolve. Severity levels and their response expectations are written down
  before the incident.
- **On-call & ownership.** Every production service has a clear owner and a sustainable on-call rotation —
  humane load, escalation paths, and a handoff. "Who is paged when this breaks?" has an answer before
  launch, not during the outage.
- **Blameless postmortems.** Every significant incident gets a written, **blameless** postmortem: timeline,
  contributing causes (systemic, not "human error"), and concrete follow-up actions tracked to closure. The
  goal is a system that can't fail that way again — psychological safety is what makes the analysis honest.
- **Operational documentation lives with the tool** — the `09_DEVOPS` doc (Documentation & Architecting
  Standard) carries the runbook index, the on-call/ownership statement, the deploy/rollback procedure, and
  the dashboards/alerts catalogue.

---

## 11. The Production-Readiness Review

Before a Tier-3 service goes to production (or a major version ships), a **production-readiness review**
confirms the operational bar is met — a gate, not a formality. It checks:

- The three signals are emitted and correlated (§3); dashboards exist; the key SLIs are visible (§5).
- SLOs are defined with alerting on symptom/burn; every alert is actionable and has a runbook (§5, §10).
- Health/readiness checks and graceful start/stop work (§6); the reliability patterns for its dependencies
  are in place and configured (§7).
- Deploy is progressive where warranted and **rollback is tested** (§8); migrations are reversible.
- Capacity is understood; behavior past saturation is graceful (§9).
- On-call, ownership, runbooks, and the incident/postmortem process exist (§10).
- Telemetry carries no secrets/sensitive data (§1, Security & OpSec Standard §4/§8); the security review
  (Security §10) is done.

The review output is recorded (the tool's `09_DEVOPS` doc / the release record). A gap is either closed or
explicitly risk-accepted before launch.

---

## 12. Verification & Gates

Observability and reliability are checked mechanically where they can be, and reviewed where they can't:

- **Structured-logging lint** — the language standard's logging rules are enforced (no prose-scraped logs;
  correct levels; no secrets in logs — Security & OpSec §4).
- **Reliability tests** — timeouts, retry/backoff, idempotency, and graceful shutdown/cancellation have
  tests (failure injection where feasible: a slow/erroring dependency, a termination signal mid-work).
- **Rollback test** — for a Tier-3 service, the rollback procedure is exercised in CI/staging, not assumed.
- **Performance budget checks** — latency/throughput budgets asserted in CI for the paths that declare them
  (§9).
- **Production-readiness review** — the §11 gate before a Tier-3 launch or major release; its sign-off is a
  release gate (Git & Release Engineering Standard §8).

A missing gate where the tier requires one (no shutdown test on a service, no rollback test, no alert
runbooks) is itself a finding.

---

## 13. Per-Tool Requirements

Each tool's `09_DEVOPS` doc (Documentation & Architecting Standard), proportional to its tier (§2), states:
its **telemetry** (what logs/metrics/traces it emits and to what backend); its **SLIs/SLOs** and alerts
(Tier 3); its **health/readiness** model and lifecycle behavior; the **reliability patterns** it relies on
with their configured parameters; its **deploy & rollback** procedure; its **capacity** envelope and any
performance budgets; and its **operational docs** (runbooks, on-call/ownership, the production-readiness
review record). A Tier-1 library or a low-surface Tier-2 tool states the reduced set that applies and why —
the *absence* of a requirement is a recorded decision, not an oversight.

---

## 14. Why This Is Right

Building observability and reliability into the architecture means an incident is a bounded, understood
event instead of a mystery: the signals show where it hurts, the patterns kept one failure from becoming
all of them, the rollback undoes the bad change in minutes, and the runbook tells whoever is on-call what to
do. That is far cheaper than reverse-engineering a production fire with no telemetry, and it is the
difference between software that *runs in a demo* and software that can be *depended on*. Sized to the tier,
it is never busywork — exactly enough to operate the thing, and no theater.

---

## Appendix A — Production-readiness checklist

Per Tier-3 service (a proportional subset for Tier 1/2), confirm:

- [ ] Structured logs with correlation context; no secrets in telemetry (Security & OpSec §4/§8).
- [ ] Metrics (RED/USE) and traces emitted; OTel-aligned, vendor-neutral backend; context propagated across boundaries.
- [ ] SLIs/SLOs defined; dashboards exist; alerts fire on symptom/burn, every alert actionable + runbooked.
- [ ] Separate liveness vs readiness; graceful startup; graceful shutdown drains + flushes + cleans up.
- [ ] Timeouts on all external calls; retries-with-backoff for idempotent ops; circuit breakers; back-pressure.
- [ ] Idempotency for retryable mutations (API & Data-Contract Standard); graceful degradation under load.
- [ ] Reversible deploys; progressive delivery for risky changes; **rollback tested**; migrations reversible.
- [ ] Feature flags decouple deploy from release; compatible across a rolling-deploy overlap window.
- [ ] Load/stress tested; behavior past saturation is graceful; capacity + performance budgets known.
- [ ] Runbooks for each alert; incident process + severities; on-call + ownership defined; blameless postmortems.
- [ ] Production-readiness review (§11) recorded in `09_DEVOPS`; gaps closed or risk-accepted; security review done.
