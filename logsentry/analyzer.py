"""Parse and summarize exported event data without network access."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALIASES = {
    "event_id": ("event_id", "eventid", "id", "event code"),
    "timestamp": ("timestamp", "timecreated", "time_created", "time", "date"),
    "provider": ("provider", "providername", "source", "sourcename"),
    "level": ("level", "leveldisplayname", "severity", "type"),
    "message": ("message", "description", "message_text"),
    "computer": ("computer", "computername", "host", "hostname"),
}


def _flatten_event(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError("Each event must be a JSON object.")
    # Support the common Windows Event XML-to-JSON wrapper shape.
    if "Event" in item and isinstance(item["Event"], dict):
        item = item["Event"]
    result: dict[str, Any] = {}
    for canonical, candidates in ALIASES.items():
        for key, value in item.items():
            normalized_key = str(key).replace("@", "").replace("_", "").replace(" ", "").lower()
            if normalized_key in {c.replace("_", "").replace(" ", "").lower() for c in candidates}:
                if isinstance(value, dict) and "#text" in value:
                    value = value["#text"]
                result[canonical] = value
                break
    if "event_id" not in result:
        # A frequent XML conversion uses System.EventID.
        system = item.get("System")
        if isinstance(system, dict):
            event_id = system.get("EventID")
            if isinstance(event_id, dict):
                event_id = event_id.get("#text")
            if event_id is not None:
                result["event_id"] = event_id
    if "timestamp" not in result:
        system = item.get("System")
        if isinstance(system, dict):
            created = system.get("TimeCreated")
            if isinstance(created, dict):
                result["timestamp"] = created.get("@SystemTime") or created.get("SystemTime")
    return result


def parse_events(path: str | Path) -> list[dict[str, Any]]:
    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ValueError(f"Cannot read input file: {exc}") from exc
    if not text.strip():
        raise ValueError("Input file is empty.")

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        rows = list(csv.DictReader(text.splitlines()))
        if not rows:
            raise ValueError("CSV must contain a header row and at least one event.")
        return [_flatten_event(row) for row in rows]
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON input: {exc.msg}") from exc
    if isinstance(raw, dict):
        raw = raw.get("Events", raw.get("events", [raw]))
    if not isinstance(raw, list):
        raise ValueError("JSON must be an event object or a list of event objects.")
    return [_flatten_event(item) for item in raw]


def _parse_datetime(value: Any) -> datetime | None:
    if value is None or not str(value).strip():
        return None
    raw = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def filter_events(
    events: list[dict[str, Any]],
    event_id: str | None = None,
    level: str | None = None,
    provider: str | None = None,
    since: str | None = None,
) -> list[dict[str, Any]]:
    cutoff = _parse_datetime(since) if since else None
    if since and cutoff is None:
        raise ValueError("The --since value must be an ISO-8601 timestamp.")
    filtered = []
    for event in events:
        if event_id and str(event.get("event_id", "")).strip() != str(event_id):
            continue
        if level and str(event.get("level", "")).lower() != level.lower():
            continue
        if provider and provider.lower() not in str(event.get("provider", "")).lower():
            continue
        if cutoff:
            event_time = _parse_datetime(event.get("timestamp"))
            if event_time is None or event_time < cutoff:
                continue
        filtered.append(event)
    return filtered


def summarize(events: list[dict[str, Any]]) -> dict[str, Any]:
    levels = Counter(str(event.get("level") or "Unknown") for event in events)
    ids = Counter(str(event.get("event_id") or "Unknown") for event in events)
    providers = Counter(str(event.get("provider") or "Unknown") for event in events)
    return {
        "tool": "LogSentry",
        "version": "0.1.0",
        "scope": "Only imported local data; no Windows event subscription or network activity.",
        "total_events": len(events),
        "levels": dict(sorted(levels.items())),
        "top_event_ids": [{"event_id": key, "count": count} for key, count in ids.most_common(10)],
        "top_providers": [{"provider": key, "count": count} for key, count in providers.most_common(10)],
        "events": events,
        "limitations": [
            "Event severity and identifiers require environment-specific interpretation.",
            "This report is a triage aid, not proof of compromise or a forensic conclusion.",
        ],
    }
