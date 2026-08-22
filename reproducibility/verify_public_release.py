"""Self-contained no-call verifier for the clean public-release candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "parallax-public-release-manifest.json"
SEAL = ROOT / "parallax-public-release-seal.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(name: str, ok: bool, detail: str):
    return {"name": name, "status": "PASS" if ok else "FAIL", "detail": detail}


def aggregate(files: list[dict]) -> str:
    payload = "".join(f"{entry['path']}\0{entry['sha256']}\n" for entry in files).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    checks = []
    manifest = read(MANIFEST)
    seal = read(SEAL)
    predecessor_manifest_path = ROOT / "predecessor" / "contest-package-manifest.json"
    predecessor_seal_path = ROOT / "predecessor" / "contest-package-seal.json"
    predecessor_manifest = read(predecessor_manifest_path)
    predecessor_seal = read(predecessor_seal_path)

    checks.append(check("predecessor manifest identity", sha(predecessor_manifest_path) == "9b1c4d373320410ff248c067e7be2fb80edaf44f88ed0816bd04f1f4b64f2522", sha(predecessor_manifest_path)))
    checks.append(check("predecessor seal identity", sha(predecessor_seal_path) == "d32450cc9b77f0ddf4c0372a5a75cb3b76e2fab96926a58fd29297af3679599f", sha(predecessor_seal_path)))
    checks.append(check("predecessor aggregate", aggregate(predecessor_manifest["files"]) == predecessor_manifest["packet_sha256"] == "5d7182dd0028c4d748d69f25eedb12c4e0cf4db500246ad4021955d4e9b0b9d5" and predecessor_seal["packet_sha256"] == predecessor_manifest["packet_sha256"], predecessor_manifest["packet_sha256"]))
    checks.append(check("release aggregate", aggregate(manifest["files"]) == manifest["packet_sha256"] == seal["packet_sha256"], manifest["packet_sha256"]))
    checks.append(check("release manifest identity", sha(MANIFEST) == seal["manifest_sha256"], sha(MANIFEST)))
    checks.append(check("release payload hashes", manifest["file_count"] == len(manifest["files"]) and all((ROOT / entry["path"]).is_file() and sha(ROOT / entry["path"]) == entry["sha256"] for entry in manifest["files"]), f"{len(manifest['files'])} payload files"))

    allowlist = read(ROOT / "governance" / "public-release-allowlist.json")
    physical = sorted(path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file())
    allowed = sorted(set(allowlist["PUBLIC"]) | set(allowlist["PUBLIC_SANITIZED"]))
    checks.append(check("physical allowlist", physical == allowed, f"{len(physical)} physical files; exact allowlist"))

    confirm = read(ROOT / "evidence" / "confirmatory-reference-summary.json")
    checks.append(check("confirmatory constants", confirm["providers"] == 2 and confirm["cells_per_provider"] == 30 and confirm["N_execution"] == 9270 and confirm["calls_per_provider"] == 278100 and confirm["total_scheduled_calls"] == 556200 and confirm["M"] == 210 and confirm["alpha_global"] == 0.05 and confirm["full_joint_power_claim"] == "NONE" and confirm["confirmatory_execution"] == "NOT_PERFORMED" and confirm["funding"] == "NOT_SECURED", "2 providers; N=9270; M=210; 556200 calls; no full-joint power"))

    shadow = read(ROOT / "evidence" / "synthetic-shadow-summary.json")
    checks.append(check("synthetic shadow evidence", shadow["world_count"] == 12 and shadow["scheduled_evaluations"] == 6674400 and shadow["all_worlds_match"] is True and shadow["scientific_provider_calls"] == 0 and shadow["real_model_calls"] == 0, "12 worlds; 6,674,400 evaluations; software evidence only"))
    local = read(ROOT / "evidence" / "local-surrogate-summary.json")
    checks.append(check("local accounting", local["attempted"] == 4800 and local["terminal"] == 4800 and local["valid_ordinal"] == 4544 and local["schema_invalid"] == 256 and local["duplicate_attempts"] == 0 and local["replacement_attempts"] == 0 and local["status"] == "ACCEPTED_DESCRIPTIVE_ONLY", "4,800 attempted; 4,544 valid; 256 invalid; descriptive only"))

    qualification = read(ROOT / "evidence" / "provider-qualification-summary.json")
    checks.append(check("qualification boundary", qualification["calls"] == 6 and qualification["scientific_prompts"] == 0 and qualification["confirmatory_calls"] == 0 and qualification["scientific_provider_result"] == "NONE" and qualification["retries"] == 0 and qualification["status"] == "ACCEPTED_NON_SCIENTIFIC_QUALIFICATION", "6 calls; zero scientific prompts; non-scientific only"))
    accounting = read(ROOT / "hardening-accounting-reproduction.json")
    total = sum(Decimal(str(row["cost_usd"])) for row in accounting["rows"] if row.get("cost_usd") is not None)
    checks.append(check("cost arithmetic", total in (Decimal("0.01723375"), Decimal("0.017233750000000003")) and accounting["record_type"] == "DERIVED_ACCOUNTING_METADATA_CORRECTION" and accounting["provider_calls"] == 0 and accounting["outcome_changed"] is False, str(total)))

    claim_text = (ROOT / "governance" / "claim-firewall-review.md").read_text(encoding="utf-8").lower()
    matrix = list(csv.DictReader((ROOT / "governance" / "claim-evidence-matrix.csv").open(encoding="utf-8", newline="")))
    audit = read(ROOT / "governance" / "claim-audit.json")
    prohibited = ["measures whether ai believes evidence", "general strategic competence", "correct strategic policy", "optimal action", "faithful internal reasoning"]
    checks.append(check("claim firewall", "prohibited-claim tests" in claim_text and "not asserted" in claim_text and len(matrix) == 14 and audit["classification_counts"] == {"SUPPORTED": 10, "QUALIFIED": 2, "DESIGN_ONLY": 0, "PROHIBITED": 0, "EDITORIAL_NONSCIENTIFIC": 0} and not any(term in claim_text for term in prohibited), "14 rows; 10 supported; 2 qualified; prohibited rows explicitly tests"))

    failure = (ROOT / "governance" / "failure-semantics.md").read_text(encoding="utf-8").lower()
    checks.append(check("failure and temporal boundary", all(term in failure for term in ["http/api error", "schema failure", "refusal/decline", "not a timeless guarantee", "2026-08-22"]), "distinct failure states and dated qualification"))
    status_text = "\n".join(path.read_text(encoding="utf-8").lower() for path in [ROOT / "README.md", ROOT / "contest-narrative.md", ROOT / "executive-summary.md", ROOT / "reproducibility" / "README.md"])
    checks.append(check("current release status", "public_release_candidate = sealed" in status_text and "confirmatory execution = not performed" in status_text and "scientific provider result = none" in status_text and "baseline = ready_for_pre_submission_local_model_hardening" not in status_text and "verify_public_release.py" in status_text, "sealed candidate; execution absent; canonical command current"))

    privacy = read(ROOT / "governance" / "release-privacy-receipt.json")
    checks.append(check("privacy receipt", privacy["status"] == "PASS" and privacy["violations"] == [] and privacy["physical_tree_files"] == len(physical), "physical tree scan recorded"))
    windows_user_prefix = r"[A-Z]:\\" + "Users" + r"\\"
    posix_user_prefix = "/" + "Users" + "/"
    posix_home_prefix = "/" + "home" + "/"
    secret_patterns = [
        re.compile(r"(?i)(?:" + windows_user_prefix + "|" + re.escape(posix_user_prefix) + "|" + re.escape(posix_home_prefix) + r")[^\s`\"']+"),
        re.compile(r"(?i)sk-ant-[A-Za-z0-9_-]{8,}|AIza[A-Za-z0-9_-]{20,}"),
        re.compile(r"(?i)(?:x-api-key|x-goog-api-key)\s*[:=]\s*[^\s`\"']+"),
        re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{12,}"),
        re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
        re.compile(r"(?i)(?:[0-9a-f]{2}:){5}[0-9a-f]{2}"),
    ]
    privacy_hits = []
    excluded_physical = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("local-review/raw/") or rel == "local-review/local-review-run.json":
            excluded_physical.append(rel)
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(pattern.search(text) for pattern in secret_patterns):
            privacy_hits.append(rel)
    checks.append(check("physical privacy scan", not privacy_hits and not excluded_physical, f"{len(physical)} files; {len(privacy_hits)} sensitive hits; {len(excluded_physical)} excluded files present"))
    links_bad = []
    link_pattern = re.compile(r"\]\(([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        for target in link_pattern.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            if target and not (path.parent / target).exists() and not (ROOT / target).exists():
                links_bad.append(f"{path.relative_to(ROOT)}:{target}")
    checks.append(check("internal links", not links_bad, json.dumps(links_bad)))

    seal_status = seal["status"] == "SEALED_READY_FOR_PUBLIC_DEPLOYMENT_AND_SUBMISSION_AUTHORIZATION" and seal["next_operation"] == "PUBLIC_DEPLOYMENT_AND_SUBMISSION_AUTHORIZATION" and seal["scientific_result_mutation"] is False
    checks.append(check("release seal status", seal_status, seal["status"]))

    passed = all(item["status"] == "PASS" for item in checks)
    output = {"status": "PASS" if passed else "FAIL", "checks": checks, "external_provider_calls": 0, "scientific_model_calls": 0, "confirmatory_calls": 0}
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
