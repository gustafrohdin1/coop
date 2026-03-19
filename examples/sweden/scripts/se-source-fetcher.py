#!/usr/bin/env python3
"""
se-source-fetcher.py — Fetch API records from the Swedish national data portal.

Source: admin.dataportal.se (EntryStore / DCAT-AP-SE catalog)
Primary endpoint: https://admin.dataportal.se/store/search (EntryStore REST)
Fallback: https://sparql.dataportal.se/sparql (SPARQL)

Emits one JSON data event per record to stdout.
Conforms to coop event contract: start → data* → exit.

Environment:
    AGENT_INPUT — JSON string with:
        limit         int   max records to return (default 20; 0 = unlimited corpus mode)
        offset        int   pagination offset (default 0)
        corpus_mode   bool  if true, paginate with *:* for full coverage (default false)
        query         str   search terms passed to EntryStore in search mode (default "*:*")
        filter_type   str   reserved for future use
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import re

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------

ENTRYSTORE_BASE  = "https://admin.dataportal.se/store"
SPARQL_ENDPOINT  = "https://sparql.dataportal.se/sparql"

# Wildcard query that retrieves all entries regardless of keyword;
# EntryStore Solr rejects short queries but accepts Lucene wildcard *:*
ENTRYSTORE_WILDCARD = "*:*"
PAGE_SIZE = 100   # EntryStore maximum per request

# RDF namespaces
DCTERMS = "http://purl.org/dc/terms/"
DCAT    = "http://www.w3.org/ns/dcat#"
FOAF    = "http://xmlns.com/foaf/0.1/"
RDF     = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

USER_AGENT = "coop-se-source-fetcher/0.1 (+https://github.com/coop)"

# ------------------------------------------------------------------
# Event helpers
# ------------------------------------------------------------------

def emit(event_type: str, **kwargs):
    payload = {"event": event_type, "agent": "se-source-fetcher", **kwargs}
    print(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()

def emit_data(record: dict):
    emit("data", **record)

def emit_output(line: str):
    emit("output", line=line)

def emit_error(msg: str):
    emit("error", msg=msg)

# ------------------------------------------------------------------
# HTTP helpers
# ------------------------------------------------------------------

def get_json(url: str, params: dict = None) -> dict:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_sparql(query: str) -> dict:
    params = {"query": query, "format": "application/sparql-results+json"}
    req = urllib.request.Request(
        f"{SPARQL_ENDPOINT}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

# ------------------------------------------------------------------
# Publisher name resolution
# ------------------------------------------------------------------

_publisher_cache = {}

def resolve_publisher_name(pub_uri: str) -> str:
    """Resolve a publisher URI to a human-readable name.

    Two cases:
      - Internal EntryStore ref  https://admin.dataportal.se/store/{ctx}/resource/{id}
        → fetch /store/{ctx}/metadata/{id} and extract foaf:name
      - Org ID URI  http://dataportal.se/organisation/SE2021XXXXXX
        → return the org ID itself as a fallback identifier
    """
    if not pub_uri:
        return ""
    if pub_uri in _publisher_cache:
        return _publisher_cache[pub_uri]

    name = ""

    # Internal EntryStore resource ref
    m = re.match(
        r"https://admin\.dataportal\.se/store/(\w+)/resource/([a-f0-9]+)$",
        pub_uri
    )
    if m:
        ctx_id, res_id = m.group(1), m.group(2)
        try:
            meta_url = f"{ENTRYSTORE_BASE}/{ctx_id}/metadata/{res_id}"
            data = get_json(meta_url)
            for uri, props in data.items():
                foaf_name = props.get(FOAF + "name", [])
                if foaf_name:
                    name = foaf_name[0].get("value", "")
                    break
        except Exception:
            pass

    # External org URI — extract org number as fallback
    if not name:
        m2 = re.search(r"/organisation/([^/]+)$", pub_uri)
        if m2:
            name = m2.group(1)

    _publisher_cache[pub_uri] = name
    return name

# ------------------------------------------------------------------
# EntryStore metadata helpers
# ------------------------------------------------------------------

def _rdf_val(props: dict, predicate: str, lang: str = "sv") -> str:
    vals = props.get(predicate, [])
    if not vals:
        return ""
    preferred = next((v.get("value", "") for v in vals if v.get("lang") == lang), None)
    if preferred is not None:
        return preferred
    return vals[0].get("value", "")

def _rdf_uri(props: dict, predicate: str) -> str:
    vals = props.get(predicate, [])
    return next((v.get("value", "") for v in vals if v.get("type") == "uri"), "")

def _main_subject(meta: dict) -> tuple:
    candidates = [(uri, props) for uri, props in meta.items()
                  if not uri.startswith("_:")]
    if not candidates:
        return "", {}
    return max(candidates, key=lambda x: len(x[1]))

def _is_data_service(props: dict) -> bool:
    """Check if the subject has a dcat:DataService or ServiceDistribution type."""
    types = [v.get("value", "") for v in props.get(RDF, [])]
    return any(
        t in (
            DCAT + "DataService",
            "http://entryscape.com/terms/ServiceDistribution",
        )
        for t in types
    )

# ------------------------------------------------------------------
# Strategy 1: EntryStore REST (paginated)
# ------------------------------------------------------------------

def fetch_page_entrystore(offset: int, page_size: int, query: str = ENTRYSTORE_WILDCARD) -> tuple:
    """Fetch one page. Returns (records, total_available)."""
    params = {
        "query":  query,
        "type":   "solr",
        "limit":  page_size,
        "offset": offset,
    }
    data = get_json(f"{ENTRYSTORE_BASE}/search", params)
    total = data.get("results", 0)
    children = data.get("resource", {}).get("children", [])
    records = []
    for child in children:
        rec = _normalize_entrystore_child(child)
        if rec:
            records.append(rec)
    return records, total


def fetch_via_entrystore(limit: int, offset: int, corpus_mode: bool, query: str = "") -> list:
    """
    Fetch records from EntryStore.

    corpus_mode=False: use query term for relevance-first retrieval (search path).
    corpus_mode=True:  use *:* wildcard and paginate for full corpus coverage.
    """
    es_query = ENTRYSTORE_WILDCARD if corpus_mode else (query or ENTRYSTORE_WILDCARD)
    all_records = []
    fetched     = 0
    current_off = offset

    while True:
        page_size = min(PAGE_SIZE, limit - fetched) if limit > 0 else PAGE_SIZE
        records, total = fetch_page_entrystore(current_off, page_size, es_query)

        # Strip internal flag — let normalizer/scorer handle classification
        for r in records:
            r.pop("_is_data_service", None)

        all_records.extend(records)
        fetched     += len(records)
        current_off += len(records)

        emit_output(
            f"  page offset={current_off - len(records)}: "
            f"{len(records)} records fetched "
            f"(total catalog: {total})"
        )

        if not corpus_mode:
            break
        if len(records) < PAGE_SIZE:
            break  # last page
        if limit > 0 and len(all_records) >= limit:
            break

    return all_records[:limit] if limit > 0 else all_records


def _normalize_entrystore_child(child: dict) -> dict:
    meta      = child.get("metadata", {})
    uri, props = _main_subject(meta)
    if not props:
        return None

    title = _rdf_val(props, DCTERMS + "title")
    desc  = _rdf_val(props, DCTERMS + "description")

    # When title is generic ("API") or missing, use description as title
    if not title or title.strip().upper() == "API":
        title = desc or title

    endpoint  = _rdf_uri(props, DCAT + "endpointURL") or _rdf_uri(props, DCAT + "accessURL")
    landing   = _rdf_uri(props, DCAT + "landingPage") or _rdf_uri(props, FOAF + "homepage")
    pub_uri   = _rdf_uri(props, DCTERMS + "publisher")
    license_  = _rdf_uri(props, DCTERMS + "license")
    modified  = _rdf_val(props, DCTERMS + "modified") or _rdf_val(props, DCTERMS + "issued")

    fmt_vals  = props.get(DCTERMS + "format", [])
    formats   = [v.get("value", "") for v in fmt_vals if v.get("value")]

    theme_vals = props.get(DCAT + "theme", [])
    themes    = [v.get("value", "") for v in theme_vals if v.get("value")]

    source_url = landing or (uri if uri.startswith("http") else "")

    # Resolve publisher: keep both stable ID and display name
    publisher_name = resolve_publisher_name(pub_uri)

    # Carry rdf:type info so normalizer can use it for api_confidence
    rdf_types = [v.get("value", "") for v in props.get(RDF, [])]

    return {
        "_raw_type":      "entrystore",
        "_rdf_types":     rdf_types,
        "source_id":      uri,
        "title":          title,
        "description":    desc,
        "publisher":      publisher_name or pub_uri,
        "publisher_id":   pub_uri,
        "source_url":     source_url,
        "access_url":     endpoint,
        "themes":         themes,
        "license":        license_,
        "format":         formats,
        "modified":       modified,
        "_entrystore_ctx":   child.get("contextId", ""),
        "_entrystore_entry": child.get("entryId", ""),
        "_trust_tier":    "tier_1",
        "_source_system": "admin.dataportal.se",
        "_fetched_at":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


# ------------------------------------------------------------------
# Strategy 2: SPARQL fallback
# ------------------------------------------------------------------

def fetch_via_sparql(limit: int, offset: int) -> list:
    query = f"""
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dcterms: <http://purl.org/dc/terms/>

    SELECT ?service ?title ?description ?publisher ?landingPage ?endpointURL ?license
    WHERE {{
        ?service a dcat:DataService .
        OPTIONAL {{ ?service dcterms:title ?title .
                   FILTER(LANG(?title) = "sv" || LANG(?title) = "") }}
        OPTIONAL {{ ?service dcterms:description ?description .
                   FILTER(LANG(?description) = "sv" || LANG(?description) = "") }}
        OPTIONAL {{ ?service dcterms:publisher ?publisher }}
        OPTIONAL {{ ?service dcat:landingPage ?landingPage }}
        OPTIONAL {{ ?service dcat:endpointURL ?endpointURL }}
        OPTIONAL {{ ?service dcterms:license ?license }}
    }}
    LIMIT {limit if limit > 0 else 100}
    OFFSET {offset}
    """
    result = get_sparql(query)
    bindings = result.get("results", {}).get("bindings", [])

    def val(b, key):
        return b.get(key, {}).get("value", "") if key in b else ""

    records = []
    for b in bindings:
        pub_uri = val(b, "publisher")
        records.append({
            "_raw_type":    "sparql",
            "source_id":    val(b, "service"),
            "title":        val(b, "title"),
            "description":  val(b, "description"),
            "publisher":    pub_uri,
            "publisher_id": pub_uri,
            "source_url":   val(b, "landingPage"),
            "access_url":   val(b, "endpointURL"),
            "themes":       [],
            "license":      val(b, "license"),
            "format":       [],
            "modified":     "",
            "_trust_tier":  "tier_2",
            "_source_system": "sparql.dataportal.se",
            "_fetched_at":  time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
    return records


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    raw_input = os.environ.get("AGENT_INPUT", "{}")
    try:
        inp = json.loads(raw_input)
    except json.JSONDecodeError:
        inp = {}

    limit       = int(inp.get("limit", 20))
    offset      = int(inp.get("offset", 0))
    corpus_mode = bool(inp.get("corpus_mode", False))
    query       = inp.get("query", "")

    emit("start", agent="se-source-fetcher", title="Sweden API Source Fetcher")
    mode_label = "corpus" if corpus_mode else "search"
    emit_output(f"Fetching from dataportal.se (limit={limit}, offset={offset}, mode={mode_label})")

    records  = []
    strategy = "unknown"

    # Strategy 1: EntryStore REST
    try:
        emit_output("Trying EntryStore REST API...")
        records  = fetch_via_entrystore(limit, offset, corpus_mode, query)
        strategy = "entrystore"
        emit_output(f"EntryStore: {len(records)} records (classifier will filter)")
    except Exception as e:
        emit_output(f"EntryStore failed ({e}), falling back to SPARQL...")

        # Strategy 2: SPARQL
        try:
            records  = fetch_via_sparql(limit, offset)
            strategy = "sparql"
            emit_output(f"SPARQL: got {len(records)} records")
        except Exception as e2:
            emit_error(f"Both fetch strategies failed. EntryStore: skipped. SPARQL: {e2}")
            emit("exit", code=1)
            return 1

    # Emit each record as a data event
    for i, record in enumerate(records):
        emit_data(record)
        if (i + 1) % 10 == 0:
            emit_output(f"  emitted {i + 1}/{len(records)}")

    emit_output(f"Done. {len(records)} records via {strategy}.")
    emit("exit", code=0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
