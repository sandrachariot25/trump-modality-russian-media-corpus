#!/usr/bin/env python3
"""Verify integrity of the published *working*, not final, corpus."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "data"

def read(name):
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

statements = read("statements_metadata.csv")
media = read("media_metadata.csv")
pairs = read("comparisons_annotations.csv")
examples = read("sample_annotations.csv")

print("Working corpus:",len(statements),"statements,",len(media),"publications,",len(pairs),"comparisons,",len(examples),"examples")
assert len(statements) == 120 and len(media) == 160 and len(pairs) == 251 and len(examples) == 45
sids = {r["statement_id"] for r in statements}
mids = {r["media_id"] for r in media}
assert all(r["statement_id"] in sids and r["media_id"] in mids for r in pairs)
keys = {(r["statement_id"],r["media_id"],r["publication_type"]) for r in pairs}
assert all((r["statement_id"],r["media_id"],r["type"]) in keys for r in examples)
print("Referential integrity: PASS")
print("Note: this does NOT reproduce the article's final sample of 112/144/223.")
