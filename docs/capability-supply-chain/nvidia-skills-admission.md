# M14 External Skill Capability Supply Chain and Admission Gate

Document state: M14 completed.

Release state: Included in published v0.13.0.

Historical implementation evidence: PR #208.

Historical completed references: source issue #192 and M14 tracker #201. Related M14 context includes PR #202, PR #204, PR #205, and PR #206.

## 1. Purpose and scope

This document defines a model-agnostic and vendor-agnostic Capability Supply Chain and Skill Admission Gate for external agent skills. NVIDIA/skills is used only as an external capability-supply-chain reference specimen. It is not downloaded, installed, imported, executed, or made an AAOS dependency by this work.

The governing separation is:

- NVIDIA skills are external agent capability artifacts.
- AAOS is the capability admission, permission, evidence, replay, escalation, and decision-governance control plane.

A skill may describe how an agent performs a task. The skill must not decide whether it may enter the system, whether it may be activated, which permissions it receives, whether its evidence is sufficient, whether risk is accepted, whether execution is approved, or whether Decision Proof is sealed.

Capability availability is not permission. Skill installation is not execution authorization. Skill metadata is not verified behavior. A signature is not governance approval. A scan result is not risk acceptance. An evaluation result is not deployment approval. Admission ready for review is not final admission approval.

This gate evaluates fixture records only. It does not fetch repositories, resolve mutable references, install dependencies, access external networks, invoke a device, import an external skill, execute skill instructions, or execute shell commands found in metadata. It produces deterministic registry and review-routing findings, not permission grants or execution decisions.

## 2. External capability-supply-chain threat model

An external skill is untrusted until its exact artifact, declared behavior, requested authority, evidence, and runtime boundary have been independently evaluated. The admission model addresses at least these threats:

| Threat | Example failure | Required control |
| --- | --- | --- |
| Mutable identity | A branch or tag changes after review | Bind the review to source commit, artifact digest, version, permission declaration, evidence set, and policy version |
| Source ambiguity | Repository or owner is missing or spoofed | Require immutable source identity and explicit owner identity; fail closed when absent |
| Metadata/behavior divergence | Observed requirements exceed the skill card | Compare declared and observed permissions; block any mismatch or escalation |
| Permission smuggling | Shell, network, file, MCP, secret, tool, or environment access is omitted | Require an explicit declaration for every permission class, including an explicit denial |
| Metadata command injection | A field contains instructions to run a command | Treat metadata only as data; never execute commands during evaluation |
| Install-to-execute confusion | Availability or installation is treated as activation | Keep acquisition, admission, activation, and execution as separate governed states |
| Evidence laundering | A signature, scan, benchmark, or evaluation is presented as approval | Verify evidence for its limited claim and retain AAOS risk and decision authority |
| Excess authority | A signed or scanned skill requests arbitrary shell or broad secrets | Apply least privilege independently of signature or scan status and block excessive scope |
| Runtime escape | The skill can spawn processes, reach devices, or access undeclared networks | Require compatible isolation, sandbox constraints, and enforceable permission boundaries |
| Output confusion | Skill output contains an approval or authority claim | Require a validated output contract and reject forbidden governance outputs |
| Missing accountability | Execution cannot be reconstructed | Require trace policy, replay packet requirements, artifact identity, inputs, outputs, and state transitions |
| Artifact or evidence drift | Digest, permission needs, runtime, policy, or evidence changes | Invalidate the review binding and require reassessment |
| Stale confidence | Evidence ages beyond its review interval | Track reassessment interval, last reassessment, expiration, and trigger-based review |
| High-risk capability | Medical advice or physical action is enabled on thin evidence | Require domain evaluation, sandboxing, human review, escalation, and independent execution authorization |
| Authority transfer | Registry or evaluator claims final governance judgment | Restrict outputs and keep Decision Proof sealing and decision sovereignty with AAOS |

Unknown, incomplete, stale, expired, drifting, over-permissioned, or non-replayable candidates fail closed. Evaluation is offline and non-executing, so untrusted metadata cannot turn an admission check into skill execution.

## 3. NVIDIA/skills reference positioning

NVIDIA/skills illustrates the general fact that agent capabilities can arrive as external artifacts with descriptive metadata, runtime expectations, tools, and operating instructions. This document derives a vendor-neutral admission model from that supply-chain shape; it does not reproduce, execute, assess, certify, or depend on any NVIDIA skill.

All specimen evidence in this work is clearly synthetic. It contains no real NVIDIA code, device data, source commit, release, signature, scan result, benchmark result, evaluation result, or execution output. No NVIDIA endorsement, certification, signature validation, or security approval is asserted or implied. Names associated with NVIDIA or Jetson identify the reference context only, not provenance or approval of the fixture.

The same contract applies to skills from any vendor, community, internal team, or individual author. Admission policy cannot prefer or delegate governance authority to a vendor. NVIDIA skills remain external capability artifacts, and AAOS remains vendor-independent.

## 4. AAOS layer mapping

| AAOS layer | Skill-admission responsibility | Retained boundary |
| --- | --- | --- |
| L0 Governance / Business Intent | Defines purpose, prohibited outcomes, risk appetite, liability boundary, and escalation doctrine | An external skill cannot define business intent or accept risk |
| L1 Policy & Identity Plane | Authenticates owners and reviewers; binds policy, identity, permission doctrine, approval routes, and admission policy version | Metadata cannot grant identity, permissions, exceptions, or waivers |
| L2 Control Plane | Routes candidates, applies admission gates, requests review or sandboxing, and arbitrates later activation and execution decisions | A candidate state or evaluator finding is not activation or execution approval |
| L3 Model Runtime | Records supported agents and runtimes and checks compatibility with an isolated execution environment | Runtime compatibility does not authorize a skill or select it for production |
| L4 Tool / Data Execution | Defines enforceable tool, network, file, shell, MCP, secret, environment, and device boundaries | Requested capability is constrained by the AAOS permission envelope and least privilege |
| L5 Memory & Reconstruction Graph | Retains immutable artifact identity, evidence references, permission diffs, registry history, drift, reassessment, traces, and replay packets | Stored evidence and replay readiness do not seal Decision Proof |
| L6 Verification & Audit | Checks binding, scans, signature-verification evidence, benchmarks, evaluations, output schemas, traces, replay, and fail-closed conditions | Verification findings are inputs to AAOS governance, not final approval or audit closure |

External skills can supply capability descriptions to L3/L4 and evidence subjects or inputs to L5/L6. They do not own L0 purpose, L1 policy and identity, or L2 decision authority.

## 5. Skill Admission Contract

Every candidate must provide the following 53 core fields in the vendor-neutral Skill Admission Contract. The fixture evaluation record also carries normalized policy, scope, observed-requirement, evidence-binding, and immutable-review fields used by the gate. Empty, omitted, ambiguous, or non-applicable values must be explicit and policy-valid; omission cannot be interpreted as denial or safety.

1. `skill_id` — stable logical identifier for the capability.
2. `skill_name` — human-readable name; never sufficient artifact identity by itself.
3. `source_repo` — canonical source repository identity; an unknown source fails closed.
4. `source_owner` — accountable owner of the source repository.
5. `source_commit` — immutable source revision reviewed for admission.
6. `source_artifact_digest` — digest of the exact reviewed artifact bytes.
7. `version` — immutable or otherwise review-bound artifact version.
8. `license` — declared license governing the reviewed artifact.
9. `description` — bounded description of capability and behavior.
10. `intended_use` — allowed purpose and operational context.
11. `prohibited_use` — explicit disallowed purposes, domains, and actions.
12. `activation_triggers` — events that may request activation; triggers never self-authorize.
13. `supported_agents` — compatible agent interfaces or classes.
14. `supported_runtimes` — compatible runtime identities and versions.
15. `required_tools` — complete tool inventory, including an explicit empty list.
16. `required_permissions` — normalized string-enum union of all permissions requested by the skill.
17. `network_access` — explicit `none` or `restricted_outbound` declaration.
18. `allowed_network_domains` — allowlist when network access is requested.
19. `blocked_network_domains` — domains that remain prohibited.
20. `file_access` — explicit `none`, `read_only`, or `restricted_read_write` declaration.
21. `allowed_file_scopes` — least-privilege file allowlist.
22. `blocked_file_scopes` — protected paths and categories.
23. `shell_access` — explicit `none` or `restricted_command_classes` declaration.
24. `allowed_command_classes` — narrowly classified commands, never unbounded command text.
25. `blocked_command_classes` — prohibited arbitrary, destructive, privileged, install, mutation, and credential commands.
26. `mcp_access` — explicit `none` or `restricted_mcp` declaration.
27. `required_mcp_servers` — exact server identities required, or an explicit empty list.
28. `environment_variables` — names, purposes, and sensitivity only; never secret values.
29. `secret_access` — explicit `none` or `named_secret_classes` declaration; secret classes and purpose are separately scoped.
30. `data_classification` — highest data sensitivity the skill can receive or produce.
31. `risk_level` — policy-defined risk classification.
32. `known_risks` — documented safety, security, privacy, authority, and operational risks.
33. `mitigations` — controls mapped to each known risk.
34. `owner_contact` — accountable skill owner and human review contact.
35. `skill_card` — reviewable capability card bound to the artifact.
36. `scan_report` — referenced scan evidence or an explicit policy-valid not-required state.
37. `scan_tool` — scan tool identity and version for supplied scan evidence.
38. `scan_timestamp` — time of scan for freshness assessment.
39. `signature` — signature evidence or an explicit policy-valid not-required state.
40. `signature_identity` — asserted signer identity for supplied signature evidence.
41. `signature_verification_method` — method and verification artifact, not a governance conclusion.
42. `benchmark_report` — referenced task/safety benchmark evidence or a justified not-required state.
43. `evaluation_artifacts` — artifact-bound evaluation cases, results, limits, and provenance.
44. `runtime_isolation_requirements` — sandbox, process, network, filesystem, device, and resource constraints.
45. `output_contract` — machine-validatable output schema and forbidden-output rules.
46. `trace_requirements` — required identity, inputs, tool calls, outputs, decisions, and state transitions.
47. `replay_requirements` — deterministic replay packet contents and environment reconstruction rules.
48. `rollback_requirements` — containment and rollback readiness; a plan is not execution.
49. `fail_closed_rules` — conditions that require blocking or an admission-not-ready result.
50. `reassessment_interval` — maximum evidence age and review cadence.
51. `last_reassessment` — timestamp and record reference for the latest completed reassessment.
52. `expiration_date` — point after which evidence cannot support admission without reassessment.
53. `admission_policy_version` — exact AAOS policy version used for evaluation.

The contract is a declaration and evidence index, not verified behavior or a grant of authority. Observed requirements are evaluated independently against it.

Access declarations use one consistent vendor-neutral string-enum schema:

| Axis | Allowed enum values |
| --- | --- |
| Network | `none`, `restricted_outbound` |
| File | `none`, `read_only`, `restricted_read_write` |
| Shell | `none`, `restricted_command_classes` |
| MCP | `none`, `restricted_mcp` |
| Secret | `none`, `named_secret_classes` |

`required_permissions` must use the same enum value as the corresponding `network_access`, `file_access`, `shell_access`, `mcp_access`, or `secret_access` field. Every axis requires an explicit denial or bounded enum; booleans, omitted values, arbitrary strings, and unbounded access are invalid.

The fixture also carries a deterministic `permission_scope` record. Its `declared` member contains nine dimensions, each represented as an object with explicit `allowed` and `blocked` string lists: `required_tools`, `network_domains`, `file_scopes`, `command_classes`, `mcp_server_identities`, `environment_variable_names`, `secret_classes`, `data_classifications`, and `activation_triggers`. Its `observed` member contains the same nine dimensions as string lists. The declared record is a normalized projection of the contract fields, while the observed record is inert synthetic evaluation evidence; neither authorizes use.

## 6. Capability registry model

The capability registry may assign one or more routing states:

- `candidate_allowed`
- `candidate_restricted`
- `candidate_blocked`
- `needs_approval`
- `needs_sandbox`
- `needs_human_review`
- `needs_replay_log`
- `needs_signature_verification`
- `needs_scan`
- `needs_evaluation`
- `stale_reassessment_required`

These are registry and routing states only. They must not be treated as final execution approval, risk acceptance, deployment authorization, audit closure, or Decision Proof sealing. In particular, `candidate_allowed` means that the candidate passed the bounded admission checks represented by the record; it does not grant permissions, activate, install, deploy, or execute the skill.

Each registry entry contains all 12 fields below:

1. `registry_entry_id` — immutable identifier for this registry decision record.
2. `skill_id` — link to the logical skill identity.
3. `artifact_identity` — source commit, artifact digest, version, reviewed permission declaration, reviewed detailed permission scope, reviewed evidence set, and admission policy version.
4. `candidate_admission_state` — one or more candidate/routing states from the controlled vocabulary.
5. `permission_envelope` — maximum permissions that later AAOS review may consider; never a grant.
6. `evidence_status` — completeness, validity, binding, and freshness findings by evidence class.
7. `runtime_constraints` — isolation and compatibility requirements.
8. `human_review_route` — accountable role, queue, escalation path, and pending/completed state.
9. `reassessment_status` — last review, next due date, expiration, triggers, and staleness.
10. `trace_policy` — mandatory trace content and retention rules.
11. `replay_policy` — replay packet, deterministic reconstruction, and review requirements.
12. `governance_owner` — AAOS authority accountable for the next governance step.

Registry updates are append-only or otherwise reconstructable. State changes retain the prior artifact identity, permission diff, evidence diff, reviewer handoff, and reason codes.

## 7. Artifact identity and immutable review binding

The exact admitted artifact must be bound to all of the following as one review identity:

- source commit
- artifact digest
- version
- reviewed permission declaration
- reviewed detailed permission scope
- reviewed evidence set
- admission policy version

A branch name, mutable tag, repository URL, or skill name alone is insufficient artifact identity. A commit without an artifact digest is also insufficient because source identity and reviewed bytes are distinct claims.

The digest is recomputed or supplied by a trusted offline fixture boundary and compared with the reviewed digest without executing the artifact. Any change to bytes, source commit, version, coarse permissions, detailed permission scope, evidence, or policy version creates a new review subject. A digest mismatch is artifact drift and is blocked; it cannot inherit the prior candidate state. A mutable branch or tag may be recorded for context but cannot replace immutable binding.

Evidence references must themselves identify the artifact they assess. Evidence for another digest, version, permission envelope, runtime, or policy version is non-binding and cannot satisfy the gate.

## 8. Permission declaration and least-privilege rules

The contract must explicitly declare tool, network, file, shell, MCP, environment-variable, secret, data, and device needs, including explicit denials and empty scopes. Undeclared permission is blocked, not inferred. The normalized `required_permissions` union must agree with every access enum, and the normalized `permission_scope.declared` record must agree with the corresponding contract allowlists, blocklists, tool list, environment-variable names, data classification, and activation triggers.

AAOS computes a permission diff between the immutable `reviewed_permission_scope` and observed requirements recorded in synthetic evaluation evidence. For each of the nine dimensions, every observed value must be a member of the reviewed declared `allowed` set and must not match the reviewed declared `blocked` set. Any observed tool, domain, file scope, command class, MCP server identity, environment-variable name, secret class, data classification, or activation trigger outside the declaration is permission escalation and is blocked. A blocked entry overrides an allowlist collision.

A strictly narrower observed set is not permission escalation. It may produce a `permission_overdeclaration` least-privilege finding, but that finding must not be mislabeled as escalation. Wildcards and other unbounded values are invalid in both allowed and observed scopes; wildcard deny patterns may be used only in a blocked list. A new or changed tool, domain, file scope, command class, MCP server, secret class, data classification, device capability, activation trigger, environment dependency, or blocked scope requires a new review binding. If the live declared scope differs from `immutable_review_binding.reviewed_permission_scope`, the prior review binding is invalid even when the observed scope is narrower.

Environment-variable names and secret access remain separate dimensions. A non-secret configuration name such as `LOG_LEVEL` does not imply secret access. Secret access requires `secret_access: named_secret_classes` plus separately declared named secret classes. Fixture metadata may contain names, purposes, and sensitivity labels, but never raw environment-variable or secret values.

Least privilege requires:

- deny-by-default access and explicit allowlists;
- the smallest resource scope, operation class, duration, and data classification needed for intended use;
- separation of read, write, mutation, install, privileged, device-control, and arbitrary execution capabilities;
- no wildcard or unbounded value in an allowed or observed network, filesystem, secret, MCP, shell, tool, environment-variable, data, or activation scope;
- no credential values in metadata, traces, replay packets, or outputs;
- blocked scopes that override an allowlist collision;
- runtime enforcement independent of what the skill claims;
- separate AAOS activation and execution authorization after admission review.

The evaluator treats skill metadata as inert fixture data. It never executes a shell command or accesses a network to validate a permission claim.

## 9. Scan, signature, benchmark, and evaluation evidence

Evidence requirements are determined by risk, provenance, permission scope, runtime, data classification, age, and policy version. Each supplied evidence item must identify its artifact digest, source commit, version, producer or tool, method, timestamp when applicable, applicable runtime, declared limitations, and evidence artifact reference. An evidence class that policy does not require may be absent; a nonexistent scan does not require a timestamp.

- Signature evidence may support an identity/integrity claim. Artifact signature is not governance approval, and signature verification is not risk acceptance.
- Scan evidence may report bounded static or dynamic findings. Scan passed is not risk accepted, does not prove behavior, and cannot excuse undeclared permissions.
- Benchmark evidence measures only the declared scenario and method. Benchmark passed is not deployment approval.
- Evaluation evidence reports bounded observed behavior under stated conditions. Evaluation evidence is not final approval and cannot replace runtime isolation or human review.

The evaluator applies the evidence flags independently and conditionally:

| Policy state | Required behavior |
| --- | --- |
| `signature_required: true` | A supplied signature must be present and must not be a not-required marker. |
| `signature_verification_evidence_required: true` | Both a supplied signature and signature-verification evidence must be present. |
| `signature_required: false` | Signature evidence may be absent or explicitly `not_required_by_policy`; absence does not produce `required_signature_missing`. |
| `signature_verification_evidence_required: false` | Verification evidence may be absent; absence does not produce `signature_verification_evidence_missing`. |
| `scan_required: true` | `scan_report`, `scan_tool`, `scan_timestamp`, and an exact `scan_artifact_binding` for source commit, artifact digest, and version must all be present and well formed. |
| `scan_required: false` | The scan bundle may be wholly absent or explicitly `not_required_by_policy`; a nonexistent scan needs no timestamp and does not produce `required_scan_missing`. |

Optional evidence is still validated when supplied. A partial signature or scan bundle, malformed optional record, not-required marker mixed with supplied companion fields, verification requirement paired with an absent and explicitly not-required signature, or scan not-required state paired with a partial scan record is contradictory and fails closed. A supplied signature does not require verification evidence when verification evidence is not required, but it must still have well-formed identity and method metadata. Required scan binding must exactly match the contract's source commit, artifact digest, and version, and the scan-report reference must remain in the reviewed evidence set.

For `high` and `critical` risk, both artifact-bound benchmark evidence and artifact-bound evaluation evidence are mandatory. Setting `benchmark_required` or `evaluation_required` to false cannot waive either requirement. Physical-action capabilities additionally require sufficient sandbox evidence and a human-review route.

All evidence in the fixture is synthetic and must be labeled as such. No real NVIDIA signature, scan, benchmark, commit, release, or evaluation is represented. The admission evaluator performs no network lookup and makes no endorsement, certification, security-approval, signature-validation, or deployment claim.

## 10. Runtime compatibility and isolation requirements

Compatibility is checked against exact supported-agent interfaces, runtime identities and versions, output-schema support, trace hooks, replay support, and enforceable permission controls. A compatible runtime is not an authorized runtime.

Isolation requirements must define, as applicable:

- sandbox identity and version;
- process-spawn and arbitrary-code controls;
- network disabled by default and enforceable domain restrictions when separately approved;
- read/write/mutation filesystem boundaries;
- device, firmware, package-manager, kernel, and privileged-operation boundaries;
- MCP server allowlists and per-tool scopes;
- secret mediation with no raw credential exposure;
- CPU, memory, time, and output limits;
- clean environment-variable allowlists;
- trace capture outside skill control;
- deterministic replay inputs and retained runtime description;
- containment and rollback handoff.

If required isolation cannot be enforced, the candidate is blocked or marked `needs_sandbox` and `admission_not_ready`. Evaluation occurs only on fixture data, imports no third-party package, accesses no external network, executes no shell command, and does not execute the skill.

## 11. Execution trace and replay requirements

Admission evaluation does not execute a skill. It verifies that any separately authorized future execution would be traceable and replayable within the declared privacy and secret-handling boundary.

The trace policy must require the artifact identity, registry entry, admission policy version, activation request, AAOS authorization reference, agent/runtime identity, input references, permission envelope, tool/MCP requests, network/file/shell/secret mediation events, outputs and schema-validation results, state transitions, denied conditions, human handoffs, errors, containment recommendations, and timestamps. Trace collection must be tamper-evident and outside the skill's authority to suppress or rewrite.

The replay policy must require a replay packet containing immutable artifact and evidence references, sanitized inputs, runtime and isolation description, policy version, permission decisions, ordered events, output validation, expected findings, and determinism limitations. Secrets and prohibited data are referenced through governed handles, not copied into replay material.

If trace requirements are missing, or replay evidence cannot be produced, admission is blocked. `needs_replay_log` and `replay_ready` are routing/evidence states only. Missing trace is blocked. Missing replay is blocked. Replay success does not approve execution and does not seal Decision Proof.

## 12. Output contract requirements

Every skill candidate must define a machine-validatable output contract with:

- schema identity and version;
- allowed fields, types, enumerations, size limits, and data classification;
- required provenance, artifact identity, and trace correlation;
- error and partial-result forms;
- explicit separation of observation, recommendation, requested action, and approved action;
- forbidden sensitive-data, credential, authority, execution, approval, and sealing claims;
- deterministic validation failure behavior;
- safe rendering and downstream parsing rules.

Undefined, unversioned, or non-validatable output is blocked. Schema validity demonstrates conformance to a format, not truth, safety, risk acceptance, deployment authorization, or execution approval. Skill output cannot expand its permission envelope or direct AAOS to treat a recommendation as an action.

## 13. Drift, staleness, and periodic reassessment

Each registry record tracks `reassessment_interval`, `last_reassessment`, `expiration_date`, next due date, evidence timestamps, policy version, and reassessment triggers. A stale skill receives `stale_reassessment_required` and is not executable. Expired admission evidence is blocked.

Reassessment is required after any artifact, source, version, ownership, license, permission, tool, runtime, isolation, output contract, evidence, risk, data classification, intended-use, prohibited-use, activation-trigger, incident, policy, or upstream-supply-chain change. Periodic reassessment is also required at the declared interval even when no change is reported.

Artifact digest drift is always a new review subject. Permission drift is always evaluated as a possible escalation. Evidence that no longer binds, is older than policy permits, or was produced under incompatible runtime or permission assumptions cannot be carried forward. Reassessment history records who reviewed what and when; it does not certify ongoing safety or grant continuing execution authority.

## 14. Fail-closed admission rules

The evaluator must always return `candidate_blocked` or `admission_not_ready` when any of these conditions applies. Applicable `needs_*` or `stale_reassessment_required` values may be added only as registry or routing states; they never replace the blocking or not-ready result. Expiration remains blocked, and staleness remains not ready until reassessment.

1. Skill source is unknown.
2. Source owner is missing.
3. Source commit is missing.
4. Artifact digest is missing.
5. Version is missing.
6. License is missing.
7. Skill owner is missing.
8. Permission declaration is incomplete.
9. An observed coarse permission or detailed scope exceeds its reviewed declaration.
10. Shell access is undeclared.
11. Network access is undeclared.
12. File access is undeclared.
13. MCP access is undeclared.
14. Secret access is undeclared.
15. Output contract is undefined.
16. Trace requirements are missing.
17. Replay evidence cannot be produced.
18. Runtime isolation is insufficient.
19. Signature is required but missing.
20. Signature verification evidence is required but the signature or verification evidence is missing.
21. Scan evidence is required but its report, tool, timestamp, or exact artifact binding is missing.
22. High-risk or critical use lacks either benchmark evidence or evaluation evidence.
23. Artifact digest no longer matches the reviewed artifact.
24. Skill is expired or stale.
25. Reassessment is overdue.
26. Source uses only a mutable branch or tag without immutable binding.
27. Optional signature or scan evidence is partial or malformed.
28. Evidence requirement flags and supplied evidence state contradict one another.
29. An allowed or observed permission scope is wildcard or otherwise unbounded.
30. A blocked scope collides with a requested or observed scope.
31. The declared detailed scope differs from the immutable reviewed scope.

Default posture:

- Unverified skill = not executable.
- Undeclared permission = blocked.
- Permission escalation = blocked.
- Missing trace = blocked.
- Missing replay = blocked.
- High-risk domain without evaluation evidence = blocked.
- Artifact identity drift = blocked.
- Expired admission evidence = blocked.

A signature cannot override excessive permissions. A scan cannot override undeclared network access. Evidence cannot override artifact drift, missing isolation, or an authority-boundary violation. `fail_closed_recommended` is a routing recommendation; the evaluator does not execute fail-closed, rollback, installation, activation, or any skill command.

## 15. Low-risk Jetson diagnostic specimen

The fixture includes a synthetic, non-executing, read-only Jetson device diagnostic skill solely to exercise the contract. It contains no real NVIDIA code, real device data, real repository artifact, real signature, real scan, real benchmark, or real evaluation output. It does not access a device or network and does not run a shell command.

Its bounded declaration is:

- identity: a clearly synthetic fixture repository, synthetic immutable commit label, synthetic digest label, and `0.0.0-synthetic` version;
- intent: read-only diagnostic interpretation of synthetic telemetry supplied as fixture input;
- prohibited use: device mutation, firmware modification, package installation, credential access, arbitrary shell execution, network access, device access, safety control, and physical action;
- permission envelope: fixture-input read only, no host file access, no shell, no network, no MCP, no secrets, one named non-secret `LOG_LEVEL` configuration variable, no environment credentials, and no device interface;
- runtime: a synthetic isolated fixture runtime with process spawn, external filesystem, network, package manager, privileged operations, and device access disabled;
- evidence: explicitly synthetic, artifact-bound admission evidence with no claim about real NVIDIA software or hardware;
- output: a versioned read-only diagnostic schema using synthetic status observations, limitations, and trace correlation only;
- trace and replay: required artifact identity, sanitized fixture input, deterministic evaluation trace, output-schema validation, and replay packet;
- governance: human admission-review handoff remains required, and Decision Proof sealing remains AAOS-owned.

The specimen requires immutable artifact identity and output schema validation. Its maximum positive result is `admission_ready_for_review` with an applicable candidate registry state. That result is not final admission approval, permission, activation, installation, device access, execution authorization, deployment approval, risk acceptance, or Decision Proof sealing.

## 16. High-risk domain restrictions

High-risk and critical candidates require both domain-appropriate artifact-bound benchmark evidence and artifact-bound evaluation evidence, sufficient runtime isolation, sandbox routing, explicit human review, trace and replay capability, and AAOS escalation. These conditions are cumulative, cannot be disabled by evidence flags, and cannot be satisfied by a signature or scan alone.

- Medical skills must not diagnose, recommend treatment as an approved clinical action, access real patient data, or influence care without separate domain policy and human authority. Missing evaluation evidence blocks the candidate.
- Physical-action, robotics, device-control, firmware, vehicle, industrial, or actuator skills require an enforceable sandbox and human-review route. Without both, the candidate is blocked.
- Finance, employment, education, government-service, biometric, credential, cybersecurity, and other consequential domains require independent domain restrictions, appeal or review routes where applicable, and separate execution authorization.
- Skills requesting arbitrary shell, device mutation, broad network, package installation, unrestricted files, raw credentials, or uncontrolled external output are blocked or restricted regardless of signature, scan, benchmark, or vendor reputation.

`needs_evaluation`, `needs_sandbox`, `needs_human_review`, and `needs_approval` identify unresolved routing requirements. They do not mean those requirements were completed. A positive evaluation remains evidence, not risk acceptance, deployment approval, or execution authorization.

## 17. Capture / Verify / Accumulate mapping

### Capture

Capture records all of the following without approving them:

- skill identity
- source identity
- immutable artifact identity
- declared owner
- intended use
- prohibited use
- runtime
- supported agent
- requested permissions
- shell scope
- network scope
- file scope
- MCP scope
- secret scope
- data classification
- risk classification
- output contract
- activation trigger

### Verify

Verify deterministically checks all of the following without granting authority:

- source binding
- digest binding
- version binding
- owner presence
- license presence
- permission completeness
- least-privilege check
- permission mismatch check
- signature requirement
- signature evidence
- scan requirement
- scan evidence
- benchmark requirement
- evaluation evidence
- runtime isolation
- sandbox requirement
- human-review requirement
- trace availability
- replay availability
- output-contract validity
- staleness
- expiration
- reassessment requirement
- fail-closed decision

### Accumulate

Accumulate retains all of the following for review and reconstruction:

- admission evaluation trace
- evidence artifact references
- denied-condition trace
- permission-diff record
- reviewer handoff
- registry decision record
- runtime constraint record
- execution trace policy
- replay packet requirements
- drift record
- reassessment history
- incident linkage
- governance authority retention

Capture is not approval. Verify is not final judgment. Accumulation is not audit closure or Decision Proof sealing.

## 18. Governance boundary

The required boundary statements are:

- External skill capability is not governance permission.
- Skill metadata is not verified behavior.
- Skill installation is not execution authorization.
- Artifact signature is not governance approval.
- Signature verification is not risk acceptance.
- Scan passed is not risk accepted.
- Benchmark passed is not deployment approval.
- Evaluation evidence is not final approval.
- `candidate_allowed` is not execution approval.
- `needs_approval` is not approval granted.
- `admission_ready_for_review` is not final admission approval.
- `fail_closed_recommended` is not `fail_closed_executed`.
- `rollback_recommended` is not `rollback_executed`.
- `human_review_required` is not completed review.
- `evidence_complete` is not Decision Proof sealing.
- `replay_ready` is not Decision Proof sealing.
- Registry classification is not final governance judgment.
- NVIDIA skills remain external capability artifacts.
- AAOS remains model-agnostic and vendor-independent.
- Decision Proof sealing remains AAOS-owned.
- AAOS remains the decision sovereignty layer.

The skill, registry, evaluator, scan report, signature, benchmark, adapter, and runtime may declare, inspect, classify, verify, report, trace, replay, recommend, or route evidence. They must not approve execution or deployment, grant permissions, activate or install a skill, accept risk, close an audit, grant a waiver, execute rollback, execute fail-closed, transfer authority, make final governance judgment, or seal Decision Proof.

AAOS retains business intent, policy and identity authority, admission policy, permission authority, activation and execution authorization, risk acceptance, escalation, fail-closed and rollback execution, audit closure, final governance judgment, and Decision Proof sealing. No vendor, artifact, registry, or evaluator becomes the AAOS decision router or sovereignty layer.

Allowed evaluator outputs are limited to validation, readiness, candidate-routing, mismatch, drift, fail-closed recommendation, rollback recommendation, and escalation findings. They include `skill_admission_fixture_valid`, `skill_admission_fixture_invalid`, `admission_ready_for_review`, `admission_not_ready`, the 11 registry states, `permission_mismatch_detected`, `artifact_drift_detected`, `fail_closed_recommended`, `rollback_recommended`, and `escalation_required`. These outputs remain non-authoritative.

Forbidden outputs include claims of skill execution, installation, activation, execution or deployment approval, permission grant, risk acceptance, final admission approval, audit closure, waiver grant, fail-closed or rollback execution, Decision Proof verification or sealing, authority transfer, final governance judgment, M14 completion, v0.13.0 release, or closure of #201.

## 19. M14 completed and published v0.13.0 status

This document was completed as part of M14 and is included in published v0.13.0. Historical implementation evidence is PR #208. Source issue #192 and M14 tracker #201 are historical completed references.

The completed work builds on the boundaries established by merged PR #202 (voice runtime), merged PR #204 (public output gate), merged PR #205 (MODA mapping), and merged PR #206 (AI PR provenance). Those references provide historical M14 context; none transfers governance authority to an external skill.

This document records completed release state; it does not create or modify release state. It does not create or modify release files, add a GitHub Actions workflow, update the README, create a release, or claim a release tag. Release readiness, release approval, and release acts remain separate AAOS governance steps.

Package integrity or skill admission evidence does not approve installation, activation, execution, deployment, or risk acceptance.

Decision Proof sealing remains AAOS-owned.

AAOS remains the decision sovereignty layer.
