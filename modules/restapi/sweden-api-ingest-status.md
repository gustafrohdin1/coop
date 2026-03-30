# coop · sweden-api ingest status

## Purpose
Preserve and classify the Sweden/API research line so it can be extracted into
canonical `coop` work without losing what was already studied or built.

## Sources included

### Study
- origin: `/Volumes/Disk/_DEV_/__RND/sweden-public-api-search-study`
- copied to: `sources/coop/sweden-api-study/`
- nature: documentation-first research package

### Prototype
- origin repo: `coop`
- origin branch: `sweden-search-demo`
- origin commit: `0be6225`
- copied to: `sources/coop/sweden-api-prototype/`
- nature: runnable example pipeline

---

## What was already done

### In the study package
- Sweden public API/discovery landscape documented
- source selection and trust model described
- discovery model and taxonomy written
- ranking/scoring model outlined
- connection-profile thinking documented
- case studies written
- contracts defined for:
  - source records
  - API records
  - connection profiles
  - capability profiles
  - score breakdown
  - search index records
- playbooks added for:
  - adding sources
  - evaluating sources
  - harvesting source families
  - classifying API records

### In the prototype package
- multi-step pipeline exists:
  - fetch
  - normalize
  - score
  - search
- manifests exist for each step
- contracts are wired into example output
- `se-source-fetcher.py` contains real external API access logic
- REST response parsing was iterated in branch history

---

## What this proves

- There is real research material for a connector/search line in `coop`
- There is real prototype code, not just concept notes
- The work was originally Sweden-focused, but parts of it are likely reusable
- The current `ApiHandler` in `coop` is not the same thing as this connector line

---

## What still needs to be done

### Extraction work
- separate Sweden-specific logic from reusable connector logic
- identify which schemas are framework-generic vs example-specific
- identify which worker steps belong in canonical `coop` and which remain examples

### Canonical coop questions
- should `coop` own a general external API connector module?
- should `coop` own only connector primitives and leave source-specific pipelines as examples?
- what is the minimal stable contract for request/response normalization?
- how should retries, auth, timeouts, partial responses, and unstable-success be logged?

### Documentation work
- write a canonical status summary for current API capability in `coop`
- map prototype artifacts to:
  - keep as example
  - extract to framework
  - archive as study-only

---

## Suggested next step

Run a focused extraction audit over:
- `sources/coop/sweden-api-study/`
- `sources/coop/sweden-api-prototype/`

Output should classify each artifact as:
- reusable in `coop`
- example-specific
- reference only
- obsolete
