# PURPOSE
Explain where the official Swedish portal ecosystem already works well and where a better builder-facing search layer adds value.

# SCOPE
Included:
- Portal strengths
- Discovery gaps
- Search-layer opportunity

Excluded:
- Critique of policy goals or portal governance outside discovery needs

# STRUCTURE
## What the official ecosystem already does well
- provides a national metadata aggregation point
- standardizes publication around DCAT-AP-SE
- supports harvesting, validation, and sandbox tooling
- separates source ownership from catalog discovery
- exposes metadata via official APIs and dumps

## What is still hard for builders
- distinguishing true APIs from general datasets
- finding records with direct documentation and direct access URLs quickly
- ranking by practical implementation value rather than generic metadata presence
- handling inconsistent metadata quality across publishers
- filtering out records that are technically valid but operationally weak

## Why this gap exists
The portal must serve many audiences and many object types:
- compliance and metadata publication
- broad data discovery
- multiple sectors and producer types
- linked-data interoperability

A builder-facing search layer has a narrower job:
- fast API discovery
- practical integration signals
- low-friction filtering

## Value proposition of a future search layer
- normalize noisy metadata into a compact API-first contract
- expose confidence and readiness explicitly
- improve intent-aware ranking
- preserve official provenance while reducing manual review time

# CONTRACTS
Input:
- Official portal model
- Builder-oriented search requirements

Output:
- Clear justification for later implementation work

Schemas:
- `api_record.schema.json`
- `score_breakdown.schema.json`

# RULES
Allowed:
- Add stronger usability heuristics than the official portal surfaces

Forbidden:
- Misrepresenting portal limitations as infrastructure failure

# EXAMPLES
The national portal may correctly surface a metadata record, while a builder-facing search layer should still demote it because it lacks an actionable service endpoint or docs.

# NOTES
The gap is not "missing metadata aggregation." The gap is "missing builder-optimized interpretation and ranking."
