# PURPOSE
Define the path from this documentation study to a future standalone product.

# SCOPE
Included:
- Logical implementation phases
- Boundary between study and future product
- Maintenance model assumptions

Excluded:
- UI design
- Infrastructure vendor selection

# STRUCTURE
## Phase 1: Study and contracts
Deliverables:
- source model
- taxonomy
- ranking model
- canonical schemas
- playbooks for source evaluation and classification

Exit criteria:
- no unresolved core definitions
- schemas are stable enough for implementation

## Phase 2: Ingestion prototype
Deliverables:
- source fetcher for official metadata surfaces
- parser and normalizer to `ApiRecord`
- validation reports

Exit criteria:
- representative official source data can be converted into canonical records

## Phase 3: Search index and query API
Deliverables:
- index generation from canonical records
- filterable query interface
- transparent score breakdown

Exit criteria:
- core query scenarios from `06_user_queries.md` work predictably

## Phase 4: Search UI
Deliverables:
- builder-facing search interface
- result cards with docs/access confidence
- filter sets driven by taxonomy

## Phase 5: Expansion
Possible additions:
- direct agency enrichment
- municipality and region coverage
- Nordic or EU expansion
- usage analytics and feedback loops

# CONTRACTS
Input:
- All study outputs

Output:
- Sequenced implementation roadmap

Schemas:
- all contracts in `docs/contracts/`

# RULES
Allowed:
- Change technical stack later
- Add source breadth later

Forbidden:
- Starting with UI before canonical record and ranking semantics are stable

# EXAMPLES
The first product code should start at ingestion and normalization, not at frontend mockups.

# NOTES
This path keeps the official Swedish metadata model intact while allowing a sharper search product to emerge from it.
