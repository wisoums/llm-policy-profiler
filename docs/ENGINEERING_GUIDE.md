# Engineering Guide

## Normal workflow

After the one-time repository bootstrap:

1. Select one GitHub issue.
2. Move it to Ready / In Progress.
3. Create a focused branch.
4. Implement code + tests.
5. Run local quality checks.
6. Open a PR that links the issue.
7. Let CI pass.
8. Review the diff and resolve conversations.
9. Squash merge.
10. Delete the branch.

## Branch naming

Examples:
- `feature/core-profiler`
- `feature/otel-tracing`
- `test/privacy-leakage`
- `benchmark/cache-thresholds`
- `docs/telemetry-conventions`
- `fix/span-error-status`

## Commit prefixes

- `feat:`
- `fix:`
- `test:`
- `docs:`
- `refactor:`
- `perf:`
- `ci:`
- `chore:`

## Required local checks

```bash
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest
uv run bandit -r src
uv run pip-audit
uv build
```

`uv run mypy` is the single type-check command: it checks `src/` and `tests/` together under strict settings, so no separate run is needed for the test suite.

## Coding expectations

- Python 3.11+ compatibility.
- Strict type checking of source and tests.
- Intentionally small public APIs.
- Dependency injection for environment-dependent behavior.
- No hidden global OpenTelemetry mutation when an injectable provider can be used.
- Async background work must be bounded.
- Failures must remain observable without silently changing caller semantics.
