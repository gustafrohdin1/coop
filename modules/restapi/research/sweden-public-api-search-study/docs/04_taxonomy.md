# PURPOSE
Define the classification system used by the study for search, filtering, and ranking.

# SCOPE
Included:
- Domain taxonomy
- Producer taxonomy
- Access taxonomy
- Protocol and format taxonomy
- Freshness and metadata classes

Excluded:
- Full controlled vocabulary for every public-sector theme

# STRUCTURE
## Domain categories
- transport
- geospatial
- health
- education
- environment
- economy
- business_and_procurement
- demographics
- justice_and_civic
- culture_and_heritage
- research
- utilities_and_infrastructure
- cross_domain
- unknown

## Producer types
- state_agency
- municipality
- region
- public_company
- university
- mixed_catalog
- private_or_civil_source
- unknown

## Access models
- open_no_auth
- open_api_key
- authenticated_public
- restricted
- unclear

## Interface types
- rest
- graphql
- sparql
- soap
- odata
- file_download_only
- bulk_download
- unknown

## Distribution formats
- json
- xml
- rdf
- csv
- geojson
- zip
- html
- unknown

## Freshness classes
- realtime
- daily
- weekly
- monthly
- irregular
- unknown

## Metadata completeness
- high
- medium
- low

## API confidence
- confirmed_api
- probable_api
- ambiguous_service
- not_api

# CONTRACTS
Input:
- Raw source metadata
- Normalization heuristics

Output:
- Stable categorical fields on `ApiRecord` and `SearchIndexRecord`

Schemas:
- `api_record.schema.json`
- `search_index_record.schema.json`

# RULES
Allowed:
- Map multiple source vocabularies into one compact search taxonomy
- Use `unknown` when inference would be brittle

Forbidden:
- Encoding portal-specific terms directly into the public search contract unless they are normalized
- Exploding the taxonomy into hundreds of niche labels in v1

# EXAMPLES
Transport API with JSON endpoint and no auth:
- domain `transport`
- access_model `open_no_auth`
- interface_type `rest`
- format `json`
- api_confidence `confirmed_api`

Dataset page with only CSV downloads:
- interface_type `file_download_only`
- api_confidence `not_api`

# NOTES
The taxonomy is intentionally compact so that ranking and filtering stay usable instead of mirroring every upstream vocabulary literally.
