# AGENT MODEL CLARIFICATION CRITICAL

## SUMMARY
Yes.

The word `agent` means at least two different things, and they must be kept separate.

---

## 1. THE PROBLEM

`agent` is overloaded.

It can mean:
- a tool or AI working outside the codebase
- a bounded worker or system surface inside runtime

If you mix those:
- the documentation becomes unclear
- the runtime becomes over-modeled
- workflow roles get confused with executable code

---

## 2. THE RIGHT MODEL

### A. TOOL AGENTS EXTERNAL

These exist outside the codebase.

Examples:
- ChatGPT
- Claude
- Warp
- VS Code

Properties:
- they work through instructions
- they produce text, code, or operations
- they are not themselves your runtime system
- they may be useful workers, but they are not your architecture

---

### B. SYSTEM AGENTS OR WORKERS INTERNAL

These exist inside the executable boundary of the framework.

In `coop`, this currently means:
- manifest-backed workers
- `BaseAgent`
- handlers
- the small brain around the execution boundary

Properties:
- they are defined by contracts
- they have clear input and output
- they operate inside the runtime model
- they should stay narrow and bounded

---

## 3. THE KEY DISTINCTION

Tool agent = who happens to perform the work

System worker = what the heart expects at execution time

These are not the same thing.

---

## 4. THE IMPORTANT MAPPING

What matters is not:

`ChatGPT -> TechDirectorAgent class`

What matters is:
- an external worker may take a given role
- the runtime expects a given contract
- the two meet through init, constraints, and output shape

Not everything needs to become a class.

---

## 5. WHAT SHOULD BE DOCUMENTED

Primary in `coop`:
- execution model
- manifests
- constraints
- event contract
- handlers
- worker boundaries

Secondary:
- how external tools are used
- what role a given AI or editor may take in workflow

---

## 6. COMMON MISTAKE

Designing the system around tool names.

Examples:
- "ChatGPT does X"
- "Warp runs Y"

That is workflow description, not runtime architecture.

---

## 7. THE RIGHT ABSTRACTION LEVEL

Design around:
- role
- init
- scope
- constraints
- contract

A role may then be performed by:
- an AI tool
- a script
- a human
- a service

That does not mean every role needs its own runtime class.

---

## 8. THE `coop` MODEL

In `coop`, the heart is:
- `Event`
- `Manifest`
- `AgentRunner`
- `BaseAgent`
- `BaseHandler`

It is better to keep this small than to invent:
- `TechDirectorAgent`
- `QAAgent`
- `DeployAgent`

as runtime objects before they are truly needed.

---

## 9. RULE

Workflow roles may be many.

Runtime workers should be few, clear, and executable.
