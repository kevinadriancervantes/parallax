# Parallax

## Stress-testing strategic AI advice without an answer key

When a policymaker asks whether to reassure an ally, escalate, or wait, there
may be no objective label against which to score an AI answer. Parallax asks a
narrower behavioral question: **as controlled evidence moves from strongly
against to strongly toward a hypothesis, does the model's stated assessment
move too—and does it stay stable when only decision-irrelevant wording
changes?**

[Read the live research story](https://parallax.midex.app/) ·
[Executive summary](executive-summary.md) ·
[Frozen August 23 proposal](submission-aug23/proposal-final.md)

## What happened

Parallax is a three-experiment research lineage, not a single polished result:

1. **Experiment 1 — `NOT_SUPPORTED`.** The first live, two-provider protocol
   made 210 confirmatory calls across three synthetic strategic scenarios.
   Relevant evidence moved three complete units, but a nuisance paraphrase
   moved one, and refusals made observability uneven. The result failed its
   frozen rule and was not rescued post hoc.
2. **Experiment 2 — `INSUFFICIENT_EVIDENCE` for both provider arms.** The live
   successor resolved all 888 planned coordinates with stronger custody, but
   only 66 of 288 matched triples were fully valid. Offline qualification
   established replay and custody; it did not turn the campaign into a
   positive scientific result.
3. **Experiment 3 — mature protocol, provider science unexecuted.** The rebuilt
   instrument uses five evidence doses, records refusal separately, and keeps
   unavailable mass in a joint partial-identification analysis. It survived
   6,674,400 known-ground-truth synthetic checks and was stressed with 4,800
   real local Qwen2.5 generations. The full Claude/Gemini confirmatory study is
   designed but unfunded and has not run.

Detailed public records:

- [Experiment 1](experiments/experiment-1/index.html)
- [Experiment 2](experiments/experiment-2/index.html)
- [Experiment 3](experiments/experiment-3/index.html)
- [Machine-readable research lineage](governance/research-lineage.json)

## What the real local models did

The 4,800-row Qwen2.5 surrogate campaign produced 4,544 valid ordinal
responses and 256 schema-invalid enum values, all in 14B strata. Dose paths
were not uniformly monotone. Seventeen of 60 blinded nuisance pair-by-stratum
comparisons had a nonzero shift. Those are useful failures, not a pass.

![Twelve panels show local Qwen2.5 response shares over five ordered evidence doses; paths vary and are not uniformly monotone.](figures/local-model-evidence-response-profile.svg)

*Figure A. Descriptive local Qwen2.5 evidence only. This is not Claude/Gemini
evidence, a confirmatory result, a belief-revision claim, or a mechanism claim.
[Data, MATLAB source, and hashes](figures/README.md).*

![A fifteen-by-four matrix shows nuisance instability across blinded pairs and local-model strata; 17 of 60 cells are nonzero.](figures/nuisance-instability-matrix.svg)

*Figure B. Maximum A–B shift across all-scheduled response shares. This is not
a provider equivalence test or a causal model-size/decoding effect.
[Data, MATLAB source, and hashes](figures/README.md).*

## The claim firewall

Parallax currently supports claims about **observable response behavior and
evaluation machinery**. It does not establish:

- hidden belief, truth tracking, reasoning mechanism, or policy correctness;
- general strategic competence;
- that Claude or Gemini passed Experiment 3;
- that local Qwen2.5 behavior represents Chinese models or transfers to
  commercial providers;
- a causal effect of 7B versus 14B capacity;
- that surface-cue concordance identifies an internal mechanism; or
- 95% full-claim joint power from `N=9270`.

See the [claim/evidence matrix](governance/claim-evidence-matrix.csv) and
[claim-firewall review](governance/claim-firewall-review.md).

## Reproduce the publication

From this directory:

```powershell
python reproducibility/verify_public_release.py
```

The verifier requires no GPU, model weights, provider credentials, Ollama,
network access, funding, or model/provider calls. It checks the exact public
tree, accepted constants, experiment summaries, deterministic figure receipts,
proposal constraints, links, privacy boundary, and publication seal.

## Current status

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

The six Anthropic/Google calls in this release were non-scientific transport
qualification only. Publication does not constitute ChinaTalk submission.
