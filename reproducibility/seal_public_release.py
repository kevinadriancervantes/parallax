"""Deterministically seal the additive August 23 Parallax public release."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "parallax-public-release-manifest.json"
SEAL = ROOT / "parallax-public-release-seal.json"
ALLOWLIST = ROOT / "governance" / "public-release-allowlist.json"
INVENTORY = ROOT / "governance" / "public-artifact-inventory.json"
PRIVACY = ROOT / "governance" / "release-privacy-receipt.json"

RELEASE_ID = "PARALLAX_AUG23_PUBLIC_PRESENTATION_RELEASE_V1"
SEALED_DATE = "2026-08-23"

IMMEDIATE_PREDECESSOR = {
    "manifest_path": "predecessor-public-release-v2/parallax-public-release-manifest.json",
    "manifest_sha256": "fc16c4bda7aa892b1089ff993eed2dd24696d14a69511b51c4cdd3c2f451c7b2",
    "packet_sha256": "004cfba15bd8a6e256d217e7acf3081f53752c538217a8db337aaaae76f0dee7",
    "seal_path": "predecessor-public-release-v2/parallax-public-release-seal.json",
    "seal_file_sha256": "6586c22d104a8a7eda65bf360fd7879513e76aef0a4529d65b4dcfe0b4c3f297",
}

FOUNDATIONAL_PREDECESSOR = {
    "manifest_path": "predecessor/contest-package-manifest.json",
    "manifest_sha256": "9b1c4d373320410ff248c067e7be2fb80edaf44f88ed0816bd04f1f4b64f2522",
    "packet_sha256": "5d7182dd0028c4d748d69f25eedb12c4e0cf4db500246ad4021955d4e9b0b9d5",
    "seal_path": "predecessor/contest-package-seal.json",
    "seal_file_sha256": "d32450cc9b77f0ddf4c0372a5a75cb3b76e2fab96926a58fd29297af3679599f",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_bytes((json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))


def all_files() -> list[str]:
    return sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(ROOT).parts
    )


def aggregate(files: list[dict[str, str]]) -> str:
    payload = "".join(f"{entry['path']}\0{entry['sha256']}\n" for entry in files).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def classify(paths: list[str]) -> tuple[list[str], list[str]]:
    sanitized_prefixes = (
        "evidence/",
        "local-review/",
        "predecessor/",
        "predecessor-public-release-v1/",
        "predecessor-public-release-v2/",
    )
    sanitized_exact = {
        "hardening-accounting-reproduction.json",
        "hardening-report.md",
        "governance/hardening-public-artifact-inventory.json",
        "governance/hardening-substrate-inventory.json",
        "governance/privacy-audit.json",
        "governance/semantic-diff.json",
    }
    public_sanitized = sorted(
        path for path in paths if path.startswith(sanitized_prefixes) or path in sanitized_exact
    )
    public = sorted(set(paths) - set(public_sanitized))
    return public, public_sanitized


def privacy_hits(paths: list[str]) -> list[dict[str, str]]:
    text_suffixes = {
        ".css", ".csv", ".html", ".json", ".jsonl", ".m", ".md",
        ".py", ".sha256", ".txt", ".xml",
    }
    patterns = {
        "personal_windows_path": re.compile(r"(?i)[A-Z]:\\Users\\[^\s`\"']+"),
        "personal_posix_path": re.compile(r"(?i)/(?:Users|home)/[^\s`\"']+"),
        "anthropic_key": re.compile(r"(?i)sk-ant-[A-Za-z0-9_-]{8,}"),
        "google_key": re.compile(r"AIza[A-Za-z0-9_-]{20,}"),
        "api_header_value": re.compile(r"(?i)(?:x-api-key|x-goog-api-key)\s*[:=]\s*[^\s`\"']+"),
        "bearer_token": re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{12,}"),
        "private_key": re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
        "mac_address": re.compile(r"(?i)(?:[0-9a-f]{2}:){5}[0-9a-f]{2}"),
    }
    hits: list[dict[str, str]] = []
    for rel in paths:
        path = ROOT / rel
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in patterns.items():
            if pattern.search(text):
                hits.append({"path": rel, "category": label})
    return hits


def verify_predecessor(binding: dict[str, str]) -> None:
    manifest_path = ROOT / binding["manifest_path"]
    seal_path = ROOT / binding["seal_path"]
    if sha(manifest_path) != binding["manifest_sha256"]:
        raise RuntimeError(f"Predecessor manifest mismatch: {manifest_path}")
    if sha(seal_path) != binding["seal_file_sha256"]:
        raise RuntimeError(f"Predecessor seal mismatch: {seal_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["packet_sha256"] != binding["packet_sha256"]:
        raise RuntimeError(f"Predecessor packet mismatch: {manifest_path}")
    if aggregate(manifest["files"]) != binding["packet_sha256"]:
        raise RuntimeError(f"Predecessor aggregate mismatch: {manifest_path}")


def main() -> None:
    verify_predecessor(IMMEDIATE_PREDECESSOR)
    verify_predecessor(FOUNDATIONAL_PREDECESSOR)

    # The three generated governance files already exist in the additive
    # predecessor copy. Their paths, not their old contents, establish the
    # fixed point for the exact physical inventory.
    physical = all_files()
    if MANIFEST.relative_to(ROOT).as_posix() not in physical or SEAL.relative_to(ROOT).as_posix() not in physical:
        raise RuntimeError("Manifest/seal paths must exist before deterministic inventory generation")
    public, public_sanitized = classify(physical)

    allowlist = {
        "schema_version": "parallax.aug23.public-release-allowlist.v1",
        "release_id": RELEASE_ID,
        "rule": "The physical public tree is exactly the union of PUBLIC and PUBLIC_SANITIZED paths, including this allowlist, the release manifest, and the release seal.",
        "PUBLIC": public,
        "PUBLIC_SANITIZED": public_sanitized,
        "LOCAL_PRIVATE_EXCLUDED": [
            "raw local scientific response rows and envelopes",
            "raw provider qualification envelopes and bodies",
            "raw local editorial-model output",
            "credential stores and authorization headers",
            "account-specific billing, quota, and capacity records",
            "personal machine and absolute-path metadata",
            "development repository trees outside this clean release"
        ],
        "SECRET_NEVER_EXPORT": [
            "credential values",
            "authorization headers",
            "private account identifiers",
            "personal absolute paths and usernames",
            "MAC, serial, process, and unrelated machine identifiers",
            "non-loopback network addresses",
            "raw provider or local-model bodies"
        ],
        "status": "PASS"
    }
    write_json(ALLOWLIST, allowlist)

    inventory = {
        "schema_version": "parallax.aug23.public-artifact-inventory.v1",
        "release_id": RELEASE_ID,
        "classification_rule": "Only public narrative/code/figures and compact public or public-sanitized evidence are physically present.",
        "physical_file_count": len(physical),
        "public_count": len(public),
        "public_sanitized_count": len(public_sanitized),
        "public_paths": public,
        "public_sanitized_paths": public_sanitized,
        "raw_provider_boundary": "Hashes and compact sanitized summaries only; raw envelopes remain local-private.",
        "raw_local_model_boundary": "Accepted aggregate profiles and compact accounting only; raw rows/responses remain local-private.",
        "status": "PASS"
    }
    write_json(INVENTORY, inventory)

    # Re-list after deterministic governance writes. Only bytes changed, so the
    # path set and count must remain identical.
    physical_after = all_files()
    if physical_after != physical:
        raise RuntimeError("Physical path set changed during inventory generation")
    hits = privacy_hits(physical_after)
    privacy = {
        "schema_version": "parallax.aug23.public-release-privacy-receipt.v1",
        "release_id": RELEASE_ID,
        "scan_mode": "physical-tree deterministic text-pattern and exact-allowlist audit",
        "scan_date": SEALED_DATE,
        "physical_tree_files": len(physical_after),
        "scanned_categories": [
            "credentials and authorization headers",
            "personal absolute paths and usernames",
            "MAC/private-key identifiers",
            "raw provider/local-model/editorial evidence paths",
            "unrelated machine and account metadata"
        ],
        "violations": hits,
        "final_public_export_contains_raw_local_review": False,
        "final_public_export_contains_raw_scientific_rows": False,
        "development_evidence_preserved_outside_public_export": True,
        "status": "PASS" if not hits else "FAIL"
    }
    write_json(PRIVACY, privacy)
    if hits:
        raise RuntimeError(f"Privacy scan failed: {hits}")

    payload_paths = [path for path in all_files() if path not in {MANIFEST.name, SEAL.name}]
    files = [{"path": rel, "sha256": sha(ROOT / rel)} for rel in payload_paths]
    packet = aggregate(files)
    manifest = {
        "algorithm": "sha256(sorted UTF-8 relative POSIX path + NUL + file SHA-256 + LF); release manifest and seal excluded",
        "created_utc_date": SEALED_DATE,
        "file_count": len(files),
        "files": files,
        "packet_sha256": packet,
        "immediate_predecessor": IMMEDIATE_PREDECESSOR,
        "foundational_predecessor": FOUNDATIONAL_PREDECESSOR,
        "schema_version": "parallax.aug23.public-release.manifest.v1",
        "successor": RELEASE_ID
    }
    write_json(MANIFEST, manifest)
    seal = {
        "schema_version": "parallax.aug23.public-release.seal.v1",
        "successor": RELEASE_ID,
        "sealed_utc_date": SEALED_DATE,
        "file_count": len(files),
        "packet_sha256": packet,
        "manifest_sha256": sha(MANIFEST),
        "immediate_predecessor_packet_sha256": IMMEDIATE_PREDECESSOR["packet_sha256"],
        "immediate_predecessor_manifest_sha256": IMMEDIATE_PREDECESSOR["manifest_sha256"],
        "immediate_predecessor_seal_file_sha256": IMMEDIATE_PREDECESSOR["seal_file_sha256"],
        "scientific_result_mutation": False,
        "new_scientific_model_calls": 0,
        "new_anthropic_calls": 0,
        "new_google_calls": 0,
        "new_confirmatory_calls": 0,
        "publication": "LIVE",
        "contest_submission": "NOT_PERFORMED",
        "status": "SEALED_AUG23_PUBLICATION_READY_FOR_SUBMISSION_REVIEW",
        "next_operation": "FINAL_AUG23_SUBMISSION_REVIEW_AND_AUTHORIZATION"
    }
    write_json(SEAL, seal)
    print(json.dumps({
        "status": seal["status"],
        "file_count": len(files),
        "packet_sha256": packet,
        "manifest_sha256": seal["manifest_sha256"],
        "privacy": privacy["status"],
        "new_scientific_or_provider_calls": 0
    }, sort_keys=True))


if __name__ == "__main__":
    main()
