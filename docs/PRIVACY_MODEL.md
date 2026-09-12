# Privacy Model

## Threat

Observability data can become a data-loss channel because traces, logs, attributes, exceptions, and dashboards may leave the application environment.

## Default policy

LPP must not export:
- raw prompts,
- raw responses,
- PII values,
- API keys,
- credentials,
- authorization headers,
- confidential document content,
- arbitrary customer identifiers.

Where useful, LPP may export bounded metadata such as:
- PII entity count,
- PII category,
- policy outcome,
- cache HIT/MISS,
- provider/model identifier,
- token counts,
- safe duration/cost fields.

## Testing expectation

Security/privacy tests should inject conspicuous synthetic secret/PII fixture strings and verify those exact values are absent from every telemetry surface emitted by LPP.
