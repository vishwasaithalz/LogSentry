"""Command-line interface for LogSentry."""

import argparse
import json
import sys

from .analyzer import filter_events, parse_events, summarize


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="logsentry",
        description="Analyze an exported JSON or CSV event file locally. No network access is used.",
    )
    parser.add_argument("file", help="Path to exported JSON or CSV event data")
    parser.add_argument("--event-id", help="Keep only this event ID")
    parser.add_argument("--level", help="Filter by level, e.g. Warning or Error")
    parser.add_argument("--provider", help="Case-insensitive provider substring")
    parser.add_argument("--since", help="ISO-8601 timestamp lower bound")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    try:
        events = parse_events(args.file)
        events = filter_events(events, args.event_id, args.level, args.provider, args.since)
        report = summarize(events)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(report, indent=2, default=str))
        return 0

    print("LOGSENTRY | LOCAL EVENT REVIEW")
    print("=" * 36)
    print(f"Events analysed: {report['total_events']}")
    print(f"Levels: {report['levels'] or 'No matching events'}")
    print("Top event IDs:")
    for item in report["top_event_ids"]:
        print(f"  {item['event_id']}: {item['count']}")
    print("Top providers:")
    for item in report["top_providers"]:
        print(f"  {item['provider']}: {item['count']}")
    print()
    print("Triage aid only. Validate findings in the original system context.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
