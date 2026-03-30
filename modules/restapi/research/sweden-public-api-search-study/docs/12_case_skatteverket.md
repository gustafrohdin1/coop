# PURPOSE
Capture Skatteverket as a reference source profile for controlled public-sector API connection patterns.

# SCOPE
Included:
- why the source matters
- likely connection pattern
- implications for universal modeling

Excluded:
- full access-process documentation

# STRUCTURE
## Why this case matters
Skatteverket is valuable because it represents the other end of the spectrum:
- high-value public-sector data and services
- stronger onboarding and access constraints
- more explicit separation between test and production

## Likely connection profile
- discovery surface: official developer and collaboration pages
- client mode: server_only
- auth scheme: controlled and possibly organization-tied
- environment model: test and production separation
- result shape: integration-oriented entity and validation responses

## What this teaches the universal model
- universal orchestration must handle sources that are publicly discoverable but not publicly invokable
- connection modeling must include onboarding friction, environment separation, and restricted auth
- browser-direct assumptions fail quickly outside open-data cases

# CONTRACTS
Input:
- official Skatteverket API and collaboration docs

Output:
- one reference `SourceRecord`
- one reference `ConnectionProfile`
- one reference `CapabilityProfile`

# RULES
Allowed:
- use this case as the baseline for controlled partner-like API behavior

Forbidden:
- treating documentation visibility as equivalent to open access

# EXAMPLES
This case should influence `server_only`, `requires_org_approval=true`, and sandbox-aware connection archetypes.
