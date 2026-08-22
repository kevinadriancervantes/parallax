# Parallax — executive summary

## What is Parallax?

Parallax is a controlled evaluation instrument for a narrow question: when a
model receives a frozen hypothesis and evidence whose direction and strength
are prospectively ordered, do its observable response states move in the
corresponding direction, remain stable under carefully constructed nuisance
rewrites, and fail conservatively when a usable response is unavailable?

The response is deliberately small and observable: `LEANS_NOT_H`,
`UNRESOLVED`, or `LEANS_H`. Refusal is recorded separately; technical and
transport unavailability is not silently treated as a substantive answer.

## What is unusual about the method?

Parallax treats the evaluation as an evidence-and-custody problem, not just a
prompt benchmark. It freezes the corpus, renderer, provider paths, schedules,
retry rules, response parser, missingness bounds, and analysis family before
confirmatory execution. It separates providers instead of pooling them and
keeps unavailable mass in a common-denominator identified set.

## What has actually been executed?

- A full-scale known-ground-truth synthetic shadow study exercised 12 physical
  worlds across the full production geometry: 6,674,400 scheduled coordinate
  evaluations. Its independent oracle matched every world disposition.
- A local Qwen2.5 surrogate study executed 4,800 free-form generations across
  7B/14B capacity and deterministic/stochastic decoding strata.
- Six live, non-scientific provider-path qualification calls were completed:
  three Anthropic and three Google. No Parallax scientific prompt was sent to a
  provider.

## What did the local study reveal?

It exposed pathology instead of manufacturing a clean result: 4,544 valid
ordinal responses and 256 schema-invalid enum responses; all 256 invalid
observations occurred in 14B strata. The 7B profile was strongly
`LEANS_H`-dominated, while 14B was predominantly `UNRESOLVED`. Dose movement
was not uniformly monotone, nuisance pairs were often unstable, and a
predeclared surface-cue diagnostic had 2,519/4,800 concordant observations
(52.48%).

These are descriptive local-model observations, not Anthropic/Google results,
not causal capacity effects, and not evidence of internal belief revision.
Nuisance instability is visible in 17 of 60 compact comparison records.

## What remains to be run?

The full confirmatory reference execution remains funding-dependent: two
providers, 30 cells per provider, `N=9270` per cell, 278,100 calls per
provider, 556,200 total scheduled calls, and `M=210` simultaneous scalar
supports at global `alpha=.05`. No full-joint power claim is made.

## Why fund or use it?

Parallax makes expensive model evaluation auditable. Cheap deterministic
falsification and known-ground-truth simulation come first, then inexpensive
local-model stress, then tiny production-path qualification, and only then the
funding-dependent confirmatory study. The workflow makes failures visible and
prevents a successful-looking output from being mistaken for a validated
scientific conclusion.
