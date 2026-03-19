#!/usr/bin/env python3
"""
se-normalizer.py — Normalize raw SourceRecords into canonical ApiRecords.

Reads JSON data events from stdin (piped from se-source-fetcher)
or from AGENT_INPUT source_file path.

Emits one data event per ApiRecord conforming to api_record.schema.json.

Environment:
    AGENT_INPUT — JSON string with: source_file, strict
"""

import json
import os
import sys
import time
import re

# ------------------------------------------------------------------
# Event helpers
# ------------------------------------------------------------------

def emit(event_type: str, **kwargs):
    payload = {"event": event_type, "agent": "se-normalizer", **kwargs}
    print(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()

def emit_data(record: dict):
    emit("data", **record)

def emit_output(line: str):
    emit("output", line=line)

def emit_error(msg: str):
    emit("error", msg=msg)

# ------------------------------------------------------------------
# Domain tag inference
# ------------------------------------------------------------------

DOMAIN_KEYWORDS = {
    "transport":      ["transport", "trafik", "kollektivtrafik", "buss", "tåg", "flyg", "väg", "transit"],
    "geospatial":     ["geo", "kart", "map", "lantmäteri", "koordinat", "gis", "spatial"],
    "health":         ["hälsa", "vård", "sjukhus", "läkemedel", "folkhälsa", "region", "healthcare"],
    "education":      ["utbildning", "skola", "universitet", "högskola", "education"],
    "environment":    ["miljö", "klimat", "luft", "vatten", "natur", "environment"],
    "economy":        ["ekonomi", "finans", "scb", "statistik", "budget", "ekonomisk"],
    "business":       ["företag", "bolag", "bolagsverket", "org", "business", "handelsregister"],
    "demographics":   ["befolkning", "folkbokföring", "skatteverket", "person", "demographics"],
    "justice":        ["domstol", "rättsväsende", "brottsregister", "polis", "justice"],
    "culture":        ["kultur", "museum", "bibliotek", "arkiv", "kulturarv", "culture"],
    "research":       ["forskning", "slu", "research", "universitet", "vetenskap"],
    "utilities":      ["el", "vatten", "energi", "elhandel", "utilities"],
}

def infer_domain_tags(title: str, description: str, themes: list) -> list:
    text = f"{title} {description} {' '.join(str(t) for t in themes)}".lower()
    tags = []
    for tag, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    return tags if tags else ["unknown"]


# ------------------------------------------------------------------
# Access model inference
# ------------------------------------------------------------------

def infer_access_model(raw: dict) -> str:
    access_url = raw.get("access_url", "")
    description = (raw.get("description") or "").lower()
    if not access_url:
        return "unclear"
    if any(w in description for w in ["api-nyckel", "api key", "registrer", "login", "autentisering"]):
        return "open_api_key"
    if any(w in description for w in ["oauth", "organization", "avtal", "godkänn", "partner"]):
        return "authenticated_public"
    if any(w in description for w in ["restricted", "begränsad", "ej öppen", "intern"]):
        return "restricted"
    return "open_no_auth"


# ------------------------------------------------------------------
# Interface type inference
# ------------------------------------------------------------------

def infer_interface_type(raw: dict) -> str:
    formats = [str(f).lower() for f in (raw.get("format") or [])]
    url = (raw.get("access_url") or "").lower()
    description = (raw.get("description") or "").lower()
    text = f"{url} {description} {' '.join(formats)}"

    if "graphql" in text:   return "graphql"
    if "sparql" in text:    return "sparql"
    if "soap" in text:      return "soap"
    if "odata" in text:     return "odata"
    if "rest" in text or "json" in text or "api" in text:
        return "rest"
    if any(f in formats for f in ["csv", "xlsx", "xml", "rdf"]):
        return "file_download_only"
    return "unknown"


# ------------------------------------------------------------------
# API confidence
# ------------------------------------------------------------------

def infer_api_confidence(raw: dict, interface_type: str) -> str:
    has_access_url = bool(raw.get("access_url"))
    has_description = len(raw.get("description") or "") > 30

    if interface_type in ("rest", "graphql", "sparql") and has_access_url:
        return "confirmed_api"
    if interface_type in ("rest", "graphql") or has_access_url:
        return "probable_api"
    if interface_type == "file_download_only":
        return "not_api"
    return "ambiguous_service"


# ------------------------------------------------------------------
# Metadata completeness (0.0 – 1.0)
# ------------------------------------------------------------------

def compute_metadata_completeness(raw: dict, api_record: dict) -> float:
    checks = [
        bool(api_record.get("title")),
        len(api_record.get("description") or "") > 30,
        bool(api_record.get("provider")),
        bool(api_record.get("documentation_url") or api_record.get("access_url")),
        bool(api_record.get("domain_tags") and api_record["domain_tags"] != ["unknown"]),
        bool(api_record.get("license")),
        bool(api_record.get("update_frequency") and api_record["update_frequency"] != "unknown"),
        api_record.get("api_confidence") in ("confirmed_api", "probable_api"),
    ]
    return round(sum(checks) / len(checks), 2)


# ------------------------------------------------------------------
# Build ApiRecord
# ------------------------------------------------------------------

def build_api_record(raw: dict) -> dict:
    source_id = raw.get("source_id") or ""
    title = (raw.get("title") or "").strip()
    description = (raw.get("description") or "").strip()
    publisher = raw.get("publisher") or ""
    if isinstance(publisher, dict):
        publisher = publisher.get("name") or ""

    domain_tags = infer_domain_tags(title, description, raw.get("themes") or [])
    interface_type = infer_interface_type(raw)
    access_model = infer_access_model(raw)
    api_confidence = infer_api_confidence(raw, interface_type)

    # Generate a stable record ID
    clean_id = re.sub(r'[^a-z0-9]', '-', (source_id or title).lower())[:64].strip('-')
    record_id = f"se-{clean_id}" if clean_id else f"se-unknown-{int(time.time())}"

    record = {
        "record_id": record_id,
        "title": title,
        "aliases": [],
        "provider": publisher,
        "provider_type": "state_agency",
        "source_portal": "dataportal.se",
        "source_url": raw.get("source_url") or "",
        "documentation_url": raw.get("source_url") or None,
        "access_url": raw.get("access_url") or None,
        "description": description,
        "domain_tags": domain_tags,
        "geography": "se",
        "auth_model": access_model,
        "interface_type": interface_type,
        "distribution_formats": raw.get("format") or [],
        "update_frequency": "unknown",
        "license": raw.get("license") or "",
        "api_confidence": api_confidence,
        "documentation_quality_notes": "",
        "search_keywords": [],
        "source_trust_tier": raw.get("_trust_tier") or "tier_2",
        "provenance": {
            "source_id": raw.get("_source_system") or "dataportal.se",
            "fetched_from": raw.get("source_url") or "",
            "raw_identifier": source_id,
            "raw_format": "dcat-ap-se",
            "last_seen_at": raw.get("_fetched_at") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    }

    record["metadata_completeness"] = compute_metadata_completeness(raw, record)
    return record


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    raw_input = os.environ.get("AGENT_INPUT", "{}")
    try:
        inp = json.loads(raw_input)
    except json.JSONDecodeError:
        inp = {}

    strict = inp.get("strict", False)
    source_file = inp.get("source_file")

    emit("start", agent="se-normalizer", title="Sweden API Normalizer")

    # Collect raw SourceRecord dicts
    raw_records = []

    if source_file:
        emit_output(f"Reading from file: {source_file}")
        try:
            with open(source_file) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                        if ev.get("event") == "data":
                            raw_records.append({k: v for k, v in ev.items()
                                               if k not in ("event", "agent", "timestamp")})
                    except json.JSONDecodeError:
                        pass
        except OSError as e:
            emit_error(f"Cannot open source_file: {e}")
            emit("exit", code=1)
            return 1
    else:
        emit_output("Reading data events from stdin...")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                if ev.get("event") == "data":
                    raw_records.append({k: v for k, v in ev.items()
                                       if k not in ("event", "agent", "timestamp")})
            except json.JSONDecodeError:
                pass

    emit_output(f"Normalizing {len(raw_records)} raw records...")

    normalized = 0
    skipped = 0

    for raw in raw_records:
        try:
            record = build_api_record(raw)

            if strict and not record.get("title"):
                emit_output(f"SKIP (strict): missing title for {raw.get('source_id', '?')}")
                skipped += 1
                continue

            emit_data(record)
            normalized += 1

        except Exception as e:
            msg = f"Normalization error for {raw.get('source_id', '?')}: {e}"
            if strict:
                emit_error(msg)
                emit("exit", code=1)
                return 1
            else:
                emit_output(f"WARN: {msg}")
                skipped += 1

    emit_output(f"Done. normalized={normalized} skipped={skipped}")
    emit("exit", code=0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
