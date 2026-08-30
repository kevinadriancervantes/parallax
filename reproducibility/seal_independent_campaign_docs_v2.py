#!/usr/bin/env python3
"""Seal the exact P1 stale-command correction as docs successor v2."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from verify_independent_campaign_docs_v2 import (
    AUTHORITY, AUTHORITY_SHA, CONTENT_FILES, ENTERING_COMMIT, ENTERING_TREE,
    FROZEN, INVARIANCE, MANIFEST, MANIFEST_SHA, META, PACKET_SHA, ROOT, SEAL,
    SEAL_SHA, V1_HASHES, baseline_mismatches, canonical, git, records, sha_bytes,
    sha_file, verify,
)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--content-commit", required=True); args = parser.parse_args()
    content_commit = args.content_commit
    if git("rev-parse", content_commit) != content_commit:
        raise SystemExit("content commit must be a full exact Git commit")
    preseal = verify(require_release=False)
    if preseal["status"] != "PASS":
        raise SystemExit(json.dumps(preseal, indent=2))
    META.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    write_json(AUTHORITY, {
        "schema_version": "parallax.sep1-independent-campaign-docs-authority.v2",
        "authority": "CONTINUOUS_CLOSURE_REPRODUCED_P1_STALE_COMMAND_REPAIR",
        "scope": "EXACT_CURRENT_VERIFIER_REFERENCE_CORRECTION",
        "entering_commit": ENTERING_COMMIT,
        "entering_tree": ENTERING_TREE,
        "documentation_content_commit": content_commit,
        "recorded_utc": now,
        "scientific_mutation_authority": "NONE",
        "byom_implementation_authority": "NONE",
        "license_selection_authority": "NONE",
        "provider_call_authority": "NONE",
        "submission_authority": "NONE",
    })
    AUTHORITY_SHA.write_text(sha_file(AUTHORITY) + "  authority-receipt.json\n", encoding="ascii", newline="\n")
    mismatches = baseline_mismatches()
    write_json(INVARIANCE, {
        "schema_version": "parallax.sep1-independent-campaign-docs-invariance.v2",
        "baseline_commit": ENTERING_COMMIT,
        "baseline_tree": ENTERING_TREE,
        "baseline_mismatches": mismatches,
        "scientific_files_changed": 0,
        "frozen_files_changed": sum(sha_file(ROOT / name) != digest for name, digest in FROZEN.items()),
        "presentation_files_changed": ["reproduce/index.html"],
        "presentation_change": "CURRENT_VERIFIER_REFERENCE_ONLY",
        "docs_v1_identities": V1_HASHES,
    })
    if mismatches:
        raise SystemExit("v1 invariance failed: " + ", ".join(mismatches))
    manifest_core = {
        "schema_version": "parallax.sep1-independent-campaign-docs-manifest.v2",
        "scope": "EXACT_CURRENT_VERIFIER_REFERENCE_CORRECTION",
        "entering_commit": ENTERING_COMMIT,
        "entering_tree": ENTERING_TREE,
        "documentation_content_commit": content_commit,
        "files": records(list(CONTENT_FILES)),
        "file_count": len(CONTENT_FILES),
        "scientific_files_changed": 0,
        "frozen_files_changed": 0,
        "new_execution_functionality": 0,
    }
    manifest_identity = sha_bytes(canonical(manifest_core)); write_json(MANIFEST, {**manifest_core, "manifest_identity": manifest_identity})
    MANIFEST_SHA.write_text(sha_file(MANIFEST) + "  release-manifest.json\n", encoding="ascii", newline="\n")
    seal_core = {
        "schema_version": "parallax.sep1-independent-campaign-docs-seal.v2",
        "status": "PARALLAX_SEP1_DOCUMENTATION_P1_CLOSED",
        "sealed_utc": now,
        "scope": "EXACT_CURRENT_VERIFIER_REFERENCE_CORRECTION",
        "entering_commit": ENTERING_COMMIT,
        "documentation_content_commit": content_commit,
        "manifest_identity": manifest_identity,
        "manifest_sha256": sha_file(MANIFEST),
        "authority_receipt_sha256": sha_file(AUTHORITY),
        "scientific_invariance_sha256": sha_file(INVARIANCE),
        "scientific_files_changed": 0,
        "frozen_files_changed": 0,
        "new_execution_functionality": 0,
        "model_calls": 0,
        "provider_calls": 0,
        "scientific_calls": 0,
        "campaigns_created": 0,
        "seeds_generated": 0,
        "seeds_committed": 0,
        "licenses_selected": 0,
        "byom_runner_implemented": 0,
        "contest_submission": "NOT_PERFORMED",
        "next_operation": "HUMAN_FINAL_SUBMISSION_REVIEW",
    }
    packet_identity = sha_bytes(canonical(seal_core)); write_json(SEAL, {**seal_core, "packet_identity": packet_identity})
    SEAL_SHA.write_text(sha_file(SEAL) + "  release-seal.json\n", encoding="ascii", newline="\n")
    PACKET_SHA.write_text(packet_identity + "\n", encoding="ascii", newline="\n")
    print(json.dumps({"status": "SEALED", "documentation_content_commit": content_commit, "manifest_identity": manifest_identity, "manifest_sha256": sha_file(MANIFEST), "packet_identity": packet_identity, "seal_sha256": sha_file(SEAL)}, indent=2))


if __name__ == "__main__":
    main()

