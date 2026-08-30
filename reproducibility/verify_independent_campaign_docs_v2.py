#!/usr/bin/env python3
"""Verify the P1-corrected Sep-1 documentation successor offline."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from verify_independent_campaign_docs import FROZEN, claim_firewall, markdown_link_failures
from verify_policy_reader_presentation import link_failures

ROOT = Path(__file__).resolve().parents[1]
ENTERING_COMMIT = "b861fec49b0086a01abdd0213d7060c173fac940"
ENTERING_TREE = "59efa7641f45334550c6c63d64ba46ab4bbb5703"
META = ROOT / "publication" / "sep1-independent-campaign-docs-v2"
AUTHORITY = META / "authority-receipt.json"
AUTHORITY_SHA = META / "authority-receipt.sha256"
INVARIANCE = META / "scientific-invariance.json"
MANIFEST = META / "release-manifest.json"
MANIFEST_SHA = META / "release-manifest.sha256"
SEAL = META / "release-seal.json"
SEAL_SHA = META / "release-seal.sha256"
PACKET_SHA = META / "release-packet.sha256"

CHANGED = ("README.md", "reproducibility/README.md", "reproduce/index.html")
CONTENT_FILES = (*CHANGED, "reproducibility/verify_independent_campaign_docs_v2.py", "reproducibility/seal_independent_campaign_docs_v2.py")
META_FILES = tuple(f"publication/sep1-independent-campaign-docs-v2/{name}" for name in (
    "authority-receipt.json", "authority-receipt.sha256", "scientific-invariance.json",
    "release-manifest.json", "release-manifest.sha256", "release-seal.json",
    "release-seal.sha256", "release-packet.sha256",
))
V1_HASHES = {
    "reproducibility/verify_independent_campaign_docs.py": "bedaa846e98260308edfab90a14c8be7d56316108bd53e1425c2c4396c3a0f62",
    "reproducibility/seal_independent_campaign_docs.py": "7021adc2ed038928ed080453f22dec4598185b8a097256c7cd2c4d43030b229e",
    "publication/sep1-independent-campaign-docs-v1/authority-receipt.json": "558e9096dd9873e753668de64415cd9caa6096991a3080dec7f798b9e63f366d",
    "publication/sep1-independent-campaign-docs-v1/release-manifest.json": "2df3fb21675cf374539842902931f6681653ac2c5fe275be1ca6c4c9cf1339de",
    "publication/sep1-independent-campaign-docs-v1/release-seal.json": "d98b3e70a59a41467fd4fcc2a4cd2049b988b2aec8fab8b2eddbbbbe8c683d28",
    "publication/sep1-independent-campaign-docs-v1/release-packet.sha256": "5b3486979c13d09bc251286086b592ecb9aba10af3be793b6445f50d47e00c99",
}
OLD = "verify_policy_reader_presentation.py"
NEW = "verify_independent_campaign_docs_v2.py"


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


def baseline_mismatches() -> list[str]:
    return [name for name in baseline_paths() if name not in CHANGED and ((not (ROOT / name).exists()) or (ROOT / name).read_bytes() != baseline_bytes(name))]


def exact_command_repairs() -> dict[str, bool]:
    checks = {}
    for name in CHANGED:
        before = baseline_bytes(name).decode("utf-8")
        expected = before.replace(OLD, NEW)
        if name == "reproducibility/README.md":
            expected = expected.replace(
                "- the full public release manifest, packet, and file hashes;",
                "- the preserved public-presentation release and additive documentation packet;\n- the current documentation manifest, packet, and file hashes;",
            ).replace(
                "The current verifier is for this public presentation successor. Predecessor\nverifiers remain preserved for their original releases.",
                "The current verifier covers the public presentation plus the additive\nindependent-campaign documentation successor. Predecessor verifiers remain\npreserved for their original release commits.",
            )
        checks[name] = (ROOT / name).read_text(encoding="utf-8") == expected
    return checks


def records(paths: tuple[str, ...] | list[str]) -> list[dict[str, object]]:
    return [{"path": name, "bytes": (ROOT / name).stat().st_size, "sha256": sha_file(ROOT / name)} for name in sorted(paths)]


def all_files() -> set[str]:
    return {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts}


def unapproved_new_files() -> list[str]:
    return sorted(all_files() - (set(baseline_paths()) | set(CONTENT_FILES) | set(META_FILES)))


def privacy_hits() -> list[str]:
    patterns = (
        re.compile(r"(?:[A-Za-z]:\\(?:Users|Workspace)\\|/(?:Users|home)/[A-Za-z0-9._-]+/)", re.I),
        re.compile(r"(?:gh[opsu]_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|sk-ant-[A-Za-z0-9_-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"),
        re.compile(r"Authorization\s*:\s*(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{8,}", re.I),
    )
    hits = []
    for name in CONTENT_FILES:
        text = (ROOT / name).read_text(encoding="utf-8", errors="replace")
        if any(pattern.search(text) for pattern in patterns):
            hits.append(name)
    return hits


def verify(*, require_release: bool) -> dict[str, object]:
    checks = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})

    add("entering docs-v1 commit is ancestor", subprocess.run(["git", "merge-base", "--is-ancestor", ENTERING_COMMIT, "HEAD"], cwd=ROOT).returncode == 0, git("rev-parse", "HEAD"))
    add("entering docs-v1 tree", git("rev-parse", f"{ENTERING_COMMIT}^{{tree}}") == ENTERING_TREE, ENTERING_TREE)
    add("docs-v1 predecessor unchanged outside exact repair", not (mismatches := baseline_mismatches()), mismatches)
    repairs = exact_command_repairs()
    add("exact stale-command repair only", all(repairs.values()), repairs)
    add("only approved additive files", not (extra := unapproved_new_files()), extra)
    add("docs-v1 identities preserved", {name: sha_file(ROOT / name) for name in V1_HASHES} == V1_HASHES, V1_HASHES)
    add("frozen SR-11R1 identities", {name: sha_file(ROOT / name) for name in FROZEN} == FROZEN, FROZEN)
    add("current command everywhere", all(NEW in (ROOT / name).read_text(encoding="utf-8") and OLD not in (ROOT / name).read_text(encoding="utf-8") for name in CHANGED), list(CHANGED))
    add("Markdown links", not (md_links := markdown_link_failures()), md_links)
    add("all local HTML links", not (html_links := link_failures()), html_links)
    firewall = claim_firewall()
    add("documentation functionality firewall", not firewall["violations"] and all(firewall["positive_checks"].values()), firewall)
    add("privacy and credential scan", not (privacy := privacy_hits()), privacy)
    add("no license selected", not any((ROOT / name).exists() for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")), "unresolved")

    if require_release:
        required = [AUTHORITY, AUTHORITY_SHA, INVARIANCE, MANIFEST, MANIFEST_SHA, SEAL, SEAL_SHA, PACKET_SHA]
        add("v2 release records", all(path.exists() for path in required), [path.relative_to(ROOT).as_posix() for path in required])
        if all(path.exists() for path in required):
            authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))
            content_commit = authority.get("documentation_content_commit", "")
            ancestor = bool(content_commit) and subprocess.run(["git", "merge-base", "--is-ancestor", content_commit, "HEAD"], cwd=ROOT).returncode == 0
            add("v2 authority and content commit", authority.get("entering_commit") == ENTERING_COMMIT and ancestor, authority)
            add("v2 authority hash", sha_file(AUTHORITY) == AUTHORITY_SHA.read_text(encoding="ascii").split()[0], sha_file(AUTHORITY))
            content_bad = []
            for name in CONTENT_FILES:
                try:
                    committed = subprocess.check_output(["git", "show", f"{content_commit}:{name}"], cwd=ROOT)
                except subprocess.CalledProcessError:
                    content_bad.append(name)
                    continue
                if committed != (ROOT / name).read_bytes():
                    content_bad.append(name)
            add("sealed v2 content commit", not content_bad, content_bad)
            invariance = json.loads(INVARIANCE.read_text(encoding="utf-8"))
            add("v2 scientific/frozen invariance", invariance.get("baseline_mismatches") == [] and invariance.get("scientific_files_changed") == 0 and invariance.get("frozen_files_changed") == 0, invariance)
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); declared = manifest.pop("manifest_identity", None)
            add("v2 manifest identity", sha_bytes(canonical(manifest)) == declared and manifest.get("files") == records(list(CONTENT_FILES)), declared)
            add("v2 manifest hash", sha_file(MANIFEST) == MANIFEST_SHA.read_text(encoding="ascii").split()[0], sha_file(MANIFEST))
            seal = json.loads(SEAL.read_text(encoding="utf-8")); packet = seal.pop("packet_identity", None)
            add("v2 packet identity", sha_bytes(canonical(seal)) == packet and PACKET_SHA.read_text(encoding="ascii").strip() == packet, packet)
            add("v2 seal hash", sha_file(SEAL) == SEAL_SHA.read_text(encoding="ascii").split()[0], sha_file(SEAL))
            add("zero science/execution/submission", all(seal.get(field) == 0 for field in ("scientific_files_changed", "frozen_files_changed", "new_execution_functionality", "model_calls", "provider_calls", "scientific_calls", "campaigns_created", "seeds_generated", "seeds_committed", "licenses_selected")) and seal.get("contest_submission") == "NOT_PERFORMED", seal)

    status = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    return {"schema_version": "parallax.sep1-independent-campaign-docs-verification.v2", "status": status, "checks": checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--preseal", action="store_true"); args = parser.parse_args()
    result = verify(require_release=not args.preseal)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "PASS" else 1)
