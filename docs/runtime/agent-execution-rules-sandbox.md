# AGENT EXECUTION RULES (SANDBOX / NETWORK / COST / SAFETY)

## PURPOSE
Define how `coop` keeps a worker bounded at runtime.

These rules exist to prevent:
- damage
- uncontrolled cost
- scope drift
- stale or untraceable execution

---

## 1. CORE PRINCIPLE

Default = deny

Explicit = allow

Nothing should be assumed available.
Capabilities should be attached deliberately.

---

## 2. IN `coop`

The current declaration boundary already contains:
- `timeout`
- `requires_admin`
- `network_allowed`

This file defines how those constraints should behave as real runtime policy.

Constraint fields are not comments.
They are execution gates.

---

## 3. NETWORK RULES

### DEFAULT

- no network access
- no external API calls
- no downloads
- no uploads

### WHY

Prevent:
- cost explosions
- data leaks
- dependency drift
- unpredictable outputs

### CONTROLLED MODE

Network may be allowed only if:
- enabled explicitly for the worker
- host or endpoint scope is known
- requests can be logged
- usage can be bounded

Example:

```json
{
  "constraints": {
    "network_allowed": true
  }
}
```

Future policy may refine this with:
- allowed hosts
- request caps
- rate limits

---

## 4. ADMIN / DESTRUCTIVE RULES

### DEFAULT

- no admin privileges
- no destructive operations

### WHY

Workers should not be able to escalate silently.

If a worker can destroy data or alter the system:
- it must declare that
- it must be gated explicitly
- it should require confirmation

`requires_admin` should block execution unless the runtime has an explicit path for approval.

---

## 5. FILE SYSTEM RULES

### DEFAULT

A worker should only read and write within its assigned execution boundary.

### RULES

- no uncontrolled traversal outside allowed scope
- no silent writes to unrelated areas
- no modification of shared core unless explicitly allowed

The exact path policy may differ by runtime, but the intent is fixed:
- bounded access
- bounded writes
- no accidental spread

---

## 6. RESOURCE LIMITS

### TIME

- execution must have a bounded timeout
- long-running drift should be cut off

### MEMORY / OUTPUT

- large payloads should be bounded
- logs should not grow without limit
- binary or blob output should be rejected unless explicitly expected

### WHY

Prevent:
- runaway processes
- frozen sessions
- hidden cost loops

---

## 7. OUTPUT RULES

### DEFAULT

Workers should return:
- structured events
- small payloads
- diffs or focused results

### FORBIDDEN

- massive code dumps
- unbounded logs
- binary blobs
- repo-scale rewrites without explicit scope

The heart should favor event flow over output dumping.

---

## 8. COST CONTROL

### DEFAULT

- no paid APIs unless approved
- no hidden compute escalation
- no recursive external calling

### WHY

Worker effectiveness dies when cost is invisible.

Cost must be:
- bounded
- visible
- attributable

---

## 9. ISOLATION

### RULE

A bounded worker should not:
- modify unrelated modules
- change shared contracts casually
- reach across the system without permission

### WHY

Prevent:
- cascading bugs
- hidden dependencies
- architectural drift

---

## 10. EXECUTION FLOW

All execution should pass through the heart:

heart
-> validate declaration
-> validate constraints
-> handshake if required
-> execute
-> emit events
-> return

Direct, unbounded execution should be treated as a bypass.

---

## 11. RULE

If a worker is not constrained, it is not really initialized.
    "allowed_commands": ["python", "pytest"],
    "max_execution_time_sec": 20,
    "max_output_size_kb": 200
  }
}

---

# 13. BEST PRACTICE

- everything explicit  
- everything logged  
- everything bounded  
- nothing implicit  

---

# 14. FINAL PRINCIPLE

Agents are untrusted by default  
Framework enforces reality  
