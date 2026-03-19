# AGENT DEFINITIONS SYSTEM AND WORKFLOW

## PURPOSE
Define the roles that matter to `coop`.

This document is not a catalog of every imaginable agent.
It describes the bounded workers and system surfaces that keep work effective.

---

## CORE IDEA

The point of an agent in this system is not personality.
The point is effectiveness under bounded initialization.

That means every worker should have:
- a role
- a scope
- a clear input shape
- a clear output shape
- explicit constraints

If those are missing, the worker accumulates stale context and wastes tokens.

---

## 1. SYSTEM HEART

### ROLE
The execution heart of the framework.

### IN `coop`
- `Event`
- `Manifest`
- `AgentRunner`
- `BaseAgent`
- `BaseHandler`

### PURPOSE
- load declarations
- enforce boundaries
- execute work
- normalize all traffic into events

### INPUT
- manifest
- input payload
- execution constraints

### OUTPUT
- event stream
- exit state

### RULES
- does not own business logic
- does not own presentation
- should stay small

---

## 2. WORKER AGENT

### ROLE
A bounded worker that performs one narrow class of work.

### PURPOSE
- do the task directly
- emit structured progress or results
- stay inside its allowed scope

### INPUT
- task payload
- manifest
- explicit constraints

### OUTPUT
- `output`
- `data`
- `error`
- `exit`

### RULES
- no hidden assumptions
- no extra features
- no broad context by default
- no network unless explicitly allowed
- no admin unless explicitly allowed

---

## 3. HANDLER

### ROLE
Translate event flow into a usable surface.

### IN `coop`
- terminal handler
- API handler
- dashboard layer
- future Swift or JS renderers

### PURPOSE
- consume events
- render them
- collect them
- forward them

### INPUT
- event stream

### OUTPUT
- terminal output
- API responses
- SSE streams
- visual state

### RULES
- does not own execution
- does not mutate task meaning
- should stay transport-specific, not system-wide

---

## 4. INIT ROLE

### ROLE
Bind a worker to a specific task boundary before execution.

### PURPOSE
- define who the worker is for this task
- define what it may do
- define what it must ignore

### INPUT
- role
- scope
- allowed capabilities
- constraints
- task payload

### OUTPUT
- a bounded worker state ready to execute

### RULES
- init should target one limb, not the whole body
- do not initialize broad worldview when a narrow task is enough
- if a new task needs a different capability family, it gets a new init path

---

## 5. CONSTRAINT LAYER

### ROLE
Keep workers effective by restricting drift.

### PURPOSE
- limit network access
- limit admin access
- limit runtime duration
- limit capability surface

### CURRENT SHAPE
- `timeout`
- `requires_admin`
- `network_allowed`

### RULES
- constraints are part of the role contract
- constraints must be enforced, not just described
- if a worker is unbounded, it is not really initialized

---

## 6. ORCHESTRATION

### ROLE
Route work between bounded parts without becoming the whole system.

### PURPOSE
- decide next step
- select worker
- pass input forward
- preserve boundaries

### RULES
- orchestration is optional
- orchestration should stay thin
- do not rebuild a giant management layer unless the runtime truly needs it

---

## 7. HUMAN / TOOL WORKFLOW ROLES

These are real workflow roles, but they are not the same thing as system agents.

### EXAMPLES
- creative direction
- technical direction
- implementation
- validation
- deployment

### RULES
- tool roles may guide the work
- system roles must stay executable
- do not confuse human workflow labels with runtime architecture

---

## SUMMARY

`coop` works best when:
- the heart stays small
- workers stay narrow
- handlers stay separate
- init stays explicit
- constraints stay real

That is how the system keeps a worker effective instead of letting it drown in old context.
