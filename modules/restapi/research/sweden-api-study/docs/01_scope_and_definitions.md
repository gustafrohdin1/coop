# PURPOSE
Define what is in scope for the study and establish shared terms.

# SCOPE
Included:
- Canonical definitions for search, indexing, and evaluation
- Inclusion and exclusion rules
- Edge-case handling for ambiguous records

Excluded:
- Legal interpretation beyond operational assumptions
- Deep semantic modeling of every DCAT-AP-SE class

# STRUCTURE
## Core terms

`API`
- A machine-consumable service interface exposed over a network.
- Typical signs: endpoint documentation, protocol details, authentication model, distribution or access URL that points to a service rather than a static file.

`Dataset`
- A published collection of data.
- A dataset may be downloadable, queryable, streamable, or attached to an API.

`Catalog entry`
- A metadata record surfaced by a catalog or portal.
- It may describe a dataset, data service, specification, concept set, or related object.

`Searchable source`
- An official portal, catalog, or metadata surface that is intentionally queried or harvested as an upstream source.

`Normalized API record`
- The study's implementation-facing canonical record for an API or API-like service.

## Inclusion rules
Include:
- Entries that clearly expose or describe a network-accessible API or datatjanst
- Entries whose metadata strongly indicates machine-consumable service access
- Entries that are not perfect APIs but are likely to be searched by builders as APIs

Exclude:
- Records that only describe downloadable files with no service interface
- Records with no practical access signal and no developer-relevant machine interface
- Editorial pages, news, forum posts, and non-catalog content

## Edge-case rules
Ambiguous dataset with both files and service access:
- Include if the service access is real and discoverable.

Weak metadata but likely API:
- Include with low metadata completeness and low implementation-readiness scores.

Rich dataset with no API:
- Keep out of `ApiRecord`.
- It may still exist in a broader future catalog model, but not in the API-focused v1 normalized contract.

# CONTRACTS
Input:
- Official metadata records from trusted Swedish sources

Output:
- Binary decisions for inclusion in the API-focused normalized model
- Explicit flags for ambiguity

Schemas:
- `api_record.schema.json`
- `score_breakdown.schema.json`

# RULES
Allowed:
- Use practical developer value as a filter
- Preserve ambiguity via flags rather than hiding it

Forbidden:
- Equating "published on a portal" with "usable API"
- Expanding v1 to all public data objects

# EXAMPLES
Included:
- A catalog record with a service endpoint, protocol, and provider.

Excluded:
- A record that only points to a CSV download page.

Conditional:
- A dataset with a vague "API available" note but no direct documentation link.

# NOTES
V1 is API-first, not data-universe-first.
