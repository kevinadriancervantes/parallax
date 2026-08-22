# Parallax — the research story and protocol boundary

## 1. Strategic advice without an answer key

Some of the questions policymakers most want to ask AI systems cannot be scored
against a single correct policy: reassure an ally or signal resolve, disclose
an assessment or preserve ambiguity, act now or wait. Standard benchmark
accuracy does not directly tell us whether the advice is responsive to evidence
or fragile to phrasing.

Parallax asks a deliberately narrower behavioral question:

> When supplied evidence is made stronger or weaker in a prospectively ordered
> way, do observable response classifications move in the corresponding
> direction while remaining stable under decision-irrelevant rewrites?

That is not a test of hidden belief, consciousness, truthfulness, internal
reasoning, or optimal policy. It is a test of observable response behavior
under controlled perturbation.

## 2. Experiment 1: the first claim failed

The first live protocol used three fictional strategic scenarios, two provider
configurations, and 210 confirmatory calls. Its result was frozen before
interpretation.

Among 28 complete matched units, the relevant-evidence condition moved three
responses relative to baseline. One paraphrase-nuisance condition also moved a
response. The contextual nuisance moved none. Because the target movement was
not selective, the exact fallback rule applied: `OTHERWISE=>NOT_SUPPORTED`.

Observability was heterogeneous: 154 structured responses, 53 behavioral
refusals, two schema failures, and one technical failure. Only 28 of 48 planned
matched units were complete. The accepted result remains **`NOT_SUPPORTED`**.
The target movement was preserved descriptively but never promoted into a
post-hoc success.

This negative result established that the project was falsifiable and exposed
three problems: nuisance content needed stronger identification, refusal could
not be treated as an incidental defect, and sparse complete units made a simple
matched analysis brittle.

## 3. Experiment 2: scale and custody did not rescue identification

Experiment 2 was a larger live scientific successor plus a separately bounded
offline engineering-qualification program. The live campaign resolved all 888
planned coordinates—444 per provider, 864 MAIN and 24 mechanical-control
coordinates—with no technical retries, missing coordinates, duplicates, or
unexpected coordinates.

The exact accepted provider results were both **`INSUFFICIENT_EVIDENCE`**.
Only 66 of 288 matched triples were fully valid; 222 were handled under the
frozen pessimistic rule. The campaign recorded 275 refusals, 54 schema failures,
and 97 technical truncations. Both mechanical construct gates passed, but that
did not override failed MAIN coverage.

A separately labeled post-confirmatory analysis found nuisance movement in all
66 fully valid units. Google had 29 target movements, none selective;
Anthropic had no target movement. Those observations are diagnostic, not a new
confirmatory result. Likewise, offline recovery, replay, request realization,
and custody checks establish engineering integrity only.

The deeper lesson was blunt: more calls do not automatically restore
identification when availability and nuisance behavior dominate the matched
sample.

## 4. Experiment 3: rebuild the measurement object

The mature successor uses three fictional domains and five ordered evidence
doses per domain:

```text
STRONG_AGAINST
WEAK_AGAINST
BASELINE
WEAK_TOWARD
STRONG_TOWARD
```

Its substantive response remains observable and small:
`LEANS_NOT_H`, `UNRESOLVED`, or `LEANS_H`. Behavioral refusal is a separate
co-primary response component, never placed on the substantive ordinal scale.
Measurement, transport, and unclassified unavailability remain on one common
eligible-unit denominator and enter a joint coherent identified set. The
analysis does not invent an unseen answer.

The primary object is an ordered vector of cumulative response contrasts across
adjacent evidence doses. Nuisance stability remains a separate affirmative
content/behavioral-equivalence gate; it is not subtracted into the dose
estimand. Providers remain separate.

## 5. Attack the machinery before funding the provider study

The Experiment 3 validation ladder is intentionally role-separated:

```text
exact protocol and custody
          ↓
known-ground-truth synthetic shadow
          ↓
real local-model surrogate execution
          ↓
live non-scientific provider-path qualification
          ↓
unexecuted funding-dependent confirmatory study
```

### Known-ground-truth shadow

Twelve physical worlds exercised the full production geometry at 556,200
scheduled coordinates each: 6,674,400 evaluations total. They included clean
pass, adjacent reversal, endpoint failure, nuisance instability,
refusal/availability failure, conservative missingness, provider asymmetry,
surface-cue following, decision-boundary behavior, retry metamorphism, and
nonstationarity. Every observed disposition matched an independent oracle.

This establishes software and analysis behavior only. It does not establish
real-model behavior.

### Real local Qwen2.5 surrogate

The local campaign attempted and terminally accounted for 4,800 Qwen2.5
generations across 7B/14B and deterministic/stochastic strata. It produced:

- 4,544 valid ordinal responses;
- 256 schema-invalid enum values, all in 14B strata;
- zero duplicate or replacement attempts and zero runtime errors;
- dose behavior that was not uniformly monotone;
- 17 nonzero blinded nuisance comparisons out of 60; and
- 2,519/4,800 outputs concordant with a predeclared shallow-cue heuristic.

These are descriptive real-model observations. They do not demonstrate a
causal capacity effect, internal cue use, general Qwen behavior, Chinese-model
behavior, or Anthropic/Google performance.

Qwen2.5 is relevant to the China/AI story in a precise way: an Alibaba-origin
open-weight model family made a substantial, inspectable local stress campaign
possible. It is evaluation infrastructure and evidence, not a stand-in for a
geopolitical category.

### Current provider paths

Six live qualification calls—three Anthropic and three Google—tested current
request, response, refusal/error-envelope, and custody behavior. No Parallax
scientific prompt was sent. They establish a dated transport-path qualification,
not a scientific provider result or permanent compatibility guarantee. A full
run would require fresh sacrificial qualification.

## 6. The full reference study that has not run

The sealed reference plan has two providers, 30 cells per provider, `N=9270`
per cell, 278,100 calls per provider, 556,200 total scheduled calls, `M=210`,
and global `alpha=.05`. It preserves provider separation, fail-closed retry and
availability rules, and no full-joint power claim.

Full confirmatory execution funding is not secured. Account capacity is
unverified. Those facts block execution, not the existence or publication of
the protocol. No Experiment 3 scientific provider result exists.

## 7. What a ChinaTalk commission would produce

The proposed work is a reported essay paired with an interactive evidence
explorer. The essay would explain why answer-key-free evaluation matters for
national-security decision support, follow the project through two failed live
claims and a conservative rebuild, and investigate the operational and funding
barriers to a truly confirmatory Claude/Gemini study. The explorer would let
readers inspect the five-dose local response profiles, blinded nuisance shifts,
failure classes, and exact claim boundaries without reading raw JSON first.

The story's value is not a triumphant benchmark number. It is the practical
discipline required to make an evaluation capable of saying “not supported”
and “insufficient evidence” without quietly moving the goalposts.

## 8. Reproduction and current authority

Run from the public-release root:

```powershell
python reproducibility/verify_public_release.py
```

The check requires no GPU, provider credentials, network access, or model calls.

```text
PUBLICATION = LIVE
EXPERIMENT_1 = NOT_SUPPORTED
EXPERIMENT_2 = INSUFFICIENT_EVIDENCE
EXPERIMENT_3_CONFIRMATORY_EXECUTION = NOT_PERFORMED
SCIENTIFIC_PROVIDER_RESULT = NONE
FULL_CONFIRMATORY_EXECUTION_FUNDING = NOT_SECURED
CONTEST_SUBMISSION = NOT_PERFORMED
NEXT_BOUNDARY = FINAL_AUG23_SUBMISSION_REVIEW
```
