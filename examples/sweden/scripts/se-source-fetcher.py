#!/usr/bin/env python3
"""
se-source-fetcher.py — Fetch API records from the Swedish national data portal.

Source: admin.dataportal.se (EntryStore / DCAT-AP-SE catalog)
Primary endpoint: https://admin.dataportal.se/store/search (EntryStore REST)
Fallback: https://sparql.dataportal.se/sparql (SPARQL)

Emits one JSON data event per record to stdout.
Conforms to coop event contract: start → data* → exit.

Environment:
    AGENT_INPUT  — JSON string with: limit, offset, filter_type
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

ENTRYSTORE_BASE = "https://admin.dataportal.se/store"
SPARQL_ENDPOINT = "https://sparql.dataportal.se/sparql"

# RDF namespaces
DCTERMS = "http://purl.org/dc/terms/"
DCAT    = "http://www.w3.org/ns/dcat#"
FOAF    = "http://xmlns.com/foaf/0.1/"
RDF     = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

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
# HTTP helper
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
# EntryStore metadata helpers
# ------------------------------------------------------------------

def _rdf_val(props: dict, predicate: str, lang: str = "sv") -> str:
    """Get the first literal value for a predicate, preferring the given lang."""
    vals = props.get(predicate, [])
    if not vals:
        return ""
    preferred = next((v.get("value", "") for v in vals if v.get("lang") == lang), None)
    if preferred is not None:
        return preferred
    return vals[0].get("value", "")

def _rdf_uri(props: dict, predicate: str) -> str:
    """Get the first URI value for a predicate."""
    vals = props.get(predicate, [])
    return next((v.get("value", "") for v in vals if v.get("type") == "uri"), "")

def _publisher_name(pub_uri: str) -> str:
    """Extract a human-readable publisher identifier from a publisher URI.

    E.g. http://dataportal.se/organisation/SE2021005000 → SE2021005000
         https://admin.dataportal.se/store/43/resource/abc123 → (empty, internal ref)
    """
    if not pub_uri:
        return ""
    m = re.search(r"/organisation/([^/]+)$", pub_uri)
    if m:
        return m.group(1)
    return ""


def _main_subject(meta: dict) -> tuple:
    """Return (uri, props) for the primary subject in an EntryStore metadata dict.

    Picks the subject with the most predicates that isn't a blank node.
    """
    candidates = [(uri, props) for uri, props in meta.items()
                  if not uri.startswith("_:")]
    if not candidates:
        return "", {}
    return max(candidates, key=lambda x: len(x[1]))


# ------------------------------------------------------------------
# Strategy 1: EntryStore REST
# ------------------------------------------------------------------

def fetch_via_entrystore(limit: int, offset: int) -> list:
    """
    Query the EntryStore search API for dcat:DataService entries.
    Returns list of normalized SourceRecord dicts.
    """
    params = {
        "query": "api",                  # broad term — EntryStore requires min length; "api" matches 2500+ DataServices
        "type": "solr",
        "rdfType": f"{DCAT}DataService",
        "limit": min(limit, 100),        # EntryStore caps at 100
        "offset": offset,
    }
    data = get_json(f"{ENTRYSTORE_BASE}/search", params)
    children = data.get("resource", {}).get("children", [])
    records = []
    for child in children:
        rec = _normalize_entrystore_child(child)
        if rec:
            records.append(rec)
    return records


def _normalize_entrystore_child(child: dict) -> dict:
    """Map a single EntryStore child entry to a partial SourceRecord."""
    meta = child.get("metadata", {})
    uri, props = _main_subject(meta)
    if not props:
        return None

    title = _rdf_val(props, DCTERMS + "title")
    desc  = _rdf_val(props, DCTERMS + "description")

    # Description often contains the real dataset name ("Bryggor (API)")
    # Use it as title when the title is just "API" or missing
    if not title or title.strip().upper() == "API":
        title = desc or title

    endpoint = _rdf_uri(props, DCAT + "endpointURL") or _rdf_uri(props, DCAT + "accessURL")
    landing  = _rdf_uri(props, DCAT + "landingPage") or _rdf_uri(props, FOAF + "homepage")
    pub_uri  = _rdf_uri(props, DCTERMS + "publisher")
    license_ = _rdf_uri(props, DCTERMS + "license")
    modified = _rdf_val(props, DCTERMS + "modified") or _rdf_val(props, DCTERMS + "issued")

    fmt_vals = props.get(DCTERMS + "format", [])
    formats  = [v.get("value", "") for v in fmt_vals if v.get("value")]

    theme_vals = props.get(DCAT + "theme", [])
    themes = [v.get("value", "") for v in theme_vals if v.get("value")]

    # Use the subject URI as source_id
    source_id = uri

    # Derive a source_url: prefer the landing page, else the subject URI itself
    source_url = landing or (uri if uri.startswith("http") else "")

    ctx_id   = child.get("contextId", "")
    entry_id = child.get("entryId", "")

    return {
        "_raw_type": "entrystore",
        "source_id": source_id,
        "title": title,
        "description": desc,
        "publisher": _publisher_name(pub_uri) or pub_uri,
        "source_url": source_url,
        "access_url": endpoint,
        "themes": themes,
        "license": license_,
        "format": formats,
        "modified": modified,
        "_entrystore_ctx": ctx_id,
        "_entrystore_entry": entry_id,
        "_trust_tier": "tier_1",
        "_source_system": "admin.dataportal.se",
        "_fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


# ------------------------------------------------------------------
# Strategy 2: SPARQL fallback
# ------------------------------------------------------------------

def fetch_via_sparql(limit: int, offset: int) -> list:
    """
    Fallback: SPARQL query for DataService entries.
    Returns list of normalized SourceRecord dicts.
    """
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
        records.append({
            "_raw_type": "sparql",
            "source_id": val(b, "service"),
            "title": val(b, "title"),
            "description": val(b, "description"),
            "publisher": val(b, "publisher"),
            "source_url": val(b, "landingPage"),
            "access_url": val(b, "endpointURL"),
            "themes": [],
            "license": val(b, "license"),
            "format": [],
            "modified": "",
            "_trust_tier": "tier_2",
            "_source_system": "sparql.dataportal.se",
            "_fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
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
    filter_type = inp.get("filter_type", "api")  # reserved for future use

    emit("start", agent="se-source-fetcher", title="Sweden API Source Fetcher")
    emit_output(f"Fetching from dataportal.se (limit={limit}, offset={offset})")

    records  = []
    strategy = "unknown"

    # Strategy 1: EntryStore REST
    try:
        emit_output("Trying EntryStore REST API...")
        records  = fetch_via_entrystore(limit, offset)
        strategy = "entrystore"
        emit_output(f"EntryStore: got {len(records)} records")
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
