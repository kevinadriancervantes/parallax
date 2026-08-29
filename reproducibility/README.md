# Reproduce the current Parallax public presentation

Run one command from the repository root:

```powershell
python reproducibility/verify_policy_reader_presentation.py
```

The verifier is self-contained, deterministic, and read-only. It requires no
GPU, local model runtime, model weights, credentials, provider account, network
access, or model/provider calls.

It verifies:

- the full public release manifest, packet, and file hashes;
- the five original SR-11R1 artifacts at their byte-preserved provenance route;
- the unchanged governing 1,600-row evidence projection;
- the 1,600-run governing versus 4,800-run predecessor campaign distinction;
- required scientific caveats, exclusions, and public release language;
- the single current reproduction command;
- all local HTML, image, script, and stylesheet links;
- the declared scientific-invariance ledger; and
- the public privacy and credential boundary.

## What the check does not do

It does not reanalyze scientific results, regenerate figures, issue requests,
or create a new claim. MATLAB figure generation and the earlier August-23
release verifier remain available as historical reproduction paths.

## Current public research state

- Publication: live.
- Frontier-provider Experiment-3 scientific result: none.

The current verifier is for this public presentation successor. Predecessor
verifiers remain preserved for their original releases.
