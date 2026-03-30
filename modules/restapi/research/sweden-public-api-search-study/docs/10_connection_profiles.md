# PURPOSE
Define the connection-first method used to study APIs before freezing universal structure.

# SCOPE
Included:
- connection variation dimensions
- browser versus standalone app implications
- recurring patterns worth generalizing

Excluded:
- frontend implementation details
- SDK design

# STRUCTURE
## Why connection profiles come first
If the project tries to define a universal API model before enough real sources have been studied, the result will be too abstract to be useful or too narrow to generalize.

The safer method is:
1. study how sources are actually reached
2. capture recurring access and operational patterns
3. extract the stable universal layer after that

## Core dimensions to capture
- discovery surface
  - portal, developer docs, OpenAPI page, metadata API, dump, partner onboarding page
- transport
  - HTTP/HTTPS, webhook, streaming, file dump
- client mode
  - browser-direct, server-only, mixed
- auth scheme
  - none, API key, OAuth, certificate, organization onboarding, session-based, unclear
- environment model
  - production only, sandbox plus production, test-only, unknown
- versioning model
  - URL versioning, header versioning, no explicit versioning, unknown
- pagination model
  - offset, cursor, page number, none, unknown
- rate-limit model
  - published, inferred, hidden, unknown

## Browser versus standalone app
The right default is not "browser or standalone app." It is:
- connectors run server-side by default
- browser-direct access is allowed only when the source is genuinely safe and practical for it

Reasons:
- CORS may block browser access
- API keys should not be exposed client-side
- partner APIs usually require server-side auth handling
- rate limiting and retry behavior belong in the connector layer

## Recurring patterns likely to come back
- open public read APIs
- metadata portals with separate access URLs
- partner APIs with test and production environments
- APIs with weak metadata but strong practical utility
- bulk export surfaces that behave like APIs for ingestion purposes

Those patterns should become reusable connection archetypes later.

# CONTRACTS
Input:
- source documentation
- developer portal docs
- onboarding instructions

Output:
- `ConnectionProfile`
- `CapabilityProfile`

Schemas:
- `contracts/connection_profile.schema.json`
- `contracts/capability_profile.schema.json`

# RULES
Allowed:
- infer likely client mode from official docs and auth model

Forbidden:
- assume browser access is acceptable just because a source is public

# EXAMPLES
Arbetsförmedlingen open data:
- likely `client_mode=mixed`
- `auth_scheme=none` for some read access

Skatteverket partner-oriented APIs:
- likely `client_mode=server_only`
- `requires_org_approval=true`

# NOTES
This document is the bridge between Sweden v1 and the later universal API handler vision.
