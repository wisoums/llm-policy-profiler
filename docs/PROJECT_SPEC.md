# Project Specification

## Mission

LLM Policy Profiler (LPP) measures the cost, latency, quality, privacy, and security impact introduced by middleware policies around LLM applications.

It should answer questions such as:

- How much latency does PII anonymization add?
- How often does a semantic cache HIT or MISS?
- What cost/latency savings from caching are observed versus estimated?
- How often are semantic cache hits actually equivalent?
- What threshold gives the best measured quality/savings trade-off for a specific benchmark configuration?
- Does shadow evaluation add foreground latency?
- Are overlapping misses creating a cache stampede?
- Does telemetry itself leak sensitive data?
- What is LPP's p50/p95/p99 overhead under concurrency?

## Non-goals

LPP does not replace:
- LiteLLM or another LLM gateway,
- Presidio or another PII engine,
- semantic-cache backends,
- prompt-injection/security classifiers,
- OpenTelemetry collectors/backends,
- Grafana/Datadog/Langfuse/Phoenix.

LPP measures and compares the impact of those components through adapters.

## Core invariants

### Privacy-safe by default
No raw prompt, response, PII, credential, API key, secret, or customer data may be emitted into telemetry by default.

### OpenTelemetry-native
Use established OpenTelemetry semantic conventions where appropriate. Use project-specific `lpp.*` names only for concepts not represented by standard conventions.

### Adapter architecture
Heavy/vendor-specific dependencies must remain optional. Importing the core package must not require Presidio, LiteLLM, FAISS, Torch, etc.

### Actual vs estimated
Observed facts and modeled estimates must use distinct names/types. A cache hit can produce an estimated avoided cost, but a provider call that did not happen cannot be represented as an observed call.

### Deterministic tests
Timing logic must use injectable clocks. Unit tests must not rely on arbitrary wall-clock sleeps.

### Low cardinality
Metric dimensions must remain bounded. Raw prompts, response text, cache keys, request hashes, arbitrary user IDs, and tenant values must not become unbounded metric labels.

### Quality first
Semantic-cache usefulness must be evaluated against ground truth and/or shadow evaluation, not embedding similarity alone.
