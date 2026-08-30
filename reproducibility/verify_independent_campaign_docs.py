#!/usr/bin/env python3
"""Verify the additive independent-campaign documentation successor offline."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ENTERING_COMMIT = "bce5a409ad9c8b21d0eda38a9346fff5006171a5"
ENTERING_TREE = "bf41ae61d7c2df833fba0bf6cad36ae51789eaca"
META = ROOT / "publication" / "sep1-independent-campaign-docs-v1"
AUTHORITY = META / "authority-receipt.json"
AUTHORITY_SHA = META / "authority-receipt.sha256"
INVARIANCE = META / "scientific-invariance.json"
MANIFEST = META / "release-manifest.json"
MANIFEST_SHA = META / "release-manifest.sha256"
SEAL = META / "release-seal.json"
SEAL_SHA = META / "release-seal.sha256"
PACKET_SHA = META / "release-packet.sha256"

DOCS = (
    "docs/independent-campaigns.md",
    "docs/adapter-contract.md",
    "docs/campaign-manifest.md",
    "docs/security-and-credentials.md",
)
CONTENT_FILES = (
    "README.md",
    *DOCS,
    "reproducibility/verify_independent_campaign_docs.py",
    "reproducibility/seal_independent_campaign_docs.py",
)
META_FILES = (
    "publication/sep1-independent-campaign-docs-v1/authority-receipt.json",
    "publication/sep1-independent-campaign-docs-v1/authority-receipt.sha256",
    "publication/sep1-independent-campaign-docs-v1/scientific-invariance.json",
    "publication/sep1-independent-campaign-docs-v1/release-manifest.json",
    "publication/sep1-independent-campaign-docs-v1/release-manifest.sha256",
    "publication/sep1-independent-campaign-docs-v1/release-seal.json",
    "publication/sep1-independent-campaign-docs-v1/release-seal.sha256",
    "publication/sep1-independent-campaign-docs-v1/release-packet.sha256",
)
PREDECESSOR_HASHES = {
    "reproducibility/verify_policy_reader_presentation.py": "de3f4277aaf0cfceb1bdf9f5568d3a9d589e255515076582566dbe41a3bcd3ba",
    "publication/policy-reader-presentation-v1/release-manifest.json": "a1289d5141daa517ac9531eaa87287ded7fefb5cebc67aeb46d670518ac1ce9e",
    "publication/policy-reader-presentation-v1/release-seal.json": "92ae3feacc204ca14f7fc810afe85f12ff7e0739f96f1d7618150426d7e24ec4",
    "publication/policy-reader-presentation-v1/release-packet.sha256": "242f5c59f8063db1febb031e60c41f206250477bea9282ec314a5e088ef8b534",
    "publication/policy-reader-presentation-v1/authority-receipt.json": "1f9582620864a5d078f027f86b643347180fcf01a30091591bd00661815efd36",
    "publication/policy-reader-presentation-v1/scientific-invariance.json": "44cf0af5012066d827b4da6ba91d14e248ddcca21d91df194043388794d94033",
}
FROZEN = {
    "situation-room/provenance/sr11r1-frozen/app.js": "21dcf31c2bd61ccdb73a3de9877150067b21c95a7dc81ce9c79b15af414cc1e0",
    "situation-room/provenance/sr11r1-frozen/data/data.json": "db107bf3c2080f431d0eaaee044b09d63af3f8e4b349c2c85f2110289cdfd9c0",
    "situation-room/provenance/sr11r1-frozen/index.html": "012aacd2f2334d5c60999f9c944aedcd79ca625b58b84cce473701fd5695b1ab",
    "situation-room/provenance/sr11r1-frozen/README.md": "b8fdc3eab319bdc30ac9d04881563019a1a49a1119005fffcb621f7afeeb498c",
    "situation-room/provenance/sr11r1-frozen/styles.css": "ca147a49e00b0a814ab5658eeee48318a3723155cbab8fe3c5d6a4db8e3b89c0",
}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, encoding="utf-8"
    ).strip()


def baseline_paths() -> list[str]:
    return git("ls-tree", "-r", "--name-only", ENTERING_COMMIT).splitlines()


def baseline_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{ENTERING_COMMIT}:{path}"], cwd=ROOT)


def immutable_baseline_mismatches() -> list[str]:
    mismatches: list[str] = []
    for path in baseline_paths():
        if path == "README.md":
            continue
        current = ROOT / path
        if not current.exists() or current.read_bytes() != baseline_bytes(path):
            mismatches.append(path)
    return mismatches


def records(paths: tuple[str, ...] | list[str]) -> list[dict[str, object]]:
    result = []
    for name in sorted(paths):
        path = ROOT / name
        result.append({"path": name, "bytes": path.stat().st_size, "sha256": sha_file(path)})
    return result


def all_files() -> set[str]:
    return {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts
    }


def unapproved_new_files() -> list[str]:
    allowed = set(baseline_paths()) | set(CONTENT_FILES) | set(META_FILES)
    return sorted(all_files() - allowed)


def markdown_link_failures() -> list[str]:
    failures: list[str] = []
    pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for name in ("README.md", *DOCS):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        for raw in pattern.findall(text):
            target = raw.split("#", 1)[0].strip()
            if not target or urlsplit(target).scheme or target.startswith("#"):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                failures.append(f"{name} -> {raw}: outside repository")
                continue
            if not resolved.exists():
                failures.append(f"{name} -> {raw}: missing")
    return failures


def privacy_hits() -> list[str]:
    patterns = {
        "private_path": re.compile(r"(?:[A-Za-z]:\\(?:Users|Workspace)\\|/(?:Users|home)/[A-Za-z0-9._-]+/)", re.I),
        "credential": re.compile(r"(?:gh[opsu]_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|sk-ant-[A-Za-z0-9_-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"),
        "authorization": re.compile(r"Authorization\s*:\s*(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{8,}", re.I),
    }
    hits: list[str] = []
    for name in CONTENT_FILES:
        text = (ROOT / name).read_text(encoding="utf-8", errors="replace")
        for label, pattern in patterns.items():
            if pattern.search(text):
                hits.append(f"{label}:{name}")
    return hits


def claim_firewall() -> dict[str, object]:
    text = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in ("README.md", *DOCS))
    lower = text.lower()
    normalized = re.sub(r"\s+", " ", lower.replace("**", "")).strip()
    unsupported_present_tense = {
        "unqualified bring-your-own-model": re.compile(r"parallax (?:supports|provides|offers) (?:a )?bring your own model", re.I),
        "run-any-model": re.compile(r"(?:you|evaluators?) can run (?:parallax (?:against|with) )?any model", re.I),
        "provider-agnostic": re.compile(r"parallax is provider[- ]agnostic", re.I),
        "openai-support": re.compile(r"parallax supports openai-compatible endpoints", re.I),
        "independent-e3-execution": re.compile(r"independent evaluators can (?:run|execute) experiment 3", re.I),
        "internal-government-support": re.compile(r"parallax (?:supports|can evaluate) internal government models", re.I),
    }
    violations = [name for name, pattern in unsupported_present_tense.items() if pattern.search(text)]
    positives = {
        "execution absent": "does not provide a general-purpose independent campaign runner" in normalized,
        "future architecture": "future extension contract" in normalized,
        "one-model limitation": "one-model" in normalized and "cannot silently inherit" in normalized,
        "reference geometry": all(token in normalized for token in ("9,270", "278,100", "556,200", "m = 210")),
        "qualification not science": "qualification produces no scientific result" in normalized,
        "demonstration not science": "technical demonstration is not an experiment 3 scientific result" in normalized,
        "reference separated": "cannot overwrite or impersonate the canonical" in normalized,
        "credentials local": "evaluator-local" in normalized,
        "no hosted credential collection": "public-web credential collection" in normalized and "hosted parallax credential proxy" in normalized,
        "license unresolved": "licensing for a future reusable execution kit remains unresolved" in normalized,
        "runner not implemented": "public byom runner = not implemented" in normalized,
    }
    return {"violations": violations, "positive_checks": positives}


def verify(*, require_release: bool) -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})

    head = git("rev-parse", "HEAD")
    add("entering commit is ancestor", subprocess.run(["git", "merge-base", "--is-ancestor", ENTERING_COMMIT, "HEAD"], cwd=ROOT).returncode == 0, head)
    add("entering tree identity", git("rev-parse", f"{ENTERING_COMMIT}^{{tree}}") == ENTERING_TREE, ENTERING_TREE)
    mismatches = immutable_baseline_mismatches()
    add("all predecessor files except README unchanged", not mismatches, mismatches)
    add("only approved additive files", not (extra := unapproved_new_files()), extra)
    add("four architecture documents", all((ROOT / name).is_file() for name in DOCS), list(DOCS))
    add("README links architecture documents", all(name in (ROOT / "README.md").read_text(encoding="utf-8") for name in DOCS), list(DOCS))
    add("documentation links", not (links := markdown_link_failures()), links)

    predecessor = {name: sha_file(ROOT / name) for name in PREDECESSOR_HASHES}
    add("predecessor publication and verifier identities", predecessor == PREDECESSOR_HASHES, predecessor)
    frozen = {name: sha_file(ROOT / name) for name in FROZEN}
    add("frozen SR-11R1 identities", frozen == FROZEN, frozen)
    add("website presentation unchanged", all((ROOT / name).read_bytes() == baseline_bytes(name) for name in baseline_paths() if Path(name).suffix.lower() in {".html", ".css", ".js", ".svg", ".xml"}), "all baseline presentation bytes")

    firewall = claim_firewall()
    add("no unsupported present-tense functionality claims", not firewall["violations"], firewall["violations"])
    add("required documentation claim firewall", all(firewall["positive_checks"].values()), firewall["positive_checks"])
    add("privacy and credential scan", not (privacy := privacy_hits()), privacy)
    add("no public license selected", not any((ROOT / name).exists() for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")), "license remains unresolved")
    add("no execution package introduced", not any((ROOT / name).exists() for name in ("src", "providers", "adapters", "pyproject.toml", "requirements.txt", "package.json")), "documentation/verifier only")
    docs_text = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in DOCS)
    add("no actual seed or campaign identity", not re.search(r'"seed_commitment_sha256"\s*:\s*"[0-9a-f]{64}"', docs_text, re.I) and "<required evaluator-assigned identity>" in docs_text, "placeholders only")

    if require_release:
        required = [AUTHORITY, AUTHORITY_SHA, INVARIANCE, MANIFEST, MANIFEST_SHA, SEAL, SEAL_SHA, PACKET_SHA]
        add("documentation release records", all(path.exists() for path in required), [path.relative_to(ROOT).as_posix() for path in required])
        if all(path.exists() for path in required):
            authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))
            content_commit = authority.get("documentation_content_commit", "")
            content_ancestor = bool(content_commit) and subprocess.run(["git", "merge-base", "--is-ancestor", content_commit, "HEAD"], cwd=ROOT).returncode == 0
            add("authority and content commit", authority.get("entering_commit") == ENTERING_COMMIT and authority.get("scope") == "SEP1_INDEPENDENT_CAMPAIGN_DOCUMENTATION" and content_ancestor, authority)
            add("authority receipt hash", sha_file(AUTHORITY) == AUTHORITY_SHA.read_text(encoding="ascii").split()[0], sha_file(AUTHORITY))
            content_mismatches = []
            for name in CONTENT_FILES:
                try:
                    committed = subprocess.check_output(["git", "show", f"{content_commit}:{name}"], cwd=ROOT)
                except subprocess.CalledProcessError:
                    content_mismatches.append(name)
                    continue
                if committed != (ROOT / name).read_bytes():
                    content_mismatches.append(name)
            add("sealed documentation content commit", not content_mismatches, content_mismatches)
            invariance = json.loads(INVARIANCE.read_text(encoding="utf-8"))
            add("scientific and frozen invariance receipt", invariance.get("baseline_mismatches") == [] and invariance.get("scientific_files_changed") == 0 and invariance.get("frozen_files_changed") == 0, invariance)
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
            declared = manifest.pop("manifest_identity", None)
            add("documentation manifest identity", sha_bytes(canonical(manifest)) == declared and manifest.get("files") == records(list(CONTENT_FILES)), declared)
            add("documentation manifest file hash", sha_file(MANIFEST) == MANIFEST_SHA.read_text(encoding="ascii").split()[0], sha_file(MANIFEST))
            seal = json.loads(SEAL.read_text(encoding="utf-8"))
            packet = seal.pop("packet_identity", None)
            add("documentation packet identity", sha_bytes(canonical(seal)) == packet and PACKET_SHA.read_text(encoding="ascii").strip() == packet, packet)
            add("documentation seal file hash", sha_file(SEAL) == SEAL_SHA.read_text(encoding="ascii").split()[0], sha_file(SEAL))
            add("zero execution mutation", all(seal.get(field) == 0 for field in ("new_execution_functionality", "model_calls", "provider_calls", "scientific_calls", "campaigns_created", "seeds_generated", "seeds_committed", "licenses_selected", "website_files_changed")), seal)
            add("submission not performed", seal.get("contest_submission") == "NOT_PERFORMED", seal.get("contest_submission"))

    status = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    return {"schema_version": "parallax.sep1-independent-campaign-docs-verification.v1", "status": status, "checks": checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preseal", action="store_true", help="verify content before additive release records exist")
    args = parser.parse_args()
    result = verify(require_release=not args.preseal)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "PASS" else 1)
