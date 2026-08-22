# Failure, refusal, and interpretation semantics

The public package uses these states distinctly:

| State | Meaning | Scientific interpretation |
|---|---|---|
| Successful model response | Provider returned the expected model object and a parseable response | Observable response only |
| Refusal/decline | Provider or local model declined the requested assessment under the applicable rule | Separate refusal component; never an ordinal value |
| HTTP/API error | Request received an HTTP/API-level error response | Unavailable; not a substantive assessment |
| Provider/server failure | Provider/runtime failure before a usable response | Unavailable; retry/attempt semantics remain governed by the contract |
| Malformed response | Response envelope or typed content cannot be extracted | Unavailable; no inferred answer |
| Schema failure | Extracted text is not exactly the frozen one-field enum | Unusable observation; not semantic model failure |
| Incomplete/invalid evidence | Evidence or denominator cannot support the requested analysis | Retained in the common denominator/identified-set treatment |
| Qualification failure | A path or fixture does not satisfy its predeclared transport/parser gate | Qualification disposition only; not a scientific result |
| Prohibited interpretation | Claim exceeds the accepted evidence boundary | Editorial claim-firewall violation |

Refusal is never collapsed into transport failure. Schema failure is never
called semantic model failure. Missing admissibility is never converted into a
zero effect estimate. The local lexical refusal flag is only an observable
flag; it does not infer intent or provider-native refusal semantics.

## Temporal provider boundary

The live path qualification is a dated observation of the configured
Anthropic Messages and Google Interactions paths on 2026-08-22, using the
sealed models and request schemas recorded in the qualification packet. It is
not a timeless guarantee about future provider behavior, model versions, API
schemas, pricing, or endpoints. Fresh sacrificial qualification is required
before any future confirmatory execution.
