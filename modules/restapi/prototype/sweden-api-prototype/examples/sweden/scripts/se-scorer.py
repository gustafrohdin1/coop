#!/usr/bin/env python3
"""
se-scorer.py — Score ApiRecords using the three-factor model from the study.

Scoring dimensions (from 05_ranking_and_scoring.md):
  discovery_relevance     55% — how likely to satisfy user intent
  implementation_readiness 30% — usable right now?
  metadata_completeness   15% — how rich is the metadata?

Emits {api_record, score_breakdown} data event per record.

Environment:
    AGENT_INPUT — JSON string with: query, source_file
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
    payload = {"event": event_type, "agent": "se-scorer", **kwargs}
    print(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()

def emit_data(record: dict):
    emit("data", **record)

def emit_output(line: str):
    emit("output", line=line)

# ------------------------------------------------------------------
# Scoring
# ------------------------------------------------------------------

SCORE_VERSION = "v1.0"

# Weights
W_DISCOVERY    = 0.55
W_READINESS    = 0.30
W_COMPLETENESS = 0.15

# Confidence multipliers for discovery relevance
CONFIDENCE_MULTIPLIER = {
    "confirmed_api":    1.0,
    "probable_api":     0.75,
    "ambiguous_service": 0.4,
    "not_api":          0.1,
}

# Access model multipliers for discovery relevance
ACCESS_MULTIPLIER = {
    "open_no_auth":        1.0,
    "open_api_key":        0.85,
    "authenticated_public": 0.6,
    "restricted":          0.3,
    "unclear":             0.4,
}


def text_match_score(query: str, record: dict) -> float:
    """Simple text relevance: term overlap between query and record text fields."""
    if not query:
        return 0.5  # neutral when no query

    terms = set(re.sub(r'[^\w\s]', '', query.lower()).split())
    if not terms:
        return 0.5

    text = " ".join([
        record.get("title") or "",
        record.get("description") or "",
        " ".join(record.get("domain_tags") or []),
        " ".join(record.get("search_keywords") or []),
        record.get("provider") or "",
    ]).lower()

    matched = sum(1 for t in terms if t in text)
    return min(matched / len(terms), 1.0)


def score_discovery_relevance(record: dict, query: str) -> tuple:
    """Returns (score, penalties)."""
    penalties = []

    text_score = text_match_score(query, record)

    conf = record.get("api_confidence", "ambiguous_service")
    conf_mult = CONFIDENCE_MULTIPLIER.get(conf, 0.4)

    access = record.get("auth_model", "unclear")
    access_mult = ACCESS_MULTIPLIER.get(access, 0.4)

    base = text_score * conf_mult * access_mult

    if conf == "ambiguous_service":
        penalties.append({"code": "ambiguous_api", "weight": -0.1,
                          "reason": "api_confidence is ambiguous_service"})
    if conf == "not_api":
        penalties.append({"code": "not_api", "weight": -0.3,
                          "reason": "Record classified as not_api"})

    return round(min(base, 1.0), 3), penalties


def score_implementation_readiness(record: dict) -> tuple:
    """Returns (score, penalties)."""
    penalties = []
    score = 0.0

    # Direct access URL (0.35)
    if record.get("access_url"):
        score += 0.35
    else:
        penalties.append({"code": "no_access_url", "weight": -0.2,
                          "reason": "No direct access URL"})

    # Documentation (0.30)
    if record.get("documentation_url"):
        score += 0.30
    else:
        penalties.append({"code": "no_docs", "weight": -0.15,
                          "reason": "No documentation URL"})

    # Clear auth model (0.20)
    if record.get("auth_model") not in ("unclear", None):
        score += 0.20
    else:
        penalties.append({"code": "unclear_auth", "weight": -0.1,
                          "reason": "Auth model is unclear"})

    # Clear interface type (0.15)
    if record.get("interface_type") not in ("unknown", None):
        score += 0.15
    else:
        penalties.append({"code": "unknown_interface", "weight": -0.05,
                          "reason": "Interface type unknown"})

    return round(min(score, 1.0), 3), penalties


def score_metadata_completeness(record: dict) -> tuple:
    """Returns (score, penalties)."""
    penalties = []

    # Use pre-computed completeness if available
    base = record.get("metadata_completeness", 0.0)

    description = record.get("description") or ""
    if len(description) < 30:
        penalties.append({"code": "generic_description", "weight": -0.1,
                          "reason": "Description too short or generic"})
        base = max(0.0, base - 0.1)

    return round(min(base, 1.0), 3), penalties


def compute_score(record: dict, query: str) -> dict:
    dr_score, dr_penalties = score_discovery_relevance(record, query)
    ir_score, ir_penalties = score_implementation_readiness(record)
    mc_score, mc_penalties = score_metadata_completeness(record)

    all_penalties = dr_penalties + ir_penalties + mc_penalties
    penalty_total = sum(p["weight"] for p in all_penalties)

    raw_total = (dr_score * W_DISCOVERY +
                 ir_score * W_READINESS +
                 mc_score * W_COMPLETENESS)

    total = round(max(0.0, min(raw_total + penalty_total, 1.0)), 3)

    return {
        "discovery_relevance": dr_score,
        "implementation_readiness": ir_score,
        "metadata_completeness": mc_score,
        "penalties": all_penalties,
        "total_score": total,
        "score_version": SCORE_VERSION,
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

    query       = inp.get("query", "")
    source_file = inp.get("source_file")

    emit("start", agent="se-scorer", title="Sweden API Scorer")
    if query:
        emit_output(f"Scoring against query: '{query}'")

    # Collect ApiRecords
    api_records = []

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
                        if ev.get("event") == "data" and "record_id" in ev:
                            api_records.append({k: v for k, v in ev.items()
                                               if k not in ("event", "agent", "timestamp")})
                    except json.JSONDecodeError:
                        pass
        except OSError as e:
            emit("error", msg=f"Cannot open source_file: {e}")
            emit("exit", code=1)
            return 1
    else:
        emit_output("Reading ApiRecord data events from stdin...")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                if ev.get("event") == "data" and "record_id" in ev:
                    api_records.append({k: v for k, v in ev.items()
                                       if k not in ("event", "agent", "timestamp")})
            except json.JSONDecodeError:
                pass

    emit_output(f"Scoring {len(api_records)} records...")

    scored = []
    for record in api_records:
        score_breakdown = compute_score(record, query)
        scored.append((record, score_breakdown))

    # Sort by total score descending
    scored.sort(key=lambda x: x[1]["total_score"], reverse=True)

    for record, score_breakdown in scored:
        emit_data({"api_record": record, "score_breakdown": score_breakdown})

    emit_output(f"Done. {len(scored)} records scored and ranked.")
    emit("exit", code=0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
