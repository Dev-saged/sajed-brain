#!/usr/bin/env python3
"""رادار الاعتماديات: يقرأ gradle/libs.versions.toml ويقارن مع Google Maven / Maven Central / Gradle Portal.
patch/minor = T1 (يُطبَّق بـ --apply)، major = T2 (اقتراح فقط)."""
import argparse
import concurrent.futures as cf
import pathlib
import re
import tomllib
import urllib.request
import xml.etree.ElementTree as ET

GOOGLE = ("androidx.", "com.android.", "com.google.android.", "com.google.firebase", "com.google.gms", "com.google.mlkit")
PRE = re.compile(r"(?i)(alpha|beta|rc|dev|m\d+|snapshot|eap)")
RANK = {"alpha": 0, "beta": 1, "rc": 2}


def urls(group, artifact):
    path = f"{group.replace('.', '/')}/{artifact}/maven-metadata.xml"
    g = "https://dl.google.com/dl/android/maven2/" + path
    c = "https://repo1.maven.org/maven2/" + path
    p = "https://plugins.gradle.org/m2/" + path
    return [g, c, p] if group.startswith(GOOGLE) else [c, g, p]


def fetch_text(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None


def vkey(v):
    base, _, qual = v.partition("-")
    nums = [int(x) for x in re.findall(r"\d+", base)][:5]
    nums += [0] * (5 - len(nums))
    q = re.match(r"(?i)(alpha|beta|rc)[.\-]?(\d*)", qual)
    rank = 3 if not qual else (RANK[q.group(1).lower()] if q else -1)
    return (*nums, rank, int(q.group(2) or 0) if q else 0)


def latest(group, artifact, current, fetch):
    for u in urls(group, artifact):
        xml = fetch(u)
        if not xml:
            continue
        try:
            versions = [e.text for e in ET.fromstring(xml).iter("version") if e.text]
        except ET.ParseError:
            continue
        pool = versions if PRE.search(current) else [v for v in versions if not PRE.search(v)]
        if pool:
            return max(pool, key=vkey)
    return None


def bump(cur, new):
    a, b = vkey(cur), vkey(new)
    if b <= a:
        return "none"
    return "major" if b[0] > a[0] else "minor" if b[1] > a[1] else "patch"


def targets(data):
    versions = data.get("versions", {})
    found = {}
    for alias, lib in data.get("libraries", {}).items():
        mod = lib.get("module") or f"{lib.get('group')}:{lib.get('name')}"
        ver = lib.get("version")
        ref, cur = (ver.get("ref"), versions.get(ver.get("ref"))) if isinstance(ver, dict) else (None, ver)
        if cur is None or ":" not in mod:
            continue
        g, a = mod.split(":", 1)
        found.setdefault(ref or alias, {"current": cur, "ref": ref, "mods": []})["mods"].append((g, a))
    for alias, pl in data.get("plugins", {}).items():
        ver = pl.get("version")
        ref, cur = (ver.get("ref"), versions.get(ver.get("ref"))) if isinstance(ver, dict) else (None, ver)
        if cur is None:
            continue
        found.setdefault(ref or alias, {"current": cur, "ref": ref, "mods": []})["mods"].append((pl["id"], pl["id"] + ".gradle.plugin"))
    return found


def run(toml_path, fetch=fetch_text):
    data = tomllib.loads(pathlib.Path(toml_path).read_text(encoding="utf-8"))
    tg = targets(data)

    def one(item):
        key, t = item
        vs = [latest(g, a, t["current"], fetch) for g, a in t["mods"]]
        vs = [v for v in vs if v]
        new = min(vs, key=vkey) if vs else None
        return {"key": key, "ref": t["ref"], "current": t["current"], "latest": new,
                "bump": bump(t["current"], new) if new else "?", "mods": [f"{g}:{a}" for g, a in t["mods"]][:2]}

    with cf.ThreadPoolExecutor(8) as ex:
        return sorted(ex.map(one, tg.items()), key=lambda r: r["key"])


def tier(bump_kind):
    return {"patch": "T1", "minor": "T1", "major": "T2"}.get(bump_kind, "-")


def to_markdown(rows):
    out = ["# Deps radar", "", "| مفتاح | الحالي | الأحدث | النوع | Tier | المصدر |", "|---|---|---|---|---|---|"]
    for r in rows:
        if r["bump"] in ("none",):
            continue
        out.append(f"| {r['key']} | {r['current']} | {r['latest'] or 'غير متاح'} | {r['bump']} | {tier(r['bump'])} | {r['mods'][0]} |")
    if len(out) == 4:
        out.append("| كل شيء محدّث | | | | | |")
    unreachable = sum(r["bump"] == "?" for r in rows)
    if unreachable:
        out += ["", f"لم يُتحقق من {unreachable} مفتاحاً (شبكة/مستودع غير متاح)."]
    return "\n".join(out) + "\n"


def apply(toml_path, rows):
    p = pathlib.Path(toml_path)
    text, n = p.read_text(encoding="utf-8"), 0
    for r in rows:
        if r["ref"] and r["bump"] in ("patch", "minor"):
            text, k = re.subn(rf'^({re.escape(r["ref"])}\s*=\s*")[^"]+(")', rf"\g<1>{r['latest']}\g<2>", text, flags=re.M)
            n += k
    p.write_text(text, encoding="utf-8")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--out")
    ap.add_argument("--apply", action="store_true", help="طبّق patch/minor فقط")
    a = ap.parse_args()
    toml = pathlib.Path(a.project) / "gradle" / "libs.versions.toml"
    if not toml.exists():
        print("لا libs.versions.toml")
        return
    rows = run(toml)
    out = pathlib.Path(a.out or pathlib.Path(a.project) / "docs")
    out.mkdir(parents=True, exist_ok=True)
    (out / "deps-report.md").write_text(to_markdown(rows), encoding="utf-8")
    behind = sum(r["bump"] in ("patch", "minor", "major") for r in rows)
    print(f"deps: {behind} متأخرة من {len(rows)}")
    if a.apply:
        print(f"طُبّق {apply(toml, rows)} تحديث")


if __name__ == "__main__":
    main()
