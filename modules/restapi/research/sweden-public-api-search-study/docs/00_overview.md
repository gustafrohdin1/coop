# PURPOSE
Define the problem this study solves, the intended outcome, and the method used to reach a universal handling model.

# SCOPE
Included:
- Why Swedish public API discovery is still harder than it should be
- What a better search layer must improve
- Why connection variation must be studied before canonical structure is frozen
- What this study enables later

Excluded:
- Implementation details beyond architecture-level design
- Policy analysis beyond what affects search and developer usability

# STRUCTURE
The current Swedish ecosystem already has a national portal layer, but that layer is optimized for metadata publication, compliance, and broad discoverability across many kinds of data objects.

That is necessary, but not sufficient for builders who ask questions like:
- Which transport APIs are machine-consumable right now?
- Which records expose a direct access URL instead of only catalog prose?
- Which entries are true APIs versus generic downloadable datasets?
- Which results are likely to be usable without manual detective work?

This study defines a future search layer that keeps the official metadata ecosystem intact while making it easier to:
- find relevant APIs fast
- normalize inconsistent source metadata
- rank by builder usefulness
- separate APIs from other data assets without hiding related context

The broader ambition is larger than Swedish public APIs alone. This repository treats Sweden v1 as a disciplined training ground for a future universal API handling framework.

That means the method matters:
1. discover real connection patterns
2. capture recurring access and capability shapes
3. define canonical internal contracts only after those variations are visible

The universal part should live in orchestration and internal contracts, not in pretending every upstream API behaves the same way.

# CONTRACTS
Input:
- Official Swedish metadata and portal documentation
- Future source records that describe official catalogs
- Future connection and capability profiles that describe how sources actually behave

Output:
- Decision-complete documentation for a standalone project
- Contracts for normalized searchable records
- Contracts for connection and capability modeling
- Ranking model for later implementation

Schemas:
- `docs/contracts/source_record.schema.json`
- `docs/contracts/connection_profile.schema.json`
- `docs/contracts/capability_profile.schema.json`
- `docs/contracts/api_record.schema.json`
- `docs/contracts/search_index_record.schema.json`
- `docs/contracts/score_breakdown.schema.json`

# RULES
Allowed:
- Interpret official source behavior in search-product terms
- Define stricter normalization than official portals expose
- Distinguish builder-oriented search needs from catalog compliance needs
- Use Sweden v1 to extract durable connection patterns that can later generalize to social and partner APIs

Forbidden:
- Pretending the national portal is inadequate as infrastructure
- Assuming all datasets are APIs
- Designing a v1 that requires broad source federation beyond official Swedish portal surfaces
- Freezing a universal schema before enough connection variation has been studied

# EXAMPLES
Good outcome:
- A future implementer can build connectors, normalizers, and a search API without inventing new core definitions.

Bad outcome:
- A future implementer must guess what counts as an API, how to score results, or how official metadata maps to search records.

# NOTES
The core thesis is not "replace the portal." It is "learn from real connection variation, then build a faster builder-facing discovery layer on top of the official metadata ecosystem."
