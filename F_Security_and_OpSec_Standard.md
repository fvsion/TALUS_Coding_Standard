# Security & OpSec Standard

> **Security and operational security are design properties, decided during architecture — not a hardening
> pass bolted on before release.** Every tool is built so the safe path is the default: untrusted input is
> validated at the boundary, queries are parameterized, secrets never touch source or logs, consequential
> actions are authorized and audited, and a tool operating in a sensitive environment minimizes what it
> leaves behind. This standard is the deep treatment that the umbrella (§8), each language standard (e.g.
> Python §25), and each tool's `05_SECURITY_AND_OPSEC` doc inherit.
>
> Language-agnostic; under the `A_TALUS_Coding_Standard.md` umbrella. **Mandatory.** "Must" is a gate; a
> documented, risk-accepted exception is not a finding.
>
> Status: **Accepted, v1.0** (2026-06-25). Part of **Standards Suite v1.0**.

---

## Contents

§1 Purpose & Principles · §2 Threat Modeling · §3 Secure-by-Construction Controls · §4 Secrets · §5
Authorization & Scope · §6 Audit & Accountability · §7 Operational Security (OpSec) · §8 Data Handling,
Retention & Privacy · §9 Cryptography · §10 Verification & Gates · §11 Per-Tool Requirements · §12 Why
This Is Right · Appendix A: control checklist

---

## 1. Purpose & Principles

Bolted-on security fails because the insecure path is already the easy one. This standard makes the secure
path the default, and treats *operational* security — what a running tool reveals and leaves behind — as a
first-class design concern wherever a tool acts in a sensitive or adversarial environment.

Principles:

1. **Secure by construction.** The architecture makes whole classes of bug impossible: parameterized
   queries (no string-built SQL/queries), validated untrusted input, encoded output, an authorization
   chokepoint. Not "remember to sanitize."
2. **OpSec by construction.** A tool that operates against external or sensitive systems is designed to
   minimize observable footprint and on-disk residue, and to clean up after itself — by design, not by a
   later checklist (§7).
3. **Least privilege.** Every component, credential, token, and process gets the minimum access it needs,
   for the minimum time.
4. **Defense in depth.** No single control is load-bearing; validate at the boundary *and* parameterize
   *and* encode.
5. **Fail closed.** On error or ambiguity, deny — never default-allow. A failure must not silently widen
   access or leak data.
6. **Auditable & accountable.** Consequential actions are recorded to an immutable trail; nothing
   high-impact happens without an attributable, approved trigger (§6).

---

## 2. Threat Modeling

Threat modeling happens **during design**, recorded in the tool's `05_SECURITY_AND_OPSEC` doc
(Documentation & Architecting Standard):

- **Assets** — what is worth protecting (credentials, client data, findings, the audit trail) and each
  asset's sensitivity.
- **Adversaries** — who might attack, with what capability and motive (an external attacker, a malicious
  insider, a curious operator, a target's defenders).
- **Attack surface** — every place untrusted data or an untrusted actor enters: inputs, parsers,
  deserializers, network boundaries, external-tool output, the UI.
- **Controls** — for each realistic threat, the design control that addresses it (§3), and the residual
  risk that is explicitly accepted.

The output is a threat-model section and a **control matrix** (asset / threat / control / residual risk),
not a vague intention.

---

## 3. Secure-by-Construction Controls

The baseline controls, designed in (the language standard gives the concrete idioms):

- **Injection-safe data access.** Parameterized queries / prepared statements only — never string
  concatenation into SQL, shell, or any query language. Build commands as **argument lists, never a shell
  string with untrusted input.**
- **Validate untrusted input at the boundary.** Parse into typed, constrained models at the edge; reject
  what doesn't fit. Treat *all* external input as hostile — including another tool's output (classify it
  through an anti-corruption adapter, never trust its shape).
- **Encode output** for its sink (HTML, shell, SQL, logs) to prevent injection downstream.
- **Authorization chokepoint.** Every consequential operation passes one place that checks the caller is
  allowed and in scope (§5). No bypass paths.
- **Safe deserialization.** Never deserialize untrusted data with an executable format (`pickle`, YAML
  `!!python`, etc.); use data-only formats and schema-validate.
- **Egress discipline.** Outbound requests have an allowlist where feasible; guard against SSRF (validate
  and pin destinations). A tool does not call home or exfiltrate by default.
- **Supply chain.** Treat both what you *consume* and what you *ship* as attack surface: pin and scan
  dependencies, and produce verifiable, signed artifacts with provenance (§3.1).

### 3.1 Supply-chain integrity

The build and its inputs are part of the threat model: a compromised dependency, a tampered build step, or
an unsigned artifact lets an attacker ship malicious code under your name. Both sides are required.

**Consuming — what you depend on:**

- **Pin** every dependency to an exact, hash-verified version via a lockfile (the language standard gives
  the tool); builds are reproducible, not "latest at build time."
- **Scan** dependencies for known vulnerabilities on every build (SCA, §10); a known-vulnerable transitive
  dependency is a finding, tracked to remediation or explicit risk-acceptance.
- **Vet** a new dependency (maintenance, provenance, footprint, license) before adopting it; prefer fewer,
  well-maintained packages; vendor or replace abandoned ones.

**Producing — what you ship:**

- **SBOM.** Every release artifact carries a Software Bill of Materials (CycloneDX or SPDX) enumerating its
  components and versions, so a consumer — and your own incident response — can answer "am I affected?"
  against a newly disclosed CVE without guesswork.
- **Sign artifacts.** Release artifacts are cryptographically signed (Sigstore/cosign or equivalent) so a
  consumer can verify origin and integrity; the signature is published alongside the artifact.
- **Build provenance.** The build emits signed provenance (in-toto / SLSA attestation) recording *how*,
  *from which source commit*, and *by which builder* the artifact was produced.
- **Target SLSA Level 2.** Builds run on a hosted build service (not a developer laptop) that generates
  provenance; the source is version-controlled and the artifact is traceable to its commit. Higher-risk
  artifacts work toward L3 (isolated builds, non-falsifiable provenance). Each tool records its current SLSA
  target (§11).

The release pipeline (Git & Release Engineering Standard §7) **produces** the SBOM, signature, and
provenance; the release gate (its §8) **verifies** them before publish.

---

## 4. Secrets

- **Never in source.** No secret, key, token, or credential in code, config-in-code, or version control.
  Secrets come from the environment, a secrets manager, or an operator-provided store. A **secret scanner
  gate** (§10) blocks commits that contain them.
- **Never in logs or errors.** Captured or handled secrets do **not** travel through the logging system,
  exception messages, or telemetry. Reconfiguring or silencing logs must never be able to leak — or lose —
  a secret. Logging carries *diagnostics only*.
- **Differential reveal.** For tools that *handle* sensitive values (credentials, captured material), the
  default representation is **masked**; the full value is revealed only to a deliberate, secured sink (a
  `0600` file, an explicit `--reveal`), never to the console or a shared log by default.
- **Storage & lifetime.** Secrets at rest are encrypted; tokens are scoped and short-lived; rotation is
  designed in, not retrofitted. Least privilege (§1) applies to every credential the tool holds.

---

## 5. Authorization & Scope

- **Least privilege, enforced at a chokepoint.** Authorization is checked in one service/use-case layer
  the architecture owns (umbrella §4), not scattered or trusted to the UI.
- **Scope gating.** A tool that acts on external systems verifies the target is **in declared scope**
  before acting, and refuses out-of-scope actions. Scope is data (configuration), versioned and auditable
  (umbrella "everything is a variable").
- **Action approval for high-consequence operations.** An operation that changes or touches an external
  system requires an explicit, attributable trigger — the system proposes (math decides *order/timing*); a
  human approves. **Nothing high-impact is autonomous.**
- **Fail closed** on any authorization or scope ambiguity (§1).

---

## 6. Audit & Accountability

- **Immutable audit trail.** Every consequential action — what, when, by whom, against what, with what
  result — is recorded to an append-only, tamper-evident log. The audit trail is itself a protected asset
  (it is never where secrets land, §4).
- **Attribution.** Actions trace to an identity and an approval. "The tool did it" is never an acceptable
  answer for a consequential action.
- **Retention & integrity.** Audit records are retained per policy (§8) and protected from silent edit or
  deletion (soft-delete + integrity checks, not hard-delete).

---

## 7. Operational Security (OpSec)

For any tool that operates in a sensitive, monitored, or adversarial environment, **operational security
is a design property**: minimize what the tool reveals while running and what it leaves behind.

- **Footprint.** Minimize observable behavior — unnecessary network chatter, distinctive traffic patterns,
  noisy artifacts. Make the tool's blast radius and signature a deliberate choice, not an accident.
- **On-disk residue.** Sensitive data and temporary files are created in controlled locations, with tight
  permissions, and **removed on every exit path including errors and cancellation** (scoped resource
  management; cleanup is mandatory and *tested*). A leaked artifact on disk is an OpSec failure, not a
  cosmetic one.
- **Output hygiene.** Plain-text outputs (reports, logs) contain no secrets (§4) and no unintended
  sensitive data; redaction is available before anything is shared externally.
- **Predictable & reproducible.** Behavior is deterministic (umbrella Principle 7) so OpSec properties hold
  run to run, not by luck.

---

## 8. Data Handling, Retention & Privacy

- **Classify** data by sensitivity (public, internal, confidential, secret) and apply controls to match.
- **Minimize.** Collect and retain only what the tool needs; don't hoard sensitive material.
- **Encrypt** sensitive data at rest (field-level where appropriate) and always in transit (§9).
- **Retention & deletion.** Define how long each data class is kept and how it is destroyed; support legal
  hold where required; deletion is real (and audited), not just a hidden flag.
- **Client/third-party material** is handled to the strictest applicable standard; never commit it to a
  repo (real samples are synthetic or sanitized — language standard testing rules).

---

## 9. Cryptography

- **Never roll your own.** Use vetted, current library primitives (authenticated encryption, modern KDFs,
  vetted TLS) — no custom crypto, no deprecated algorithms (MD5/SHA-1 for security, ECB, static IVs).
- **TLS everywhere** for data in transit, with certificate validation on (never disabled to "make it
  work").
- **Key management** follows least privilege and rotation (§4); keys are not embedded in source or images.

---

## 10. Verification & Gates

Security is mechanically gated in CI (the language standard pins the tools):

- **Secret scanning** — blocks secrets entering version control.
- **Dependency / SCA scanning** — flags known-vulnerable dependencies (e.g. `pip-audit`); pinned,
  reproducible builds.
- **SBOM generation** — every release artifact has a generated, attached SBOM (CycloneDX/SPDX) (§3.1).
- **Artifact signing & provenance** — release artifacts are signed and carry signed build provenance
  (SLSA L2 target); the release gate **verifies** signature + provenance before publish (Git & Release
  Engineering Standard §8).
- **Injection / static analysis** — lint and SAST for injection, unsafe deserialization, `shell=True`,
  and the like.
- **Tests** for the security-relevant paths: authorization is tested, cleanup is tested, "secrets never in
  output" is verified.
- **Security review** — a human review (and, for high-risk tools, a pen test / threat-model review)
  before a release; findings tracked to closure.

A gate's absence (no secret scan, no SCA, no authorization tests) is itself a finding.

---

## 11. Per-Tool Requirements

Every tool's `05_SECURITY_AND_OPSEC` doc states: its **threat model** + **control matrix** (§2); how it
meets the §3 controls; its **supply-chain posture** (§3.1 — SBOM format, artifact signing, and its SLSA
target); its **secrets** handling (§4); its **authorization/scope** model (§5); its **audit** design (§6);
its **OpSec** properties where it acts in a sensitive environment (§7); its **data handling / retention**
(§8); and the **CI security gates** it runs (§10). A tool with a low security surface says so
explicitly — the absence of a control is a recorded decision, not an oversight.

---

## 12. Why This Is Right

Designing security and operational security into the architecture means the easy path is the safe path:
the injection can't be written, the secret can't reach the log, the out-of-scope action is refused, and
the sensitive artifact is gone when the run ends. That is cheaper than auditing for those bugs later, and
far cheaper than the incident — and for tools that operate in adversarial environments, the operational
discipline is part of the tool working at all.

---

## Appendix A — Control checklist

Per tool, confirm:

- [ ] Threat model + control matrix in `05` (assets, adversaries, attack surface, residual risk).
- [ ] Parameterized queries; subprocess as arg-lists; no `shell=True` with untrusted input.
- [ ] Untrusted input validated at the boundary; external-tool output via an anti-corruption adapter.
- [ ] Output encoded for its sink; safe deserialization (no executable formats on untrusted data).
- [ ] Authorization chokepoint; scope gating; high-consequence actions require approval; fail closed.
- [ ] No secrets in source / logs / errors; secret scanner gate; differential reveal for sensitive values.
- [ ] Immutable, attributable audit trail; audit retained + integrity-protected.
- [ ] OpSec: minimal footprint; temp/artifact cleanup on every exit path (tested); output hygiene/redaction.
- [ ] Data classified; encrypted at rest/in transit; retention + real deletion defined; no client data in repo.
- [ ] Vetted crypto + TLS-with-validation; least-privilege, rotatable keys/tokens.
- [ ] Supply chain: dependencies pinned + SCA-scanned; releases ship an SBOM, signed artifacts, and signed
      build provenance (SLSA L2 target), verified at the release gate.
- [ ] CI gates: secret scan · SCA/dep scan · injection/SAST · security tests · pre-release security review.
