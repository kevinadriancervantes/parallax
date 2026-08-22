# Parallax

## Can a model follow ordered evidence?

Parallax asks whether a model's observable assessment moves coherently as
evidence becomes stronger or weaker, remains stable under blinded nuisance
rewrites, and fails conservatively when a response is refused or unavailable.
This is a behavioral measurement question—not a claim about hidden belief,
truthfulness, consciousness, or internal mechanism.

## Why it matters

Strategic-policy AI evaluations need to distinguish a useful evidence-sensitive
response from a fluent but unstable answer. Parallax makes direction, nuisance
stability, refusal, missingness, custody, and transport failure visible in the
evaluation contract.

## How it works

The instrument freezes five ordered evidence doses, three observable
substantive response states, a separate refusal component, blinded nuisance
pairs, provider-separated analysis, fail-closed retry/transport rules, and a
common-denominator treatment of technical unavailability. The full design is
described in the [contest narrative](../contest-narrative.md).

## What has actually been validated

- The known-ground-truth synthetic shadow covered 12 worlds and 6,674,400
  scheduled coordinate evaluations with matching independent oracle decisions.
- The real local-model exercise attempted 4,800 Qwen2.5 generations and
  exposed 256 schema-invalid responses, non-monotone dose profiles, nuisance
  instability, and a 52.48% shallow-cue diagnostic concordance.
- Six live Anthropic/Google calls qualified production transport paths only.
  No scientific Parallax prompt was sent.

## What Parallax does not claim

The local result is descriptive. The provider qualification is non-scientific.
There is no scientific provider result, no confirmatory result, no full-joint
power claim, and no inference about hidden belief revision or internal model
mechanism.

## Confirmatory plan and status

The reference plan has two providers, 30 cells per provider, `N=9270` per
cell, 278,100 calls per provider, 556,200 scheduled calls, and `M=210`.
Execution is not performed and funding is not secured.

## Reproduce and inspect

From the public-release root:

```powershell
python reproducibility/verify_public_release.py
```

Review the [executive summary](../executive-summary.md), [evidence](../evidence),
[claim matrix](../governance/claim-evidence-matrix.csv), [GitHub repository](https://github.com/kevinadriancervantes/parallax), and [submission draft](../submission/form-draft.md).

## Deployment status

`PENDING_PUBLIC_DEPLOYMENT`
