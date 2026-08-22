"""Validate, hash, and seal deterministic public figure outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
BASELINE = DATA / "figure-determinism-baseline.json"
RECEIPT = DATA / "figure-data-receipt.json"

SOURCES = {
    "accepted-dose-profile.json": "4511ad91028773c004697c8fdcf9d905f8265ebadd2b32c58945739cc35a8b01",
    "accepted-nuisance-profile.json": "a5a7c422e4f69b86c663c0f0657ac46c552e5ff002a99aaa06cbc6f541e5df05",
}

OUTPUTS = [
    "local-model-evidence-response-profile.svg",
    "local-model-evidence-response-profile.png",
    "nuisance-instability-matrix.svg",
    "nuisance-instability-matrix.png",
    "social-preview.png",
    "data/local-model-evidence-response-profile.csv",
    "data/nuisance-instability-matrix.csv",
    "data/matlab-runtime.txt",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def current_hashes() -> dict[str, str]:
    missing = [name for name in OUTPUTS if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit(f"missing generated outputs: {missing}")
    return {name: sha(ROOT / name) for name in OUTPUTS}


def canonicalize_png(path: Path) -> None:
    """Remove only nondeterministic PNG time chunks; preserve rendered bytes."""
    raw = path.read_bytes()
    signature = b"\x89PNG\r\n\x1a\n"
    if not raw.startswith(signature):
        raise SystemExit(f"invalid PNG signature: {path}")
    cursor = len(signature)
    output = bytearray(signature)
    while cursor < len(raw):
        if cursor + 12 > len(raw):
            raise SystemExit(f"truncated PNG chunk: {path}")
        length = struct.unpack(">I", raw[cursor : cursor + 4])[0]
        chunk_type = raw[cursor + 4 : cursor + 8]
        data_start = cursor + 8
        data_end = data_start + length
        crc_end = data_end + 4
        if crc_end > len(raw):
            raise SystemExit(f"invalid PNG chunk length: {path}")
        data = raw[data_start:data_end]
        observed_crc = struct.unpack(">I", raw[data_end:crc_end])[0]
        expected_crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        if observed_crc != expected_crc:
            raise SystemExit(f"PNG CRC mismatch: {path}")
        if chunk_type != b"tIME":
            output.extend(raw[cursor:crc_end])
        cursor = crc_end
    path.write_bytes(bytes(output))


def validate_sources_and_tables() -> dict:
    for name, expected in SOURCES.items():
        observed = sha(DATA / name)
        if observed != expected:
            raise SystemExit(f"source identity mismatch: {name}: {observed}")

    dose = read_json(DATA / "accepted-dose-profile.json")
    nuisance = read_json(DATA / "accepted-nuisance-profile.json")
    profile_rows = list(csv.DictReader((DATA / "local-model-evidence-response-profile.csv").open(encoding="utf-8-sig", newline="")))
    nuisance_rows = list(csv.DictReader((DATA / "nuisance-instability-matrix.csv").open(encoding="utf-8-sig", newline="")))

    if len(profile_rows) != 60:
        raise SystemExit(f"expected 60 profile rows, observed {len(profile_rows)}")
    if len(nuisance_rows) != 60:
        raise SystemExit(f"expected 60 nuisance rows, observed {len(nuisance_rows)}")

    profile_map = {
        (p["scenario_id"], p["capacity"], p["regime"]): p
        for p in dose["profiles"]
    }
    for row in profile_rows:
        source = profile_map[(row["scenario_id"], row["capacity"], row["regime"])]["doses"][row["dose_id"]]
        expected = [
            source["state_all_scheduled"]["LEANS_NOT_H"]["rate"],
            source["state_all_scheduled"]["UNRESOLVED"]["rate"],
            source["state_all_scheduled"]["LEANS_H"]["rate"],
            source["local_unusable"]["rate"],
        ]
        observed = [float(row[k]) for k in ("leans_not_h_rate", "unresolved_rate", "leans_h_rate", "unusable_rate")]
        if any(abs(a - b) > 1e-12 for a, b in zip(expected, observed)):
            raise SystemExit(f"profile derivation mismatch: {row}")

    nuisance_map = {
        (c["scenario_id"], c["dose"], c["capacity"], c["regime"]): c
        for c in nuisance["comparisons"]
    }
    nonzero = 0
    for row in nuisance_rows:
        source = nuisance_map[(row["scenario_id"], row["dose_id"], row["capacity"], row["regime"])]["differences"]
        expected = [
            source["state_LEANS_NOT_H_all_scheduled"],
            source["state_UNRESOLVED_all_scheduled"],
            source["state_LEANS_H_all_scheduled"],
            source["local_unusable_rate"],
        ]
        observed = [float(row[k]) for k in ("diff_leans_not_h", "diff_unresolved", "diff_leans_h", "diff_unusable")]
        if any(abs(a - b) > 1e-12 for a, b in zip(expected, observed)):
            raise SystemExit(f"nuisance derivation mismatch: {row}")
        maximum = max(abs(value) for value in expected)
        if abs(maximum - float(row["max_abs_primary_difference"])) > 1e-12:
            raise SystemExit(f"nuisance maximum mismatch: {row}")
        nonzero += maximum > 1e-12
    if nonzero != 17:
        raise SystemExit(f"expected 17 nonzero nuisance comparisons, observed {nonzero}")

    return {"profile_rows": len(profile_rows), "nuisance_rows": len(nuisance_rows), "nuisance_nonzero": nonzero}


def write_json(path: Path, value: dict) -> None:
    path.write_bytes((json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("capture-baseline", "finalize"))
    args = parser.parse_args()

    for png_name in ("local-model-evidence-response-profile.png", "nuisance-instability-matrix.png", "social-preview.png"):
        canonicalize_png(ROOT / png_name)
    counts = validate_sources_and_tables()
    hashes = current_hashes()
    if args.mode == "capture-baseline":
        write_json(BASELINE, {
            "schema_version": "parallax.aug23.figure-determinism-baseline.v1",
            "generated_outputs": hashes,
            **counts,
        })
        print(json.dumps({"status": "BASELINE_CAPTURED", **counts, "outputs": len(hashes)}, sort_keys=True))
        return

    baseline = read_json(BASELINE)
    match = baseline["generated_outputs"] == hashes
    if not match:
        changed = sorted(name for name in set(baseline["generated_outputs"]) | set(hashes) if baseline["generated_outputs"].get(name) != hashes.get(name))
        raise SystemExit(f"MATLAB output rerun mismatch: {changed}")

    receipt = {
        "schema_version": "parallax.aug23.figure-data-receipt.v1",
        "status": "PASS",
        "source_artifacts": [
            {
                "public_path": f"figures/data/{name}",
                "repository_authority_path": (
                    "research/reviews/experiment-3/v3-local-model-surrogate-primary-result-v2/"
                    + ("dose-profile.json" if "dose" in name else "nuisance-profile.json")
                ),
                "sha256": digest,
                "accepted_role": "AGGREGATE_DESCRIPTIVE_LOCAL_MODEL_EVIDENCE",
            }
            for name, digest in SOURCES.items()
        ],
        "matlab_script": {
            "path": "figures/matlab/build_evidence_figures.m",
            "sha256": sha(ROOT / "matlab" / "build_evidence_figures.m"),
        },
        "deterministic_rerun": {
            "runs": 2,
            "byte_identical": True,
            "baseline_receipt_sha256": sha(BASELINE),
        },
        "generated_outputs": hashes,
        "derivations": {
            "local-model-evidence-response-profile": "All-scheduled shares of LEANS_NOT_H, UNRESOLVED, LEANS_H, and local unusable output by scenario, stratum, and ordered dose.",
            "nuisance-instability-matrix": "Maximum absolute A-minus-B difference across the four all-scheduled outcome shares for each of 15 blinded pairs and four local-model strata.",
        },
        "claim_boundaries": {
            "local-model-evidence-response-profile": "Descriptive local Qwen2.5 behavior only; not provider evidence, a confirmatory result, a monotonicity claim, or an inference about belief or mechanism.",
            "nuisance-instability-matrix": "Descriptive blinded A/B instability only; not a provider nuisance-equivalence test and not a causal decoding/capacity effect.",
        },
        **counts,
    }
    write_json(RECEIPT, receipt)
    print(json.dumps({"status": "PASS", **counts, "outputs": len(hashes), "receipt_sha256": sha(RECEIPT)}, sort_keys=True))


if __name__ == "__main__":
    main()
