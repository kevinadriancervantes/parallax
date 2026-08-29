#!/usr/bin/env python3
"""Verify the additive Parallax Situation Room publication without network access."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "publication" / "situation-room-v1"
MANIFEST = META / "publication-manifest.json"
MANIFEST_SHA = META / "publication-manifest.sha256"
SEAL = META / "publication-seal.json"
PACKET_SHA = META / "publication-packet.sha256"

EXCLUDED_FROM_MANIFEST = {
    "publication/situation-room-v1/publication-manifest.json",
    "publication/situation-room-v1/publication-manifest.sha256",
    "publication/situation-room-v1/publication-seal.json",
    "publication/situation-room-v1/publication-packet.sha256",
}

FROZEN = {
    "situation-room/app.js": (21319, "21dcf31c2bd61ccdb73a3de9877150067b21c95a7dc81ce9c79b15af414cc1e0"),
    "situation-room/data/data.json": (788968, "db107bf3c2080f431d0eaaee044b09d63af3f8e4b349c2c85f2110289cdfd9c0"),
    "situation-room/index.html": (2016, "012aacd2f2334d5c60999f9c944aedcd79ca625b58b84cce473701fd5695b1ab"),
    "situation-room/README.md": (322, "b8fdc3eab319bdc30ac9d04881563019a1a49a1119005fffcb621f7afeeb498c"),
    "situation-room/styles.css": (7799, "ca147a49e00b0a814ab5658eeee48318a3723155cbab8fe3c5d6a4db8e3b89c0"),
}

REQUIRED_ROOT_TEXT = {
    "situation-room/",
    "1,600 SR-8R1 rows",
    "777 / 1,600",
    "Frontier-provider result",
    "4,800-row campaign",
    "kevinadriancervantes@gmail.com",
    "https://www.linkedin.com/in/kevinadriancervantes/",
    "CONTEST_SUBMISSION = NOT_PERFORMED",
}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def payload_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in EXCLUDED_FROM_MANIFEST:
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix())


def records(paths: list[Path]) -> list[dict[str, object]]:
    return [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in paths
    ]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if value and ((tag == "a" and key == "href") or (tag in {"img", "script", "link"} and key in {"src", "href"})):
                self.links.append(value)


def local_link_failures() -> list[str]:
    failures: list[str] = []
    for html_path in sorted(ROOT.rglob("*.html")):
        if ".git" in html_path.parts:
            continue
        parser = LinkParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        for raw in parser.links:
            split = urlsplit(raw)
            if split.scheme in {"http", "https", "mailto", "tel", "data"} or raw.startswith("#"):
                continue
            target_text = unquote(split.path)
            if not target_text:
                continue
            target = ROOT / target_text.lstrip("/") if target_text.startswith("/") else html_path.parent / target_text
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                failures.append(f"{html_path.relative_to(ROOT).as_posix()} -> {raw}")
    return failures


def privacy_hits() -> list[str]:
    text_suffixes = {".html", ".css", ".js", ".json", ".md", ".txt", ".csv", ".py", ".xml"}
    patterns = {
        "windows_private_path": re.compile(r"[A-Za-z]:\\(?:Users|Workspace)\\", re.IGNORECASE),
        "unix_private_path": re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/"),
        "github_token": re.compile(r"gh[opsu]_[A-Za-z0-9]{20,}"),
        "google_api_key": re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
        "anthropic_api_key": re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
        "private_ipv4": re.compile(r"(?<![0-9])(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3})(?![0-9])"),
    }
    hits: list[str] = []
    for path in payload_files():
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, pattern in patterns.items():
            if pattern.search(text):
                hits.append(f"{name}:{path.relative_to(ROOT).as_posix()}")
    return hits


def verify() -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})

    frozen_results = {}
    for rel, (expected_bytes, expected_hash) in FROZEN.items():
        path = ROOT / rel
        actual = (path.stat().st_size, sha256_file(path)) if path.exists() else (None, None)
        frozen_results[rel] = {"expected": [expected_bytes, expected_hash], "actual": list(actual)}
    add("five frozen SR-11R1 artifacts", all(tuple(item["actual"]) == tuple(item["expected"]) for item in frozen_results.values()), frozen_results)

    receipt = META / "authority-receipt.json"
    receipt_hash_text = (META / "authority-receipt.sha256").read_text(encoding="ascii").split()[0]
    add("publication authority receipt", receipt.exists() and sha256_file(receipt) == receipt_hash_text, receipt_hash_text)

    root_text = (ROOT / "index.html").read_text(encoding="utf-8")
    missing_root_text = sorted(value for value in REQUIRED_ROOT_TEXT if value not in root_text)
    add("essential homepage integration and contact", not missing_root_text, missing_root_text)
    add("historical noindex/private labels preserved", "noindex,nofollow" in (ROOT / "situation-room/index.html").read_text(encoding="utf-8") and "PRIVATE CANDIDATE" in (ROOT / "situation-room/index.html").read_text(encoding="utf-8"), "frozen labels present")

    link_failures = local_link_failures()
    add("internal links", not link_failures, link_failures)
    privacy = privacy_hits()
    add("public privacy and credential scan", not privacy, privacy)

    if MANIFEST.exists() and MANIFEST_SHA.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        declared_identity = manifest.pop("manifest_identity", None)
        manifest_ok = sha256_bytes(canonical(manifest)) == declared_identity
        file_ok = manifest.get("files") == records(payload_files())
        manifest_sha_ok = sha256_file(MANIFEST) == MANIFEST_SHA.read_text(encoding="ascii").split()[0]
        add("successor publication manifest identity", manifest_ok, declared_identity)
        add("successor full-tree payload", file_ok, f"{len(manifest.get('files', []))} files")
        add("successor manifest file hash", manifest_sha_ok, sha256_file(MANIFEST))
    else:
        add("successor publication manifest", False, "missing")

    if SEAL.exists() and PACKET_SHA.exists():
        seal = json.loads(SEAL.read_text(encoding="utf-8"))
        packet = seal.pop("packet_identity", None)
        packet_ok = sha256_bytes(canonical(seal)) == packet and PACKET_SHA.read_text(encoding="ascii").strip() == packet
        add("successor publication packet", packet_ok, packet)
        add("submission firewall", seal.get("chinatalk_submission") == "NOT_PERFORMED", seal.get("chinatalk_submission"))
    else:
        add("successor publication packet", False, "missing")

    status = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    return {"schema_version": "parallax.situation-room-publication-verification.v1", "status": status, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "PASS" else 1)
