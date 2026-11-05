"""Command-line interface for LogSentry."""

import argparse
import json
import sys
from pathlib import Path

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
    parser.add_argument("--output", help="Write the report to this path instead of stdout")
    args = parser.parse_args()

    try:
        events = parse_events(args.file)
        events = filter_events(events, args.event_id, args.level, args.provider, args.since)
        report = summarize(events)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        output = json.dumps(report, indent=2, default=str) + "\n"
    else:
        lines = [
            "LOGSENTRY | LOCAL EVENT REVIEW",
            "=" * 36,
            f"Events analysed: {report['total_events']}",
            f"Levels: {report['levels'] or 'No matching events'}",
            "Top event IDs:",
        ]
        lines.extend(f"  {item['event_id']}: {item['count']}" for item in report["top_event_ids"])
        lines.append("Top providers:")
        lines.extend(f"  {item['provider']}: {item['count']}" for item in report["top_providers"])
        lines.extend(["", "Triage aid only. Validate findings in the original system context."])
        output = "\n".join(lines) + "\n"

    if args.output:
        try:
            destination = Path(args.output).expanduser()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(output, encoding="utf-8")
        except OSError as exc:
            print(f"error: could not write report: {exc}", file=sys.stderr)
            return 2
        print(f"Report written to: {destination}")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
