# Prospective independent-campaign manifest

## Status and purpose

This document describes a **future, illustrative** campaign identity schema.
It does not create a campaign, generate a seed, commit a seed, authorize
scientific execution, or implement a public runner.

An independent campaign must remain distinct from the frozen canonical
Claude/Gemini reference campaign and from qualification or demonstration runs.

## Illustrative manifest only

Every value below is a placeholder. None is an active identity or commitment.

```json
{
  "protocol_version": "<required protocol version>",
  "campaign_type": "<required identity class>",
  "campaign_id": "<required evaluator-assigned identity>",
  "provider": "<required provider or internal service identity>",
  "model": "<required exact model identity>",
  "model_revision": "<optional revision or UNAVAILABLE>",
  "adapter": "<required adapter identity>",
  "adapter_version": "<required version or content hash>",
  "endpoint_identity": "<optional public endpoint or privacy-safe hash>",
  "generation_configuration": "<required exact object>",
  "reasoning_configuration": "<required exact object or unsupported declaration>",
  "unsupported_capabilities": "<required list>",
  "scenario_corpus_sha256": "<required future identity>",
  "renderer_sha256": "<required future identity>",
  "response_contract_sha256": "<required future identity>",
  "analysis_contract_sha256": "<required future identity>",
  "seed_commitment_sha256": "<required future commitment; not generated here>",
  "schedule_sha256": "<derived after future deterministic generation>",
  "scheduled_calls": "<derived integer>",
  "qualification_receipt_sha256": "<required before future execution>",
  "privacy_mode": "<required privacy declaration>",
  "created_at": "<required UTC timestamp>"
}
```

## Field classification

| Field | Class | Rule |
|---|---|---|
| `protocol_version` | REQUIRED | Identifies the accepted campaign protocol. |
| `campaign_type` | REQUIRED | Uses the identity firewall defined in [independent campaigns](independent-campaigns.md). |
| `campaign_id` | REQUIRED | Stable, unique, and fixed before execution. |
| `provider` | REQUIRED | Exact provider, gateway, or internal-service identity. |
| `model` | REQUIRED | Exact requested model identity. |
| `model_revision` | OPTIONAL | Required when exposed by the service; otherwise declare unavailable. |
| `adapter` | REQUIRED | Stable adapter identity. |
| `adapter_version` | REQUIRED | Version and/or content hash. |
| `endpoint_identity` | OPTIONAL | Public endpoint or privacy-safe commitment; never credentials. |
| `generation_configuration` | REQUIRED | Exact, no silent defaults. |
| `reasoning_configuration` | REQUIRED | Exact controls or explicit unsupported status. |
| `unsupported_capabilities` | REQUIRED | Empty list only after positive verification. |
| scientific contract hashes | REQUIRED | Corpus, renderer, response, and analysis identities. |
| `seed_commitment_sha256` | REQUIRED | Future pre-execution commitment; raw seed excluded. |
| `schedule_sha256` | DERIVED | Computed from the complete deterministic schedule. |
| `scheduled_calls` | DERIVED | Computed from the sealed schedule. |
| `qualification_receipt_sha256` | REQUIRED | Binds sacrificial path qualification. |
| `privacy_mode` | REQUIRED | Records public/private identity treatment. |
| `created_at` | REQUIRED | UTC creation time for the sealed identity. |

## Prohibited contents

The manifest and campaign artifacts must not contain:

- API keys or bearer tokens;
- authorization headers;
- private endpoint credentials;
- private certificates or raw secret material;
- the raw CSPRNG seed in a public pre-execution manifest;
- unrelated local-machine inventory;
- personal or account identifiers not required for scientific custody.

## Campaign immutability

The campaign identity must be fixed before scientific execution. Changing the
provider, model, revision, adapter, endpoint identity, generation settings,
scientific contracts, schedule, or qualification binding after sealing creates
a successor campaign. It is never a silent edit to an attempted campaign.

## Seed custody

The accepted architectural pattern is:

```text
evaluator-local operating-system CSPRNG
→ commitment before scientific execution
→ deterministic complete schedule
→ no seed shopping
→ reveal or retain according to the accepted privacy/custody rule
```

This documentation generates and commits no seed. It does not alter the
canonical reference campaign's existing seed or schedule custody.

