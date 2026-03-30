# PURPOSE
Describe real builder search intents and the result characteristics that satisfy them.

# SCOPE
Included:
- Canonical user query scenarios
- Query-to-result expectations

Excluded:
- UI copywriting
- Relevance evaluation framework beyond representative scenarios

# STRUCTURE
## Query: transport APIs in Sweden
Intent:
- Find machine-consumable transport-related APIs fast.

Good results:
- transport-tagged records
- high API confidence
- direct access or docs links
- clear provider and auth model

Bad results:
- general transport datasets with only downloadable files
- records with no service evidence

## Query: health public APIs
Intent:
- Find public-sector health-related APIs or service endpoints.

Good results:
- health-tagged records
- explicit service model or endpoint documentation
- clear access conditions

Bad results:
- policy pages
- portal category pages
- datasets with no machine interface

## Query: only real APIs, not generic datasets
Intent:
- Suppress records that are useful for data discovery but not for direct integration.

Good results:
- `api_confidence=confirmed_api` or `probable_api`
- `interface_type!=file_download_only`

Bad results:
- records where the only access pattern is file download

## Query: sources with clear documentation and direct access
Intent:
- Reduce manual filtering time.

Good results:
- docs URL present
- access URL present
- explicit auth model
- explicit format/protocol

Bad results:
- descriptive metadata only

# CONTRACTS
Input:
- Query string
- Optional structured filters

Output:
- Result expectations for ranking validation

Schemas:
- `search_index_record.schema.json`
- `score_breakdown.schema.json`

# RULES
Allowed:
- Use intent-specific filtering and boosts

Forbidden:
- Returning broad catalog noise as top results for builder-intent queries

# EXAMPLES
If a user searches `transport api`, a downloadable PDF timetable dataset should never outrank a documented REST endpoint.

# NOTES
These scenarios double as acceptance criteria for future search quality.
