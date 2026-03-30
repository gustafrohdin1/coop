# PURPOSE
Define how records should be ranked for "find APIs fast" rather than general metadata browsing.

# SCOPE
Included:
- Scoring dimensions
- Ranking signals
- Tie-breaking logic

Excluded:
- Search engine implementation details
- Machine learning approach

# STRUCTURE
## Scoring dimensions

### 1. Discovery relevance
How likely the record is to satisfy the user's intent quickly.

Signals:
- query term match in title
- query term match in aliases or keywords
- domain match
- interface type match
- access model match
- exact provider or source match

### 2. Implementation readiness
How usable the record is for a developer right now.

Signals:
- direct access URL exists
- documentation URL exists
- auth model is explicit
- interface/protocol is explicit
- provider identity is clear
- examples or machine-readable distributions exist

### 3. Metadata completeness
How complete and internally useful the metadata is as a record.

Signals:
- title and description quality
- domain/theme presence
- update frequency present
- license present
- contact or publisher metadata present
- protocol/format fields present

## Default weighting
- discovery_relevance: 0.55
- implementation_readiness: 0.30
- metadata_completeness: 0.15

## Penalties
- ambiguous API classification
- missing direct access URL
- no documentation link
- generic or very short description
- conflicting format/interface indicators

## Tie-breaks
Prefer, in order:
1. higher API confidence
2. better implementation readiness
3. higher source trust
4. fresher metadata

# CONTRACTS
Input:
- Query intent
- `ApiRecord`

Output:
- `ScoreBreakdown`
- Total ranking score

Schemas:
- `score_breakdown.schema.json`

# RULES
Allowed:
- Optimize for builder speed over abstract metadata richness
- Penalize records that are technically present but practically weak

Forbidden:
- Using only text match
- Treating completeness as more important than practical usability

# EXAMPLES
Two transport records match a query:
- Record A has direct docs and endpoint details.
- Record B has only a short dataset summary.

Record A should rank first even if Record B has broader metadata coverage.

# NOTES
This study deliberately separates "easy to find" from "easy to implement." A future product should expose both rather than collapse them into a single opaque number.
