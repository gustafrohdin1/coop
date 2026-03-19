# TOPICS YOU ASKED FOR STRUCTURED

## SUMMARY
In `coop`, everything revolves around the same core:
- heart
- workers
- handlers
- init
- constraints
- handshake

These are the topics you keep returning to around that model.

---

## 1. HEART / FRAMEWORK

- the small heart that executes work
- `Event`, `Manifest`, `AgentRunner`
- `BaseAgent` and `BaseHandler`
- the difference between heart and business logic
- how the heart stays small

---

## 2. WORKERS

- bounded workers
- manifest-backed workers
- worker responsibility
- input and output shape
- how workers stay effective

This replaces much of the older idea of many named runtime agents.

---

## 3. HANDLERS

- terminal
- API / SSE
- dashboard
- future Swift or JS layers

Visualization and transport belong here, not in the heart.

---

## 4. INIT

- how a worker is bound to a task
- role + scope + constraints
- minimal context injection
- init per limb instead of the whole body

This is the practical answer to context rot.

---

## 5. CONSTRAINTS

- timeout
- network_allowed
- requires_admin
- bounded output
- bounded cost
- bounded file access

Constraints are not comments.
They are runtime rules.

---

## 6. HANDSHAKE / CONTRACTS

- manifest as declaration boundary
- handshake as verification boundary
- schema hash
- version compatibility
- identity check
- hash echo for thin connection checks

---

## 7. DATA FLOW

- heart -> worker -> event flow -> handler
- up/down flow between execution and surface
- validation before and after execution
- when orchestration is truly needed

---

## 8. TOOL / WORKFLOW LAYER

- ChatGPT
- Claude
- Warp
- VS Code
- Xcode

These are workflow roles and tools, not the same thing as runtime workers.

---

## 9. DOCUMENTATION

- docs as contracts
- docs as API
- contract-based documentation
- refactoring docs
- keeping the mother system separate from `coop`

---

## 10. VISUALIZATION

- dashboard as face
- event flow as blood
- neck as signaling upward
- component trees as arms / legs
- default graphics to show and control work

---

## 11. THE LARGER SYSTEM

Outside `coop`, there are still larger topics such as:
- assets
- layout
- creative pipeline
- docs system
- broader production model

They may matter, but they are not the heart of `coop`.

---

## 12. META GOAL

```text
You are not only building "AI agents".
You are building a system that keeps a worker effective
once it enters the task.
```
