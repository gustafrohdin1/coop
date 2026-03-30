# PURPOSE
Apply the study's taxonomy and scoring inputs to a single normalized record.

# SCOPE
Included:
- API confidence
- Taxonomy assignment
- Scoring inputs

Excluded:
- Query-time ranking

# STRUCTURE
1. Check whether the record exposes evidence of a real service interface.
2. Assign `api_confidence`.
3. Assign domain tags conservatively.
4. Determine access model.
5. Determine interface type and distribution formats separately.
6. Mark metadata completeness.
7. Note documentation quality issues.
8. Preserve provenance and ambiguity.

# CONTRACTS
Input:
- Raw metadata
- `SourceRecord`

Output:
- `ApiRecord`

# RULES
Allowed:
- Use `unknown` and `unclear` when evidence is weak

Forbidden:
- Marking file-download-only records as confirmed APIs

# EXAMPLES
If a record has a clear docs page and a JSON endpoint:
- `api_confidence=confirmed_api`
- `interface_type=rest`
- `distribution_formats=["json"]`
