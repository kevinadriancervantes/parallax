"""Read-only, no-call verifier for the August 23 Parallax public release."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "parallax-public-release-manifest.json"
SEAL = ROOT / "parallax-public-release-seal.json"

IMMEDIATE_PREDECESSOR = {
    "manifest": ROOT / "predecessor-public-release-v2" / "parallax-public-release-manifest.json",
    "manifest_sha256": "fc16c4bda7aa892b1089ff993eed2dd24696d14a69511b51c4cdd3c2f451c7b2",
    "packet_sha256": "004cfba15bd8a6e256d217e7acf3081f53752c538217a8db337aaaae76f0dee7",
    "seal": ROOT / "predecessor-public-release-v2" / "parallax-public-release-seal.json",
    "seal_sha256": "6586c22d104a8a7eda65bf360fd7879513e76aef0a4529d65b4dcfe0b4c3f297",
}

FOUNDATIONAL_PREDECESSOR = {
    "manifest": ROOT / "predecessor" / "contest-package-manifest.json",
    "manifest_sha256": "9b1c4d373320410ff248c067e7be2fb80edaf44f88ed0816bd04f1f4b64f2522",
    "packet_sha256": "5d7182dd0028c4d748d69f25eedb12c4e0cf4db500246ad4021955d4e9b0b9d5",
    "seal": ROOT / "predecessor" / "contest-package-seal.json",
    "seal_sha256": "d32450cc9b77f0ddf4c0372a5a75cb3b76e2fab96926a58fd29297af3679599f",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(name: str, ok: bool, detail: object) -> dict[str, object]:
    return {"name": name, "status": "PASS" if ok else "FAIL", "detail": detail}


def aggregate(files: list[dict[str, str]]) -> str:
    payload = "".join(f"{entry['path']}\0{entry['sha256']}\n" for entry in files).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def physical_files() -> list[str]:
    return sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(ROOT).parts
    )


def verify_predecessor(label: str, binding: dict[str, object]) -> list[dict[str, object]]:
    manifest_path = binding["manifest"]
    seal_path = binding["seal"]
    manifest = read(manifest_path)
    seal = read(seal_path)
    return [
        check(f"{label} manifest identity", sha(manifest_path) == binding["manifest_sha256"], sha(manifest_path)),
        check(f"{label} seal identity", sha(seal_path) == binding["seal_sha256"], sha(seal_path)),
        check(
            f"{label} aggregate",
            aggregate(manifest["files"]) == manifest["packet_sha256"] == binding["packet_sha256"]
            and seal["packet_sha256"] == binding["packet_sha256"],
            manifest["packet_sha256"],
        ),
    ]


class LinkAndMetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.images: list[dict[str, str]] = []
        self.canonical: list[str] = []
        self.meta: dict[tuple[str, str], str] = {}
        self.html_lang: str | None = None
        self.main_count = 0
        self.skip_link = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = values.get("lang")
        if tag == "main":
            self.main_count += 1
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
            if "skip-link" in values.get("class", "").split():
                self.skip_link = True
        if tag in {"img", "script", "link"}:
            target = values.get("src") or values.get("href")
            if target:
                self.links.append(target)
        if tag == "img":
            self.images.append(values)
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical.append(values.get("href", ""))
        if tag == "meta":
            for key in ("name", "property"):
                if values.get(key):
                    self.meta[(key, values[key])] = values.get("content", "")


def local_target(source: Path, raw_target: str) -> Path | None:
    if raw_target.startswith(("http://", "https://", "mailto:", "data:")):
        return None
    parsed = urlsplit(raw_target)
    if not parsed.path:
        return None
    path_part = unquote(parsed.path)
    target = ROOT / path_part.lstrip("/") if path_part.startswith("/") else source.parent / path_part
    if path_part.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target.resolve()


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError(f"Not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


def main() -> int:
    checks: list[dict[str, object]] = []
    checks.extend(verify_predecessor("immediate public predecessor", IMMEDIATE_PREDECESSOR))
    checks.extend(verify_predecessor("foundational package predecessor", FOUNDATIONAL_PREDECESSOR))

    manifest = read(MANIFEST)
    seal = read(SEAL)
    checks.append(check("release aggregate", aggregate(manifest["files"]) == manifest["packet_sha256"] == seal["packet_sha256"], manifest["packet_sha256"]))
    checks.append(check("release manifest identity", sha(MANIFEST) == seal["manifest_sha256"], sha(MANIFEST)))
    payload_ok = manifest["file_count"] == len(manifest["files"]) and all(
        (ROOT / entry["path"]).is_file() and sha(ROOT / entry["path"]) == entry["sha256"]
        for entry in manifest["files"]
    )
    checks.append(check("release payload hashes", payload_ok, f"{len(manifest['files'])} payload files"))

    physical = physical_files()
    allowlist = read(ROOT / "governance" / "public-release-allowlist.json")
    allowed = sorted(set(allowlist["PUBLIC"]) | set(allowlist["PUBLIC_SANITIZED"]))
    checks.append(check("physical allowlist", physical == allowed and allowlist["status"] == "PASS", f"{len(physical)} physical files; exact allowlist"))
    inventory = read(ROOT / "governance" / "public-artifact-inventory.json")
    checks.append(check("public inventory", inventory["physical_file_count"] == len(physical) and inventory["public_count"] + inventory["public_sanitized_count"] == len(physical) and inventory["status"] == "PASS", f"{inventory['public_count']} public; {inventory['public_sanitized_count']} sanitized"))

    exp1 = read(ROOT / "evidence" / "experiment-1-summary.json")
    exp1_ok = (
        exp1["scientific_disposition"] == "NOT_SUPPORTED"
        and exp1["selected_rule"] == "OTHERWISE=>NOT_SUPPORTED"
        and exp1["design"] == {
            "synthetic_strategic_scenarios": 3,
            "provider_configurations": 2,
            "planned_calls": 210,
            "planned_matched_units": 48,
            "complete_matched_units": 28,
            "incomplete_matched_units": 20,
        }
        and exp1["outcome_accounting"]["structured"] == 154
        and exp1["outcome_accounting"]["behavioral_refusals"] == 53
        and exp1["outcome_accounting"]["schema_failures"] == 2
        and exp1["outcome_accounting"]["technical_failures"] == 1
        and exp1["complete_unit_vectors"] == {"X0": [0, 28, 0], "XE": [3, 25, 0], "XN-I": [0, 28, 0], "XN-P": [0, 27, 1]}
        and exp1["posthoc_rescue"] is False
        and [item["sha256"] for item in exp1["source_bindings"]] == [
            "5944d61fc7fc498ec4b3f9d4fc0b6dea77c157978c076dcddd0abfeacf51125e",
            "a2907dd3c15b611eb7fc5d428e17a99c320feb45a9614793563f3960ed43c429",
            "ab8cad875986ced8dbfa849cc38707bd518fd3df5ed87346742271ef5f4ab296",
        ]
    )
    checks.append(check("Experiment 1 accepted result", exp1_ok, "210 calls; 28/48 complete; NOT_SUPPORTED; no post-hoc rescue"))

    exp2 = read(ROOT / "evidence" / "experiment-2-summary.json")
    exp2_ok = (
        exp2["scientific_result"] == {"anthropic": "INSUFFICIENT_EVIDENCE", "google": "INSUFFICIENT_EVIDENCE", "provider_specific_support_claim": "NONE_AUTHORIZED"}
        and exp2["campaign_accounting"]["planned_coordinates"] == exp2["campaign_accounting"]["resolved_coordinates"] == 888
        and exp2["campaign_accounting"]["anthropic"] == exp2["campaign_accounting"]["google"] == 444
        and exp2["campaign_accounting"]["planned_matched_triples"] == 288
        and exp2["campaign_accounting"]["fully_valid_matched_units"] == 66
        and exp2["campaign_accounting"]["pessimistically_coded_matched_units"] == 222
        and exp2["invalidity_accounting"] == {"behavioral_refusals": 275, "schema_failures": 54, "technical_truncations": 97}
        and exp2["post_confirmatory_descriptive"]["authority"] == "EXPLORATORY_ONLY_NOT_A_REPLACEMENT_CONFIRMATORY_RESULT"
        and [item["sha256"] for item in exp2["source_bindings"]] == [
            "0eef1d6678617f68080c2e20cb57c4bf6aa7d79af408a0b599c5b75981784f1a",
            "310d467af27dbdaa1568a2385efe88455de1de0aea35e399e41dc0a061cd94f5",
            "95030ad03f3afaf8fe92bb7a53b76b637baca0b1950f46211435005f028f976e",
            "3649198eddf7e1898de03e7ea919a676cb54fa1dd17fc37858d6dfec7f4d77a9",
            "56a1256e6acfa006b4af11790556b2d8f5f9fbd5cf2d7493c38afcf99aeec707",
        ]
    )
    checks.append(check("Experiment 2 accepted result", exp2_ok, "888/888 resolved; 66/288 fully valid; both arms INSUFFICIENT_EVIDENCE"))

    lineage = read(ROOT / "governance" / "research-lineage.json")
    lineage_ok = (
        [item["experiment"] for item in lineage["experiments"]] == [1, 2, 3]
        and lineage["experiments"][0]["disposition"] == "NOT_SUPPORTED"
        and lineage["experiments"][1]["disposition"] == {"anthropic": "INSUFFICIENT_EVIDENCE", "google": "INSUFFICIENT_EVIDENCE"}
        and lineage["experiments"][2]["validation"]["scientific_provider_calls"] == 0
        and len(lineage["forbidden_collapses"]) == 5
    )
    checks.append(check("Experiment 1->2->3 lineage", lineage_ok, "three role-separated stages; negative results preserved"))

    shadow = read(ROOT / "evidence" / "synthetic-shadow-summary.json")
    checks.append(check("synthetic shadow evidence", shadow["world_count"] == 12 and shadow["scheduled_evaluations"] == 6674400 and shadow["all_worlds_match"] is True and shadow["scientific_provider_calls"] == 0 and shadow["real_model_calls"] == 0, "12 worlds; 6,674,400 evaluations; software evidence only"))
    local = read(ROOT / "evidence" / "local-surrogate-summary.json")
    checks.append(check("local accounting", local["attempted"] == local["terminal"] == 4800 and local["valid_ordinal"] == 4544 and local["schema_invalid"] == 256 and local["nuisance_nonzero_comparisons"] == 17 and local["dose_behavior"] == "not uniformly monotone" and local["status"] == "ACCEPTED_DESCRIPTIVE_ONLY", "4,800 attempted; 4,544 valid; 256 invalid; 17/60 nuisance nonzero"))
    qualification = read(ROOT / "evidence" / "provider-qualification-summary.json")
    checks.append(check("provider qualification boundary", qualification["calls"] == 6 and qualification["scientific_prompts"] == 0 and qualification["confirmatory_calls"] == 0 and qualification["scientific_provider_result"] == "NONE" and qualification["retries"] == 0 and qualification["status"] == "ACCEPTED_NON_SCIENTIFIC_QUALIFICATION", "six dated path calls; zero scientific prompts"))
    confirm = read(ROOT / "evidence" / "confirmatory-reference-summary.json")
    checks.append(check("unexecuted confirmatory reference", confirm["providers"] == 2 and confirm["cells_per_provider"] == 30 and confirm["N_execution"] == 9270 and confirm["calls_per_provider"] == 278100 and confirm["total_scheduled_calls"] == 556200 and confirm["M"] == 210 and confirm["alpha_global"] == 0.05 and confirm["full_joint_power_claim"] == "NONE" and confirm["confirmatory_execution"] == "NOT_PERFORMED" and confirm["funding"] == "NOT_SECURED", "2 providers; N=9270; M=210; 556,200 calls; no full-joint power"))

    accounting = read(ROOT / "hardening-accounting-reproduction.json")
    total = sum(Decimal(str(row["cost_usd"])) for row in accounting["rows"] if row.get("cost_usd") is not None)
    checks.append(check("historical qualification cost arithmetic", total in (Decimal("0.01723375"), Decimal("0.017233750000000003")) and accounting["record_type"] == "DERIVED_ACCOUNTING_METADATA_CORRECTION" and accounting["provider_calls"] == 0 and accounting["outcome_changed"] is False, str(total)))

    figure_receipt_path = ROOT / "figures" / "data" / "figure-data-receipt.json"
    figure_receipt = read(figure_receipt_path)
    figure_baseline = read(ROOT / "figures" / "data" / "figure-determinism-baseline.json")
    source_ok = all(sha(ROOT / "figures" / item["public_path"].removeprefix("figures/")) == item["sha256"] for item in figure_receipt["source_artifacts"])
    output_ok = all(sha(ROOT / "figures" / rel) == digest for rel, digest in figure_receipt["generated_outputs"].items())
    baseline_ok = figure_baseline["generated_outputs"] == figure_receipt["generated_outputs"] and figure_receipt["deterministic_rerun"]["byte_identical"] is True and figure_receipt["deterministic_rerun"]["runs"] == 2
    profile_rows = sum(1 for _ in csv.DictReader((ROOT / "figures" / "data" / "local-model-evidence-response-profile.csv").open(encoding="utf-8", newline="")))
    nuisance_rows = list(csv.DictReader((ROOT / "figures" / "data" / "nuisance-instability-matrix.csv").open(encoding="utf-8", newline="")))
    figure_ok = source_ok and output_ok and baseline_ok and profile_rows == 60 and len(nuisance_rows) == 60 and figure_receipt["nuisance_nonzero"] == 17 and sha(ROOT / figure_receipt["matlab_script"]["path"]) == figure_receipt["matlab_script"]["sha256"] and png_dimensions(ROOT / "figures" / "social-preview.png") == (1218, 661)
    checks.append(check("deterministic MATLAB figures", figure_ok, f"60 profile rows; 60 nuisance rows; 17 nonzero; receipt {sha(figure_receipt_path)}"))

    proposal_text = (ROOT / "submission-aug23" / "proposal-plain.txt").read_text(encoding="utf-8").strip()
    proposal_words = re.findall(r"[\w]+(?:[’'-][\w]+)*", proposal_text, flags=re.UNICODE)
    proposal_md = (ROOT / "submission-aug23" / "proposal-final.md").read_text(encoding="utf-8")
    checks.append(check("August 23 proposal", 1 <= len(proposal_words) <= 300 and proposal_text in proposal_md and "Experiment 1" not in proposal_text and "first live" in proposal_text and "4,800 real local Qwen2.5" in proposal_text and "not claims about Chinese models" in proposal_text, f"{len(proposal_words)} words; {len(proposal_text)} characters"))
    form_map = read(ROOT / "submission-aug23" / "form-field-map.json")
    deadline = read(ROOT / "submission-aug23" / "deadline-receipt.json")
    form_ok = form_map["primary_idea"]["description"]["visible_limit"] == "maximum 300 words" and form_map["primary_idea"]["title"]["required"] is True and form_map["identity_fields"][0]["value"] == "USER_INPUT_REQUIRED" and form_map["submission_authority"] == "NONE" and form_map["contest_submission"] == "NOT_PERFORMED" and deadline["aug23_deadline_clock"] == "NOT_PUBLICLY_SPECIFIED" and deadline["deadline_timezone"] == "NOT_PUBLICLY_SPECIFIED" and deadline["form_was_submitted"] is False
    checks.append(check("read-only ChinaTalk form/deadline mapping", form_ok, "Pitch 1 <=300 words; personal fields unresolved; deadline clock/timezone not published; not submitted"))

    index_parser = LinkAndMetaParser()
    index_text = (ROOT / "index.html").read_text(encoding="utf-8")
    index_parser.feed(index_text)
    metadata_ok = (
        index_parser.canonical == ["https://parallax.midex.app/"]
        and index_parser.meta.get(("name", "description"), "").startswith("Parallax tests whether strategic AI assessments")
        and index_parser.meta.get(("property", "og:url")) == "https://parallax.midex.app/"
        and index_parser.meta.get(("property", "og:image")) == "https://parallax.midex.app/figures/social-preview.png"
        and index_parser.meta.get(("name", "twitter:card")) == "summary_large_image"
        and '"@type": "ResearchProject"' in index_text
        and "Sitemap: https://parallax.midex.app/sitemap.xml" in (ROOT / "robots.txt").read_text(encoding="utf-8")
        and "https://parallax.midex.app/experiments/experiment-3/" in (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    )
    checks.append(check("search/social metadata", metadata_ok, "canonical, Open Graph, Twitter, JSON-LD, robots, and sitemap"))

    html_accessibility_ok = True
    html_details: list[str] = []
    link_failures: list[str] = []
    for html_path in sorted(ROOT.rglob("*.html")):
        parser = LinkAndMetaParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        if parser.html_lang != "en" or parser.main_count != 1 or not parser.skip_link or any(not image.get("alt", "").strip() for image in parser.images):
            html_accessibility_ok = False
            html_details.append(html_path.relative_to(ROOT).as_posix())
        for raw in parser.links:
            target = local_target(html_path, raw)
            if target is not None and not target.exists():
                link_failures.append(f"{html_path.relative_to(ROOT).as_posix()}:{raw}")
    md_pattern = re.compile(r"\]\(([^)]+)\)")
    for md_path in sorted(ROOT.rglob("*.md")):
        for raw in md_pattern.findall(md_path.read_text(encoding="utf-8")):
            target = local_target(md_path, raw.strip("<>"))
            if target is not None and not target.exists():
                link_failures.append(f"{md_path.relative_to(ROOT).as_posix()}:{raw}")
    checks.append(check("HTML accessibility structure", html_accessibility_ok and "@media (max-width: 620px)" in (ROOT / "styles.css").read_text(encoding="utf-8"), "lang, skip link, one main, alt text, and mobile stylesheet" if html_accessibility_ok else html_details))
    checks.append(check("internal links", not link_failures, link_failures))

    matrix = list(csv.DictReader((ROOT / "governance" / "claim-evidence-matrix.csv").open(encoding="utf-8", newline="")))
    audit = read(ROOT / "governance" / "claim-audit.json")
    prohibited_tests = [row for row in matrix if row["EVIDENCE CLASS"] == "prohibited claim firewall"]
    claim_ok = len(matrix) == 25 and len(prohibited_tests) == 4 and audit["claim_matrix_rows"] == 25 and audit["classification_counts"] == {"SUPPORTED_OR_ROLE_BOUNDED": 19, "QUALIFIED": 2, "PROHIBITED_CLAIM_TESTS": 4} and audit["status"] == "PASS" and not audit["prohibited_patterns_found"] and not audit["negative_result_weakening_found"]
    checks.append(check("claim firewall", claim_ok, "25 rows; 19 supported/role-bounded; 2 qualified; 4 prohibited-claim tests"))

    current_scope = [
        ROOT / "README.md", ROOT / "index.html", ROOT / "executive-summary.md",
        ROOT / "contest-narrative.md", ROOT / "microsite" / "index.md",
        ROOT / "reproducibility" / "README.md",
    ]
    current_text = "\n".join(path.read_text(encoding="utf-8").lower() for path in current_scope)
    status_ok = all(token in current_text for token in [
        "publication = live",
        "experiment_1 = not_supported",
        "experiment_2 = insufficient_evidence",
        "experiment_3_confirmatory_execution = not_performed",
        "scientific_provider_result = none",
        "contest_submission = not_performed",
        "next_boundary = final_aug23_submission_review",
    ]) and "next_boundary = public_deployment_and_submission_authorization" not in current_text
    checks.append(check("current publication boundary", status_ok, "publication live; contest not submitted; final August 23 review next"))

    privacy = read(ROOT / "governance" / "release-privacy-receipt.json")
    text_suffixes = {".css", ".csv", ".html", ".json", ".jsonl", ".m", ".md", ".py", ".sha256", ".txt", ".xml"}
    secret_patterns = [
        re.compile(r"(?i)[A-Z]:\\Users\\[^\s`\"']+"),
        re.compile(r"(?i)/(?:Users|home)/[^\s`\"']+"),
        re.compile(r"(?i)sk-ant-[A-Za-z0-9_-]{8,}|AIza[A-Za-z0-9_-]{20,}"),
        re.compile(r"(?i)(?:x-api-key|x-goog-api-key)\s*[:=]\s*[^\s`\"']+"),
        re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{12,}"),
        re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
        re.compile(r"(?i)(?:[0-9a-f]{2}:){5}[0-9a-f]{2}"),
    ]
    privacy_hits = []
    for rel in physical:
        path = ROOT / rel
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(pattern.search(text) for pattern in secret_patterns):
            privacy_hits.append(rel)
    checks.append(check("physical privacy scan", privacy["status"] == "PASS" and privacy["violations"] == [] and privacy["physical_tree_files"] == len(physical) and not privacy_hits, f"{len(physical)} files; {len(privacy_hits)} sensitive-pattern hits"))

    surface = read(ROOT / "submission-aug23" / "public-surface-receipt.json")
    surface_ok = surface["microsite"] == "LIVE_AUDITED" and surface["github"] == "LIVE_AUDITED" and surface["contest_submission"] == "NOT_PERFORMED" and surface["responsive_audit"]["desktop"] == "PASS" and surface["responsive_audit"]["mobile_390px"] == "PASS" and surface["postpublication_identity_location"] == "LOCAL_IMMUTABLE_AUG23_SNAPSHOT_TO_AVOID_PACKET_SELF_REFERENCE"
    checks.append(check("public-surface receipt", surface_ok, "live/audited surfaces; containing identities delegated to immutable snapshot"))

    seal_ok = (
        seal["status"] == "SEALED_AUG23_PUBLICATION_READY_FOR_SUBMISSION_REVIEW"
        and seal["next_operation"] == "FINAL_AUG23_SUBMISSION_REVIEW_AND_AUTHORIZATION"
        and seal["publication"] == "LIVE"
        and seal["contest_submission"] == "NOT_PERFORMED"
        and seal["scientific_result_mutation"] is False
        and sum(seal[key] for key in ["new_scientific_model_calls", "new_anthropic_calls", "new_google_calls", "new_confirmatory_calls"]) == 0
    )
    checks.append(check("August 23 release seal status", seal_ok, seal["status"]))

    passed = all(item["status"] == "PASS" for item in checks)
    output = {
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "new_qwen_scientific_generations": 0,
        "new_anthropic_calls": 0,
        "new_google_calls": 0,
        "new_confirmatory_calls": 0,
        "contest_submission": "NOT_PERFORMED",
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
