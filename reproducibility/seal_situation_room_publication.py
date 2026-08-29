#!/usr/bin/env python3
"""Seal the additive Situation Room publication with non-circular identities."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from verify_situation_room_publication import MANIFEST, MANIFEST_SHA, META, PACKET_SHA, ROOT, SEAL, canonical, payload_files, records, sha256_bytes, sha256_file


def write_json(path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    files = records(payload_files())
    manifest_core = {
        "schema_version": "parallax.situation-room-publication-manifest.v1",
        "source_aug23_commit": "fa9ca97ab6633093e7225d851531dab53ad0a4ab",
        "sr11r1_packet": "1a590a4ab72922008657fc39acabead7f9f3923113ee0bcbc648ff99db0251e4",
        "sr11r1_public_safe_projection": "4fb3cb59518afbc7f3b41901925a1c8fb2ec172b211c0b795fd0d5f1035785c5",
        "file_count": len(files),
        "files": files,
    }
    manifest_identity = sha256_bytes(canonical(manifest_core))
    write_json(MANIFEST, {**manifest_core, "manifest_identity": manifest_identity})
    manifest_sha = sha256_file(MANIFEST)
    MANIFEST_SHA.write_text(manifest_sha + "  publication-manifest.json\n", encoding="ascii", newline="\n")

    receipt_sha = sha256_file(META / "authority-receipt.json")
    seal_core = {
        "schema_version": "parallax.situation-room-publication-seal.v1",
        "sealed_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "status": "PARALLAX_SITUATION_ROOM_PUBLICATION_PACKAGE_SEALED",
        "manifest_identity": manifest_identity,
        "manifest_sha256": manifest_sha,
        "authority_receipt_sha256": receipt_sha,
        "sr11r1_packet": "1a590a4ab72922008657fc39acabead7f9f3923113ee0bcbc648ff99db0251e4",
        "sr11r1_public_safe_projection": "4fb3cb59518afbc7f3b41901925a1c8fb2ec172b211c0b795fd0d5f1035785c5",
        "frozen_artifacts_mutated": "NO",
        "new_scientific_calls": 0,
        "provider_calls": 0,
        "chinatalk_submission": "NOT_PERFORMED",
        "next_boundary": "HUMAN_CHINATALK_SUBMISSION_DECISION",
    }
    packet_identity = sha256_bytes(canonical(seal_core))
    write_json(SEAL, {**seal_core, "packet_identity": packet_identity})
    PACKET_SHA.write_text(packet_identity + "\n", encoding="ascii", newline="\n")
    print(json.dumps({
        "status": "SEALED",
        "file_count": len(files),
        "manifest_identity": manifest_identity,
        "manifest_sha256": manifest_sha,
        "authority_receipt_sha256": receipt_sha,
        "packet_identity": packet_identity,
    }, indent=2))


if __name__ == "__main__":
    main()
