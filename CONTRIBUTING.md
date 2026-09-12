# Contributing

Thank you for contributing to LLM Policy Profiler.

## Before coding

1. Pick an existing GitHub Issue or open a focused proposal.
2. Read:
   - `docs/PROJECT_SPEC.md`
   - `docs/ARCHITECTURE.md`
   - `docs/ENGINEERING_GUIDE.md`
   - `docs/TELEMETRY_CONVENTIONS.md`
   - `docs/PRIVACY_MODEL.md`
3. Create a focused branch.
4. Keep the change within the issue scope.

## Setup

```bash
uv sync --all-groups
uv run pre-commit install
```

## Required checks

```bash
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest
uv run bandit -r src
uv run pip-audit
uv build
```

## Pull requests

- Link the issue with `Closes #...`.
- Explain what changed and why.
- Include test evidence.
- Call out telemetry/privacy implications.
- Update docs for public API or architectural changes.
- Keep unrelated refactors out of the PR.

## Privacy invariant

Prompt, response, PII, secret, credential, and customer data must never be exported through telemetry by default.
