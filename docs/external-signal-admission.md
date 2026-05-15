# External Signal Admission

External signal admission defines how external sources enter AAOS Hub.

An external signal may be a tool, scanner, model runtime, local inference engine, GitHub Action, MCP server, agent framework, repository-intelligence tool, or audit utility.

## Admission Boundary

External signals are admitted as evidence candidates only.

They do not define:

- business intent
- risk appetite
- identity trust chain
- approval doctrine
- decision router logic
- fail-closed rules
- escalation semantics
- risk calibration thresholds

## Admission Lifecycle

```text
external source
→ governed signal
→ radar node
→ admission review
→ evidence candidate
→ adapter issue
→ implementation pack
→ replay / audit evidence
```
