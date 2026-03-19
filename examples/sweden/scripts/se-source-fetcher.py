#!/usr/bin/env python3
"""
se-source-fetcher.py — Fetch API records from the Swedish national data portal.

Source: admin.dataportal.se (Digg DCAT-AP-SE catalog)
Endpoint: https://admin.dataportal.se/catalog/apis (SPARQL or REST depending on availability)

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

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------

DIGG_BASE = "https://admin.dataportal.se"
CATALOG_API = f"{DIGG_BASE}/catalog"

# SPARQL endpoint for the official linked data portal
SPARQL_ENDPOINT = "https://sparql.dataportal.se/sparql"

# REST-style search (used as primary — simpler to parse)
SEARCH_API = f"{DIGG_BASE}/search"

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
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_sparql(query: str) -> dict:
    params = {"query": query, "format": "application/sparql-results+json"}
    req = urllib.request.Request(
        f"{SPARQL_ENDPOINT}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

# ------------------------------------------------------------------
# Fetch strategies
# ------------------------------------------------------------------

def fetch_via_rest(limit: int, offset: int, filter_type: str) -> list:
    """
    Try the dataportal search REST API.
    Returns list of raw result dicts.
    """
    params = {
        "q": "",
        "limit": limit if limit > 0 else 100,
        "offset": offset,
        "esType": "esterms:ServedByDataService" if filter_type == "api" else "",
    }
    # Remove empty params
    params = {k: v for k, v in params.items() if v != ""}

    data = get_json(f"{DIGG_BASE}/search", params)
    hits = data.get("hits", {}).get("hits", []) or data.get("results", []) or []
    return hits


def fetch_via_sparql(limit: int, offset: int) -> list:
    """
    Fallback: SPARQL query for DataService entries (APIs).
    Returns list of raw result dicts.
    """
    query = f"""
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

    SELECT ?service ?title ?description ?publisher ?landingPage ?endpointURL
    WHERE {{
        ?service a dcat:DataService .
        OPTIONAL {{ ?service dcterms:title ?title . FILTER(LANG(?title) = "sv" || LANG(?title) = "") }}
        OPTIONAL {{ ?service dcterms:description ?description . FILTER(LANG(?description) = "sv" || LANG(?description) = "") }}
        OPTIONAL {{ ?service dcterms:publisher ?publisher }}
        OPTIONAL {{ ?service dcat:landingPage ?landingPage }}
        OPTIONAL {{ ?service dcat:endpointURL ?endpointURL }}
    }}
    LIMIT {limit if limit > 0 else 100}
    OFFSET {offset}
    """
    result = get_sparql(query)
    return result.get("results", {}).get("bindings", [])


# ------------------------------------------------------------------
# Normalize raw hits to SourceRecord shape
# ------------------------------------------------------------------

def normalize_rest_hit(hit: dict) -> dict:
    """Map a REST search hit to a partial SourceRecord."""
    src = hit.get("_source", hit)
    return {
        "_raw_type": "rest",
        "source_id": src.get("id") or src.get("identifier") or "",
        "title": src.get("title") or src.get("name") or "",
        "description": src.get("description") or "",
        "publisher": src.get("publisher", {}).get("name") if isinstance(src.get("publisher"), dict) else src.get("publisher") or "",
        "source_url": src.get("url") or src.get("landingPage") or "",
        "access_url": src.get("endpointURL") or src.get("accessURL") or "",
        "themes": src.get("theme") or src.get("themes") or [],
        "license": src.get("license") or "",
        "format": src.get("format") or [],
        "modified": src.get("modified") or src.get("issued") or "",
        "_trust_tier": "tier_2",
        "_source_system": "dataportal.se",
        "_fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def normalize_sparql_binding(b: dict) -> dict:
    """Map a SPARQL binding to a partial SourceRecord."""
    def val(key):
        return b.get(key, {}).get("value", "") if key in b else ""

    return {
        "_raw_type": "sparql",
        "source_id": val("service"),
        "title": val("title"),
        "description": val("description"),
        "publisher": val("publisher"),
        "source_url": val("landingPage"),
        "access_url": val("endpointURL"),
        "themes": [],
        "license": "",
        "format": [],
        "modified": "",
        "_trust_tier": "tier_2",
        "_source_system": "sparql.dataportal.se",
        "_fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


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
    filter_type = inp.get("filter_type", "api")

    emit("start", agent="se-source-fetcher", title="Sweden API Source Fetcher")
    emit_output(f"Fetching from dataportal.se (limit={limit}, offset={offset}, filter={filter_type})")

    records = []
    strategy = "unknown"

    # Strategy 1: REST search API
    try:
        emit_output("Trying REST search API...")
        hits = fetch_via_rest(limit, offset, filter_type)
        records = [normalize_rest_hit(h) for h in hits]
        strategy = "rest"
        emit_output(f"REST: got {len(records)} records")
    except Exception as e:
        emit_output(f"REST failed ({e}), falling back to SPARQL...")

        # Strategy 2: SPARQL
        try:
            bindings = fetch_via_sparql(limit, offset)
            records = [normalize_sparql_binding(b) for b in bindings]
            strategy = "sparql"
            emit_output(f"SPARQL: got {len(records)} records")
        except Exception as e2:
            emit_error(f"Both fetch strategies failed. REST: skipped. SPARQL: {e2}")
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
