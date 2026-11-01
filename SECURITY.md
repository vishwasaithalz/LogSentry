# Security Policy

LogSentry's initial release parses files explicitly supplied by the user. It does not subscribe to Windows Event Log, request elevation, run commands, or transmit data.

- Use only logs you are authorised to inspect.
- Treat exported logs as sensitive. They may contain usernames, hostnames, IP addresses, and operational details.
- Do not commit real logs. Use synthetic examples in issues and pull requests.
- Keep analysis local and deterministic.
- Report suspected vulnerabilities privately to the repository owner where private reporting is available.
