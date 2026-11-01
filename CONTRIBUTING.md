# Contributing

## Requirements

Python 3.10+. The current project uses only the standard library.

## Run tests

    py -3 -m unittest discover -s tests -v

## Guidelines

- Keep file parsing local and deterministic.
- Add tests for every supported input shape and filter.
- Never add real Windows event exports to the repository.
- Do not add automatic collection, elevation, command execution, or telemetry without a separate security review.
- Document false-positive and interpretation limitations.

## Pull request checklist

- [ ] Tests pass.
- [ ] New behavior has tests.
- [ ] Samples contain synthetic data only.
- [ ] Privacy and scope documentation remains accurate.
