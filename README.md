# Parallax — public release candidate V1

Parallax is a governed evaluation instrument for a narrow behavioral question:
when evidence is prospectively ordered, do observable response states move in
the corresponding direction, remain stable under nuisance rewrites, and fail
conservatively when a usable response is unavailable?

This clean tree is an additive public-release successor to the independently
accepted hardening package. It contains only public or public-sanitized
artifacts. Raw local editorial output, raw scientific rows, provider bodies,
private machine metadata, and credentials are excluded physically.

## Start here

1. [Executive summary](executive-summary.md)
2. [Full contest narrative](contest-narrative.md)
3. [Evaluation protocol and claim matrix](governance/claim-evidence-matrix.csv)
4. [Local surrogate evidence](evidence/local-surrogate-summary.json)
5. [Provider-path qualification](evidence/provider-qualification-summary.json)
6. [Failure semantics](governance/failure-semantics.md)
7. [Microsite content](microsite/index.md)
8. [Submission materials](submission/form-draft.md)
9. [Reproduction instructions](reproducibility/README.md)

## Canonical reproduction

From this directory, with no repository sibling or network access:

```powershell
python reproducibility/verify_public_release.py
```

The command is deterministic, requires no GPU, model weights, provider
credentials, Ollama runtime, funding, or model/provider calls, and verifies
this release rather than a predecessor directory.

## Status boundary

```text
CONTEST_PACKAGE_HARDENING = INDEPENDENTLY_ACCEPTED
PUBLIC_RELEASE_CANDIDATE = SEALED
CONFIRMATORY_EXECUTION = NOT_PERFORMED
SCIENTIFIC_PROVIDER_RESULT = NONE
FUNDING = NOT_SECURED
NEXT_BOUNDARY = PUBLIC_DEPLOYMENT_AND_SUBMISSION_AUTHORIZATION
```

The local 4,800-row result is descriptive only. The six live provider calls
were non-scientific path qualification. The full two-provider confirmatory
plan remains unexecuted and funding-dependent.
