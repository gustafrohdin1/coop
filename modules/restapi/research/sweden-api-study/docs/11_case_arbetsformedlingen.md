# PURPOSE
Capture Arbetsformedlingen as a reference source profile for open public API connection patterns.

# SCOPE
Included:
- why the source matters
- likely connection pattern
- implications for universal modeling

Excluded:
- exhaustive endpoint inventory

# STRUCTURE
## Why this case matters
Arbetsformedlingen is valuable because it combines:
- public-sector legitimacy
- explicit API and open data posture
- developer-facing discovery surfaces
- multiple data categories that builders actually care about

## Likely connection profile
- discovery surface: public portal and developer docs
- client mode: mixed, with server-side integration still preferable
- auth scheme: none or low-friction for open datasets, depending on endpoint
- environment model: public production-facing surfaces
- result shape: search/list/detail style data objects

## What this teaches the universal model
- some sources are genuinely open enough to support lighter integration
- public read APIs still benefit from a server-side connector for caching, normalization, and ranking
- open access does not remove the need for canonical response structure

# CONTRACTS
Input:
- official Arbetsformedlingen and JobTech docs

Output:
- one reference `SourceRecord`
- one reference `ConnectionProfile`
- one reference `CapabilityProfile`

# RULES
Allowed:
- use this case as the baseline for open public API behavior

Forbidden:
- assuming all public-sector APIs will be this accessible

# EXAMPLES
This case should influence the `mixed` client mode and the open-auth connection archetype.
