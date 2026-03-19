# MODULE MANIFEST AND HANDSHAKE STANDARD

## PURPOSE
Define the execution contract between the `coop` heart and a bounded worker/module.

The point is not just identity.
The point is safe execution with verified compatibility.

---

## 1. CORE PRINCIPLE

A worker must never run just because a file exists.

Execution is allowed only if:
- manifest is valid
- worker identity matches
- framework compatibility matches
- schema or contract hashes match
- worker is enabled

---

## 2. CURRENT `coop` SHAPE

In `coop`, the manifest is the current declaration boundary.

Today this already includes:
- `id`
- `version`
- `title`
- `script`
- `input_schema`
- `output_schema`
- `constraints`

The handshake layer is the next verification step on top of that manifest.

---

## 3. MANIFEST PURPOSE

The manifest declares:
- who the worker is
- what it expects
- what it emits
- what constraints apply

This is static compatibility metadata.

Example shape:

```json
{
  "id": "auth.login",
  "version": "1.0.0",
  "title": "Auth Login",
  "script": "auth_login.py",
  "input_schema": {
    "type": "object"
  },
  "output_schema": {
    "type": "object"
  },
  "constraints": {
    "timeout": 10,
    "requires_admin": false,
    "network_allowed": false
  }
}
```

---

## 4. HANDSHAKE PURPOSE

The handshake is a runtime verification step.

Framework asks:
- are you the worker I intended to run
- are you compatible with this runtime contract
- do you agree on the expected schema boundary

Worker answers:
- yes, here is my identity and compatibility state

This can be minimal.
It does not need to be heavy ceremony.

---

## 5. MINIMAL HANDSHAKE REQUEST

```json
{
  "request_id": "req-001",
  "worker_id": "auth.login",
  "expected_framework_api_version": "1.0",
  "expected_input_schema_hash": "abc123",
  "expected_output_schema_hash": "def456"
}
```

---

## 6. MINIMAL HANDSHAKE RESPONSE

```json
{
  "request_id": "req-001",
  "worker_id": "auth.login",
  "worker_version": "1.0.0",
  "framework_api_version": "1.0",
  "input_schema_hash": "abc123",
  "output_schema_hash": "def456",
  "handshake_status": "accepted"
}
```

---

## 7. VALIDATION RULES

The framework must verify:
- worker id matches
- framework API version matches
- input schema hash matches
- output schema hash matches
- worker is enabled

If any fail:
- reject execution
- emit a clear error
- do not continue "best effort"

---

## 8. FAILURE RESPONSE

```json
{
  "request_id": "req-001",
  "worker_id": "auth.login",
  "handshake_status": "rejected",
  "errors": [
    "framework_api_version mismatch",
    "input_schema_hash mismatch"
  ]
}
```

---

## 9. EXECUTION FLOW

Heart
-> load manifest
-> validate manifest
-> perform handshake
-> validate response
-> execute or reject

---

## 10. HASH ECHO VARIANT

For thin connections, the handshake may be reduced to a token echo.

Framework sends:

```json
{
  "handshake": "abc123"
}
```

Worker returns:

```json
{
  "handshake": "abc123",
  "ack": true
}
```

If the same token returns, the path is confirmed alive.

This is useful when the goal is:
- liveness
- route integrity
- very cheap connection confirmation

---

## 11. FUTURE DIRECTION

If `coop` grows beyond script manifests, this standard can support:
- Python workers
- service workers
- Swift or JS bridges
- remote execution surfaces

But the rule stays the same:
- manifest declares
- handshake verifies
- heart decides

---

## 12. RULE

Manifest is declaration.
Handshake is proof.
Execution happens only after both.
