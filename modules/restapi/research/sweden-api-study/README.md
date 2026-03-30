# Sweden Public API Search Study

## Purpose
This repository is a contract-first master study for a Sweden-focused public API search layer, designed as the first slice of a broader universal API handling framework.

The goal is simple: help builders find Swedish public and open APIs faster than they can through today's portal and catalog surfaces alone.

V1 is documentation-only. There is no search application, crawler, UI, or code-generated index in this repository.

## Audience
- Developers and technical product teams
- Researchers or integrators evaluating Swedish public data access
- Future implementers of a search service built on top of official metadata sources

## Scope
Included:
- Sweden-only source landscape for v1
- Official portal and catalog sources as the trust anchor
- Connection-pattern discovery across real sources
- Definitions, inclusion rules, taxonomy, ranking model, and data contracts
- Product path from study to future implementation

Excluded:
- Full ingestion implementation
- Search UI
- Ranking engine code
- Municipality-by-municipality mapping
- Nordic or EU expansion beyond reference context

## Working Assumptions
- The primary national discovery surface is Sveriges dataportal, operated by Digg.
- The portal surfaces metadata, not hosted data itself.
- Metadata publication and harvesting are built around DCAT-AP-SE.
- The right sequence is connection discovery first, canonical structure second.
- A better search layer adds value mainly through normalization, query intent handling, and more useful ranking for builders.

## Repository Structure
- `docs/00_overview.md`
- `docs/01_scope_and_definitions.md`
- `docs/02_source_landscape.md`
- `docs/03_discovery_model.md`
- `docs/04_taxonomy.md`
- `docs/05_ranking_and_scoring.md`
- `docs/06_user_queries.md`
- `docs/07_data_contracts.md`
- `docs/08_gap_analysis.md`
- `docs/09_product_path.md`
- `docs/10_connection_profiles.md`
- `docs/11_case_arbetsformedlingen.md`
- `docs/12_case_skatteverket.md`
- `docs/13_source_family_matrix.md`
- `docs/contracts/`
- `docs/playbooks/`

## How To Use This Study
1. Start with the overview and definitions.
2. Treat the source landscape as the source-of-truth model for v1.
3. Use the connection profiles to capture real-world access variation before refining contracts.
4. Use the taxonomy and scoring model together.
5. Use the contracts as the implementation boundary for any later ingestion, indexing, filtering, and unified response work.

## Source Grounding
This study is grounded in official Swedish documentation from Digg and Sveriges dataportal, including:
- Digg's description of Sveriges dataportal as the place to search data and APIs
- Dataportal docs for harvesting, nightly updates, and metadata API access
- DCAT-AP-SE documentation for the Swedish metadata profile

See the source landscape and gap analysis documents for the applied interpretation.
