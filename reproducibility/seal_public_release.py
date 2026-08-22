"""Create the deterministic manifest and seal for the clean public release."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "parallax-public-release-manifest.json"
SEAL = ROOT / "parallax-public-release-seal.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    excluded = {MANIFEST.name, SEAL.name}
    files = []
    for path in sorted(p for p in ROOT.rglob("*") if p.is_file() and p.name not in excluded):
        rel = path.relative_to(ROOT).as_posix()
        files.append({"path": rel, "sha256": sha(path)})
    payload = "".join(f"{entry['path']}\0{entry['sha256']}\n" for entry in files).encode("utf-8")
    packet = hashlib.sha256(payload).hexdigest()
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    manifest = {
        "algorithm": "sha256(sorted UTF-8 relative POSIX path + NUL + file SHA-256 + LF); release manifest and seal excluded",
        "created_utc": now,
        "file_count": len(files),
        "files": files,
        "packet_sha256": packet,
        "predecessor_manifest_sha256": "9b1c4d373320410ff248c067e7be2fb80edaf44f88ed0816bd04f1f4b64f2522",
        "predecessor_packet_sha256": "5d7182dd0028c4d748d69f25eedb12c4e0cf4db500246ad4021955d4e9b0b9d5",
        "predecessor_seal_file_sha256": "d32450cc9b77f0ddf4c0372a5a75cb3b76e2fab96926a58fd29297af3679599f",
        "schema_version": "parallax.public-release.manifest.v1",
        "successor": "PARALLAX_PUBLIC_RELEASE_CANDIDATE_V1"
    }
    MANIFEST.write_bytes((json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    seal = {
        "confirmatory_calls": 0,
        "file_count": len(files),
        "manifest_sha256": sha(MANIFEST),
        "next_operation": "PUBLIC_DEPLOYMENT_AND_SUBMISSION_AUTHORIZATION",
        "packet_sha256": packet,
        "predecessor_manifest_sha256": manifest["predecessor_manifest_sha256"],
        "predecessor_packet_sha256": manifest["predecessor_packet_sha256"],
        "predecessor_seal_file_sha256": manifest["predecessor_seal_file_sha256"],
        "schema_version": "parallax.public-release.seal.v1",
        "scientific_result_mutation": False,
        "scientific_model_calls": 0,
        "sealed_utc": now,
        "status": "SEALED_READY_FOR_PUBLIC_DEPLOYMENT_AND_SUBMISSION_AUTHORIZATION",
        "successor": "PARALLAX_PUBLIC_RELEASE_CANDIDATE_V1"
    }
    SEAL.write_bytes((json.dumps(seal, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"status": seal["status"], "file_count": len(files), "packet_sha256": packet, "manifest_sha256": seal["manifest_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
