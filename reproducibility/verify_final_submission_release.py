#!/usr/bin/env python3
"""Verify the final Sep-1 submission successor and its single copy repair."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from verify_independent_campaign_docs_v2 import FROZEN, claim_firewall, markdown_link_failures
from verify_policy_reader_presentation import link_failures

ROOT = Path(__file__).resolve().parents[1]
ENTERING_COMMIT = "b21ff52fcef41f8400b4b27cb7f2b36a7331615a"
ENTERING_TREE = "df88dcd7b5926de50ad2ba53787453c0c18fb409"
META = ROOT / "publication" / "sep1-final-submission-v1"
AUTHORITY = META / "authority-receipt.json"
AUTHORITY_SHA = META / "authority-receipt.sha256"
INVARIANCE = META / "scientific-invariance.json"
MANIFEST = META / "release-manifest.json"
MANIFEST_SHA = META / "release-manifest.sha256"
SEAL = META / "release-seal.json"
SEAL_SHA = META / "release-seal.sha256"
PACKET_SHA = META / "release-packet.sha256"

REPAIRED = ("README.md", "reproducibility/README.md", "reproduce/index.html", "index.html")
CONTENT_FILES = (*REPAIRED, "submission/sep1-final-form-draft.md", "reproducibility/verify_final_submission_release.py", "reproducibility/seal_final_submission_release.py")
META_FILES = tuple(f"publication/sep1-final-submission-v1/{name}" for name in (
    "authority-receipt.json", "authority-receipt.sha256", "scientific-invariance.json",
    "release-manifest.json", "release-manifest.sha256", "release-seal.json",
    "release-seal.sha256", "release-packet.sha256",
))
OLD_VERIFIER = "verify_independent_campaign_docs_v2.py"
NEW_VERIFIER = "verify_final_submission_release.py"
OLD_LABEL = "<strong>Claude/Gemini science:</strong> not run."
NEW_LABEL = "<strong>Experiment 3 Claude/Gemini science:</strong> not run."


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def baseline_paths() -> list[str]:
    return git("ls-tree", "-r", "--name-only", ENTERING_COMMIT).splitlines()


def baseline_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{ENTERING_COMMIT}:{path}"], cwd=ROOT)


def expected_repaired(path: str) -> bytes:
    before = baseline_bytes(path).decode("utf-8")
    if path == "index.html":
        return before.replace(OLD_LABEL, NEW_LABEL).encode("utf-8")
    return before.replace(OLD_VERIFIER, NEW_VERIFIER).encode("utf-8")


def baseline_mismatches() -> list[str]:
    return [name for name in baseline_paths() if name not in REPAIRED and (
        not (ROOT / name).exists() or (ROOT / name).read_bytes() != baseline_bytes(name)
    )]


def repaired_matches() -> dict[str, bool]:
    return {name: (ROOT / name).read_bytes() == expected_repaired(name) for name in REPAIRED}


def all_files() -> set[str]:
    return {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts}


def unapproved_new_files() -> list[str]:
    return sorted(all_files() - (set(baseline_paths()) | set(CONTENT_FILES) | set(META_FILES)))


def privacy_hits() -> list[str]:
    patterns = (
        re.compile(r"(?:[A-Za-z]:\\(?:Users|Workspace)\\|/(?:Users|home)/[A-Za-z0-9._-]+/)", re.I),
        re.compile(r"(?:gh[opsu]_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|sk-ant-[A-Za-z0-9_-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"),
        re.compile(r"Authorization\s*:\s*(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{8,}", re.I),
    )
    hits = []
    for name in sorted(all_files()):
        path = ROOT / name
        if path.suffix.lower() not in {".md", ".html", ".py", ".json", ".txt", ".xml", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(pattern.search(text) for pattern in patterns):
            hits.append(name)
    return hits


def records(paths: tuple[str, ...] | list[str]) -> list[dict[str, object]]:
    return [{"path": name, "bytes": (ROOT / name).stat().st_size, "sha256": sha_file(ROOT / name)} for name in sorted(paths)]


def verify(*, require_release: bool) -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})

    add("accepted capstone commit is ancestor", subprocess.run(["git", "merge-base", "--is-ancestor", ENTERING_COMMIT, "HEAD"], cwd=ROOT).returncode == 0, git("rev-parse", "HEAD"))
    add("accepted capstone tree", git("rev-parse", f"{ENTERING_COMMIT}^{{tree}}") == ENTERING_TREE, ENTERING_TREE)
    add("predecessor unchanged outside bounded repair", not (bad := baseline_mismatches()), bad)
    repairs = repaired_matches()
    add("exact one-copy repair and current verifier references", all(repairs.values()), repairs)
    add("only approved additive files", not (extra := unapproved_new_files()), extra)
    add("frozen SR-11R1 identities", {name: sha_file(ROOT / name) for name in FROZEN} == FROZEN, FROZEN)
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    add("Experiment 3 label is scoped", NEW_LABEL in index and OLD_LABEL not in index, {"present": NEW_LABEL in index, "unscoped_absent": OLD_LABEL not in index})
    add("Experiment 1 and 2 history remains visible", "Experiments 1 and 2" in index or "Experiment 1" in index and "Experiment 2" in index, "historical sections retained")
    add("current verifier references", all(NEW_VERIFIER in (ROOT / name).read_text(encoding="utf-8") and OLD_VERIFIER not in (ROOT / name).read_text(encoding="utf-8") for name in ("README.md", "reproducibility/README.md", "reproduce/index.html")), NEW_VERIFIER)
    form = (ROOT / "submission/sep1-final-form-draft.md").read_text(encoding="utf-8")
    add("human submission packet is prepared, not submitted", all(token in form for token in ("6,674,400 known-ground-truth synthetic evaluations", "HUMAN DECISION REQUIRED", "NOT PERFORMED")) and "independent oracles" not in form, "employment left human-decided")
    add("Markdown links", not (md := markdown_link_failures()), md)
    add("local HTML links", not (html := link_failures()), html)
    firewall = claim_firewall()
    add("claim firewall", not firewall["violations"] and all(firewall["positive_checks"].values()), firewall)
    add("privacy and credential scan", not (privacy := privacy_hits()), privacy)
    add("no license selected", not any((ROOT / name).exists() for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")), "unresolved")

    if require_release:
        required = [AUTHORITY, AUTHORITY_SHA, INVARIANCE, MANIFEST, MANIFEST_SHA, SEAL, SEAL_SHA, PACKET_SHA]
        add("final release records", all(path.exists() for path in required), [p.relative_to(ROOT).as_posix() for p in required])
        if all(path.exists() for path in required):
            authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))
            content_commit = authority.get("submission_content_commit", "")
            ancestor = bool(content_commit) and subprocess.run(["git", "merge-base", "--is-ancestor", content_commit, "HEAD"], cwd=ROOT).returncode == 0
            add("authority and content commit", authority.get("entering_commit") == ENTERING_COMMIT and ancestor, authority)
            add("authority hash", sha_file(AUTHORITY) == AUTHORITY_SHA.read_text(encoding="ascii").split()[0], sha_file(AUTHORITY))
            content_bad = []
            for name in CONTENT_FILES:
                try:
                    committed = subprocess.check_output(["git", "show", f"{content_commit}:{name}"], cwd=ROOT)
                except subprocess.CalledProcessError:
                    content_bad.append(name)
                    continue
                if committed != (ROOT / name).read_bytes():
                    content_bad.append(name)
            add("sealed final content commit", not content_bad, content_bad)
            invariance = json.loads(INVARIANCE.read_text(encoding="utf-8"))
            add("scientific and frozen invariance", invariance.get("baseline_mismatches") == [] and invariance.get("scientific_files_changed") == 0 and invariance.get("frozen_files_changed") == 0, invariance)
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); declared_manifest = manifest.pop("manifest_identity", None)
            add("manifest identity", sha_bytes(canonical(manifest)) == declared_manifest and manifest.get("files") == records(list(CONTENT_FILES)), declared_manifest)
            add("manifest hash", sha_file(MANIFEST) == MANIFEST_SHA.read_text(encoding="ascii").split()[0], sha_file(MANIFEST))
            seal = json.loads(SEAL.read_text(encoding="utf-8")); declared_packet = seal.pop("packet_identity", None)
            add("packet identity", sha_bytes(canonical(seal)) == declared_packet and PACKET_SHA.read_text(encoding="ascii").strip() == declared_packet, declared_packet)
            add("seal hash", sha_file(SEAL) == SEAL_SHA.read_text(encoding="ascii").split()[0], sha_file(SEAL))
            zero = all(seal.get(field) == 0 for field in ("scientific_files_changed", "frozen_files_changed", "data_projection_changed", "classification_changes", "threshold_changes", "analysis_changes", "model_calls", "provider_calls", "scientific_calls", "campaigns_created", "seeds_generated", "byom_functionality_added", "license_selected"))
            add("zero science/execution/submission", zero and seal.get("contest_submission") == "NOT_PERFORMED", seal)

    return {"schema_version": "parallax.sep1-final-submission-release-verification.v1", "status": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL", "checks": checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--preseal", action="store_true"); args = parser.parse_args()
    result = verify(require_release=not args.preseal)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
