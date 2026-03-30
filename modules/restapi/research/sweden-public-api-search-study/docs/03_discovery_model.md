# PURPOSE
Define how a future search layer would discover connection patterns, ingest source metadata, normalize records, and expose searchable results.

# SCOPE
Included:
- Logical ingestion model
- Connection-pattern discovery
- Normalization stages
- Search-facing record flow

Excluded:
- Implementation language
- Storage engine choice
- UI details

# STRUCTURE
## Logical pipeline
1. Source registration
2. Connection profiling
3. Metadata fetch
4. Parse and validate
5. Normalize into canonical records
6. Classify into API-first search buckets
7. Compute score breakdown
8. Index for query-time retrieval

## Source registration
Each upstream source is represented by a `SourceRecord` with:
- trust level
- fetch mode
- format
- update cadence
- provenance rules

## Connection profiling
Each upstream source should also be represented by a `ConnectionProfile` and a `CapabilityProfile`.

The purpose is to capture recurring variation before canonical contracts are overfit to one ecosystem.

Important connection dimensions:
- browser-safe versus server-only
- anonymous access versus API key versus organizational onboarding
- direct endpoint access versus portal-mediated discovery
- static dump versus search API versus record-detail API
- pagination, throttling, and versioning behavior
- sandbox or test environment availability

Important capability dimensions:
- search
- list
- detail lookup
- bulk export
- filtering
- streaming
- webhook support
- write operations

## Metadata fetch
V1 future implementation should support:
- official dump ingestion
- official metadata API ingestion
- controlled source refresh based on documented update cadence

Later implementations may extend to:
- social media APIs
- partner APIs
- hybrid public/private sources

Those should reuse the same `ConnectionProfile` and `CapabilityProfile` seam.

## Parse and validate
Parsing is expected to preserve raw provenance fields.

Validation goals:
- detect missing minimum fields
- separate invalid metadata from merely weak metadata
- preserve recoverable records when useful for discovery

## Normalize
Normalization converts source-specific fields into the canonical `ApiRecord`.

Important normalization tasks:
- collapse multiple labels into one search title plus aliases
- identify provider and source portal separately
- extract access URLs and documentation URLs
- infer auth model when explicit metadata is missing but evidence is strong
- distinguish API protocols from file formats
- create searchable keyword expansions without losing source truth

## Classify
Each record should be labeled at least by:
- object type confidence
- domain tags
- access model
- geography
- freshness class

## Expose
Future search interfaces should operate on the normalized record, not directly on DCAT-AP-SE source shape.

# CONTRACTS
Input:
- `SourceRecord`
- `ConnectionProfile`
- `CapabilityProfile`
- Raw metadata objects from official sources

Output:
- `ApiRecord`
- `SearchIndexRecord`
- `ScoreBreakdown`

Schemas:
- `source_record.schema.json`
- `connection_profile.schema.json`
- `capability_profile.schema.json`
- `api_record.schema.json`
- `search_index_record.schema.json`
- `score_breakdown.schema.json`

# RULES
Allowed:
- Preserve raw source identifiers alongside canonical IDs
- Enrich for searchability if provenance stays traceable
- Keep connection semantics separate from data semantics

Forbidden:
- Throwing away provenance
- Assuming every record can be perfectly normalized
- Collapsing auth, transport, capability, and content semantics into one record too early

# EXAMPLES
A future implementation may ingest the nightly RDF dump for bulk indexing, use metadata API lookups for record enrichment, and use connection profiles to decide which sources can be queried from a browser versus only from a server.

# NOTES
The canonical record is one implementation seam. The connection and capability profiles are the others. Together they make a universal orchestration layer possible without flattening source differences.
