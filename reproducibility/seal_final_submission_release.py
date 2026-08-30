#!/usr/bin/env python3
"""Seal the final Sep-1 submission release after the bounded copy repair."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from verify_final_submission_release import (
    AUTHORITY, AUTHORITY_SHA, CONTENT_FILES, ENTERING_COMMIT, ENTERING_TREE,
    FROZEN, INVARIANCE, MANIFEST, MANIFEST_SHA, META, PACKET_SHA, ROOT, SEAL,
    SEAL_SHA, baseline_mismatches, canonical, git, records, sha_bytes, sha_file,
    verify,
)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--content-commit", required=True); args = parser.parse_args()
    if len(args.content_commit) != 40 or git("rev-parse", args.content_commit) != args.content_commit:
        raise SystemExit("content commit must be a full exact Git commit")
    preseal = verify(require_release=False)
    if preseal["status"] != "PASS":
        raise SystemExit(json.dumps(preseal, indent=2))
    META.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    write_json(AUTHORITY, {
        "schema_version": "parallax.sep1-final-submission-authority.v1",
        "authority": "FINAL_SUBMISSION_P1_COPY_REPAIR",
        "scope": "SCOPED_EXPERIMENT_3_FRONTIER_LABEL",
        "entering_commit": ENTERING_COMMIT,
        "entering_tree": ENTERING_TREE,
        "submission_content_commit": args.content_commit,
        "recorded_utc": now,
        "scientific_mutation_authority": "NONE",
        "byom_implementation_authority": "NONE",
        "provider_call_authority": "NONE",
        "submission_authority": "NONE",
    })
    AUTHORITY_SHA.write_text(sha_file(AUTHORITY) + "  authority-receipt.json\n", encoding="ascii", newline="\n")
    mismatches = baseline_mismatches()
    write_json(INVARIANCE, {
        "schema_version": "parallax.sep1-final-submission-invariance.v1",
        "baseline_commit": ENTERING_COMMIT,
        "baseline_tree": ENTERING_TREE,
        "baseline_mismatches": mismatches,
        "scientific_files_changed": 0,
        "frozen_files_changed": sum(sha_file(ROOT / name) != digest for name, digest in FROZEN.items()),
        "data_projection_changed": 0,
        "classification_changes": 0,
        "threshold_changes": 0,
        "analysis_changes": 0,
        "presentation_files_changed": ["index.html", "README.md", "reproducibility/README.md", "reproduce/index.html"],
        "presentation_change": "SCOPED_EXPERIMENT_3_FRONTIER_LABEL_AND_CURRENT_VERIFIER_REFERENCE",
        "byom_functionality_added": 0,
    })
    if mismatches:
        raise SystemExit("predecessor invariance failed: " + ", ".join(mismatches))
    manifest_core = {
        "schema_version": "parallax.sep1-final-submission-manifest.v1",
        "scope": "SCOPED_EXPERIMENT_3_FRONTIER_LABEL",
        "entering_commit": ENTERING_COMMIT,
        "entering_tree": ENTERING_TREE,
        "submission_content_commit": args.content_commit,
        "files": records(list(CONTENT_FILES)),
        "file_count": len(CONTENT_FILES),
        "scientific_files_changed": 0,
        "frozen_files_changed": 0,
        "new_scientific_execution": 0,
    }
    manifest_identity = sha_bytes(canonical(manifest_core)); write_json(MANIFEST, {**manifest_core, "manifest_identity": manifest_identity})
    MANIFEST_SHA.write_text(sha_file(MANIFEST) + "  release-manifest.json\n", encoding="ascii", newline="\n")
    seal_core = {
        "schema_version": "parallax.sep1-final-submission-seal.v1",
        "status": "PARALLAX_FINAL_SUBMISSION_RELEASE_ACCEPTED",
        "sealed_utc": now,
        "scope": "SCOPED_EXPERIMENT_3_FRONTIER_LABEL",
        "entering_commit": ENTERING_COMMIT,
        "submission_content_commit": args.content_commit,
        "manifest_identity": manifest_identity,
        "manifest_sha256": sha_file(MANIFEST),
        "authority_receipt_sha256": sha_file(AUTHORITY),
        "scientific_invariance_sha256": sha_file(INVARIANCE),
        "scientific_files_changed": 0,
        "frozen_files_changed": 0,
        "data_projection_changed": 0,
        "classification_changes": 0,
        "threshold_changes": 0,
        "analysis_changes": 0,
        "model_calls": 0,
        "provider_calls": 0,
        "scientific_calls": 0,
        "campaigns_created": 0,
        "seeds_generated": 0,
        "byom_functionality_added": 0,
        "license_selected": 0,
        "contest_submission": "NOT_PERFORMED",
        "next_operation": "HUMAN_FORM_ENTRY_AND_SUBMISSION",
    }
    packet_identity = sha_bytes(canonical(seal_core)); write_json(SEAL, {**seal_core, "packet_identity": packet_identity})
    SEAL_SHA.write_text(sha_file(SEAL) + "  release-seal.json\n", encoding="ascii", newline="\n")
    PACKET_SHA.write_text(packet_identity + "\n", encoding="ascii", newline="\n")
    print(json.dumps({"status": "SEALED", "submission_content_commit": args.content_commit, "manifest_identity": manifest_identity, "manifest_sha256": sha_file(MANIFEST), "packet_identity": packet_identity, "seal_sha256": sha_file(SEAL)}, indent=2))


if __name__ == "__main__":
    main()
