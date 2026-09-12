# LLM Policy Profiler

> OpenTelemetry-native profiling for the cost, latency, quality, privacy, and security impact of LLM middleware policies.

LLM Policy Profiler (LPP) is an early-stage open-source Python framework for measuring what privacy filters, semantic caches, guardrails, and provider middleware actually cost—and what they save.

## Status

Pre-alpha. The public API is not stable yet.

## What LPP measures

- middleware latency and failures,
- cache HIT/MISS behavior,
- actual versus estimated LLM cost,
- semantic-cache quality trade-offs,
- privacy/security policy overhead,
- shadow-evaluation quality,
- cache-stampede behavior,
- p50/p95/p99 application overhead.

## What LPP is not

LPP is not a new LLM gateway, PII detector, cache backend, prompt-injection classifier, or observability backend. Those systems are integrated through adapters.

## Core principles

1. Privacy-safe by default.
2. OpenTelemetry-native.
3. Optional adapter architecture.
4. Actual and estimated values are clearly separated.
5. Deterministic tests.
6. Low-cardinality telemetry.
7. Reproducible benchmark claims.
8. Small, reviewable pull requests.

## Development

```bash
uv sync --all-groups
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest
uv run bandit -r src
uv run pip-audit
uv build
```

Read `docs/PROJECT_SPEC.md` and `CONTRIBUTING.md` before implementing an issue.
