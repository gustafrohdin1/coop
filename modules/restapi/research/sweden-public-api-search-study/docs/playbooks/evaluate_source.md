# PURPOSE
Evaluate whether an upstream source should be trusted and how it should be ingested.

# SCOPE
Included:
- Officiality
- Stability
- Metadata usefulness
- Ingestion recommendation

Excluded:
- Building the ingestion code

# STRUCTURE
1. Confirm ownership and official status.
2. Identify whether the source is docs, portal, API, dump, or shared catalog.
3. Confirm access method and format.
4. Confirm update cadence from official documentation when possible.
5. Assign trust tier.
6. Record how provenance should be stored.
7. Decide whether the source is primary, secondary, or deferred.

# CONTRACTS
Input:
- Candidate source URL
- Supporting official documentation

Output:
- `SourceRecord`

# RULES
Allowed:
- Use official docs as the basis for trust assignment

Forbidden:
- Promoting third-party mirrors to tier 1 or tier 2

# EXAMPLES
`admin.dataportal.se` metadata API:
- official
- machine-accessible
- suitable as a tier 2 source
