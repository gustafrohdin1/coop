# PURPOSE
Harvest a new source family in a way that directly feeds framework design.

# SCOPE
Included:
- source-family classification
- connection analysis
- handler fit
- normalized-shape pressure

Excluded:
- implementation code

# STRUCTURE
1. Identify the source family.
   - social
   - news
   - weather
   - food
   - public sector
   - process/terminal
   - streaming
   - file-based
   - other

2. Record the representative source.
   - name
   - official docs URL
   - entrypoint URL

3. Capture connection shape.
   - client mode
   - auth scheme
   - transport
   - pagination model
   - rate-limit model
   - environment model

4. Capture capability shape.
   - search
   - list
   - detail lookup
   - stream/listen
   - bulk export
   - write support

5. Capture response-shape pressure.
   - object catalog
   - time-series metrics
   - text feed
   - event stream
   - mixed

6. Decide handler fit.
   - reuses existing handler family
   - extends existing family
   - requires new family

7. Record what the source teaches the framework.
   - what repeats
   - what breaks
   - what must become a reusable contract

## Harvest template
```md
# Source Family Harvest

- Family:
- Representative source:
- Official docs:
- Entrypoint:

## Connection
- Client mode:
- Auth:
- Transport:
- Pagination:
- Rate limits:
- Environment:

## Capabilities
- Search:
- List:
- Detail lookup:
- Stream/listen:
- Bulk export:
- Write:

## Response Shape
- Primary shape:
- Freshness model:
- Normalization difficulty:
- Visualization fit:

## Handler Decision
- Existing family:
- New family needed:
- Why:

## Framework Lessons
- Repeating patterns:
- Missing contracts:
- Risks:
```

# CONTRACTS
Input:
- representative source docs
- sample response descriptions

Output:
- repeatable source-family evaluation artifact

# RULES
Allowed:
- use a single representative source to probe a broader family initially

Forbidden:
- invent a new handler family before checking whether an existing one already fits

# EXAMPLES
RSS should likely reuse a feed/listener family unless a specific feed source introduces fundamentally new runtime behavior.
