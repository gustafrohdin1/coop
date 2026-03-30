# PURPOSE
Define the canonical machine-readable contracts for the future system boundary.

# SCOPE
Included:
- `SourceRecord`
- `ConnectionProfile`
- `CapabilityProfile`
- `ApiRecord`
- `SearchIndexRecord`
- `ScoreBreakdown`

Excluded:
- Full raw DCAT-AP-SE schema mapping

# STRUCTURE
## SourceRecord
Describes a trusted upstream source surface.

Core fields:
- `source_id`
- `name`
- `owner`
- `trust_tier`
- `source_type`
- `base_url`
- `access_mode`
- `format`
- `update_cadence`
- `country_scope`
- `notes`

## ConnectionProfile
Describes how a source can actually be connected to and under what operational constraints.

Core fields:
- `connection_id`
- `source_id`
- `transport`
- `entrypoint_url`
- `client_mode`
- `auth_scheme`
- `requires_org_approval`
- `supports_browser_direct`
- `supports_server_to_server`
- `sandbox_available`
- `versioning_model`
- `pagination_model`
- `rate_limit_model`
- `notes`

## CapabilityProfile
Describes what the source can do once connected.

Core fields:
- `capability_id`
- `source_id`
- `supports_search`
- `supports_list`
- `supports_detail_lookup`
- `supports_bulk_export`
- `supports_filtering`
- `supports_streaming`
- `supports_webhooks`
- `supports_write`
- `primary_result_shape`
- `notes`

## ApiRecord
Canonical normalized record for API-first discovery.

Core fields:
- `api_id`
- `stable_source_identifier`
- `title`
- `aliases`
- `provider`
- `provider_type`
- `source_portal`
- `source_url`
- `documentation_url`
- `access_url`
- `description`
- `domain_tags`
- `geography`
- `auth_model`
- `interface_type`
- `distribution_formats`
- `update_frequency`
- `license`
- `api_confidence`
- `metadata_completeness`
- `documentation_quality_notes`
- `search_keywords`
- `source_trust_tier`
- `provenance`

## SearchIndexRecord
Read-optimized search record derived from `ApiRecord`.

Core fields:
- `record_id`
- `title`
- `provider`
- `domain_tags`
- `api_confidence`
- `access_model`
- `interface_type`
- `has_docs`
- `has_direct_access`
- `search_text`
- `filter_tokens`

## ScoreBreakdown
Transparent scoring interface.

Core fields:
- `discovery_relevance`
- `implementation_readiness`
- `metadata_completeness`
- `penalties`
- `total_score`
- `score_version`

# CONTRACTS
Input:
- Official source metadata

Output:
- Stable typed records for future ingestion and search implementation

Schemas:
- `contracts/source_record.schema.json`
- `contracts/connection_profile.schema.json`
- `contracts/capability_profile.schema.json`
- `contracts/api_record.schema.json`
- `contracts/search_index_record.schema.json`
- `contracts/score_breakdown.schema.json`

# RULES
Allowed:
- Add optional fields later as long as core semantics stay stable

Forbidden:
- Reinterpreting the meaning of core fields across implementations

# EXAMPLES
`ApiRecord.access_url`:
- should be the best known direct access point for integration, not just the catalog page.

`ApiRecord.source_url`:
- should point to the source metadata or landing page where the record originated.

`ConnectionProfile.client_mode`:
- should tell an implementer whether the source is realistically browser-direct, server-only, or mixed.

`CapabilityProfile.primary_result_shape`:
- should summarize whether the source mainly returns search hits, entities, feeds, documents, or mixed objects.

# NOTES
The contracts are intentionally compact. They separate source, connection, capability, content, and scoring so later implementations can generalize beyond Swedish public APIs without rewriting the core model.
