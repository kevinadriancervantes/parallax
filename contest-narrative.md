# Parallax — contest-facing narrative

## 1. The question

Can a model’s observable assessment move coherently as supplied evidence is
made stronger or weaker, while remaining stable under nuisance rewrites and
failing conservatively when the requested assessment is refused or unavailable?

This is a behavioral measurement question. It is not a claim about hidden
belief, consciousness, truthfulness, or mechanism.

## 2. Why existing evaluations are not enough

Many evaluations inspect a single answer, a preference, or a benchmark score.
Those designs can miss directionality, nuisance sensitivity, schema failure,
provider asymmetry, and the difference between an answer and an unavailable
observation. Parallax makes those failure modes part of the contract.

## 3. What Parallax measures

For each frozen scenario, Parallax presents five ordered evidence doses from
`STRONG_AGAINST` through `STRONG_TOWARD`. The substantive response has three
observable categories: `LEANS_NOT_H`, `UNRESOLVED`, and `LEANS_H`. Refusal is a
separate co-primary observable component and is not placed on the substantive
ordinal scale.

The central empirical object is:

> observable directional response behavior under ordered evidence perturbations
> while surviving blinded nuisance transformations, refusal/unavailability
> accounting, and conservative partial-identification treatment.

## 4. Experimental design

The reference corpus uses three fictional domains, five doses per domain, and
15 exact A/B nuisance pairs. Providers are analyzed separately. The renderer,
provider-visible request construction, response extraction, retry state
machine, and analysis identities are prospectively bound.

## 5. Conservative missing and refused responses

Behavioral refusal is not technical missingness. Parser, schema, truncation,
safety, custody, and transport failures remain unavailable observations on the
common denominator and are handled through a joint coherent identified set.
The analysis does not invent an unseen substantive response.

## 6. Statistical contract

The reference contract preserves `M=210`, `N=9270` per cell, global
`alpha=.05`, provider separation, no pooling, no majority rescue, and no full
joint power claim. The four adjacent dose contrasts must meet the predeclared
directional rule, endpoint movement must clear its bound, nuisance components
must remain within their bound, and refusal support must remain bounded.

## 7. Adversarial validation ladder

```text
scientific contract / protocol
              ↓
adversarial falsification
              ↓
full-scale known-ground-truth synthetic shadow
              ↓
real local-model surrogate execution
              ↓
live Anthropic / Google path qualification
              ↓
funding-dependent confirmatory execution
```

Each layer validates a different risk. None is allowed to impersonate the
next layer.

## 8. Full-scale synthetic shadow study

The shadow study ran 12 known-ground-truth worlds across the full production
geometry: 6,674,400 scheduled coordinate evaluations. It tested boundary
behavior, partial identification, retry metamorphism, provider asymmetry,
Route-B nonstationarity, and the surface-cue limitation. Every independent
oracle disposition matched the observed disposition. It establishes software
and analysis behavior, not real-model behavior.

## 9. Real local-model surrogate study

The local study ran 4,800 Qwen2.5 generations across 7B/14B and deterministic/
stochastic strata. It is a real-model exercise of the instrument and parser,
not a provider study. It found 256 schema-invalid enum outputs, non-monotone
dose profiles, nuisance instability, and a 52.48% all-scheduled surface-cue
concordance. The result is descriptive only.

## 10. Live Anthropic / Google path qualification

The six live calls were qualification-only. Anthropic qualified structured
Messages handling and a native refusal path. Google qualified the current
Interactions `steps/model_output` success path and current error envelope. No
scientific Parallax prompt was used; no model result was inferred.

This is a dated interface qualification, not a permanent provider guarantee.
The observed paths, models, request schemas, and evidence packet are bound to
the qualification context recorded on 2026-08-22. Future confirmatory use
requires fresh sacrificial qualification.

## 11. What the evidence shows

The strongest current claim is methodological: the instrument, custody rules,
analysis machinery, full-scale synthetic geometry, local stress execution, and
current production transport paths have been exercised and documented with
fail-closed boundaries.

## 12. What the evidence does not show

It does not show that Claude or Gemini passed Parallax scientifically. It does
not establish belief updating, truth tracking, reasoning mechanism, deception
resistance, or a causal effect of parameter count. It does not establish a
confirmatory result or 95% full-claim joint power.

## 13. Full confirmatory execution plan

The unchanged reference plan has two providers, 30 cells per provider,
`N=9270` per cell, 278,100 calls/provider, 556,200 total scheduled calls, and
`M=210`. Funding and account capacity remain prerequisites for execution, not
for existence of the protocol or its validation evidence.

## 14. Reproduce and inspect

From this public-release directory, run:

`python reproducibility/verify_public_release.py`

It checks this release identity, predecessor receipts, constants, compact
evidence, local counts, shadow status, provider qualification boundary, cost
arithmetic, privacy, links, and claim firewalls without a GPU, provider
credentials, network access, or model calls.

## 15. Funding and execution status

```text
CONFIRMATORY EXECUTION = NOT PERFORMED
FUNDING = NOT SECURED
SCIENTIFIC PROVIDER RESULT = NONE
CONTEST_PACKAGE_HARDENING = INDEPENDENTLY ACCEPTED
PUBLIC_RELEASE_CANDIDATE = SEALED
NEXT_BOUNDARY = PUBLIC_DEPLOYMENT_AND_SUBMISSION_AUTHORIZATION
```
