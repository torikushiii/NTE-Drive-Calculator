# 校验翻译目录：统计未翻译项，检查占位符、换行与残留中文。
"""Validate `locales/<language>/ui_*.json` translations.

    python tools/i18n/check_catalog.py [files...] [--language en] [--strict]

Reports, per file: untranslated count, and errors for translations whose
`{field}` placeholders differ from the source, whose line count differs,
that still contain Chinese ideographs, or that lost leading/trailing
whitespace. Exits 1 if any error is found (or, with --strict, if anything is
untranslated).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_FIELD = re.compile(r"\{[^{}]*\}")
_IDEOGRAPH = re.compile(r"[㐀-鿿]")
_HTML_TAG = re.compile(r"</?[a-zA-Z][^<>]*>")


def check_pair(source: str, translation: str) -> list[str]:
    problems = []
    if Counter(_FIELD.findall(source)) != Counter(_FIELD.findall(translation)):
        problems.append(f"placeholders {sorted(_FIELD.findall(source))} -> {sorted(_FIELD.findall(translation))}")
    if source.count("\n") != translation.count("\n"):
        problems.append(f"line breaks {source.count(chr(10))} -> {translation.count(chr(10))}")
    if _IDEOGRAPH.search(translation):
        problems.append("contains Chinese")
    if Counter(_HTML_TAG.findall(source)) != Counter(_HTML_TAG.findall(translation)):
        problems.append("HTML tags differ")
    for edge, label in ((source[:1], "leading"), (source[-1:], "trailing")):
        if edge.isspace() and (translation[:1] if label == "leading" else translation[-1:]) != edge:
            problems.append(f"{label} whitespace lost")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path)
    parser.add_argument("--language", default="en")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    files = args.files or sorted((ROOT / "locales" / args.language).glob("ui_*.json"))

    errors = untranslated = total = 0
    for path in files:
        try:
            catalog = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"{path.name}: INVALID JSON: {exc}")
            errors += 1
            continue
        missing = sum(1 for value in catalog.values() if not value)
        total += len(catalog)
        untranslated += missing
        file_errors = []
        for source, translation in catalog.items():
            if translation:
                file_errors += [f"  {source!r}: {problem}" for problem in check_pair(source, translation)]
        errors += len(file_errors)
        print(f"{path.name}: {len(catalog) - missing}/{len(catalog)} translated, {len(file_errors)} errors")
        for line in file_errors[:50]:
            print(line)
    print(f"TOTAL: {total - untranslated}/{total} translated, {errors} errors")
    return 1 if errors or (args.strict and untranslated) else 0


if __name__ == "__main__":
    sys.exit(main())
