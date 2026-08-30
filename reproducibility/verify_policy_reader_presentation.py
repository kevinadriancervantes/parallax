#!/usr/bin/env python3
"""Verify the policy-reader presentation without network, model, or provider calls."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "publication" / "policy-reader-presentation-v1"
MANIFEST = META / "release-manifest.json"
MANIFEST_SHA = META / "release-manifest.sha256"
SEAL = META / "release-seal.json"
SEAL_SHA = META / "release-seal.sha256"
PACKET_SHA = META / "release-packet.sha256"
AUTHORITY = META / "authority-receipt.json"
AUTHORITY_SHA = META / "authority-receipt.sha256"
INVARIANCE = META / "scientific-invariance.json"
ENTERING_COMMIT = "0fcd5f8b099ffdcbf7d5ab11f97fab40f7f139b6"
ENTERING_TREE = "c187ce9154ebe18ca362ff783e6b27889b07d63d"
ENTERING_DEPLOYMENT = "dpl_eVEaM4usuoz7aWvzLvVmevED9dNF"
EXCLUDED = {
    "publication/policy-reader-presentation-v1/release-manifest.json",
    "publication/policy-reader-presentation-v1/release-manifest.sha256",
    "publication/policy-reader-presentation-v1/release-seal.json",
    "publication/policy-reader-presentation-v1/release-seal.sha256",
    "publication/policy-reader-presentation-v1/release-packet.sha256",
}
FROZEN = {
    "situation-room/provenance/sr11r1-frozen/app.js": (21319, "21dcf31c2bd61ccdb73a3de9877150067b21c95a7dc81ce9c79b15af414cc1e0"),
    "situation-room/provenance/sr11r1-frozen/data/data.json": (788968, "db107bf3c2080f431d0eaaee044b09d63af3f8e4b349c2c85f2110289cdfd9c0"),
    "situation-room/provenance/sr11r1-frozen/index.html": (2016, "012aacd2f2334d5c60999f9c944aedcd79ca625b58b84cce473701fd5695b1ab"),
    "situation-room/provenance/sr11r1-frozen/README.md": (322, "b8fdc3eab319bdc30ac9d04881563019a1a49a1119005fffcb621f7afeeb498c"),
    "situation-room/provenance/sr11r1-frozen/styles.css": (7799, "ca147a49e00b0a814ab5658eeee48318a3723155cbab8fe3c5d6a4db8e3b89c0"),
}
SCIENTIFIC_PREFIXES = (
    "evidence/",
    "figures/",
    "governance/",
    "submission-aug23/",
    "predecessor/",
    "predecessor-public-release-v1/",
    "predecessor-public-release-v2/",
    "local-review/",
)
PRESENTATION_EXCEPTIONS = {
    "evidence/local-surrogate-summary/index.html",
    "governance/claim-firewall/index.html",
}
PUBLIC_DOCS = [
    "index.html",
    "experiments/index.html",
    "experiments/experiment-1/index.html",
    "experiments/experiment-2/index.html",
    "experiments/experiment-3/index.html",
    "evidence/local-surrogate-summary/index.html",
    "governance/claim-firewall/index.html",
    "reproduce/index.html",
    "research/narrative/index.html",
    "README.md",
    "reproducibility/README.md",
    "situation-room/index.html",
    "situation-room/app.js",
    "situation-room/README.md",
]


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def scientific_path(path: str) -> bool:
    return path == "situation-room/data/data.json" or (path.startswith(SCIENTIFIC_PREFIXES) and path not in PRESENTATION_EXCEPTIONS)


def baseline_paths() -> list[str]:
    return [path for path in git("ls-tree", "-r", "--name-only", ENTERING_COMMIT).splitlines() if scientific_path(path)]


def baseline_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{ENTERING_COMMIT}:{path}"], cwd=ROOT)


def current_scientific_mismatches() -> list[str]:
    mismatches: list[str] = []
    for path in baseline_paths():
        current = ROOT / path
        if not current.exists() or current.read_bytes() != baseline_bytes(path):
            mismatches.append(path)
    return mismatches


def payload_files() -> list[Path]:
    return sorted(
        [
            path for path in ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and "__pycache__" not in path.parts
            and path.relative_to(ROOT).as_posix() not in EXCLUDED
        ],
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def records(paths: list[Path]) -> list[dict[str, object]]:
    return [{"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha_file(path)} for path in paths]


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if value and ((tag == "a" and key == "href") or (tag in {"img", "script", "link"} and key in {"src", "href"})):
                self.items.append(value)


def link_failures() -> list[str]:
    failures: list[str] = []
    for html in sorted(ROOT.rglob("*.html")):
        if ".git" in html.parts:
            continue
        parser = Links()
        parser.feed(html.read_text(encoding="utf-8"))
        for raw in parser.items:
            split = urlsplit(raw)
            if split.scheme in {"http", "https", "mailto", "tel", "data"} or raw.startswith("#"):
                continue
            target_text = unquote(split.path)
            if not target_text:
                continue
            target = ROOT / target_text.lstrip("/") if target_text.startswith("/") else html.parent / target_text
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                failures.append(f"{html.relative_to(ROOT).as_posix()} -> {raw}")
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
        if path.suffix.lower() not in suffixes:
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

    add("entering commit", git("rev-parse", "HEAD") == ENTERING_COMMIT or git("merge-base", "--is-ancestor", ENTERING_COMMIT, "HEAD") == "", git("rev-parse", "HEAD"))
    add("entering tree authority", git("rev-parse", f"{ENTERING_COMMIT}^{{tree}}") == ENTERING_TREE, ENTERING_TREE)
    frozen = {}
    for path, expected in FROZEN.items():
        file_path = ROOT / path
        actual = (file_path.stat().st_size, sha_file(file_path)) if file_path.exists() else (None, None)
        frozen[path] = {"expected": list(expected), "actual": list(actual)}
    add("frozen SR-11R1 artifacts", all(value["expected"] == value["actual"] for value in frozen.values()), frozen)
    add("current evidence projection unchanged", sha_file(ROOT / "situation-room/data/data.json") == FROZEN["situation-room/provenance/sr11r1-frozen/data/data.json"][1], sha_file(ROOT / "situation-room/data/data.json"))
    mismatches = current_scientific_mismatches()
    add("scientific files unchanged from entering commit", not mismatches, mismatches)

    evidence = json.loads((ROOT / "situation-room/data/data.json").read_text(encoding="utf-8"))
    aggregate = evidence["aggregate_observability"]
    substantive = sum(aggregate.get(state, 0) for state in ("LEANS_NOT_H", "UNRESOLVED", "LEANS_H"))
    add("1,600 scheduled rows", aggregate.get("TOTAL") == 1600, aggregate.get("TOTAL"))
    add("777 transport-unavailable rows", aggregate.get("TRANSPORT_UNAVAILABLE") == 777, aggregate.get("TRANSPORT_UNAVAILABLE"))
    add("822 substantive ordinal assessments", substantive == 822, substantive)
    add("one measurement-unavailable row", aggregate.get("MEASUREMENT_UNAVAILABLE") == 1, aggregate.get("MEASUREMENT_UNAVAILABLE"))
    add("823 non-transport terminal rows", substantive + aggregate.get("MEASUREMENT_UNAVAILABLE", 0) == 823, substantive + aggregate.get("MEASUREMENT_UNAVAILABLE", 0))
    add("320 masking rows excluded", evidence["masked_exclusion"].get("observations_excluded") == 320 and evidence["masked_exclusion"].get("status") == "EXCLUDED", evidence["masked_exclusion"])
    add("1,280 governing profile rows", sum(row["n"] for row in evidence["profiles"]) == 1280, sum(row["n"] for row in evidence["profiles"]))
    roots = evidence["transport_root_cause"].get("causes", {})
    add("758 connection-refused failures", roots.get("CONNECTION_REFUSED") == 758, roots.get("CONNECTION_REFUSED"))
    add("5 CPU OOM failures", roots.get("HTTP_500_CPU_OOM") == 5, roots.get("HTTP_500_CPU_OOM"))
    add("10 GPU OOM failures", roots.get("HTTP_500_GPU_OOM") == 10, roots.get("HTTP_500_GPU_OOM"))
    add("3 connection resets", roots.get("CONNECTION_RESET") == 3, roots.get("CONNECTION_RESET"))
    add("one heap-corruption failure", roots.get("HTTP_500_HEAP_CORRUPTION") == 1, roots.get("HTTP_500_HEAP_CORRUPTION"))
    add("five-dose architecture", list(evidence["dose_labels"]) == ["D1", "D2", "D3", "D4", "D5"], list(evidence["dose_labels"]))
    add("two local model families", {row["model_key"] for row in evidence["profiles"]} == {"QWEN_14B", "GEMMA_4B"}, sorted({row["model_key"] for row in evidence["profiles"]}))

    exp1 = json.loads((ROOT / "evidence/experiment-1-summary.json").read_text(encoding="utf-8"))
    add("Experiment 1 disposition and count", exp1.get("scientific_disposition") == "NOT_SUPPORTED" and exp1.get("design", {}).get("planned_calls") == 210, {"result": exp1.get("scientific_disposition"), "planned_calls": exp1.get("design", {}).get("planned_calls")})
    add("Experiment 1 design breadth", exp1.get("design", {}).get("synthetic_strategic_scenarios") == 3 and exp1.get("design", {}).get("provider_configurations") == 2, exp1.get("design"))
    exp2 = json.loads((ROOT / "evidence/experiment-2-summary.json").read_text(encoding="utf-8"))
    add("Experiment 2 count", exp2.get("campaign_accounting", {}).get("planned_coordinates") == 888 and exp2.get("campaign_accounting", {}).get("resolved_coordinates") == 888, exp2.get("campaign_accounting"))
    add("Experiment 2 provider decisions", exp2.get("scientific_result") == {"anthropic": "INSUFFICIENT_EVIDENCE", "google": "INSUFFICIENT_EVIDENCE", "provider_specific_support_claim": "NONE_AUTHORIZED"}, exp2.get("scientific_result"))
    add("provider qualification separated", json.loads((ROOT / "evidence/provider-qualification-summary.json").read_text(encoding="utf-8")).get("scientific_provider_result") == "NONE", "non-scientific qualification only")
    reference = json.loads((ROOT / "evidence/confirmatory-reference-summary.json").read_text(encoding="utf-8"))
    add("frontier reference counts", reference.get("N_execution") == 9270 and reference.get("M") == 210 and reference.get("total_scheduled_calls") == 556200, {"N_execution": reference.get("N_execution"), "M": reference.get("M"), "total_scheduled_calls": reference.get("total_scheduled_calls")})
    add("frontier execution remains unexecuted", reference.get("funding") == "NOT_SECURED" and reference.get("account_capacity") == "UNVERIFIED", {"funding": reference.get("funding"), "account_capacity": reference.get("account_capacity")})

    root = (ROOT / "index.html").read_text(encoding="utf-8")
    exp1_page = (ROOT / "experiments/experiment-1/index.html").read_text(encoding="utf-8")
    exp2_page = (ROOT / "experiments/experiment-2/index.html").read_text(encoding="utf-8")
    exp3_page = (ROOT / "experiments/experiment-3/index.html").read_text(encoding="utf-8")
    situation = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in ("situation-room/index.html", "situation-room/app.js", "situation-room/README.md"))
    public = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in PUBLIC_DOCS)
    add("policy question prominent", "Why this matters in government" in root and "Before relying on AI advice" in root, "homepage policy framing")
    add("current/terrible/track guide", all(term in public for term in ("What it can show now", "Terrible at", "Track over time")), "reader interpretation guide")
    add("Experiment 1 provider identity", all(term in exp1_page for term in ("Anthropic Claude Fable 5", "Google Gemini 3.6 Flash", "live frontier-provider science")), "accepted frontier-provider history")
    add("Experiment 1 live frontier accounting", all(term in exp1_page for term in ("105 scientific calls per provider", "210 total", "NOT SUPPORTED")), "105 per provider / 210 total / negative result")
    add("Experiment 2 provider identity", all(term in exp2_page for term in ("Anthropic Claude Fable 5", "Google Gemini 3.6 Flash", "Live frontier-provider science")), "accepted frontier-provider history")
    add("Experiment 2 live frontier accounting", all(term in exp2_page for term in ("444 resolved coordinates per provider", "888 total", "INSUFFICIENT_EVIDENCE")), "444 per provider / 888 total / insufficient evidence")
    add("Experiment 3 execution geometry", all(term in exp3_page for term in ("1,600 executed", "50 executed profiles × 32", "320 excluded", "10 executed profiles × 32", "1,280 governing", "40 accepted profiles × 32", "execution history and full-ledger accounting")), "executed ledger versus governing projection")
    add("Experiment 3 execution prerequisites", all(term in exp3_page for term in ("secure funding", "verify provider/account capacity", "fresh provider/model/path review", "sacrificial qualification", "explicit execution authority")), "all five pre-execution requirements")
    add("accounting language is qualified", "823 rows reached a non-transport terminal state" in public and "822 substantive ordinal assessments" in public, "823 = 822 + 1")
    add("823 not described as observable assessments", "823 observable assessments" not in public, "preserve terminal-state distinction")
    add("exact transport decomposition is visible", all(term in situation for term in ("758 connection-refused failures", "5 CPU OOM failures", "10 GPU OOM failures", "3 connection resets", "1 heap-corruption failure")), "777 root causes")
    add("governing/predecessor boundary", "Current Situation Room evidence" in situation and "Earlier stress evidence" in situation and "never pooled" in public, "SR-8R1 versus 4,800-row campaign")
    add("frontier boundary visible", "No frontier Experiment 3 scientific result exists" in public and "Funding" in root and "account/capacity verification" in root, "no provider science")
    add("policy-use caveats visible", "Operational user validation was not performed" in situation and "not been operationally validated" in situation, "Vela/Afghanistan illustrative users")
    add("Afghanistan cutoff/outcome boundary", "20 Dec 1979 · 12:06Z" in situation and "not used as an answer key" in situation, "fixed cutoff and no answer key")
    add("excluded diagnostic visible", "320 observations and 10 contrasts are excluded" in situation, "masking branch excluded")
    add("nuisance caveat visible", "No equivalence claim" in situation and "no affirmative behavioral-equivalence threshold" in public, "descriptive only")
    add("Useful today absent from current Situation Room", "Useful today" not in situation, "current public label is translated")
    add("operational instability overclaim absent", "operationally unstable" not in root, "use presentation-fragile wording")
    add("contest-coded judge-facing instrument absent", "judge-facing instrument" not in root, "independent research voice")
    cache_pages = ("index.html", "experiments/index.html", "experiments/experiment-1/index.html", "experiments/experiment-2/index.html", "experiments/experiment-3/index.html", "evidence/local-surrogate-summary/index.html", "governance/claim-firewall/index.html", "reproduce/index.html", "research/narrative/index.html", "situation-room/index.html")
    cache_versions = {path: "styles.css?v=public-presentation-v2" in (ROOT / path).read_text(encoding="utf-8") for path in cache_pages}
    add("current stylesheet cache versions", all(cache_versions.values()), cache_versions)
    add("hidden-state/correctness firewall", all(term in public for term in ("hidden belief", "correctness", "general strategic competence")), "observable construct only")
    add("operational-utility firewall", "No operational-utility evidence" in public and "operational usefulness" in public, "utility not established")
    add("no current China/contest pitch", "Why this is a China + AI story" not in root and "ChinaTalk" not in root and "Submission history" not in public, "current reader chrome")
    add("no current submission-state chrome", all(term not in public for term in ("SEPTEMBER_1_SITUATION_ROOM_CONTEST", "Situation Room contest form", "not submitted")), "neutral public release")
    add("no publication administration in primary navigation", "publication/" not in (ROOT / "sitemap.xml").read_text(encoding="utf-8") and "Publication receipt" not in root and "release receipt" not in situation, "technical records remain in GitHub")
    add("GitHub handoff visible", "github.com/kevinadriancervantes/parallax" in root and "technical repository" in root and "Technical provenance on GitHub" in situation, "website/GitHub split")
    add("mobile menu structure", all(term in root for term in ("id=\"primary-navigation\"", "class=\"nav-toggle\"", "aria-controls=\"primary-navigation\"", "mobile-sr-cta")), "44px mobile control declared in CSS")
    add("responsive CSS target", "@media (max-width: 620px)" in (ROOT / "styles.css").read_text(encoding="utf-8") and "min-height: 44px" in (ROOT / "styles.css").read_text(encoding="utf-8"), "mobile layout")
    add("current reproduction command", "verify_policy_reader_presentation.py" in public and "verify_public_presentation_successor.py" not in (ROOT / "reproduce/index.html").read_text(encoding="utf-8"), "policy-reader verifier")
    add("Situation Room remains first-class", "href=\"situation-room/\"" in root and "Situation Room" in (ROOT / "situation-room/index.html").read_text(encoding="utf-8"), "public route")
    add("contact links visible", "kevinadriancervantes@gmail.com" in root and "linkedin.com/in/kevinadriancervantes" in root, "public contact")
    add("history remains linked without admin chrome", "Historical" in (ROOT / "experiments/index.html").read_text(encoding="utf-8") and "publication/situation-room-v1" not in root, "historical review remains available")

    add("internal links", not (links := link_failures()), links)
    add("privacy and credential scan", not (privacy := privacy_hits()), privacy)
    if INVARIANCE.exists():
        invariance = json.loads(INVARIANCE.read_text(encoding="utf-8"))
        inv_mismatches = []
        for record in invariance.get("files", []):
            path = ROOT / record["path"]
            if not path.exists() or path.stat().st_size != record["bytes"] or sha_file(path) != record["sha256"]:
                inv_mismatches.append(record["path"])
        add("scientific invariance ledger", not inv_mismatches and invariance.get("changed_scientific_files") == [], inv_mismatches or invariance.get("changed_scientific_files"))
    else:
        add("scientific invariance ledger", False, "missing")
    if AUTHORITY.exists() and AUTHORITY_SHA.exists():
        authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))
        add("authority receipt scope", authority.get("scope") == "POLICY_READER_PRESENTATION_SUCCESSOR" and authority.get("scientific_mutation_authority") == "NONE", authority)
        add("authority receipt entering state", authority.get("entering_git_commit") == ENTERING_COMMIT and authority.get("entering_git_tree") == ENTERING_TREE and authority.get("entering_deployment") == ENTERING_DEPLOYMENT, authority)
        add("authority receipt hash", sha_file(AUTHORITY) == AUTHORITY_SHA.read_text(encoding="ascii").split()[0], sha_file(AUTHORITY))
    else:
        add("authority receipt", False, "missing")
    if MANIFEST.exists() and MANIFEST_SHA.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        declared = manifest.pop("manifest_identity", None)
        add("manifest identity", sha_bytes(canonical(manifest)) == declared, declared)
        add("full-tree payload", manifest.get("files") == records(payload_files()), f"{len(manifest.get('files', []))} files")
        add("manifest file hash", sha_file(MANIFEST) == MANIFEST_SHA.read_text(encoding="ascii").split()[0], sha_file(MANIFEST))
    else:
        add("release manifest", False, "missing")
    if SEAL.exists() and SEAL_SHA.exists() and PACKET_SHA.exists():
        seal = json.loads(SEAL.read_text(encoding="utf-8"))
        packet = seal.pop("packet_identity", None)
        add("release packet identity", sha_bytes(canonical(seal)) == packet and PACKET_SHA.read_text(encoding="ascii").strip() == packet, packet)
        add("release seal file hash", sha_file(SEAL) == SEAL_SHA.read_text(encoding="ascii").split()[0], sha_file(SEAL))
        add("zero new science/provider calls", seal.get("new_scientific_calls") == 0 and seal.get("provider_calls") == 0, {"new_scientific_calls": seal.get("new_scientific_calls"), "provider_calls": seal.get("provider_calls")})
        add("submission firewall", seal.get("external_submission") == "NOT_PERFORMED", seal.get("external_submission"))
        add("successor status", seal.get("status") == "PARALLAX_POLICY_READER_PRESENTATION_READY", seal.get("status"))
    else:
        add("release packet", False, "missing")
    status = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    return {"schema_version": "parallax.policy-reader-presentation-verification.v1", "status": status, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "PASS" else 1)
