#!/usr/bin/env python3
"""تحديث ملفات الدماغ — append أو replace_section."""
import argparse, pathlib, re, sys

def append_content(path: pathlib.Path, content: str):
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    sep  = "\n" if text and not text.endswith("\n") else ""
    path.write_text(text + sep + content + "\n", encoding="utf-8")

def replace_section(path: pathlib.Path, header: str, content: str):
    if not path.exists():
        path.write_text(f"## {header}\n{content}\n", encoding="utf-8")
        return
    text   = path.read_text(encoding="utf-8")
    # يبحث عن القسم من ## header حتى ## التالي (أو نهاية الملف)
    pattern = rf"(## {re.escape(header)}\n).*?(?=\n## |\Z)"
    replacement = rf"\g<1>{content}\n"
    new_text = re.sub(pattern, replacement, text, flags=re.DOTALL)
    if new_text == text:
        # القسم غير موجود — أضفه في النهاية
        new_text = text.rstrip("\n") + f"\n\n## {header}\n{content}\n"
    path.write_text(new_text, encoding="utf-8")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file",    required=True)
    p.add_argument("--action",  required=True, choices=["append", "replace_section"])
    p.add_argument("--content", required=True)
    p.add_argument("--section", default="")
    args = p.parse_args()

    path = pathlib.Path(args.file)
    path.parent.mkdir(parents=True, exist_ok=True)

    if args.action == "append":
        append_content(path, args.content)
    elif args.action == "replace_section":
        if not args.section:
            print("--section مطلوب مع replace_section", file=sys.stderr)
            sys.exit(1)
        replace_section(path, args.section, args.content)

    print(f"✓ {args.file} updated ({args.action})")

if __name__ == "__main__":
    main()
