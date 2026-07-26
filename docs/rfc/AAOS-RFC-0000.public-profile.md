# AAOS-RFC-0000 Public Interface Profile

## Publication metadata — Informative

```text
RFC ID: AAOS-RFC-0000
Publication Class: public-profile
Projection Scope: interface-only
Authority Status: non-authoritative
Derivative Status: review-material
Original Public Source: docs/rfc/AAOS-RFC-0000.md
Original Source Commit: 92b4503c5834f993ccf6b0a28e097564c468c4b8
Restricted Registry Record: AAOS-PRIVATE-RFC-REGISTRY / AAOS-RFC-0000
Supersession Marker: none
```

This document is a public-safe derivative. It does not replace, amend, or supersede the exact `AAOS-RFC-0000` Candidate Package. It does not disclose or prove private institutional controls. The original public RFC candidate and all existing candidate-package artifacts remain unchanged.

## 1. Interface-only obligations

Public implementations and profiles should preserve the following externally reviewable boundaries from the exact RFC source:

1. **Stable identity.** RFC identifiers, versions, repository paths, commits, blobs, rendered documents, semantic manifests, requirement registries, and package digests are distinct identities.
2. **Exact binding.** Material review and lifecycle dispositions must bind an exact RFC version and canonical semantic-manifest digest; repository materialization must additionally bind repository, commit, and tree identity.
3. **Lifecycle separation.** RFC class, review state, lifecycle status, implementation state, conformance outcome, and deployment state must remain distinct.
4. **Human disposition.** GitHub state, merge state, CI, tests, evaluator output, runtime behavior, elapsed time, or publication do not independently perform an RFC lifecycle transition.
5. **Fail-closed unknowns.** Unknown mandatory semantics must produce `fail_closed`, `not_evaluable`, or explicit human disposition; they must not become permissive by default.
6. **Traceability without authority promotion.** Schemas, interfaces, tests, fixtures, validators, runtime controls, and claims must trace to stable RFC and requirement identities, but traceability or test success does not itself prove authority, adoption, deployment authorization, or conformance.
7. **Public/private separation.** Restricted institutional doctrine may constrain applicability or decline adoption but must not silently rewrite public RFC semantics.
8. **Historical resolution.** Deprecated, superseded, withdrawn, and rejected identities and claims must remain historically resolvable with explicit migration and claim effects.

## 2. Explicit exclusions

This public profile does not contain or establish:

- private authority assignments or trust roots;
- institutional risk appetite or calibration thresholds;
- private escalation, emergency, restore, or cutover doctrine;
- protected threat-model, dependency-map, or restore-map details;
- private evidence locations or operational identifiers;
- implementation, deployment, certification, waiver, risk-acceptance, restore, cutover, or proof-sealing authority.

## 3. Non-authoritative status

`Authority Status: non-authoritative` means this projection cannot independently change AAOS semantics or institutional authority. Any conflict must be resolved against the exact public source identity and the applicable restricted authority review; it must not be resolved through last-write-wins, newest-file-wins, or permissive fallback.

## 4. Derivation control

Future public revisions must be generated from an exact source-bound restricted record and must identify the source commit, applicable digests, projection scope, exclusions, and publication disposition. The public projection must not evolve as an independently edited fork.

## 5. Current governance effect

This file is Draft PR review material only. It does not resolve `R1-U01`, create an `R1-U02` subject, assign an RFC lifecycle status, supersede the original public RFC, authorize publication or merge, or create implementation, conformance, deployment, restore, cutover, or proof-sealing effects.
