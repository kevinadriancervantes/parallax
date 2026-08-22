# Contest package hardening report V1

## Disposition

`PRE_SUBMISSION_HARDENING_PASS_WITH_QUALIFICATIONS`

The sealed contest baseline was preserved byte-for-byte. This additive
successor applies only clarification, claim restriction, reproducibility,
privacy, verifier, and editorial hardening. No accepted scientific result,
protocol parameter, provider qualification outcome, or confirmatory status was
changed.

## Local editorial review

Two already-installed local Qwen2.5 models reviewed the public package as
adversarial editors. They returned editorial PASS judgments. Their output is
not scientific evidence. A Windows terminal-control encoding/redraw issue in
the first parser was repaired locally; raw redraw output remains outside the
public payload, and the normalized findings are recorded in
`local-review/local-review-normalized.json`.

The only findings were low-severity clarity issues: make the provider
qualification temporal, distinguish statistical implementation from funded
execution, and repeat the descriptive-local boundary in reproduction prose.
All three were repaired additively.

## Deterministic hardening

- Added a failure/refusal/schema/API-error terminology table.
- Added a dated provider qualification boundary.
- Added exact cost arithmetic from preserved token counts.
- Added explicit local-model substrate and call accounting.
- Added a deterministic successor verifier and contradiction audit.
- Kept all raw provider and local generation evidence outside the public
  successor payload.
- Preserved the full `M=210`, `N=9270`, 556,200-call design as design-only.

## Call accounting

```text
external_provider_calls = 0
external_model_calls = 0
local_model_calls = 2
confirmatory_calls = 0
```

## Remaining qualification

The local editorial reviewer is not a scientific adjudicator. Its runner was
repaired to request canonical JSON, suppress terminal word wrapping and
thinking display, and use explicit UTF-8 subprocess decoding. The successor
is ready for exactly one independent hardening adjudication and not for
submission, deployment, provider execution, or confirmatory execution.

## Final public-release editorial QA

The exact clean release copy was reviewed for first-page judge comprehension,
claim ceiling, provider-qualification versus scientific-execution boundaries,
funding visibility, privacy wording, and reproduction usability. The bounded
local editorial invocation produced no usable output before its local timeout;
it was stopped without retry and was not treated as scientific evidence. The
deterministic/manual review found no new claim or release defect. The stale
predecessor command and status language were repaired in this successor, and
the clean public tree contains no raw local editorial files.
