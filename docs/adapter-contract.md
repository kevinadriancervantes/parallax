# Future transport adapter contract

## Status

This document specifies a **future, not implemented** transport boundary. The
current public release has no general-purpose adapter interface or independent
campaign runner.

The preferred architecture is:

```text
PARALLAX CORE
→ local subprocess JSONL adapter
→ evaluator-controlled model or inference framework
```

The adapter is transport-only. It is not the scientific instrument and does
not own the final response classification.

## Adapter responsibilities

A future adapter may handle:

- provider, model, revision, endpoint, and adapter identity;
- evaluator-local authentication;
- provider-native request construction;
- system and user role representation;
- exact generation and reasoning configuration;
- provider-native response capture;
- timestamps, request identifiers, usage, and native stop reasons;
- provider-defined refusal and truncation evidence;
- transport errors and declarations of unsupported capabilities.

## Prohibited behavior

A future adapter must not:

- rewrite the scientific prompt;
- change an evidence dose or nuisance assignment;
- choose or reorder the schedule;
- change an attempt number;
- repair malformed output;
- infer a convenient substantive assessment;
- convert transport failure into model behavior;
- convert unknown provider behavior into refusal without qualification;
- automatically retry a scientific row;
- replace an unavailable row;
- change analysis, thresholds, or claim boundaries.

Unsupported controls must be recorded as unsupported. They must not be
silently approximated.

## Proposed process boundary

The future core would pass one canonical JSON object per line to a locally
configured adapter process. Conceptually, the input contains:

```text
campaign identity
schedule coordinate
attempt number
immutable logical prompt bytes and hash
response schema and hash
generation requirements
provider/model configuration
```

The adapter would return one canonical JSON object per line containing:

```text
adapter/provider/model identity
exact provider request bytes and hash
request start and end timestamps
transport outcome and native status
raw response bytes and hash
provider request ID, if available
native stop or finish reason
native refusal evidence, if defined
truncation evidence
usage metadata
unsupported capability declarations
```

Binary request or response bytes should be represented through a deterministic
encoding such as base64. A future executable contract must define byte limits,
encoding, canonicalization, and version negotiation before implementation.

The adapter does **not** return `LEANS_NOT_H`, `UNRESOLVED`, `LEANS_H`, or a
final refusal/unavailability classification. The Parallax core retains strict
parsing and scientific classification, using preserved native evidence and an
adapter-specific decoder that has passed qualification.

## Trust boundary

The adapter is evaluator-controlled, trusted local executable code. A
subprocess boundary improves language and framework portability, but does not
make a malicious adapter safe.

The future design therefore permits no automatic adapter download, hosted
Parallax credential proxy, or public-web credential collection. Adapter
identity and bytes must be fixed in the campaign manifest and verified before
execution.

Every provider, model, endpoint, and adapter combination would require its own
sacrificial qualification. Similar API branding— including
“OpenAI-compatible”—does not establish compatible refusal, truncation, error,
usage, or schema behavior.

