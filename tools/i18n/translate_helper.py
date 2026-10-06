# 翻译工作辅助：列出待翻译条目，并把译文补丁校验后合并进目录文件。
"""Helper for filling a catalog file in small, validated steps.

    python tools/i18n/translate_helper.py todo <catalog.json> [--limit 80]
        Print the next untranslated entries as a JSON object (source -> "")
        plus where each string appears in the code (from build/i18n).

    python tools/i18n/translate_helper.py apply <catalog.json> <patch.json>
        Merge a patch (source -> translation) into the catalog. Entries that
        fail validation (see check_catalog.check_pair) or whose key is not in
        the catalog are rejected and listed; valid ones are written.

    python tools/i18n/translate_helper.py glossary <word>...
        Look up official game terms in locales/en/game.json (substring match).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_catalog import check_pair  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path) -> dict[str, str]:
    return json.loads(path.read_text(encoding="utf-8"))


def todo(catalog_path: Path, limit: int) -> None:
    catalog = _load(catalog_path)
    sources_path = ROOT / "build" / "i18n" / f"{catalog_path.stem}.sources.json"
    sources = _load(sources_path) if sources_path.is_file() else {}
    pending = [key for key, value in catalog.items() if not value]
    batch = pending[:limit]
    print(f"# {len(pending)} untranslated in {catalog_path.name}; showing {len(batch)}")
    print("# where used:")
    for key in batch:
        print(f"#   {sources.get(key, '?')}  {key[:60]!r}")
    print(json.dumps({key: "" for key in batch}, ensure_ascii=False, indent=1))


def apply(catalog_path: Path, patch_path: Path) -> int:
    catalog = _load(catalog_path)
    patch = _load(patch_path)
    accepted = rejected = 0
    for source, translation in patch.items():
        if source not in catalog:
            print(f"REJECT (key not in catalog): {source!r}")
            rejected += 1
            continue
        if not isinstance(translation, str) or not translation:
            continue
        problems = check_pair(source, translation)
        if problems:
            print(f"REJECT {source!r} -> {translation!r}: {'; '.join(problems)}")
            rejected += 1
            continue
        catalog[source] = translation
        accepted += 1
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    remaining = sum(1 for value in catalog.values() if not value)
    print(f"accepted {accepted}, rejected {rejected}, remaining untranslated {remaining}")
    return 1 if rejected else 0


def glossary(words: list[str]) -> None:
    game = _load(ROOT / "locales" / "en" / "game.json")
    for word in words:
        hits = [(key, value) for key, value in game.items() if word in key and not key.startswith("「")]
        hits.sort(key=lambda item: len(item[0]))
        print(f"{word}:")
        for key, value in hits[:12]:
            print(f"  {key} => {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    todo_parser = commands.add_parser("todo")
    todo_parser.add_argument("catalog", type=Path)
    todo_parser.add_argument("--limit", type=int, default=80)
    apply_parser = commands.add_parser("apply")
    apply_parser.add_argument("catalog", type=Path)
    apply_parser.add_argument("patch", type=Path)
    glossary_parser = commands.add_parser("glossary")
    glossary_parser.add_argument("words", nargs="+")
    args = parser.parse_args()
    if args.command == "todo":
        todo(args.catalog, args.limit)
        return 0
    if args.command == "apply":
        return apply(args.catalog, args.patch)
    glossary(args.words)
    return 0


if __name__ == "__main__":
    sys.exit(main())
