# Architecture

## High-level model

```text
Application
    |
    v
PolicyProfiler
    |
    +-- PrivacyPolicy adapter
    +-- CachePolicy adapter
    +-- SecurityPolicy adapter
    +-- Provider adapter
    |
    v
OpenTelemetry traces + metrics
    |
    v
OTLP / Prometheus / observability backend
```

## Planned package boundaries

```text
src/llm_policy_profiler/
├── profiler.py
├── types.py
├── exceptions.py
├── telemetry/
├── policies/
├── integrations/
├── evaluation/
├── detection/
└── cli/
```

The core profiler knows contracts, timing, execution outcomes, and telemetry. It must not contain Presidio-, LiteLLM-, or cache-backend-specific logic.

## Layering

1. Core contracts and timing.
2. OpenTelemetry instrumentation.
3. Privacy-safe telemetry policy.
4. Optional adapters.
5. Evaluation/benchmark features.
6. CLI/demo surfaces.

Higher layers may depend on lower layers. Lower layers must not import higher-level/vendor integrations.
