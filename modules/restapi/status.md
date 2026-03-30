# REST API Module Status

## What this is
A holding area for REST/API-related work that already exists but is not yet a
finished, canonical framework module.

## Collected now
- Research study: `research/sweden-public-api-search-study/`
- Prototype artifacts: `prototype/examples/sweden/`
- Existing framework-adjacent handler still in root surface: `handlers/api.py`

## Interpretation
- Useful work has been done.
- The work is not yet unified into one finished module.
- Research, contracts, and prototype code should be preserved before deciding
  what becomes reusable framework capability.
- `handlers/api.py` is already a functioning part of coop, not just a name stub.

## What seems already done
- Sweden-focused API source study
- Data contracts and connection thinking
- Prototype fetch/normalize/search scripts in branch material
- API-facing handler surface in coop
- Passing handler tests for `ApiHandler` in `tests/test_handler.py`

## What still needs to be done
- separate generic framework logic from Sweden-specific example logic
- define module boundary and public contract for a real restapi module
- decide what belongs in research, prototype, handler surface, and framework core
- design the next implementation job from preserved material instead of memory

## Current rule
Nothing here should be presented as complete just because it has been collected.

## Verified now
- `handlers/api.py` is used by `tests/test_handler.py`
- `ApiHandler` passes the current handler test suite
- the open question is not whether it works, but how it should relate to the
  larger REST/API module line
