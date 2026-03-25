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

## pending work (from project-init.md)

- Input validation stubbed, timeout ignored, stderr dropped, constraints not enforced
- Composition layer (fan-out/fan-in, typed handoff) not built
- Publisher name resolution needs Bolagsverket integration
- ApiHandler is a stub

## this branch

Branch `copilot` is the permanent log branch. It is never merged.  
Read `.github/copilot/log/` for task history.  
Read this file for current snapshot before starting any task.
