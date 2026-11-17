#!/usr/bin/env python3
"""sajed-kit: يستخرج الدوال المتطابقة عبر المشاريع إلى وحدة Kotlin/JVM مشتركة، ثم يحوّل المشاريع لاستخدامها.
kit.py extract --index index --projects DIR --out OUT [--kotlin 2.1.0]
kit.py adopt PROJECT --manifest FILE --kit-version X [--body FILE]
الاستخراج متحفّظ: دوال top-level عامة، بلا annotations، بلا اعتماد على رموز المشروع أو android/androidx."""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import crossref  # noqa: E402
from scoutlib import cli, findings, symbols  # noqa: E402
from scoutlib.lexer import lex  # noqa: E402

PKG = "dev.saged.kit"
ALLOWED_IMPORTS = ("java.", "javax.", "kotlin.", "kotlinx.")
IMP = re.compile(r"^import[ \t]+([\w.]+)[ \t]*$", re.M)
PACKAGE = re.compile(r"^package[ \t]+([\w.]+)", re.M)


def func_span(raw, lx, line):
    """(بداية السطر، نهاية الدالة) في raw، أو None."""
    lines = lx.code.split("\n")
    start = sum(len(l) + 1 for l in lines[:line - 1])
    span = symbols.body_span(lx.code, start)
    return (start, span[1] + 1) if span else None


def own_candidates(rows):
    shared, _ = crossref.analyse(rows)
    return [g for g in shared if all(r["scope"] == "top" and r["vis"] == "public" for r in g)]


def build_kotlin_file(stem, imports, funcs):
    head = f"package {PKG}\n\n"
    if imports:
        head += "".join(f"import {i}\n" for i in sorted(imports)) + "\n"
    return head + "\n\n".join(funcs) + "\n"


def extract(index, projects, out, kotlin="2.1.0"):
    rows = crossref.load(pathlib.Path(index))
    names_by_project = {}
    for r in rows:
        names_by_project.setdefault(r["project"], set()).add(r["name"])
    by_file, manifest, skipped, taken = {}, [], [], set()
    for group in own_candidates(rows):
        first = group[0]
        name = first["name"]
        path, line = first["loc"].rsplit(":", 1)
        src_file = pathlib.Path(projects) / first["project"] / path
        if not src_file.exists():
            skipped.append((name, "المصدر غير متاح"))
            continue
        raw = src_file.read_text(encoding="utf-8")
        lx = lex(raw)
        span = func_span(raw, lx, int(line))
        if not span:
            skipped.append((name, "جسم غير قابل للاستخراج"))
            continue
        text = raw[span[0]:span[1]]
        before = raw[:span[0]].rstrip().splitlines()
        if before and before[-1].strip().startswith("@"):
            skipped.append((name, "annotated"))
            continue
        idents = set(findings.IDENT.findall(lx.code[span[0]:span[1]]))
        deps = (idents & names_by_project[first["project"]]) - {name}
        if deps:
            skipped.append((name, "يعتمد على رموز المشروع: " + ", ".join(sorted(deps)[:4])))
            continue
        used = [m.group(1) for m in IMP.finditer(raw) if m.group(1).rsplit(".", 1)[-1] in idents]
        bad = [i for i in used if not i.startswith(ALLOWED_IMPORTS)]
        if bad:
            skipped.append((name, "import خارجي: " + bad[0]))
            continue
        if name in taken:
            skipped.append((name, "تعارض اسم"))
            continue
        taken.add(name)
        stem = re.sub(r"\W", "", pathlib.Path(path).stem) or "Kit"
        slot = by_file.setdefault(stem, {"imports": set(), "funcs": []})
        slot["imports"] |= set(used)
        slot["funcs"].append(text.rstrip())
        manifest.append({"name": name, "hash": first["hash"], "package": PKG,
                         "origins": [{"project": r["project"], "loc": r["loc"]} for r in group]})
    write_module(pathlib.Path(out), by_file, manifest, skipped, kotlin)
    return manifest, skipped


def write_module(out, by_file, manifest, skipped, kotlin):
    src = out / "src" / "main" / "kotlin" / "dev" / "saged" / "kit"
    src.mkdir(parents=True, exist_ok=True)
    for stem, slot in by_file.items():
        (src / f"{stem}.kt").write_text(build_kotlin_file(stem, slot["imports"], slot["funcs"]), encoding="utf-8")
    version = out / "VERSION"
    if not version.exists():
        version.write_text("0.1.0\n", encoding="utf-8")
    (out / "settings.gradle.kts").write_text('rootProject.name = "kit"\n', encoding="utf-8")
    (out / "build.gradle.kts").write_text(f'''plugins {{
    kotlin("jvm") version "{kotlin}"
    `maven-publish`
}}

group = "dev.saged"
version = file("VERSION").readText().trim()

repositories {{
    mavenCentral()
}}

kotlin {{
    jvmToolchain(17)
}}

publishing {{
    publications {{
        create<MavenPublication>("kit") {{
            from(components["java"])
        }}
    }}
    repositories {{
        maven {{
            name = "GitHubPackages"
            url = uri("https://maven.pkg.github.com/Dev-saged/sajed-kit")
            credentials {{
                username = System.getenv("GITHUB_ACTOR")
                password = System.getenv("GITHUB_TOKEN")
            }}
        }}
    }}
}}
''', encoding="utf-8")
    (out / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (out / ".github" / "workflows" / "publish.yml").write_text('''name: publish

on:
  push:
    tags: ["v*"]
  workflow_dispatch:

permissions:
  contents: read
  packages: write

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "17"
      - uses: gradle/actions/setup-gradle@v4
        with:
          gradle-version: "8.10.2"
      - run: gradle build publish
        env:
          GITHUB_ACTOR: ${{ github.actor }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
''', encoding="utf-8")
    (out / "kit-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = ["# sajed-kit", "", "مولَّد من scripts/kit.py في sajed-brain. لا تُعدَّل الدوال هنا يدوياً دون تحديث المشاريع.", "",
             f"## مُستخرَج ({len(manifest)})"] + [f"- {m['name']} ← " + ", ".join(o["project"] for o in m["origins"]) for m in manifest]
    lines += ["", f"## متروك ({len(skipped)})"] + [f"- {n}: {why}" for n, why in skipped]
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def remove_span(raw, lx, line):
    span = func_span(raw, lx, line)
    if not span:
        return raw
    s, e = span
    while s > 0 and raw[s - 1] == "\n" and raw[max(0, s - 2):s] == "\n\n":
        s -= 1
    if e < len(raw) and raw[e] == "\n":
        e += 1
    return raw[:s] + raw[e:]


def has_declarations(raw):
    code = lex(raw).code
    body = findings.HEADER_LINES.sub("", code)
    return bool(body.strip())


def swap_import(raw, old_pkg, name):
    old = f"import {old_pkg}.{name}"
    new = f"import {PKG}.{name}"
    if re.search(rf"^{re.escape(old)}[ \t]*$", raw, re.M):
        return re.sub(rf"^{re.escape(old)}[ \t]*$", new, raw, flags=re.M), True
    return raw, False


def adopt(project, manifest, version, body_path=None):
    from scoutlib.fixes import ensure_import

    root = pathlib.Path(project).resolve()
    entries = {m["name"]: m for m in json.loads(pathlib.Path(manifest).read_text(encoding="utf-8"))}
    cfg = cli.load_cfg(root)
    files = cli.collect(root, cfg)
    kt = {rel: src for rel, src in files.items() if rel.endswith(".kt")}
    removed, callers = [], 0
    for rel, src in sorted(kt.items()):
        for s in symbols.extract(rel, src.lexed):
            m = entries.get(s.name)
            if not (m and s.kind == "fun" and s.hash == m["hash"] and s.scope == "top"):
                continue
            pkg_m = PACKAGE.search(src.raw)
            old_pkg = pkg_m.group(1) if pkg_m else ""
            raw = remove_span(src.raw, src.lexed, s.line)
            if raw == src.raw:
                continue
            removed.append((s.name, rel, old_pkg))
            kt[rel] = cli.Src(raw, lex(raw))
            files[rel] = kt[rel]
            (root / rel).write_text(raw, encoding="utf-8")
            break
    touched = set()
    for name, decl_rel, old_pkg in removed:
        for rel, src in sorted(kt.items()):
            if name not in set(findings.IDENT.findall(src.lexed.code)) | set(src.lexed.templates):
                continue
            raw, swapped = swap_import(src.raw, old_pkg, name)
            pkg_m = PACKAGE.search(raw)
            same_pkg = bool(pkg_m) and pkg_m.group(1) == old_pkg
            wildcard = re.search(rf"^import[ \t]+{re.escape(old_pkg)}\.\*", raw, re.M) is not None
            if not swapped and (same_pkg or wildcard):
                raw = ensure_import(raw, f"{PKG}.{name}")
            if raw != src.raw:
                kt[rel] = cli.Src(raw, lex(raw))
                (root / rel).write_text(raw, encoding="utf-8")
                callers += 1
                touched.add(rel)
    for rel in sorted({r for _, r, _ in removed} | touched):
        src = kt[rel]
        unused = findings.unused_imports(rel, src)
        if unused:
            drop = {ln - 1 for ln, _ in unused}
            raw = "\n".join(l for i, l in enumerate(src.raw.split("\n")) if i not in drop)
            kt[rel] = cli.Src(raw, lex(raw))
            (root / rel).write_text(raw, encoding="utf-8")
        if rel in {r for _, r, _ in removed} and not has_declarations(kt[rel].raw):
            (root / rel).unlink()
    wired = wire_catalog(root, version) if removed else False
    text = pr_body(removed, callers, wired, version)
    if body_path and removed:
        pathlib.Path(body_path).write_text(text, encoding="utf-8")
    return {"removed": [n for n, _, _ in removed], "callers": callers, "wired": wired}


def wire_catalog(root, version):
    toml = root / "gradle" / "libs.versions.toml"
    gradle = root / "app" / "build.gradle.kts"
    if not toml.exists() or not gradle.exists():
        return False
    t = toml.read_text(encoding="utf-8")
    if "sajed-kit" not in t:
        t = re.sub(r"^\[versions\]\n", f'[versions]\nsajed-kit = "{version}"\n', t, count=1, flags=re.M)
        t = re.sub(r"^\[libraries\]\n", '[libraries]\nsajed-kit = { module = "dev.saged:kit", version.ref = "sajed-kit" }\n', t, count=1, flags=re.M)
        toml.write_text(t, encoding="utf-8")
    g = gradle.read_text(encoding="utf-8")
    if "libs.sajed.kit" not in g:
        g, n = re.subn(r"^dependencies \{\n", "dependencies {\n    implementation(libs.sajed.kit)\n", g, count=1, flags=re.M)
        if not n:
            return False
        gradle.write_text(g, encoding="utf-8")
    return True


def pr_body(removed, callers, wired, version):
    lines = ["## تبنّي sajed-kit", "", f"الإصدار: {version}. أُزيلت {len(removed)} دالة محلية متطابقة مع نسختها في الكيت وحُدِّثت imports في {callers} ملف.", ""]
    lines += [f"- {n} ({rel})" for n, rel, _ in removed]
    lines += ["", "### خطوات يدوية قبل الدمج",
              "- نشر الكيت (tag في Dev-saged/sajed-kit) والتأكد من وجود الإصدار.",
              "- إضافة مستودع GitHub Packages في settings.gradle.kts بحساب قراءة (سر GH_PACKAGES_TOKEN في CI).",
              "- لم يُبنَ هذا الفرع بعد: لا يُدمج قبل build + tests خضراء."]
    if not wired:
        lines.append("- لم يُعثر على libs.versions.toml/app/build.gradle.kts: أضف الاعتمادية `dev.saged:kit` يدوياً.")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    e.add_argument("--index", default="index")
    e.add_argument("--projects")
    e.add_argument("--clone", help="projects.json: يستنسخ المشاريع (يحتاج GH_PAT) بدل --projects")
    e.add_argument("--out", required=True)
    e.add_argument("--kotlin", default="2.1.0")
    a_ = sub.add_parser("adopt")
    a_.add_argument("project")
    a_.add_argument("--manifest", required=True)
    a_.add_argument("--kit-version", required=True)
    a_.add_argument("--body")
    a = ap.parse_args(argv)
    if a.cmd == "extract":
        if a.clone:
            import os
            import tempfile

            import collect
            tmp = tempfile.mkdtemp()
            for p in json.loads(pathlib.Path(a.clone).read_text(encoding="utf-8")):
                collect.clone(p["repo"], pathlib.Path(tmp) / p["name"], os.environ["GH_PAT"])
            a.projects = tmp
        if not a.projects:
            ap.error("--projects أو --clone مطلوب")
        manifest, skipped = extract(a.index, a.projects, a.out, a.kotlin)
        print(f"kit: استُخرجت {len(manifest)} ومتروكة {len(skipped)}")
    else:
        r = adopt(a.project, a.manifest, a.kit_version, a.body)
        print(f"kit: أُزيلت {len(r['removed'])} وعُدّلت {r['callers']} ملف مستدعٍ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
