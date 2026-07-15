# M14 MODA AI Risk Framework Mapping

Document state: M14 completed.

Release state: Included in published v0.13.0.

Historical implementation evidence: PR #205.

Historical completed references: source issue #181 and M14 tracker #201. Related M14 context includes PR #202 and PR #204.

This document maps Taiwan MODA AI Risk Classification Framework v1.0 risk codes to AAOS Decision Proof evidence controls. It is an engineering governance mapping, not legal advice, legal approval, regulatory certification, a full-compliance claim, or deployment approval.

## Source And Provenance

The source taxonomy is the Taiwan Ministry of Digital Affairs (MODA) **Artificial Intelligence Risk Classification Framework**, version v1.0, issued on 2026-07-07 under notice `數位策略字第 1150015933 號`.

- [Official MODA notice](https://moda.gov.tw/press/bulletin/20086)
- [Official MODA v1.0 PDF](https://www-api.moda.gov.tw/File/Get/moda/zh-tw/UieEfux5Yv0iJuR)
- Taxonomy location: Table 1, `AI 風險類型表`, printed pages 4–6.

`source_label_zh_tw` preserves the official Traditional Chinese label. `source_label` is an AAOS working English label used for deterministic records. The B6 working label is fixed by #181 and this mapping as exactly `AI autonomous agent unauthorized behavior`.

MODA v1.0 is treated as an external regulatory-risk taxonomy reference. It does not become an AAOS governance authority. Source taxonomy coverage records what was mapped; it does not decide legal status, compliance, deployment permission, or final risk classification.

## Taxonomy-To-Control Mapping

| Code | Official source label (`zh-TW`) | AAOS working label | AAOS control category |
| --- | --- | --- | --- |
| A1 | AI 系統的安全漏洞與攻擊 | AI system security vulnerabilities and attacks | `system_security_and_adversarial_resilience` |
| A2 | 缺乏透明性或可解釋性 | lack of transparency or explainability | `transparency_explainability_and_traceability` |
| A3 | AI 行為偏離人類意圖與社會價值 | AI behavior deviating from human intent and social values | `intent_alignment_and_value_boundary` |
| A4 | AI 具有危險的能力 | AI with dangerous capabilities | `dangerous_capability_and_containment` |
| A5 | 影響隱私與違反個人資料保護法規 | privacy impacts and personal-data protection violations | `privacy_and_personal_data_governance` |
| A6 | 侵害智慧財產權疑慮 | intellectual property infringement concerns | `intellectual_property_provenance` |
| A7 | 不公平的歧視或偏見 | unfair discrimination or bias | `fairness_bias_and_non_discrimination` |
| A8 | 錯誤或誤導訊息 | false or misleading information | `information_integrity_and_misleading_output` |
| B1 | 過度依賴與不安全使用 | overreliance and unsafe use | `human_reliance_and_safe_use` |
| B2 | 喪失人類自主性 | loss of human autonomy | `human_autonomy_and_override` |
| B3 | 生成違法內容 | generation of illegal content | `illegal_content_prevention_and_escalation` |
| B4 | 詐欺與深偽技術濫用 | fraud and deepfake technology misuse | `identity_provenance_and_deepfake_misuse` |
| B5 | 用於網路攻擊 | use in cyberattacks | `cyber_misuse_and_tool_boundary` |
| B6 | AI 自主代理之授權外行為 | AI autonomous agent unauthorized behavior | `agent_authorization_and_action_boundary` |
| C1 | 企業及國家間競爭秩序失衡 | imbalance in competition between enterprises and countries | `competitive_pressure_and_safe_deployment` |
| C2 | 權力集中與利益分配不公平 | concentration of power and unfair distribution of benefits | `power_concentration_and_distributional_impact` |
| C3 | 不平等加劇、就業品質下降 | increased inequality and reduced job quality | `inequality_employment_quality_and_appeal` |
| C4 | 人類在經濟與文化上之創作價值受損 | damage to the economic and cultural value of human creation | `human_creation_value_and_cultural_diversity` |
| C5 | 環境傷害 | environmental harm | `environmental_impact_and_resource_use` |
| C6 | 認知作戰與資訊主權 | cognitive warfare and information sovereignty | `cognitive_security_and_information_sovereignty` |

## B6 First-Class Control

B6 is a first-class AAOS control category rather than a generic agent-risk tag:

- `risk_code`: `B6`
- `source_label`: `AI autonomous agent unauthorized behavior`
- `aaos_control_category`: `agent_authorization_and_action_boundary`

Every B6 Decision Proof record must bind:

1. `permission_scope` — the maximum data, repository, tool, and operation scope available to the agent.
2. `authorization_decision` — the explicit authorization evidence and policy decision for the action.
3. `action_target` — the resource, subject, account, system, or artifact affected.
4. `output_channel` — the destination and visibility of generated or published output.
5. `execution_trace_id` — the replayable request, tool-call, response, and state-transition trace.

Agent capability is not action authorization. Detecting a B6 control pass is not deployment approval or final governance judgment.

## Capture / Verify / Accumulate Checklist

### Capture

- `application_scenario`
- `stakeholders`
- `model_tool_stack`
- `permission_scope`
- `data_sources`
- `deployment_context`
- `output_channel`
- `source_taxonomy_provenance`

Capture records what was proposed and what context was available. It does not approve the scenario.

### Verify

- `taxonomy_risk_codes`
- `inherent_risk_screening`
- `serious_harm_screening`
- `existing_control_coverage`
- `b6_authorization_boundary`
- `human_review_requirement`
- `appealability_requirement`

Serious-harm screening identifies a review boundary. `serious_harm_screening_required` and `inherent_risk_screened` are not `serious_harm_cleared`, risk acceptance, or final legal determination.

### Accumulate

- `trace_logs`
- `review_evidence`
- `rollback_records`
- `incident_examples`
- `periodic_reassessment_record`
- `framework_version_history`
- `replay_packet_id`

Accumulated evidence remains subject to AAOS review. Evidence completeness is not Decision Proof sealing.

## Sector Scenarios

### Healthcare

Capture restricted health and personal-data scope, model and tool access, clinical context, and intended use. Verify inherent risk, serious-harm screening, diagnostic or treatment authority boundaries, and mandatory human review. The mapping must not approve diagnosis or treatment.

### Finance

Separate analysis capability from transaction authority. An AI system may generate analysis or recommendations within an authorized scope; trade, payment, credit, or other transaction execution requires a separate identity-bound authorization decision. Analytical capability is not transaction authority.

### Education

Preserve human review for grading, admission, discipline, accommodation, and learner-impacting decisions. Record appealability and reviewer handoff. A taxonomy mapping must not remove a learner's route to challenge a decision.

### Labor

Preserve human review and appealability for hiring, evaluation, scheduling, discipline, and termination decisions. The mapping must not approve hiring or termination.

### Government Service

Apply a public-output gate to public notices, issue responses, eligibility explanations, and other externally visible output. The gate references the merged #204 public issue exfiltration control pattern: public output derived from privileged context requires gating and human review. Public-output gate pass is not public disclosure approval or government eligibility approval.

## Periodic Reassessment

Each sector record must retain:

- `reassessment_required`
- `reassessment_cadence`
- `last_assessment_recorded_at`
- `next_assessment_due`
- `reassessment_triggers`
- `source_framework_version_at_assessment`
- `changed_risk_codes`
- `reviewer_handoff`
- `replay_packet_id`

Reassessment triggers include source-framework revision, model or tool change, permission change, new data source, incident, serious-harm signal, output-channel change, and material deployment-context change. Periodic reassessment records evidence; they do not certify continuing compliance.

## Governance Boundary

Regulatory mapping is not legal approval.

Taxonomy mapping is not compliance certification.

Risk-code coverage is not regulatory clearance.

Control coverage complete is not deployment approval.

Serious-harm screening is not final legal determination.

`inherent_risk_screened` is not risk accepted.

`ready_for_review` is not regulated deployment approval.

`human_review_required` is not audit closure.

`fail_closed_recommended` is not `fail_closed_executed`.

`rollback_recommended` is not `rollback_executed`.

The mapping and evaluator must not approve diagnosis, treatment, trades, payments, credit decisions, hiring, termination, government eligibility, or public disclosure. They must not accept risk, make final risk classifications, execute rollback, execute fail-closed, close audits, grant waivers, transfer authority, seal Decision Proof, declare M14 complete, or release v0.13.0.

Decision Proof sealing remains AAOS-owned.

AAOS remains the decision sovereignty layer.
