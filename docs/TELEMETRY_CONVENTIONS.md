# Telemetry Conventions

This file establishes rules now and will be expanded when M2 implements concrete telemetry instruments.

## Rules

- Prefer existing OpenTelemetry semantic conventions.
- Project-specific names use the `lpp.` prefix.
- Duration units must be explicit.
- Monetary values must identify currency.
- Estimated values must be semantically distinguishable from actual observed values.
- Raw prompt/response/PII/secret content is excluded by default.
- Metric dimensions must be bounded/low-cardinality.
- Do not use per-prompt cache hashes as metric labels.

## Traces vs metrics

Use traces for per-request diagnostic structure and metrics for aggregate operational behavior.

Normal span timestamps already encode span duration. Do not duplicate span duration as an `lpp.*` attribute unless the custom value represents a distinct operation.
