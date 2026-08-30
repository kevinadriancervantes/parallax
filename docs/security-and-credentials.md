# Future execution security and credentials

## Current status

The current public Parallax release does not execute independent campaigns and
does not need evaluator credentials. This document describes controls required
before a future reusable execution kit could be considered safe enough for
publication.

Parallax should never receive or store third-party API credentials through the
public microsite.

The intended future execution model is:

```text
LOCAL CLI OR LOCAL RUNNER
→ evaluator-controlled local adapter
→ evaluator-controlled provider or endpoint
```

Credentials should come from evaluator-local environment variables, operating
system credential mechanisms, or provider SDK credential chains as
appropriate. A future public runner must not operate as a hosted credential
proxy.

## Never persist

Campaign evidence, logs, manifests, receipts, and error messages must never
persist:

- API keys;
- bearer tokens;
- authorization headers;
- private certificates;
- unnecessary private endpoint secrets;
- unrelated host, account, or local-model inventory.

## Required future safety controls

Any future implementation requires, at minimum:

- secret-pattern scanning and deterministic credential-exclusion tests;
- header allowlisting and authorization-header redaction before persistence;
- bounded raw-response capture;
- content-type and byte-count recording;
- fail-closed handling for oversized, binary, malformed, or unknown responses;
- treating model output as inert evidence, never executable instructions;
- no shell interpolation of model, endpoint, or response text;
- explicit adapter identity and content hash;
- no automatic scientific retry;
- model and revision identity verification where available;
- exact call-count and cost-risk preflight;
- disk-space preflight based on the configured response ceiling;
- explicit local execution authorization with no implicit provider default.

An arbitrary adapter remains trusted local code. A subprocess protocol does
not eliminate malicious-adapter, endpoint, filesystem, or network risk.

## Expensive execution guard

Before issuing any future scientific request, the runner should display:

```text
provider and endpoint identity
exact model and revision, if available
campaign identity class
qualification state
scheduled scientific call count
maximum attempt and retry policy
token envelope and cost risk, if known
estimated evidence storage requirement
```

Execution should require an explicit, campaign-specific local authorization.
No scientific run should begin from an ambiguous default command.

These safeguards are requirements for a future implementation. None is
implemented by this documentation successor.

