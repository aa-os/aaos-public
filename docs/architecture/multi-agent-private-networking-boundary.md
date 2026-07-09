# AAOS Multi-Agent Private Networking Boundary

Related issue: #138

## Purpose

This note defines a cloud-neutral AAOS private agent networking boundary for external agent runtimes, subagents, MCP servers, A2A endpoints, and tools.

The boundary describes how AAOS expects network-path evidence to be captured and evaluated when a governed agent action crosses from an AAOS-governed decision into an external runtime hop.

This is architecture feedback from adjacent AgentFolio/SATP identity and trust work only. It is not an integration, endorsement, certification, interoperability claim, or production-readiness claim for AgentFolio, SATP, any cloud provider, any network product, any MCP server, any A2A endpoint, or any external runtime.

## Boundary Definition

The AAOS private agent networking boundary is the evidence boundary around every external runtime hop used by an AAOS-governed decision.

External runtime hop means any hop from a governed agent or subagent into:

- an external agent runtime
- a subagent runtime
- an MCP server
- an A2A endpoint
- a tool execution endpoint
- an external API or service

The boundary is not a network perimeter alone. Private routing, private DNS, service meshes, private links, VPCs, firewall rules, workload identity, and similar controls may provide useful implementation mechanisms, but AAOS treats them as evidence sources, not final authority.

AAOS uses the boundary to ask:

- Which agent identity attempted the hop?
- Which route identity was used?
- Which policy binding authorized that route for that agent and decision?
- Which trust zone did the destination belong to?
- Which network-path evidence proves the hop stayed on the expected path?
- Which execution receipt proves what was executed and returned?
- Can the decision be replayed without trusting the external runtime as AAOS authority?

## Required Decision Proof Network-Path Metadata

Each external runtime hop must contribute a Decision Proof network-path proof record with these fields:

| Field | Required meaning |
| --- | --- |
| `agent_identity` | The governed agent, subagent, runtime actor, or workload identity that attempted the hop. |
| `route_identity` | The private route, service route, gateway route, workload route, or approved egress path used for the hop. |
| `policy_binding` | The explicit policy binding that allows the agent identity to use the route for the target trust zone and decision scope. |
| `trust_zone` | The destination classification for the runtime, MCP server, A2A endpoint, tool, API, or data service. |
| `path_evidence` | Replayable evidence showing the network path, route decision, endpoint classification, and route integrity for the hop. |
| `execution_receipt` | Replayable execution evidence showing the request, response, tool call, runtime event, or endpoint result associated with the hop. |

The proof record is incomplete if any required field is missing, empty, stale, or unverifiable.

A valid Decision Proof decision artifact with missing `path_evidence` is unresolved, not verified. AAOS must not treat it as a verified private-path decision.

## Identity-Aware And Policy-Bound Checks

AAOS treats identity-aware and policy-bound as separate checks.

Identity-aware means AAOS can resolve and bind the acting runtime identity. It answers whether `agent_identity` is known, expected for the decision, and linked to the runtime hop.

Policy-bound means AAOS can resolve the policy authorization for the route. It answers whether `policy_binding` explicitly allows that `agent_identity` to use `route_identity` for the requested `trust_zone`, destination, operation, data class, and decision scope.

Passing the identity-aware check does not imply that the route is authorized. Passing the policy-bound check for a route does not imply that the acting agent identity is correct. Both checks must pass independently before a hop can be treated as verified.

AAOS should reject or quarantine:

- known agent plus unauthorized route
- authorized route plus unclassified MCP server
- valid decision artifact plus missing path evidence

## Default-Deny Agent Egress

Agent egress is default-deny.

An external runtime hop is allowed only when AAOS can link the decision to an explicit allow rule that covers:

- the `agent_identity`
- the `route_identity`
- the `policy_binding`
- the destination `trust_zone`
- the permitted operation or tool class
- the required evidence fields
- the replay requirement
- the expiration, freshness, or revocation semantics for the route

Implicit internet egress, public fallback routes, unmanaged proxy routes, and unclassified tool endpoints are not allowed by default.

Explicit allow is scoped. A route allowed for one agent, tool, trust zone, data class, decision, or time window does not authorize another.

## MCP Server Trust-Zone Classification

Every MCP server reachable by an AAOS-governed agent must be classified before use.

Minimum MCP trust-zone states:

| Trust zone | Meaning | Default handling |
| --- | --- | --- |
| `aaos_governed_internal` | MCP server operated inside the governed AAOS evidence boundary. | May be eligible if identity, policy, path evidence, and execution receipt are complete. |
| `approved_private_external` | External MCP server reachable only through an explicit private route and classified policy binding. | May be eligible if all proof record fields are present and replayable. |
| `restricted_partner` | Partner or adjacent-system MCP server requiring additional policy, data, and evidence constraints. | Review required unless explicitly allowed for the decision scope. |
| `public_tool_endpoint` | MCP or tool endpoint exposed through public network paths. | Reject unless there is an exceptional AAOS-owned policy decision and complete evidence. |
| `unclassified` | MCP server with missing or unknown classification. | Reject or quarantine. |

Authorized route plus unclassified MCP server is not verified. Classification must be established separately from route authorization.

## A2A Private-Routing Expectations

A2A traffic used by external agents or subagents must preserve the same boundary semantics as tool and MCP traffic.

AAOS expects A2A private routing to provide:

- route identity for every agent-to-agent hop
- workload or agent identity for each sender and receiver
- policy binding for each sender, receiver, route, trust zone, operation, and decision scope
- path evidence that distinguishes private routing from public fallback or unmanaged relay paths
- execution receipts for messages, delegated tasks, tool results, and runtime handoffs
- replayable linkage back to the AAOS decision artifact

A2A routing that is private but not identity-aware is incomplete. A2A routing that is identity-aware but not policy-bound is incomplete. A2A routing that has a valid decision artifact but missing network-path evidence is unresolved, not verified.

## Private Networking Is Not Sufficient

Private networking reduces exposure, but it does not by itself prove governance correctness.

AAOS must not treat a hop as verified only because it used a private subnet, private link, private endpoint, private DNS name, service mesh route, firewall rule, or cloud-provider private connectivity feature.

Private networking is sufficient only as one evidence input. The hop still needs:

- identity-aware verification
- policy-bound verification
- trust-zone classification
- path evidence
- execution receipt
- replayability
- AAOS-owned Decision Proof sealing

## Verification Semantics

AAOS may classify a hop as verified only when all required proof fields are present, internally consistent, fresh enough for the decision, replayable, and within explicit allow policy.

AAOS should use these minimum states:

| State | Meaning |
| --- | --- |
| `verified_private_path` | Identity, policy, trust zone, path evidence, execution receipt, and replay linkage are complete. |
| `unresolved_missing_path_evidence` | Decision artifact exists, but network-path evidence is missing or insufficient. |
| `quarantined_unclassified_destination` | Route may be known, but destination trust zone is missing or unclassified. |
| `rejected_unauthorized_route` | Agent identity is known, but the route is not authorized for the decision. |
| `rejected_public_or_unmanaged_path` | Hop used public, unmanaged, fallback, or unclassified routing without an AAOS-owned exception. |

Valid decision artifact plus missing path evidence must resolve to `unresolved_missing_path_evidence`, not `verified_private_path`.

## Threat Table

| Threat | Boundary failure | Required AAOS handling |
| --- | --- | --- |
| Public tool endpoint exposure | Agent, subagent, MCP, A2A, or tool traffic reaches a public endpoint without explicit scoped approval and complete evidence. | Reject or quarantine by default; require explicit allow, trust-zone classification, path evidence, and execution receipt before replay eligibility. |
| Unauthorized external API egress | A known agent uses an external route that is not authorized for the decision, operation, data class, or trust zone. | Reject as `rejected_unauthorized_route`; known identity does not override missing or unauthorized policy binding. |
| Agent lateral movement | A runtime, subagent, or delegated agent reaches another private runtime or trust zone outside the approved route scope. | Quarantine and require separate identity-aware and policy-bound checks for each hop. |
| MCP exfiltration | An MCP server has access to tools or data beyond its trust-zone classification or policy binding. | Reject unclassified MCP use; quarantine classified MCP use if route, policy, path evidence, or execution receipt is incomplete. |
| Identity/policy mismatch | `agent_identity` is valid but `policy_binding` does not authorize `route_identity`, or the route is valid but bound to a different agent or trust zone. | Reject or quarantine as a distinct mismatch; identity-aware and policy-bound checks must remain separate. |
| Replay gap caused by missing network-path evidence | Decision artifact, execution receipt, or tool output exists, but `path_evidence` is missing, stale, or not replayable. | Mark unresolved, not verified; do not seal as path-verified Decision Proof. |

See `docs/threat-models/agent-network-boundary-threats.md` for the companion threat-model reference.

## Governance Boundary

Network path evidence may produce, inspect, report, replay, check, or link evidence.

Network path evidence must not:

- approve execution
- accept risk
- seal Decision Proof
- execute rollback
- execute fail-closed
- close audits
- grant waivers
- make final governance judgments

Decision Proof sealing remains AAOS-owned.

AAOS remains the decision sovereignty layer.
