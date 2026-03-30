# PURPOSE
Describe the official Swedish source landscape that this study treats as the v1 trust anchor.

# SCOPE
Included:
- National portal role
- Metadata publishing and harvesting model
- Official technical surfaces relevant to later search implementation
- Source trust hierarchy

Excluded:
- Exhaustive inventory of every agency catalog
- Municipal and regional long-tail mapping

# STRUCTURE
## Primary official sources

### Digg
Digg positions Sveriges dataportal as the shared national place to search for data and APIs from public and other organizations. Digg also describes the portal as metadata-focused rather than a host for the underlying data or API payloads.

### Sveriges dataportal
The public portal is the main discovery surface for metadata records.

Operational characteristics from official documentation:
- the portal exposes metadata, not hosted data
- organizations publish metadata according to DCAT-AP-SE
- data can be delivered through direct harvesting, the shared metadata catalog, or connected aggregated catalogs
- metadata is synchronized onward to the EU portal context

### Dataportal technical docs
Official docs describe:
- harvesting through HTTP or HTTPS from a stable source URL
- nightly re-harvesting and nightly RDF dump generation
- API access to metadata through `admin.dataportal.se`
- sandbox and validation tools for publishers

### DCAT-AP-SE
DCAT-AP-SE is the Swedish metadata profile used to structure publication and harvesting. It is the key interoperability layer for any future ingestion design.

## Source trust hierarchy
Tier 1:
- Official Digg pages describing Sveriges dataportal and publication obligations
- Official dataportal technical docs
- Official DCAT-AP-SE documentation

Tier 2:
- Metadata exposed by official portal infrastructure such as dumps and admin APIs

Tier 3:
- Individual agency implementations reached through official catalog metadata

Tier 4:
- Non-official secondary directories or third-party API lists

## Implications for this project
- V1 should start from the official metadata ecosystem, not from scraping arbitrary agency websites.
- Search value is added after metadata ingestion: normalization, intent handling, and builder-oriented ranking.
- The source model must preserve provenance because official metadata quality varies across producers and connected catalogs.

# CONTRACTS
Input:
- Official portal documentation
- Official metadata endpoints and dumps

Output:
- `SourceRecord` definitions for each trusted source surface
- Source trust level and ingestion strategy metadata

Schemas:
- `source_record.schema.json`

# RULES
Allowed:
- Treat official docs as the normative description of how metadata flows
- Rank sources by trust and operational stability

Forbidden:
- Flattening all sources into one undifferentiated pool
- Treating third-party API directories as equivalent to Digg-managed sources

# EXAMPLES
Tier 1 source:
- Digg documentation stating that Sveriges dataportal collects metadata and that data and APIs remain with the publishing organization.

Tier 2 source:
- The admin metadata API or nightly RDF dump used for secondary indexing.

# NOTES
This project is not anti-portal. It assumes the portal is the official metadata backbone and that the search opportunity sits one layer above it.
