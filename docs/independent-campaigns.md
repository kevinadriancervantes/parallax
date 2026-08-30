# Independent campaign architecture

## Current status

The current public Parallax release **does not provide a general-purpose
independent campaign runner**. It is an evidence and reproducibility package,
not a Bring Your Own Model execution kit.

The release provides:

- public evidence and claim-bounded summaries;
- reproducibility verification;
- accepted scientific documentation;
- the Experiment 1–3 lineage;
- the public Situation Room and its interpretation layer.

The independent-campaign architecture described below is a **future extension
contract**. It is documented so that future transport engineering cannot
silently rewrite the scientific method. It is not implemented or scientifically
authorized in this release.

## Why independent campaigns matter

Parallax should eventually let an evaluator who has access to another model,
API, local inference server, or internal framework challenge the same
measurement instrument. The intended separation is simple: provider transport
may deliver requests and preserve native responses, but it may not change the
evidence intervention, schedule, response semantics, failure accounting,
analysis, or claim boundary.

This is a long-term architectural objective, not a current capability claim.

## Identity firewall

### `QUALIFICATION_ONLY`

Sacrificial path testing that checks authentication, request construction,
raw-response capture, provider-native error behavior, and related transport
semantics. Qualification produces no scientific result.

### `TECHNICAL_DEMONSTRATION`

A reduced or development run that shows that machinery operates. A technical
demonstration is not an Experiment 3 scientific result, regardless of whether
it uses familiar prompts or models.

### `CANONICAL_CLAUDE_GEMINI_REFERENCE_CAMPAIGN`

The frozen Experiment 3 reference design for the accepted Anthropic and Google
provider strata. Its exact scientific identity, configuration, schedules, and
analysis remain unchanged. It has not been scientifically executed.

### `REFERENCE_REPLICATION`

A future replication preserving the accepted reference content, model and
provider configurations, full geometry, and analysis under a new prospective
replication identity. It cannot overwrite or impersonate the canonical
reference campaign.

### `INDEPENDENT_SCIENTIFIC_CAMPAIGN`

A future architectural target for evaluating another model or inference path.
It requires prospective acceptance of an appropriate statistical contract,
qualification, campaign identity, configuration, randomization, schedule,
complete execution accounting, immutable evidence, analysis, and claim
boundary before scientific execution. The current Experiment 3 contract does
not itself authorize this identity for an arbitrary model.

### `DERIVED_PARALLAX_STUDY`

A study that changes scenarios, response semantics, geometry, analysis, or
another scientific component. It receives a distinct study identity and may
not inherit the reference campaign's scientific authority.

## Sample-size and statistical boundary

The accepted Experiment 3 reference contract fixes:

```text
N per cell                    = 9,270
cells per provider            = 30
calls per provider            = 278,100
provider strata               = 2
total reference calls         = 556,200
simultaneous inferential family M = 210
```

The family of 210 support quantities includes both provider strata. A one-model
study or a study with a different provider count cannot silently inherit that
simultaneous-error statement. Model or provider-count changes require
prospective statistical adjudication.

A reduced schedule remains a `TECHNICAL_DEMONSTRATION` unless it receives
separate prospective scientific authority. Using the same prompts does not
turn a smaller run into Experiment 3 science.

## Long-term architecture

The intended future sequence is:

```text
PARALLAX SCIENTIFIC CORE
        ↓
prospective campaign identity
        ↓
committed seed and sealed schedule
        ↓
transport-only local adapter
        ↓
immutable raw-response custody
        ↓
strict core-owned classification
        ↓
prospectively accepted analysis
        ↓
result verification and claim-bounded disposition
```

The preferred transport boundary is a local subprocess using a documented
JSONL envelope. That design is described in the [adapter contract](adapter-contract.md),
but no such general runner or adapter interface is implemented in the current
public repository.

## Current versus future

| Currently implemented | Future architectural target |
|---|---|
| Existing public evidence and release verification | General independent-campaign runner |
| Situation Room interpretation | Evaluator-controlled local transport adapters |
| Frozen two-provider reference protocol documentation | Prospectively adjudicated variable-provider campaigns |
| Non-scientific provider-path qualification evidence | Reusable adapter qualification workflow |
| Historical local-model execution evidence | A common public execution, sealing, analysis, and verification path |
| Credentials not required for public verification | Evaluator-local credentials for future execution |

Licensing for a future reusable execution kit remains unresolved. It must be
settled, together with scenario and source publication rights, before adapter
modification or redistribution is presented as a supported public workflow.

