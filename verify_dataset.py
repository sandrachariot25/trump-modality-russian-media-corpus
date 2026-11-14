#!/usr/bin/env python3
"""Reproduce quantitative tables from the complete 251-comparison corpus."""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "data"

def read(filename):
    with (ROOT / filename).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

statements = read("statements_metadata.csv")
media = read("media_metadata.csv")
comparisons = read("comparisons_annotations.csv")
manifest = read("analysis_manifest_251.csv")
statistics = read("analysis_statistics_251.csv")
examples = read("sample_annotations.csv")

assert len(statements) == 120
assert len(media) == 160
assert len(comparisons) == len(manifest) == 251
assert len(examples) == 45

S = {r["statement_id"]: r for r in statements}
M = {r["media_id"]: r for r in media}
assert len(S) == 120 and len(M) == 160

category_map = {"сохранение": "сохранение", "усиление": "усиление", "ослабление": "ослабление"}
triplets = set()
for n, (source, row) in enumerate(zip(comparisons, manifest), 1):
    k = (source["statement_id"], source["media_id"], source["publication_type"])
    assert k not in triplets, f"duplicate {k}"
    triplets.add(k)
    assert source["statement_id"] in S and source["media_id"] in M
    assert row["comparison_id"] == f"C{n:03d}"
    assert (row["statement_id"], row["media_id"], row["publication_type"]) == k
    assert row["presidential_term"] == S[source["statement_id"]]["presidential_term"]
    assert row["modality_shift_original"] == source["modality_shift"]
    assert row["modality_shift_4groups"] == category_map.get(source["modality_shift"], "иные и неоднозначные")
    assert row["requires_human_review"] == source["requires_human_review"]

assert len({(a,b) for a,b,_ in triplets}) == 170
assert {r["statement_id"] for r in manifest} == set(S)
assert {r["media_id"] for r in manifest} == set(M)

for period in ("1","2","весь корпус"):
    selection = [r for r in manifest if period == "весь корпус" or r["presidential_term"] == period]
    for kind in ("direct_quote","paraphrase","headline","все формы"):
        rows = [r for r in selection if kind == "все формы" or r["publication_type"] == kind]
        for label in ("сохранение","усиление","ослабление","иные и неоднозначные"):
            cnt = sum(r["modality_shift_4groups"] == label for r in rows)
            statistic = next(r for r in statistics if (r["section"],r["period"],r["publication_type"],r["category"]) == ("Разметка",period,kind,label))
            assert int(statistic["count"]) == cnt
            assert int(statistic["denominator"]) == len(rows)
            assert abs(float(statistic["percent"])-round(cnt / len(rows) * 100,2)) < 0.001

group = Counter(r["modality_shift_4groups"] for r in manifest)
print("Corpus units:", len(S),"statements,", len(M),"publications,",len({(a,b) for a,b,_ in triplets}),"pairs,",len(manifest),"comparisons")
print("Four-category counts:",dict(group))
print("Direct quotes:",sum(r["publication_type"]=="direct_quote" for r in manifest))
print("Paraphrases:",sum(r["publication_type"]=="paraphrase" for r in manifest))
print("Headlines:",sum(r["publication_type"]=="headline" for r in manifest))
print("Human-review flags:",sum(r["requires_human_review"]=="True" for r in manifest))
print("Referential integrity and published statistics: PASS")
