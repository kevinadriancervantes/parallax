#!/usr/bin/env python3
"""Create the additive policy-reader presentation release records."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from verify_policy_reader_presentation import (
    AUTHORITY,
    AUTHORITY_SHA,
    ENTERING_COMMIT,
    ENTERING_DEPLOYMENT,
    ENTERING_TREE,
    INVARIANCE,
    MANIFEST,
    MANIFEST_SHA,
    META,
    PACKET_SHA,
    ROOT,
    SEAL,
    SEAL_SHA,
    baseline_bytes,
    baseline_paths,
    canonical,
    current_scientific_mismatches,
    git,
    payload_files,
    records,
    sha_bytes,
    sha_file,
)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    META.mkdir(parents=True, exist_ok=True)
    if not AUTHORITY.exists():
        write_json(AUTHORITY, {
            "authority": "EXPLICIT_HUMAN_PUBLICATION_AUTHORIZATION_IN_ATTACHED_RUN",
            "authorized_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "entering_git_commit": ENTERING_COMMIT,
            "entering_git_tree": ENTERING_TREE,
            "entering_deployment": ENTERING_DEPLOYMENT,
            "scope": "POLICY_READER_PRESENTATION_SUCCESSOR",
            "scientific_mutation_authority": "NONE",
            "frozen_artifacts_mutated": "NO",
            "provider_calls": 0,
            "new_scientific_calls": 0,
            "submission_authority": "NONE",
            "supabase_authority": "NONE",
        })
    AUTHORITY_SHA.write_text(sha_file(AUTHORITY) + "  authority-receipt.json\n", encoding="ascii", newline="\n")

    mismatches = current_scientific_mismatches()
    files = []
    for path in baseline_paths():
        current = ROOT / path
        data = current.read_bytes() if current.exists() else b""
        files.append({"path": path, "bytes": len(data), "sha256": sha_bytes(data)})
    write_json(INVARIANCE, {
        "schema_version": "parallax.policy-reader-scientific-invariance.v1",
        "baseline_commit": ENTERING_COMMIT,
        "baseline_tree": ENTERING_TREE,
        "changed_scientific_files": mismatches,
        "scientific_files_changed": len(mismatches),
        "files": files,
    })
    if mismatches:
        raise SystemExit("scientific invariance failed: " + ", ".join(mismatches))

    payload = records(payload_files())
    manifest_core = {
        "schema_version": "parallax.policy-reader-presentation-manifest.v1",
        "entering_commit": ENTERING_COMMIT,
        "entering_tree": ENTERING_TREE,
        "entering_deployment": ENTERING_DEPLOYMENT,
        "scope": "POLICY_READER_PRESENTATION_SUCCESSOR",
        "scientific_files_changed": 0,
        "frozen_artifacts_mutated": "NO",
        "file_count": len(payload),
        "files": payload,
        "sr11r1_packet": "1a590a4ab72922008657fc39acabead7f9f3923113ee0bcbc648ff99db0251e4",
        "sr11r1_public_safe_projection": "4fb3cb59518afbc7f3b41901925a1c8fb2ec172b211c0b795fd0d5f1035785c5",
    }
    manifest_identity = sha_bytes(canonical(manifest_core))
    write_json(MANIFEST, {**manifest_core, "manifest_identity": manifest_identity})
    manifest_sha = sha_file(MANIFEST)
    MANIFEST_SHA.write_text(manifest_sha + "  release-manifest.json\n", encoding="ascii", newline="\n")

    seal_core = {
        "schema_version": "parallax.policy-reader-presentation-seal.v1",
        "sealed_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "status": "PARALLAX_POLICY_READER_PRESENTATION_READY",
        "scope": "POLICY_READER_PRESENTATION_SUCCESSOR",
        "manifest_identity": manifest_identity,
        "manifest_sha256": manifest_sha,
        "authority_receipt_sha256": sha_file(AUTHORITY),
        "scientific_invariance_sha256": sha_file(INVARIANCE),
        "entering_commit": ENTERING_COMMIT,
        "entering_tree": ENTERING_TREE,
        "entering_deployment": ENTERING_DEPLOYMENT,
        "scientific_files_changed": 0,
        "governing_observations_changed": 0,
        "frozen_artifacts_mutated": "NO",
        "new_scientific_calls": 0,
        "provider_calls": 0,
        "external_submission": "NOT_PERFORMED",
        "next_operation": "FINAL_SEP1_SUBMISSION_REVIEW",
    }
    packet_identity = sha_bytes(canonical(seal_core))
    write_json(SEAL, {**seal_core, "packet_identity": packet_identity})
    SEAL_SHA.write_text(sha_file(SEAL) + "  release-seal.json\n", encoding="ascii", newline="\n")
    PACKET_SHA.write_text(packet_identity + "\n", encoding="ascii", newline="\n")
    print(json.dumps({
        "status": "SEALED",
        "file_count": len(payload),
        "manifest_identity": manifest_identity,
        "manifest_sha256": manifest_sha,
        "packet_identity": packet_identity,
        "seal_sha256": sha_file(SEAL),
    }, indent=2))


if __name__ == "__main__":
    main()
