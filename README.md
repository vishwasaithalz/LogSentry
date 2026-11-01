# LogSentry

A local-first Windows security event log analyzer for importing, filtering, and summarizing event data without sending it anywhere.

## Initial version

- Imports exported Windows Event Log data as JSON or CSV.
- Normalizes common fields such as event ID, timestamp, provider, level, and message.
- Filters events by event ID, level, provider, and time window.
- Produces a concise investigation summary.
- Includes synthetic sample data and offline tests.
- Uses only the Python standard library.

## Privacy and safety

LogSentry does not connect to Windows Event Log automatically, does not elevate privileges, and does not transmit imported data. The first version works only with files explicitly selected by the user. Use synthetic data for demonstrations and remove personal or organisational information before sharing reports.

## Requirements

- Python 3.10+
- No third-party runtime dependencies

## Quick start

    py -3 -m logsentry samples/security-events.json

JSON report:

    py -3 -m logsentry samples/security-events.json --format json

CSV input:

    py -3 -m logsentry samples/security-events.csv --format text

## Export Windows events yourself

On a Windows machine, export only the event data you are authorised to review using Event Viewer or an approved administrative process. Save the export locally, then pass the resulting JSON or CSV file to LogSentry. Export formats vary; use the included sample schema as a guide.

## Test

    py -3 -m unittest discover -s tests -v

## Current scope

This is an initial offline parser and triage helper, not an endpoint detection product, forensic suite, or automated incident-response tool. Event IDs and severity labels need interpretation in their environment and should not be treated as proof of compromise.

See SECURITY.md and CONTRIBUTING.md.
