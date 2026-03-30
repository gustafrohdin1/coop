# REST API Module Work Area

## Purpose
This area collects existing REST/API research and prototype work so it is not lost
or rediscovered repeatedly.

Nothing here is implicitly finished or canonical just because it has been
collected.

## Structure
- `research/` - studies, docs, contracts, and research material
- `prototype/` - code or branch artifacts that show what has been tried
- `status.md` - current interpretation of what exists and what remains

## Current sources
- `research/sweden-public-api-search-study/` from local R&D study material
- `prototype/examples/sweden/` extracted from `sweden-search-demo`
- `handlers/api.py` as an existing, working API-facing response handler in coop

## Rule
Treat this area as preserved work-in-progress.
Promote only verified, reusable parts into framework code or canonical module docs.

## Important distinction

`handlers/api.py` is not the full REST/API module line collected here.
It is, however, a real and working handler surface that already exists in the
framework and has passing handler tests.
