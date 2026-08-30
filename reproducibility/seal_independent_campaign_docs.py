#!/usr/bin/env python3
"""Seal the additive independent-campaign documentation successor."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from verify_independent_campaign_docs import (
    AUTHORITY,
    AUTHORITY_SHA,
    CONTENT_FILES,
    ENTERING_COMMIT,
    ENTERING_TREE,
    FROZEN,
    INVARIANCE,
    MANIFEST,
    MANIFEST_SHA,
    META,
    PACKET_SHA,
    PREDECESSOR_HASHES,
    ROOT,
    SEAL,
    SEAL_SHA,
    canonical,
    git,
    immutable_baseline_mismatches,
    records,
    sha_bytes,
    sha_file,
    verify,
)


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content-commit", required=True)
    args = parser.parse_args()
    content_commit = args.content_commit
    if git("rev-parse", content_commit) != content_commit:
        raise SystemExit("content commit must be a full exact Git commit")
    if git("rev-parse", f"{content_commit}^{{tree}}") == ENTERING_TREE:
        raise SystemExit("content commit does not contain the documentation successor")
    preseal = verify(require_release=False)
    if preseal["status"] != "PASS":
        raise SystemExit(json.dumps(preseal, indent=2))

    META.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    write_json(AUTHORITY, {
        "schema_version": "parallax.sep1-independent-campaign-docs-authority.v1",
        "authority": "EXPLICIT_HUMAN_DOCUMENTATION_SUCCESSOR_AUTHORITY_IN_ATTACHED_RUN",
        "authorized_scope": "FOUR_ARCHITECTURE_DOCUMENTS_MINIMAL_README_AND_VERIFICATION_ONLY",
        "scope": "SEP1_INDEPENDENT_CAMPAIGN_DOCUMENTATION",
        "entering_commit": ENTERING_COMMIT,
        "entering_tree": ENTERING_TREE,
        "documentation_content_commit": content_commit,
        "recorded_utc": now,
        "scientific_mutation_authority": "NONE",
        "website_mutation_authority": "NONE",
        "byom_implementation_authority": "NONE",
        "license_selection_authority": "NONE",
        "provider_call_authority": "NONE",
        "submission_authority": "NONE",
    })
    AUTHORITY_SHA.write_text(sha_file(AUTHORITY) + "  authority-receipt.json\n", encoding="ascii", newline="\n")

    mismatches = immutable_baseline_mismatches()
    write_json(INVARIANCE, {
        "schema_version": "parallax.sep1-independent-campaign-docs-invariance.v1",
        "baseline_commit": ENTERING_COMMIT,
        "baseline_tree": ENTERING_TREE,
        "baseline_mismatches": mismatches,
        "scientific_files_changed": 0 if not mismatches else len(mismatches),
        "frozen_files_changed": sum(sha_file(ROOT / name) != digest for name, digest in FROZEN.items()),
        "website_files_changed": 0,
        "predecessor_identities": PREDECESSOR_HASHES,
        "frozen_identities": FROZEN,
    })
    if mismatches:
        raise SystemExit("predecessor invariance failed: " + ", ".join(mismatches))

    manifest_core = {
        "schema_version": "parallax.sep1-independent-campaign-docs-manifest.v1",
        "scope": "SEP1_INDEPENDENT_CAMPAIGN_DOCUMENTATION",
        "entering_commit": ENTERING_COMMIT,
        "entering_tree": ENTERING_TREE,
        "documentation_content_commit": content_commit,
        "files": records(list(CONTENT_FILES)),
        "file_count": len(CONTENT_FILES),
        "scientific_files_changed": 0,
        "frozen_files_changed": 0,
        "website_files_changed": 0,
        "new_execution_functionality": 0,
    }
    manifest_identity = sha_bytes(canonical(manifest_core))
    write_json(MANIFEST, {**manifest_core, "manifest_identity": manifest_identity})
    MANIFEST_SHA.write_text(sha_file(MANIFEST) + "  release-manifest.json\n", encoding="ascii", newline="\n")

    seal_core = {
        "schema_version": "parallax.sep1-independent-campaign-docs-seal.v1",
        "status": "PARALLAX_INDEPENDENT_CAMPAIGN_ARCHITECTURE_DOCUMENTED_NOT_IMPLEMENTED",
        "sealed_utc": now,
        "scope": "SEP1_INDEPENDENT_CAMPAIGN_DOCUMENTATION",
        "entering_commit": ENTERING_COMMIT,
        "documentation_content_commit": content_commit,
        "manifest_identity": manifest_identity,
        "manifest_sha256": sha_file(MANIFEST),
        "authority_receipt_sha256": sha_file(AUTHORITY),
        "scientific_invariance_sha256": sha_file(INVARIANCE),
        "scientific_files_changed": 0,
        "frozen_files_changed": 0,
        "website_files_changed": 0,
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
        "next_operation": "FINAL_ADVERSARIAL_SUBMISSION_AUDIT",
    }
    packet_identity = sha_bytes(canonical(seal_core))
    write_json(SEAL, {**seal_core, "packet_identity": packet_identity})
    SEAL_SHA.write_text(sha_file(SEAL) + "  release-seal.json\n", encoding="ascii", newline="\n")
    PACKET_SHA.write_text(packet_identity + "\n", encoding="ascii", newline="\n")
    print(json.dumps({
        "status": "SEALED",
        "documentation_content_commit": content_commit,
        "manifest_identity": manifest_identity,
        "manifest_sha256": sha_file(MANIFEST),
        "packet_identity": packet_identity,
        "seal_sha256": sha_file(SEAL),
    }, indent=2))


if __name__ == "__main__":
    main()

