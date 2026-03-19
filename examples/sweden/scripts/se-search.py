#!/usr/bin/env python3
"""
se-search.py — End-to-end Sweden API search agent.

Orchestrates: fetch → normalize → score → filter → emit ranked SearchIndexRecords.

Environment:
    AGENT_INPUT — JSON: query (required), limit, filter_access, filter_domain
"""

import json
import os
import sys
import subprocess
import time
from pathlib import Path

# ------------------------------------------------------------------
# Event helpers
# ------------------------------------------------------------------

def emit(event_type: str, **kwargs):
    payload = {"event": event_type, "agent": "se-search", **kwargs}
    print(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()

def emit_data(record: dict):
    emit("data", **record)

def emit_output(line: str):
    emit("output", line=line)

# ------------------------------------------------------------------
# Pipeline runner — runs a Python script with AGENT_INPUT
# ------------------------------------------------------------------

SCRIPTS_DIR = Path(__file__).parent

def run_script(script_name: str, agent_input: dict) -> list:
    """Run a sibling script and collect its data events."""
    script = SCRIPTS_DIR / script_name
    env = os.environ.copy()
    env["AGENT_INPUT"] = json.dumps(agent_input)

    proc = subprocess.Popen(
        [sys.executable, str(script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    data_events = []
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
            if ev.get("event") == "data":
                data_events.append({k: v for k, v in ev.items()
                                   if k not in ("event", "agent", "timestamp")})
            elif ev.get("event") == "output":
                emit_output(f"  [{script_name}] {ev.get('line', '')}")
            elif ev.get("event") == "error":
                emit("error", msg=f"[{script_name}] {ev.get('msg', '')}")
        except json.JSONDecodeError:
            pass

    proc.wait()
    return data_events


# ------------------------------------------------------------------
# Build SearchIndexRecord
# ------------------------------------------------------------------

def to_search_index_record(scored: dict) -> dict:
    rec = scored.get("api_record", {})
    score = scored.get("score_breakdown", {})

    return {
        "record_id": rec.get("record_id", ""),
        "title": rec.get("title", ""),
        "provider": rec.get("provider", ""),
        "domain_tags": rec.get("domain_tags", []),
        "api_confidence": rec.get("api_confidence", "ambiguous_service"),
        "access_model": rec.get("auth_model", "unclear"),
        "interface_type": rec.get("interface_type", "unknown"),
        "has_docs": bool(rec.get("documentation_url")),
        "has_direct_access": bool(rec.get("access_url")),
        "search_text": f"{rec.get('title', '')} {rec.get('description', '')}".strip(),
        "filter_tokens": rec.get("domain_tags", []) + [rec.get("auth_model", "")],
        "total_score": score.get("total_score", 0.0),
        "score_breakdown": score,
    }


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    raw_input = os.environ.get("AGENT_INPUT", "{}")
    try:
        inp = json.loads(raw_input)
    except json.JSONDecodeError:
        emit("error", msg="Invalid AGENT_INPUT JSON")
        emit("exit", code=1)
        return 1

    query         = inp.get("query", "")
    limit         = int(inp.get("limit", 10))
    filter_access = inp.get("filter_access")
    filter_domain = inp.get("filter_domain")

    if not query:
        emit("error", msg="'query' is required")
        emit("exit", code=1)
        return 1

    emit("start", agent="se-search", title="Sweden API Search")
    emit_output(f"Query: '{query}'")

    # Phase 1: Fetch
    emit_output("Phase 1/3: Fetching sources...")
    raw_records = run_script("se-source-fetcher.py", {"limit": 50, "filter_type": "api"})
    emit_output(f"  {len(raw_records)} raw records fetched")

    if not raw_records:
        emit("error", msg="No records fetched — check network or source availability")
        emit("exit", code=1)
        return 1

    # Phase 2: Normalize — write raw records to a temp JSONL, pass via file
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tmp:
        for rec in raw_records:
            tmp.write(json.dumps({"event": "data", **rec}, ensure_ascii=False) + "\n")
        tmp_path = tmp.name

    emit_output("Phase 2/3: Normalizing...")
    api_records = run_script("se-normalizer.py", {"source_file": tmp_path})
    emit_output(f"  {len(api_records)} records normalized")

    # Write normalized records for scorer
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tmp2:
        for rec in api_records:
            tmp2.write(json.dumps({"event": "data", **rec}, ensure_ascii=False) + "\n")
        tmp2_path = tmp2.name

    # Phase 3: Score
    emit_output("Phase 3/3: Scoring and ranking...")
    scored_records = run_script("se-scorer.py", {"source_file": tmp2_path, "query": query})
    emit_output(f"  {len(scored_records)} records scored")

    # Build SearchIndexRecords
    results = [to_search_index_record(s) for s in scored_records]

    # Apply filters
    if filter_access:
        results = [r for r in results if r.get("access_model") == filter_access]
    if filter_domain:
        results = [r for r in results if filter_domain in (r.get("domain_tags") or [])]

    # Apply limit
    results = results[:limit]

    # Emit results
    for result in results:
        emit_data(result)

    emit_output(f"Returned {len(results)} results for '{query}'")
    emit("exit", code=0)

    # Cleanup temp files
    import os as _os
    for p in (tmp_path, tmp2_path):
        try:
            _os.unlink(p)
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
