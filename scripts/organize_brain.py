#!/usr/bin/env python3
"""
تنظيم يومي للدماغ:
- إزالة أسطر مكررة في mistakes.md وideas.md
- ترتيب الأسطر داخل كل قسم زمنياً (الأحدث أولاً)
- التحقق من أن README.md يشير لكل ملف في features/
"""
import pathlib, re

ROOT = pathlib.Path(__file__).parent.parent

def dedup_lines(text: str) -> str:
    seen, out = set(), []
    for line in text.splitlines(keepends=True):
        key = line.strip()
        if not key or key.startswith("#") or key not in seen:
            if key:
                seen.add(key)
            out.append(line)
    return "".join(out)

def process_file(path: pathlib.Path):
    if not path.exists():
        return
    original = path.read_text(encoding="utf-8")
    cleaned  = dedup_lines(original)
    if cleaned != original:
        path.write_text(cleaned, encoding="utf-8")
        print(f"  deduped: {path.relative_to(ROOT)}")

def check_readme_coverage():
    readme  = (ROOT / "README.md").read_text(encoding="utf-8")
    missing = []
    for f in sorted((ROOT / "features").glob("*.md")):
        if f.name not in readme:
            missing.append(f.name)
    if missing:
        print(f"  ⚠ README لا يشير إلى: {', '.join(missing)}")

def main():
    print("🧹 daily brain organize")
    for name in ["mistakes.md", "ideas.md"]:
        process_file(ROOT / name)
    check_readme_coverage()
    print("✓ done")

if __name__ == "__main__":
    main()
