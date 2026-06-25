# LLM / AI Integration Standard

> **When a product embeds a large language model, the model is an untrusted, non-deterministic component
> that processes untrusted input — and it is treated as such.** An LLM is glue at a named boundary: it
> transforms structured input into structured output and **decides nothing**. Its inputs are assumed
> hostile (any external text may carry instructions), its outputs are never trusted or executed unchecked,
> its privileges are minimal, and the secrets in its context are assumed to leak. This standard makes the
> umbrella's Principle 1 — *determinism decides; an LLM never makes a decision* — concrete, and maps it to
> the **OWASP LLM Top 10 (2025)**.
>
> **Scope:** LLMs used *inside a product* (a feature that calls a model at runtime). This is distinct from
> the **AI Coding Phase Guidelines**, which govern an AI *building* software. Language-agnostic; under the
> `A_TALUS_Coding_Standard.md` umbrella. **Mandatory** wherever a product integrates an LLM. "Must" is a gate.
>
> Status: **Accepted, v1.0** (2026-06-25). Part of **Standards Suite v1.0**.

---

## Contents

§1 Purpose & Principles · §2 Where LLMs Are Allowed · §3 Prompt Injection (Direct & Indirect) · §4 Output
Handling · §5 Excessive Agency & Least Privilege · §6 System-Prompt & Data Protection · §7 Determinism,
Evaluation & Cost · §8 Verification & Gates · §9 Per-Tool Requirements · §10 Why This Is Right · Appendix A:
LLM-feature checklist

---

## 1. Purpose & Principles

LLMs are powerful and uniquely unsafe to integrate naively: they are non-deterministic, they confidently
fabricate, they cannot reliably separate instructions from data, and they process exactly the untrusted
text an attacker controls. Treating a model like a trusted function call is how you ship prompt injection,
data exfiltration, and an over-privileged agent. This standard contains the model to a safe role.

Principles:

1. **The model is glue, not a decision-maker.** An LLM transforms structured input into structured output
   at a *named seam*; it never gates control flow, authorizes an action, or decides what/when/who. The
   deterministic core decides (umbrella Principle 1); the model only *renders* or *extracts*.
2. **All model input is untrusted.** Any external text the model sees — a web page, an email, a document, a
   prior model output — may contain instructions aimed at the model. There is no parsing that reliably
   separates "instructions" from "data" inside one text blob, so the architecture must (§3).
3. **All model output is untrusted.** Output is data to be validated, never code to be executed or a command
   to be obeyed (§4). It is wrong sometimes; the system is designed for that.
4. **Least privilege for the model.** The model gets the minimum tools, data, and authority to do its one
   job; high-consequence actions stay behind a human and the deterministic core (§5).
5. **Assume the context leaks.** Anything placed in the prompt — system instructions, secrets, other users'
   data — may surface in output or be extracted. So: no secrets in prompts, and data minimization (§6).
6. **Isolate the non-deterministic seam.** The model lives behind a port so the rest of the system stays
   deterministic and testable (umbrella Principle 2), and the feature is evaluated, not assumed (§7).

---

## 2. Where LLMs Are Allowed

- **Named seams only.** Every LLM call site is an explicit, documented boundary with a typed input and a
  typed output — not an ambient capability sprinkled through the code. If you cannot name the seam and its
  contract, the feature isn't designed yet.
- **Structured in, structured out.** The model receives assembled, bounded input and returns output that is
  parsed against a schema (§4). Free-form text in, free-form text trusted out is not an integration; it is a
  liability.
- **Decides nothing.** The seam's output never *is* the decision — it feeds a deterministic step that
  validates and acts. Control flow, authorization, scope, ordering, and timing are the core's job, never the
  model's (Principle 1).
- **The integration is optional and isolated.** Behind a port/adapter (umbrella Principle 2), so the product
  runs and is testable with the model stubbed, and the provider/model is a swappable choice.

---

## 3. Prompt Injection (Direct & Indirect)

Prompt injection is the **#1 LLM risk** (OWASP **LLM01**) and the one the architecture must structurally
defend, because no prompt wording fully prevents it.

- **Direct injection** — the user tells the model to ignore its instructions. Mitigated by never giving the
  model authority worth hijacking (§5) and by validating output (§4), not by a cleverer system prompt.
- **Indirect injection** — instructions hidden in *content the model ingests* (a web page, a PDF, an email,
  a tool result, another model's output). This is the dangerous case for any tool that processes external
  text, because the attacker isn't the user — it's whoever authored the content.

The structural defenses (no single one suffices — defense in depth; Security & OpSec Standard §1):

- **Separate trusted instructions from untrusted data.** Carry the system/developer instructions in a
  distinct channel (system role, a separate parameter) and place untrusted content in a clearly delimited
  data region. **Never concatenate untrusted text into the instruction position.** The model is told, and
  the architecture enforces, that the data region is *data to be processed, not instructions to follow*.
- **Constrain capability, not just wording.** The model can't do damage it has no power to do: minimal tools
  (§5), output validated before use (§4), no privileged action without a human in the loop.
- **Treat external content as hostile at the boundary** (Security & OpSec Standard §3): the same
  anti-corruption posture applied to any untrusted input — you do not trust its shape *or* its intent.
- **Human review before consequence.** Where injected output could cause harm, a human approves the action
  the output would drive (§5) — the model proposes, a person disposes.

---

## 4. Output Handling

Improper output handling is OWASP **LLM05**. Model output is untrusted data crossing a trust boundary:

- **Never execute or trust model output directly.** No `eval`, no shell, no SQL built from model text, no
  unsanitized HTML rendered, no path/URL used unchecked. Output to a downstream sink is encoded for that
  sink exactly as any untrusted input would be (Security & OpSec Standard §3).
- **Validate against a schema.** Output that must be structured (JSON, an enum, a typed object) is parsed
  and validated against a strict schema before use; malformed or out-of-contract output is rejected and
  handled (retry/fallback/fail-closed), never coerced through. This is the API & Data-Contract Standard's
  validate-at-the-boundary rule applied to the model's output edge.
- **Constrain the output space** where the provider supports it (structured-output / function-calling
  schemas, enums) so the contract is enforced at generation, not just checked after.
- **Plan for wrong.** The feature degrades sensibly when the model is confidently wrong (OWASP **LLM09**,
  misinformation): a human reviews consequential output; nothing irreversible rides on an unvalidated
  generation.

---

## 5. Excessive Agency & Least Privilege

Excessive agency is OWASP **LLM06** — harm from giving a model too much capability, autonomy, or
permission:

- **Minimum tools.** A model/agent is granted only the specific tools and data its one job needs, each with
  the narrowest scope. No broad "do anything" tool, no ambient filesystem/network/credential access.
- **No autonomous high-consequence action.** An action that changes an external system, spends money, sends
  a message, or touches a target requires an explicit human approval and passes the deterministic core's
  authorization chokepoint (Security & OpSec Standard §5). The model **proposes**; the human and the core
  **dispose**. Nothing high-impact is model-driven and autonomous.
- **Bounded resources.** Cap tokens, call depth, tool invocations, recursion, and spend per operation to
  contain runaway loops and cost (OWASP **LLM10**, unbounded consumption); enforce timeouts (Observability &
  Reliability Standard §7).
- **Least privilege end to end.** The model's identity/credentials (if any) are scoped and short-lived like
  any other (Security & OpSec Standard §1/§4).

---

## 6. System-Prompt & Data Protection

System-prompt leakage is OWASP **LLM07**; sensitive-information disclosure is **LLM02**:

- **No secrets in prompts.** Never place credentials, API keys, or sensitive internal data in a system or
  user prompt — assume the prompt's full content can be extracted, because it can. The system prompt is not
  a secret store and is not a security control.
- **Data minimization.** Put in the context only the data the task needs; don't dump a whole record, other
  users' data, or unnecessary internal detail into the prompt. Less context = smaller leak.
- **Tenant/user isolation.** One user's data never bleeds into another's context (no shared, unscoped
  conversation state); retrieved/embedded data respects the same authorization as the rest of the system
  (guard against cross-context leakage, OWASP **LLM08**).
- **Treat the provider boundary honestly.** What is sent to a third-party model leaves your control;
  classify it (Security & OpSec Standard §8) and don't send what policy or scope forbids.

---

## 7. Determinism, Evaluation & Cost

- **Isolate the non-deterministic seam.** Behind a port (umbrella Principle 2), so the deterministic core
  stays unit-testable with the model stubbed and the system's behavior doesn't hinge on a sampling outcome.
  The seam's *contract* (typed in/out) is stable even though the model isn't.
- **Evaluate the feature, don't assume it.** An LLM feature has an evaluation suite — representative inputs,
  expected-property assertions, and **adversarial/red-team cases** (injection attempts, jailbreaks,
  malformed output) — run like tests. "It looked good in a demo" is not verification.
- **Observability without leakage.** Prompts, outputs, token usage, latency, and cost are logged for
  debugging and spend control (Observability & Reliability Standard) — but **redacted of secrets/sensitive
  data** (Security & OpSec Standard §4). The audit trail records that the model was used and what action its
  output drove (Security §6), separately from telemetry.
- **Cost & latency are operational properties.** Budget and monitor token spend and latency; cache where
  sound; the non-deterministic seam still meets a performance/cost budget (Observability & Reliability
  Standard §9).

---

## 8. Verification & Gates

- **Adversarial evaluation in CI** — the red-team/eval suite (§7) runs as a gate: known injection and
  jailbreak cases must be handled (output rejected / human-gated / no privileged action), not obeyed.
- **Output-validation tests** — malformed and out-of-contract model output is rejected and handled, proven
  by tests (§4).
- **Secret-in-prompt scan** — the secret-scan gate (Security & OpSec Standard §10) covers prompt templates;
  no credential or sensitive constant is assembled into a prompt.
- **Agency review** — a human review confirms the model's tools/permissions are minimal and no
  high-consequence action is autonomous (§5).
- **Security review** — the LLM seam is in the threat model (Security & OpSec Standard §2); indirect
  injection via ingested content is explicitly considered.

---

## 9. Per-Tool Requirements

A tool that integrates an LLM documents, in its `05_SECURITY_AND_OPSEC` and architecture docs: **each named
seam** (its typed input/output contract and what deterministic step consumes the output); its **injection
threat model** (especially indirect injection from any ingested external content, §3); its **output
validation** (schema, rejection/fallback, §4); the model's **tools/permissions and the human-approval
points** for any consequential action (§5); its **prompt/data handling** (no secrets, minimization, isolation,
§6); and its **evaluation/red-team suite** and cost/latency budget (§7). A tool that uses **no** LLM states
so — the default — and nothing here applies.

---

## 10. Why This Is Right

An LLM integrated as a trusted, capable, autonomous component is a vulnerability with a friendly interface:
it will be prompt-injected through the content it reads, it will emit something wrong or malicious, and an
over-privileged agent will act on it. Contained to a named seam that decides nothing, fed input treated as
hostile, with output validated and privileges minimal and the context assumed to leak, the same model is a
safe, useful transformer — and the deterministic core stays in charge, exactly as the umbrella's first
principle requires. The constraints are what make it possible to use an LLM at all in a security-sensitive
product.

---

## Appendix A — LLM-feature checklist

Per LLM seam, confirm:

- [ ] Named seam with a typed input/output contract; the model decides nothing — a deterministic step consumes its output.
- [ ] Behind a port; product runs/tests with the model stubbed; provider is swappable.
- [ ] Trusted instructions separated from untrusted data; external/ingested content never placed as instructions (indirect-injection defense, LLM01).
- [ ] Output validated against a strict schema; never executed/trusted unchecked; encoded for its sink (LLM05).
- [ ] Minimum tools/permissions; no autonomous high-consequence action (human + core authorize); resource/cost caps (LLM06, LLM10).
- [ ] No secrets in prompts; data minimized; tenant/user isolation; provider boundary classified (LLM02/LLM07/LLM08).
- [ ] Evaluation + adversarial/red-team suite runs in CI; output-validation tests; prompt secret-scan.
- [ ] Prompts/outputs logged redacted (no secrets); model use + driven action in the audit trail; cost/latency budgeted.
