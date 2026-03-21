# Director Skills Inventory

Consolidated knowledge of all operational agents/workers in coop.
Maintained by Tech Director. Updated on session login.
Last updated: 2026-03-20

---

## Core SDK

### BaseAgent
- **Location:** `src/coop/sdk/agent.py`
- **Contract:** `execute(input_data) → int (exit code)`
- **Emitters:** `emit_output(line)`, `emit_data(dict)`, `emit_error(msg)`
- **Lifecycle:** `start → execute → exit` (error on exception, code=1)
- **Note:** Pure Python alternative to script-based workers

### BaseHandler
- **Location:** `src/coop/sdk/handler.py`
- **Purpose:** Consumes event stream, dispatches to lifecycle hooks
- **Hooks:** `on_start`, `on_output`, `on_data`, `on_error`, `on_exit`

### AgentRunner
- **Location:** `src/coop/runner.py`
- **Purpose:** Loads manifest, validates handshake, executes worker, normalizes events

### Registry
- **Location:** `src/coop/sdk/registry.py`
- **Purpose:** Decorator-based agent registration

---

## Active Workers — Sweden Pipeline (`examples/sweden/`)

### se-source-fetcher `v0.1.0`
- **Script:** `scripts/se-source-fetcher.py`
- **Role:** Fetch raw API records from dataportal.se (Digg)
- **Input:** `limit` (default 20), `offset`, `filter_type` (api|dataset|all)
- **Output:** stream of `SourceRecord` data events
- **Constraints:** network ✅ | admin ❌ | timeout 30s

### se-normalizer `v0.1.0`
- **Script:** `scripts/se-normalizer.py`
- **Role:** SourceRecord → ApiRecord (canonical schema)
- **Input:** stdin (piped) or `source_file` path, `strict` flag
- **Output:** stream of `ApiRecord` data events
- **Constraints:** network ❌ | admin ❌ | timeout 60s

### se-scorer `v0.1.0`
- **Script:** `scripts/se-scorer.py`
- **Role:** Score ApiRecords — three-factor model
  - Discovery relevance: 55%
  - Implementation readiness: 30%
  - Metadata completeness: 15%
- **Input:** optional `query` (for relevance), stdin or `source_file`
- **Output:** `{api_record, score_breakdown}` pairs
- **Constraints:** network ❌ | admin ❌ | timeout 30s

### se-search `v0.1.0`
- **Script:** `scripts/se-search.py`
- **Role:** End-to-end orchestrator — fetch → normalize → score → rank
- **Input:** `query` (required), `limit` (default 10), `filter_access`, `filter_domain`
- **Output:** ranked `SearchIndexRecord` stream, best match first
- **Constraints:** network ✅ | admin ❌ | timeout 45s

---

## Handlers (surfaces)

| Handler | Location | Status |
|---|---|---|
| TerminalHandler | `handlers/terminal.py` | Active (from ikommand) |
| ApiHandler | `handlers/api.py` | Stub — needs FastAPI |

---

## Contract Schemas (`examples/sweden/contracts/`)

| Schema | Purpose |
|---|---|
| `source_record.schema.json` | Raw record from dataportal.se |
| `api_record.schema.json` | Canonical normalized API record |
| `score_breakdown.schema.json` | Three-factor score per record |
| `search_index_record.schema.json` | Final ranked result |
| `capability_profile.schema.json` | Agent capability declaration |
| `connection_profile.schema.json` | Connection metadata |

---

## Composition Layer
**Status: NOT YET BUILT**
Planned: sequential composition, fan-out/fan-in, event pass-through, typed handoff.
Currently: se-search does manual subprocess chaining internally (scaffolding only).
