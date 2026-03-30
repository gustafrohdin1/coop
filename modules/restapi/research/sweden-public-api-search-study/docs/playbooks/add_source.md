# PURPOSE
Add a new trusted source to the study without changing core semantics.

# SCOPE
Included:
- Source registration
- Documentation updates
- Contract alignment

Excluded:
- Crawl or scraper implementation

# STRUCTURE
1. Create or update the `SourceRecord`.
2. Place the source in the trust hierarchy.
3. Document its fetch mode, format, and update cadence.
4. State whether it is in v1 scope or deferred.
5. Note any taxonomy or normalization implications.
6. Verify no existing definition needs reinterpretation.

# CONTRACTS
Input:
- New source details

Output:
- Updated source landscape
- Updated contracts only if absolutely necessary

# RULES
Allowed:
- Extend the source inventory

Forbidden:
- Quietly broadening v1 scope from Sweden official sources to arbitrary federation

# EXAMPLES
Adding a new official aggregated catalog connected to Sveriges dataportal should update the source landscape, not redefine the entire discovery model.
