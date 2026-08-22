# Reproduce and inspect the August 23 public release

Run one command from the root of this public tree:

```powershell
python reproducibility/verify_public_release.py
```

The verifier is self-contained and read-only. It requires no repository sibling,
GPU, Ollama runtime, model weights, provider credentials, network access,
funding, or model/provider calls.

It verifies:

- the immediate public-release predecessor receipts and foundational hardening
  predecessor receipts;
- the release aggregate, manifest identity, every payload hash, and exact
  physical allowlist;
- the accepted Experiment 1 and Experiment 2 results and source bindings;
- Experiment 3 synthetic, local, provider-path, and unexecuted-reference roles;
- the cross-experiment lineage and prohibition on evidentiary collapse;
- deterministic MATLAB figure data, source hashes, outputs, and rerun receipt;
- the 300-word proposal limit, live-form mapping, and unpublished deadline-clock
  status;
- canonical/search/social metadata, sitemap, robots directives, and local links;
- the claim firewall, current publication/submission boundary, and physical
  privacy scan.

The plotting workflow is separate because it requires MATLAB. To regenerate the
accepted aggregate figures, see [figures/README.md](../figures/README.md). The
public verifier confirms their deterministic receipt without invoking MATLAB.

No raw local scientific rows, raw provider bodies, raw editorial-model output,
credentials, account identifiers, or personal machine paths are present in the
public tree.

```text
PUBLICATION = LIVE
CONTEST_SUBMISSION = NOT_PERFORMED
NEXT_BOUNDARY = FINAL_AUG23_SUBMISSION_REVIEW
```
