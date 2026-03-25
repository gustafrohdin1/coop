# copilot · status

updated: 2026-03-25

## current state

repo: gustafrohdin1/coop  
description: Python framework — defensive perimeter for AI modules. Handlers, BaseAgent, Registry, runner are stable. Sweden pipeline (fetch → normalize → score → search) validated.

active branch: copilot/t-copilot-structure-002-propose-repo-structure  
pr: pending (not yet merged to main)

## top-level structure (main / working branch)

```
handlers/         agent handler implementations
schema/           manifest and handshake contracts
src/coop/         core SDK — runner, BaseAgent, BaseHandler, Registry
tests/            test suite
project-init.md   project state and pending work (source of truth for Gustaf)
pyproject.toml    package config
```

## ⚠ unmerged branch

Branch `feature/sweden-api-search` (tagged 1.0.0) diverges from the init commit and has
NEVER been merged to main. It contains:

- Full sweden API search pipeline (validated against dataportal.se) — T002
- xCOOP SwiftUI scaffold — T003
- Framework model docs (docs/model/, docs/runtime/, docs/workers/) — T003

Gustaf needs to decide: merge to main, or keep separate?

## pending work (from project-init.md)

- Input validation stubbed, timeout ignored, stderr dropped, constraints not enforced
- Composition layer (fan-out/fan-in, typed handoff) not built — se-search chains manually
- Publisher name resolution needs Bolagsverket integration
- ApiHandler is a stub (no FastAPI)

## open decisions for Gustaf

- Merge feature/sweden-api-search (T002+T003) into main?
- Which direktoru proposals to adopt? (guardrails, preflight, file-dedup, file-classifier, route-data)
- Blob concept: framework prejudikat or not?

## task log index

| id | date | type | summary | merged |
|---|---|---|---|---|
| T001 | 2026-03-19 | WORK | Init coop SDK — events, runner, BaseAgent, 16 tests | YES (root) |
| T002 | 2026-03-19 | WORK | Sweden pipeline — fetch/normalize/score/search, validated | NO |
| T003 | 2026-03-19 | WORK+ANALYSIS | xCOOP scaffold + framework model docs | NO |
| T004 | 2026-03-21 | ANALYSIS+PLAN | Repo structure proposal, project-init.md, direktoru patterns | YES (main) |
| T005 | 2026-03-25 | WORK | Establish copilot log branch (.github/copilot/) | on log branch |

## this branch

Branch `copilot` is the permanent log branch. It is never merged.  
Read `.github/copilot/log/` for task history.  
Read this file for current snapshot before starting any task.
