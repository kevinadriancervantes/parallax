# Reproduce and inspect

Run the one canonical command from the root of this clean release tree:

```powershell
python reproducibility/verify_public_release.py
```

The verifier is self-contained. It uses only the included release manifest,
seal, predecessor receipts, compact evidence summaries, claim matrix, privacy
inventory, and local files. It does not require a repository sibling, GPU,
Ollama, model weights, provider credentials, network access, or funding.

It checks release identity, every payload hash, predecessor baseline identity,
confirmatory constants, synthetic-shadow evidence, 4,800-row accounting,
provider qualification boundaries, corrected cost arithmetic, claim firewall,
physical privacy inventory, links, and current release status.

The local Qwen editorial review was bounded copy review only. It was not
scientific evidence and its raw responses are not present in this public tree.
The six Anthropic/Google calls were non-scientific transport qualification;
no scientific provider prompt or confirmatory call was made.
