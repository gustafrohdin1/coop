# PURPOSE
Capture representative source families and compare what they teach the framework.

# SCOPE
Included:
- first comparison set across very different source types
- connection shape
- handler implications
- normalization and visualization pressure

Excluded:
- exhaustive endpoint documentation
- implementation code

# STRUCTURE
## Why this matrix exists
The framework should not generalize from one API family alone.

This matrix exists to:
- compare structurally different sources
- identify recurring handler families
- expose where new cases are really needed

## Comparison matrix
| Family | Reference source | Connection shape | Likely handler family | Normalization difficulty | Visualization fit | Main lesson |
|---|---|---|---|---|---|---|
| Food | Open Food Facts | Public HTTP API, search plus lookup, published rate limits | `CatalogSearchHandler` | High | High | Messy real-world records force confidence scoring and alias handling |
| Weather | Open-Meteo | Public HTTP API, location lookup plus forecast query | `StructuredQueryHandler` | Low to medium | Very high | Time-series and location-aware structured outputs need clean metric contracts |
| News | RSS 2.0 feeds | Public pull feed, XML polling, source-specific freshness | `FeedListenerHandler` | Medium | High | Feed ingestion, dedupe, freshness, and semantic overlays should be separate stages |
| Public sector | Arbetsförmedlingen / JobTech | Official portal plus search APIs plus update-style data services | `PublicServiceApiHandler` | Medium to high | High | One family may include catalog, search, and stream-like patterns at once |

## Per-family notes

### Food
Representative source:
- Open Food Facts

Pressure points:
- multilingual values
- partial and inconsistent records
- entity identity by barcode and aliases
- search results that may look complete but are not

Framework implications:
- needs separate search and detail semantics
- needs completeness/confidence flags
- benefits from raw-versus-normalized inspection in the UI

### Weather
Representative source:
- Open-Meteo

Pressure points:
- coordinate-based querying
- current versus forecast versus historical slices
- repeated structured metrics over time

Framework implications:
- needs strong time-window semantics
- needs first-class metric and chart-friendly normalized structures
- fits very well with dashboard visualization

### News
Representative source:
- RSS 2.0 feeds

Pressure points:
- repeated polling
- duplicate stories across sources
- text-heavy payloads
- source credibility and freshness differences

Framework implications:
- listener and poller should be reusable
- summarization or sentiment should not live in the feed handler itself
- provenance matters a lot

### Public sector
Representative source:
- Arbetsförmedlingen / JobTech

Pressure points:
- official docs plus portal pages plus search APIs
- mixed object types
- public search plus richer ecosystem semantics

Framework implications:
- needs separation of source portal, access URL, and documentation URL
- may require one source to expose multiple capabilities under one umbrella

## Emerging handler families
- `CatalogSearchHandler`
- `StructuredQueryHandler`
- `FeedListenerHandler`
- `PublicServiceApiHandler`

These are provisional family names, not final base classes.

# CONTRACTS
Input:
- official docs and representative API surfaces

Output:
- framework-facing source family comparison
- evidence for handler taxonomy decisions

Schemas:
- `contracts/connection_profile.schema.json`
- `contracts/capability_profile.schema.json`

# RULES
Allowed:
- use one source as a representative of a family

Forbidden:
- overgeneralize one source into a universal rule

# EXAMPLES
If a new source behaves like Open-Meteo plus geocoding, it should probably reuse the same handler family rather than create a new one.

# NOTES
The matrix is meant to grow gradually. A new family should only be introduced when existing family patterns clearly fail.
