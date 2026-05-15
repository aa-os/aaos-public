# AAOS × Threatrix Supply Chain Evidence Governance Adapter

## Summary

This adapter admits Threatrix as a supply-chain, dependency, SBOM, license-risk, and open-source risk evidence source.

Threatrix output is evidence.

Threatrix output is not release approval, compliance closure, vulnerability waiver, license clearance, procurement approval, or AAOS governance authority.

## Source

https://github.com/marketplace/threatrix

## AAOS Layer Mapping

Threatrix maps to:

- L4.5 Evidence Adapter
- L5 Supply Chain / Dependency Reconstruction Candidate
- L6 Verification / Audit Input

Threatrix must not map to:

- L0 Governance / Business Intent
- L1 Policy / Identity Authority
- L2 Control / Decision Authority

## Governance Boundary

Supply-chain evidence is not release approval.

Scanner finding is not governance authority.

SBOM existence is not supply-chain sovereignty.

License finding is not license clearance.

Risk score is not risk acceptance.

Vulnerability detection is not vulnerability waiver.

## Core Invariants

1. Scanner finding is not release approval.
2. SBOM existence is not supply-chain sovereignty.
3. Vulnerability detection is not supply-chain remediation.
4. License finding is not license clearance.
5. Dependency inventory is not dependency trust.
6. Risk score is not risk acceptance.
7. Open-source risk signal is not procurement approval.
8. Transitive dependency visibility is not transitive dependency control.
9. Compliance evidence is not compliance closure.
10. Threatrix is an evidence source, not an AAOS L0/L1/L2 authority.

## Required Evidence Records

The adapter should retain:

- threatrix_admission_record.json
- threatrix_dependency_inventory_record.json
- threatrix_sbom_record.json
- threatrix_vulnerability_findings_record.json
- threatrix_license_risk_record.json
- threatrix_transitive_dependency_record.json
- threatrix_open_source_risk_summary.json
- threatrix_policy_mapping_record.json
- threatrix_waiver_request_record.json
- threatrix_replay_packet.json

## Required Binding Fields

Each Threatrix evidence record should bind findings to:

- repository
- repository owner
- branch
- commit SHA
- build ID
- artifact ID
- package ecosystem
- scanner version
- scan timestamp
- SBOM hash
- finding IDs
- human reviewer
- admission decision
- reason codes

## Decision Outcomes

Threatrix adapter evaluators should support:

- admit_with_constraints
- review_required
- reject
- fail_closed
- allow_with_recorded_exception

## Fail-Closed Conditions

The adapter should fail closed when:

- Threatrix output is treated as release approval.
- Vulnerability findings are waived without authority binding.
- License risk is accepted without explicit approval chain.
- SBOM artifact is missing commit, repository, build, or timestamp binding.
- Dependency findings are not reproducible.
- Critical or high findings lack recorded exception or remediation plan.
- Evidence is stale, partial, or non-replayable.
- Risk score is treated as risk acceptance.
- Scanner absence is treated as clean supply-chain state.

## Waiver Governance

Any vulnerability or license waiver must be:

- finding-bound
- scope-bound
- time-bound
- authority-bound
- replayable
- revocable

A waiver is not permanent risk acceptance unless AAOS L1/L2 policy explicitly admits it.

## Non-Goals

This adapter does not:

- implement Threatrix itself
- approve releases by default
- waive vulnerabilities
- clear license risk
- define procurement approval
- define AAOS L0/L1/L2 policy
- treat SBOM existence as supply-chain sovereignty
- treat scanner findings as audit closure
- treat missing findings as proof of safety

## Status

M2 adapter skeleton.
