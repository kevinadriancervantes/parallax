#!/usr/bin/env python3
"""Seal the additive presentation successor with non-circular identities."""
from __future__ import annotations
import json, subprocess
from datetime import datetime, timezone
from pathlib import Path
from verify_public_presentation_successor import ROOT, META, MANIFEST, MANIFEST_SHA, SEAL, PACKET_SHA, canonical, payload_files, records, sha_bytes, sha_file

BASELINE="f8f9f80e621ebff7d1ab903d0ccf58d26222d778"
INVARIANCE=META/"scientific-invariance.json"
SCIENTIFIC_PREFIXES=("evidence/","figures/","governance/","submission-aug23/","predecessor/","predecessor-public-release-v1/","predecessor-public-release-v2/","local-review/")
PRESENTATION_EXCEPTIONS={"evidence/local-surrogate-summary/index.html","governance/claim-firewall/index.html"}
def write_json(path:Path,value:object)->None:path.write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
def git(*args:str)->str:return subprocess.check_output(["git",*args],cwd=ROOT,text=True,encoding="utf-8").strip()
def scientific(path:str)->bool:return path=="situation-room/data/data.json" or (path.startswith(SCIENTIFIC_PREFIXES) and path not in PRESENTATION_EXCEPTIONS)
def main()->None:
    META.mkdir(parents=True,exist_ok=True)
    receipt=META/"authority-receipt.json";(META/"authority-receipt.sha256").write_text(sha_file(receipt)+"  authority-receipt.json\n",encoding="ascii",newline="\n")
    baseline_paths=[p for p in git("ls-tree","-r","--name-only",BASELINE).splitlines() if scientific(p)]
    changed=[p for p in git("diff","--name-only",BASELINE,"--",*baseline_paths).splitlines() if p]; inv=[]
    for rel in baseline_paths:
        current=(ROOT/rel).read_bytes()
        inv.append({"path":rel,"bytes":len(current),"sha256":sha_bytes(current)})
    write_json(INVARIANCE,{"schema_version":"parallax.public-presentation-scientific-invariance.v1","baseline_commit":BASELINE,"changed_scientific_files":changed,"files":inv})
    if changed:raise SystemExit("scientific invariance failed: "+", ".join(changed))
    files=records(payload_files())
    core={"schema_version":"parallax.public-presentation-successor-manifest.v1","entering_commit":BASELINE,"sr11r1_packet":"1a590a4ab72922008657fc39acabead7f9f3923113ee0bcbc648ff99db0251e4","sr11r1_public_safe_projection":"4fb3cb59518afbc7f3b41901925a1c8fb2ec172b211c0b795fd0d5f1035785c5","file_count":len(files),"files":files}
    identity=sha_bytes(canonical(core));write_json(MANIFEST,{**core,"manifest_identity":identity});manifest_sha=sha_file(MANIFEST);MANIFEST_SHA.write_text(manifest_sha+"  release-manifest.json\n",encoding="ascii",newline="\n")
    seal_core={"schema_version":"parallax.public-presentation-successor-seal.v1","sealed_utc":datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z"),"status":"PARALLAX_PUBLIC_PRESENTATION_SUCCESSOR_READY","manifest_identity":identity,"manifest_sha256":manifest_sha,"authority_receipt_sha256":sha_file(receipt),"frozen_artifacts_mutated":"NO","scientific_files_changed":0,"governing_observations_changed":0,"new_scientific_calls":0,"provider_calls":0,"august_23_submission":"SUBMITTED_NOT_ADVANCED_HISTORICAL","september_1_submission":"NOT_PERFORMED","next_operation":"FINAL_SEP1_SUBMISSION_REVIEW"}
    packet=sha_bytes(canonical(seal_core));write_json(SEAL,{**seal_core,"packet_identity":packet});PACKET_SHA.write_text(packet+"\n",encoding="ascii",newline="\n")
    print(json.dumps({"status":"SEALED","file_count":len(files),"manifest_identity":identity,"manifest_sha256":manifest_sha,"packet_identity":packet},indent=2))
if __name__=="__main__":main()
