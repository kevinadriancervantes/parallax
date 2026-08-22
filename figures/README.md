# Evidence figures

The two quantitative figures are deterministic views of accepted aggregate
local-model artifacts. No plotted value was typed by hand and no new model or
provider call was made.

Run from the release root:

```powershell
matlab -batch "cd('figures/matlab'); build_evidence_figures"
python figures/seal_figure_receipt.py capture-baseline
matlab -batch "cd('figures/matlab'); build_evidence_figures"
python figures/seal_figure_receipt.py finalize
```

The sealer removes MATLAB's nondeterministic PNG `tIME` metadata chunk while
preserving the rendered pixel and compression bytes. The second run must then
match every CSV, SVG, canonical PNG, and runtime receipt byte-for-byte.

`local-model-evidence-response-profile` shows all-scheduled response-state
shares across five ordered evidence doses, three fictional scenarios, and four
Qwen2.5 strata. It is descriptive local-model evidence, not Anthropic/Google
evidence or a confirmatory result.

`nuisance-instability-matrix` shows the largest absolute A-minus-B shift across
four scheduled-denominator outcome shares for each blinded pair. It makes the
17 nonzero comparisons visible; it is not an equivalence test and does not
identify a capacity or decoding effect.

Exact source, script, output, and deterministic-rerun hashes are recorded in
[the figure-data receipt](data/figure-data-receipt.json).
