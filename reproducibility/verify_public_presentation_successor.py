#!/usr/bin/env python3
"""Verify the Parallax public-presentation successor without network or model calls."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "publication" / "public-presentation-successor-v1"
MANIFEST = META / "release-manifest.json"
MANIFEST_SHA = META / "release-manifest.sha256"
SEAL = META / "release-seal.json"
PACKET_SHA = META / "release-packet.sha256"
EXCLUDED = {
    "publication/public-presentation-successor-v1/release-manifest.json",
    "publication/public-presentation-successor-v1/release-manifest.sha256",
    "publication/public-presentation-successor-v1/release-seal.json",
    "publication/public-presentation-successor-v1/release-packet.sha256",
}
FROZEN = {
    "situation-room/provenance/sr11r1-frozen/app.js": (21319, "21dcf31c2bd61ccdb73a3de9877150067b21c95a7dc81ce9c79b15af414cc1e0"),
    "situation-room/provenance/sr11r1-frozen/data/data.json": (788968, "db107bf3c2080f431d0eaaee044b09d63af3f8e4b349c2c85f2110289cdfd9c0"),
    "situation-room/provenance/sr11r1-frozen/index.html": (2016, "012aacd2f2334d5c60999f9c944aedcd79ca625b58b84cce473701fd5695b1ab"),
    "situation-room/provenance/sr11r1-frozen/README.md": (322, "b8fdc3eab319bdc30ac9d04881563019a1a49a1119005fffcb621f7afeeb498c"),
    "situation-room/provenance/sr11r1-frozen/styles.css": (7799, "ca147a49e00b0a814ab5658eeee48318a3723155cbab8fe3c5d6a4db8e3b89c0"),
}
CURRENT_DOCS = [
    "README.md", "index.html", "reproduce/index.html", "reproducibility/README.md",
    "research/narrative/index.html", "experiments/index.html", "experiments/experiment-3/index.html",
    "evidence/local-surrogate-summary/index.html", "governance/claim-firewall/index.html",
    "proposal/index.html", "situation-room/index.html", "situation-room/app.js", "situation-room/README.md",
]


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def payload_files() -> list[Path]:
    return sorted(
        [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts and p.relative_to(ROOT).as_posix() not in EXCLUDED],
        key=lambda p: p.relative_to(ROOT).as_posix(),
    )


def records(paths: list[Path]) -> list[dict[str, object]]:
    return [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha_file(p)} for p in paths]


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.items: list[str] = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if value and ((tag == "a" and key == "href") or (tag in {"img", "script", "link"} and key in {"src", "href"})):
                self.items.append(value)


def link_failures() -> list[str]:
    failures: list[str] = []
    for html in sorted(ROOT.rglob("*.html")):
        if ".git" in html.parts: continue
        parser = Links(); parser.feed(html.read_text(encoding="utf-8"))
        for raw in parser.items:
            split = urlsplit(raw)
            if split.scheme in {"http", "https", "mailto", "tel", "data"} or raw.startswith("#"): continue
            target_text = unquote(split.path)
            if not target_text: continue
            target = ROOT / target_text.lstrip("/") if target_text.startswith("/") else html.parent / target_text
            if target.is_dir(): target = target / "index.html"
            if not target.exists(): failures.append(f"{html.relative_to(ROOT).as_posix()} -> {raw}")
    return failures


def privacy_hits() -> list[str]:
    suffixes = {".html", ".css", ".js", ".json", ".md", ".txt", ".csv", ".py", ".xml"}
    patterns = {
        "private_path": re.compile(r"(?:[A-Za-z]:\\(?:Users|Workspace)\\|/(?:Users|home)/[A-Za-z0-9._-]+/)", re.I),
        "credential": re.compile(r"(?:gh[opsu]_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|sk-ant-[A-Za-z0-9_-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"),
        "authorization_header": re.compile(r"Authorization\s*:\s*(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{8,}", re.I),
        "private_ipv4": re.compile(r"(?<![0-9])(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3})(?![0-9])"),
        "mac_address": re.compile(r"\b[0-9A-F]{2}(?::[0-9A-F]{2}){5}\b", re.I),
    }
    hits: list[str] = []
    for path in payload_files():
        if path.suffix.lower() not in suffixes: continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, pattern in patterns.items():
            if pattern.search(text): hits.append(f"{name}:{path.relative_to(ROOT).as_posix()}")
    return hits


def verify() -> dict[str, object]:
    checks: list[dict[str, object]] = []
    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})

    frozen = {}
    for rel, expected in FROZEN.items():
        p = ROOT / rel; actual = (p.stat().st_size, sha_file(p)) if p.exists() else (None, None)
        frozen[rel] = {"expected": list(expected), "actual": list(actual)}
    add("frozen SR-11R1 artifacts", all(v["expected"] == v["actual"] for v in frozen.values()), frozen)
    add("current evidence projection unchanged", sha_file(ROOT / "situation-room/data/data.json") == FROZEN["situation-room/provenance/sr11r1-frozen/data/data.json"][1], sha_file(ROOT / "situation-room/data/data.json"))

    current = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in CURRENT_DOCS)
    shell = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in ["situation-room/index.html", "situation-room/app.js", "situation-room/README.md"])
    stale = [s for s in ["PRIVATE CANDIDATE", "PRIVATE STATIC DERIVATIVE", "NO PUBLICATION AUTHORITY", "no publication authority", "no submission authority"] if s in shell]
    add("current public shell has no stale private/candidate state", not stale, stale)
    historical = (ROOT / "situation-room/provenance/sr11r1-frozen/index.html").read_text(encoding="utf-8")
    add("historical status labels preserved", "PRIVATE CANDIDATE" in historical and "no publication or submission authority" in historical and "noindex,nofollow" in historical, "preserved at frozen route")
    add("one current verifier", "python reproducibility/verify_public_presentation_successor.py" in current and "python reproducibility/verify_public_release.py" not in current, "verify_public_presentation_successor.py")
    required = ["1,600", "823", "777", "4,800", "never pooled", "No frontier-provider scientific result", "No operational-utility evidence", "Human domain validation", "identity-masking diagnostic", "not used as an answer key", "no prospective behavioral-equivalence threshold", "556,200", "unfunded"]
    missing = [s for s in required if s.casefold() not in current.casefold()]
    add("required scientific caveats visible", not missing, missing)
    add("campaign hierarchy explicit", "Current Situation Room evidence" in current and "Earlier surrogate stress evidence" in current and "never pooled" in current, "1600 governing / 4800 predecessor")
    add("submission states separated", "submitted" in current.casefold() and "not advanced" in current.casefold() and "September 1 Situation Room" in current and "not submitted" in current.casefold(), "August historical / September unsubmitted")
    add("internal links", not (links := link_failures()), links)
    add("privacy and credential scan", not (privacy := privacy_hits()), privacy)

    invariance_path = META / "scientific-invariance.json"
    if invariance_path.exists():
        inv = json.loads(invariance_path.read_text(encoding="utf-8")); mismatches=[]
        for rec in inv.get("files", []):
            p=ROOT/rec["path"]
            if not p.exists() or sha_file(p)!=rec["sha256"] or p.stat().st_size!=rec["bytes"]: mismatches.append(rec["path"])
        add("scientific invariance ledger", not mismatches and inv.get("changed_scientific_files")==[], mismatches or inv.get("changed_scientific_files"))
    else: add("scientific invariance ledger", False, "missing")

    if MANIFEST.exists() and MANIFEST_SHA.exists():
        manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); declared=manifest.pop("manifest_identity",None)
        add("manifest identity", sha_bytes(canonical(manifest))==declared, declared)
        add("full-tree payload", manifest.get("files")==records(payload_files()), f"{len(manifest.get('files',[]))} files")
        add("manifest file hash", sha_file(MANIFEST)==MANIFEST_SHA.read_text(encoding="ascii").split()[0], sha_file(MANIFEST))
    else: add("release manifest", False, "missing")
    if SEAL.exists() and PACKET_SHA.exists():
        seal=json.loads(SEAL.read_text(encoding="utf-8")); packet=seal.pop("packet_identity",None)
        add("release packet", sha_bytes(canonical(seal))==packet and PACKET_SHA.read_text(encoding="ascii").strip()==packet, packet)
        add("submission firewall", seal.get("september_1_submission")=="NOT_PERFORMED", seal.get("september_1_submission"))
    else: add("release packet", False, "missing")
    status="PASS" if all(x["status"]=="PASS" for x in checks) else "FAIL"
    return {"schema_version":"parallax.public-presentation-successor-verification.v1","status":status,"checks":checks}


if __name__ == "__main__":
    result=verify(); print(json.dumps(result,indent=2,ensure_ascii=False)); sys.exit(0 if result["status"]=="PASS" else 1)
