# Parallax — executive summary

## The policy problem

Policymakers may ask an AI system strategic questions for which no objective
answer key exists. A benchmark cannot simply mark “reassure,” “escalate,” or
“wait” as correct. Yet the advice can still be tested for an observable
property: does the system's stated assessment move when decision-relevant
evidence changes, while remaining stable when only irrelevant wording changes?

Parallax is a public evaluation project built around that narrower question.
It measures an ordered three-category assessment—`LEANS_NOT_H`, `UNRESOLVED`,
or `LEANS_H`—and records refusal separately. Technical, transport, and
classification unavailability remain visible rather than being silently
converted into an answer.

## The research story

Experiment 1 was a 210-call live two-provider study across three synthetic
strategic scenarios. It returned **`NOT_SUPPORTED`** under its frozen rule.
Relevant evidence moved three complete units, but a nuisance paraphrase also
moved one. Fifty-three calls were refusals, 28 of 48 matched units were
complete, and the project did not rescue the result after seeing it.

Experiment 2 was a larger live successor, not merely offline qualification. It
resolved all 888 planned coordinates, but only 66 of 288 matched triples were
fully valid. The exact accepted result was **`INSUFFICIENT_EVIDENCE`** for both
provider arms. Its separate offline qualification established engineering
custody and replay, not scientific support.

Experiment 3 rebuilt the measurement architecture around five ordered evidence
doses, refusal-aware common denominators, and conservative joint partial
identification. Before any full provider study, the implementation was attacked
with 12 known-ground-truth synthetic worlds—6,674,400 scheduled evaluations,
all matching independent oracle dispositions—and a 4,800-row local Qwen2.5
surrogate campaign.

## What the local Qwen2.5 study found

The local campaign produced 4,544 valid ordinal responses and 256 invalid enum
responses; every invalid enum occurred in a 14B stratum. The 7B profile was
strongly `LEANS_H`-dominated, while 14B was predominantly `UNRESOLVED`. Dose
movement was not uniformly monotone. Seventeen of 60 blinded nuisance
pair-by-stratum comparisons were nonzero. A predeclared shallow-cue diagnostic
was concordant for 2,519 of 4,800 scheduled outputs (52.48%).

These are descriptive local-model observations. They are not Anthropic/Google
results, not causal capacity effects, not claims about Chinese models in
general, and not evidence of hidden belief or mechanism. Qwen2.5's role is
substantive but bounded: an Alibaba-origin open-weight family made it practical
to stress the instrument with real model output before an expensive provider
campaign.

## What remains

Six live Anthropic/Google calls qualified current production transport paths
only; no scientific Parallax prompt was sent. The full reference study remains
unexecuted: two providers, 30 cells per provider, `N=9270` per cell, 278,100
calls per provider, 556,200 total scheduled calls, and `M=210` simultaneous
scalar supports at global `alpha=.05`. No full-joint power claim is made.
Funding is not secured and account capacity is unverified.

## Why it is worth commissioning

The story is not “an AI benchmark worked.” It is how to make high-stakes,
answer-key-free evaluation genuinely falsifiable: preserve the first failure,
separate science from transport qualification, use open local models to expose
pathology cheaply, and publish the evidence and limits before asking readers to
trust a result. The proposed ChinaTalk project combines a reported essay with
an interactive evidence explorer.

```text
PUBLICATION = LIVE
CONTEST_SUBMISSION = NOT_PERFORMED
SCIENTIFIC_PROVIDER_RESULT = NONE
NEXT_BOUNDARY = FINAL_AUG23_SUBMISSION_REVIEW
```
