# ANSWERS CLARIFIED SPEC

## 1. WHAT KIND OF AGENTS

Both – but separated into two layers:

A. OPERATIONAL AGENTS (TOOLS)
Used in workflow:

- ChatGPT → Tech Director / Spec / Architecture
- Claude → alternative reasoning / validation
- Warp / CLI agents → execution (code, scripts, file system)
- IDE (VS Code / PyCharm) → human + assisted refactor

These are:
external tools acting as roles

---

B. SYSTEM AGENTS (IN CODE)

Defined in framework as executable roles and bounded surfaces.

In `coop`, this currently means:

- the system heart (`Event`, `Manifest`, `AgentRunner`)
- bounded worker agents (`BaseAgent` or manifest-backed workers)
- handlers (`BaseHandler`, terminal, API, dashboard-facing surfaces)
- optional orchestration or validation layers when needed

These are not necessarily one-class-per-workflow-role.
The larger workflow labels may still exist conceptually, but they should only become in-code agents if they are truly executable and useful at runtime.

These are:
internal abstractions with contracts

---

CORE DISTINCTION

Tool agent ≠ System agent

You are documenting BOTH:
- how to USE agents
- how to MODEL agents

---

## 2. TARGET AUDIENCE

Primary:
Yourself (system builder / architect)

Secondary:
Advanced devs / digital directors

NOT:
- beginners
- general public

---

## 3. LANGUAGE

Recommendation:

Docs: English
Thinking / chats: Swedish

Rule:
All templates / contracts / docs → English

---

## 4. WHAT'S THE GAP

You are NOT missing content.

You are missing:
STRUCTURAL CONSISTENCY

---

CURRENT STATE

You have:
- concepts/
- implementation-guide/
- scattered docs

Problem:
They are not aligned to a system model

---

WHAT YOU SHOULD DO

NOT:
- write more content
- start over

DO:
Refactor into unified system

---

## 5. TARGET STRUCTURE

docs/
├── 00_overview.md
├── 01_principles.md
├── 02_agents.md
├── 03_framework.md
├── 04_modules.md
├── 05_layout.md
├── 06_assets.md
├── 07_runtime.md
├── 08_deploy.md
├── 09_qa.md
├── playbooks/
└── contracts/

---

## 6. HOW TO HANDLE EXISTING FILES

docs/concepts/agents.md
→ merge into → 02_agents.md

docs/implementation-guide/setting-up-agents.md
→ split into:
  - 02_agents.md (concept)
  - playbooks/setup_agents.md (procedure)

---

## 7. CORE DECISION

You are building:
A SYSTEM SPEC

Not:
Documentation collection

---

## 8. FINAL POSITIONING

This is:
- an architecture spec
- a workflow system
- an agent orchestration model

Not:
- a tutorial
- a guide
- a blog

---

## SLUTSATS

You should:
- keep all content
- refactor into one consistent structure
- separate tool-agents vs system-agents
- standardize everything in English

Your problem is structure, not knowledge
