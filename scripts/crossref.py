#!/usr/bin/env python3
"""ربط عابر للمشاريع: دوال بجسم متطابق في أكثر من مشروع = مرشحة لمكتبة مشتركة؛ نفس الاسم بجسم مختلف = انحراف.
يقرأ index/<project>/symbol-index.tsv ويكتب index/CROSS.md."""
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load(index):
    rows = []
    for tsv in sorted(index.glob("*/symbol-index.tsv")):
        for line in tsv.read_text(encoding="utf-8").splitlines():
            p = line.split("\t")
            if len(p) >= 8:
                rows.append({"project": tsv.parent.name, "name": p[0], "kind": p[1], "loc": p[3], "hash": p[7]})
    return rows


def analyse(rows):
    by_hash, by_name = defaultdict(list), defaultdict(list)
    for r in rows:
        if r["kind"] == "fun":
            by_name[r["name"]].append(r)
            if r["hash"]:
                by_hash[r["hash"]].append(r)
    shared = [g for g in by_hash.values() if len({r["project"] for r in g}) > 1]
    drift = [g for g in by_name.values()
             if len({r["project"] for r in g}) > 1 and len({r["hash"] for r in g if r["hash"]}) > 1]
    return shared, drift


def to_markdown(shared, drift):
    out = ["# عبر المشاريع", "", "## مرشحة لمكتبة مشتركة (جسم متطابق)", ""]
    out += [f"- {g[0]['name']} ← " + ", ".join(f"{r['project']}:{r['loc']}" for r in g) for g in shared] or ["- لا شيء"]
    out += ["", "## انحراف (نفس الاسم، جسم مختلف)", ""]
    out += [f"- {g[0]['name']} ← " + ", ".join(f"{r['project']}:{r['loc']}" for r in g) for g in drift] or ["- لا شيء"]
    return "\n".join(out) + "\n"


def main(index=ROOT / "index"):
    shared, drift = analyse(load(index))
    (index / "CROSS.md").write_text(to_markdown(shared, drift), encoding="utf-8")
    print(f"crossref: {len(shared)} مشتركة، {len(drift)} انحراف")


if __name__ == "__main__":
    main()
