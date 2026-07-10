# Agent Network Boundary Threats

Related issue: #138

## Scope

This threat model supports the AAOS multi-agent private networking boundary for external runtimes, subagents, MCP servers, A2A endpoints, and tools.

It is cloud-neutral. Cloud-provider private networking features may be used as implementation mechanisms, but this threat model does not require or define provider-specific infrastructure.

This is architecture feedback from adjacent AgentFolio/SATP identity and trust work only. It is not an integration, endorsement, certification, interoperability claim, or production-readiness claim.

## Required Proof Record Fields

Every external runtime hop must carry:

- `agent_identity`
- `route_identity`
- `policy_binding`
- `trust_zone`
- `path_evidence`
- `execution_receipt`

Missing `path_evidence` is a replay gap. A valid Decision Proof decision artifact with missing network-path evidence is unresolved, not verified.

## Threats And Boundary Responses

| Threat | Example scenario | Required controls | AAOS response |
| --- | --- | --- | --- |
| Public tool endpoint exposure | A tool or MCP endpoint is reachable through public internet routing while an agent assumes it is private. | Default-deny egress, explicit allow routes, trust-zone classification, path evidence proving route integrity, execution receipt for the tool call. | Reject or quarantine unless an AAOS-owned exception exists with complete evidence. |
| Unauthorized external API egress | A known agent calls an external API through a route that is not authorized for that decision or data class. | Separate identity-aware check for `agent_identity`; separate policy-bound check for `route_identity` and `policy_binding`. | Reject known agent plus unauthorized route. |
| Agent lateral movement | A delegated agent reaches a peer runtime, private service, or subagent outside the approved trust zone. | Per-hop route identity, per-hop policy binding, per-hop trust-zone classification, A2A execution receipts. | Quarantine the hop and require replayable evidence before any verified-path claim. |
| MCP exfiltration | An MCP server can reach files, tools, APIs, prompts, memory, or credentials outside its approved role. | MCP server classification, scoped tool permissions, egress constraints, path evidence, execution receipt, data-class policy binding. | Reject authorized route plus unclassified MCP server; quarantine incomplete classified MCP evidence. |
| Identity/policy mismatch | The agent identity is valid, but the route policy was issued for another agent, destination, trust zone, or operation. | Independent identity-aware and policy-bound checks; route policy cannot be inferred from identity alone. | Reject or quarantine as its own mismatch class; do not merge it into a generic identity-aware label. |
| Replay gap caused by missing network-path evidence | A decision artifact and execution output exist, but the route path cannot be reconstructed. | Mandatory `path_evidence`, route event retention, route decision logs, endpoint classification linkage, execution receipt linkage. | Mark unresolved, not verified; do not seal as path-verified Decision Proof. |

## Default-Deny And Quarantine Cases

AAOS should reject or quarantine:

- known agent plus unauthorized route
- authorized route plus unclassified MCP server
- valid decision artifact plus missing path evidence
- identity-aware hop without a policy-bound route
- policy-bound route without a verified agent identity
- private route without trust-zone classification
- A2A relay without per-hop path evidence

## Governance Boundary

Network path evidence may produce, inspect, report, replay, check, or link evidence.

Network path evidence must not approve execution, accept risk, seal Decision Proof, execute rollback, execute fail-closed, close audits, grant waivers, or make final governance judgments.

Decision Proof sealing remains AAOS-owned.

AAOS remains the decision sovereignty layer.
