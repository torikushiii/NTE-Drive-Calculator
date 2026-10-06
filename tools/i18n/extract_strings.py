# 提取源码中的中文界面文本，按功能区写入 locales/<语言>/ui_*.json 待翻译目录。
"""Extract Chinese display strings from `src/` into per-area catalog files.

    python tools/i18n/extract_strings.py [--language en]

Plain literals become exact keys; f-strings become templates with numbered
fields (`f"已保存{count}件"` -> `"已保存{0}件"`), which `src.i18n.catalog`
matches at runtime. Logger calls and docstrings are skipped. Each key is
assigned to the area where it first appears (`ui_features_inventory.json`,
...), so files can be translated independently. Existing translations are
kept; new keys get an empty value; keys no longer in the source are dropped
unless they are already translated.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_CJK = re.compile(r"[㐀-鿿]")
CHUNK_SIZE = 450
_LOGGER_METHODS = {"debug", "info", "warning", "error", "exception", "critical", "success", "trace"}


def _area(path: Path) -> str:
    parts = path.relative_to(ROOT / "src").parts
    if parts[0] == "features" and len(parts) > 2:
        return f"features_{parts[1]}"
    return parts[0].removesuffix(".py")


def _is_logger_call(node: ast.Call) -> bool:
    func = node.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr in _LOGGER_METHODS
        and isinstance(func.value, ast.Name)
        and "log" in func.value.id.lower()
    )


def _template(node: ast.JoinedStr) -> str | None:
    pieces: list[str] = []
    field = 0
    for value in node.values:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            pieces.append(value.value)
        elif isinstance(value, ast.FormattedValue):
            pieces.append(f"{{{field}}}")
            field += 1
        else:
            return None
    return "".join(pieces)


def _concat_template(node: ast.BinOp) -> str | None:
    """Template for a `+` chain mixing string literals and other expressions."""
    parts: list[ast.expr] = []

    def flatten(expr: ast.expr) -> None:
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
            flatten(expr.left)
            flatten(expr.right)
        else:
            parts.append(expr)

    flatten(node)
    pieces: list[str] = []
    field = 0
    has_literal = has_field = False
    for part in parts:
        if isinstance(part, ast.Constant) and isinstance(part.value, str):
            pieces.append(part.value)
            has_literal = True
        elif isinstance(part, ast.JoinedStr):
            for value in part.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    pieces.append(value.value)
                    has_literal = True
                else:
                    pieces.append(f"{{{field}}}")
                    field += 1
                    has_field = True
        elif isinstance(part, ast.Constant):
            return None  # numeric addition, not string building
        else:
            pieces.append(f"{{{field}}}")
            field += 1
            has_field = True
    if not (has_literal and has_field):
        return None
    return "".join(pieces)


class _Collector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.found: list[tuple[str, int]] = []
        self._skip: set[int] = set()
        self._inside_concat = False

    def visit_Module(self, node: ast.Module) -> None:
        self._skip_docstring(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._skip_docstring(node)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._skip_docstring(node)
        self.generic_visit(node)

    def _skip_docstring(self, node: ast.AST) -> None:
        body = getattr(node, "body", None)
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            self._skip.add(id(body[0].value))

    def visit_Call(self, node: ast.Call) -> None:
        if _is_logger_call(node):
            return
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        # "当前" + mode + "模式不允许" is one runtime string: record it as a template
        # too. The pieces are still collected individually by generic_visit.
        if isinstance(node.op, ast.Add) and not self._inside_concat:
            text = _concat_template(node)
            if text is not None and _CJK.search(text):
                self.found.append((text, node.lineno))
            self._inside_concat = True
            self.generic_visit(node)
            self._inside_concat = False
            return
        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        text = _template(node)
        if text is not None and _CJK.search(text):
            self.found.append((text, node.lineno))
        # Visit embedded expressions only; literal parts belong to the template.
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                self.visit(value.value)

    def visit_Constant(self, node: ast.Constant) -> None:
        if id(node) in self._skip or not isinstance(node.value, str):
            return
        if _CJK.search(node.value):
            # str.format templates keep their own field names.
            self.found.append((node.value, node.lineno))


def extract() -> dict[str, dict[str, str]]:
    """Return {area: {source text: "file:line"}} with each key in its first area."""
    seen: set[str] = set()
    areas: dict[str, dict[str, str]] = {}
    for path in sorted((ROOT / "src").rglob("*.py")):
        if "i18n" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        collector = _Collector()
        collector.visit(tree)
        relative = path.relative_to(ROOT).as_posix()
        for text, line in collector.found:
            if text in seen or not text.strip():
                continue
            seen.add(text)
            areas.setdefault(_area(path), {})[text] = f"{relative}:{line}"
    return areas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", default="en")
    args = parser.parse_args()
    locale_dir = ROOT / "locales" / args.language
    locale_dir.mkdir(parents=True, exist_ok=True)

    existing: dict[str, str] = {}
    for path in locale_dir.glob("ui_*.json"):
        existing.update(json.loads(path.read_text(encoding="utf-8")))

    context_dir = ROOT / "build" / "i18n"
    context_dir.mkdir(parents=True, exist_ok=True)
    for stale in [*locale_dir.glob("ui_*.json"), *context_dir.glob("ui_*.sources.json")]:
        stale.unlink()
    areas = extract()
    placed: set[str] = set()
    total = translated = files = 0
    for area, strings in areas.items():
        items = list(strings.items())
        # Large areas are split so each file is a reasonable unit of translation work.
        chunks = [items[start:start + CHUNK_SIZE] for start in range(0, len(items), CHUNK_SIZE)]
        for number, chunk in enumerate(chunks, 1):
            name = f"ui_{area}" if len(chunks) == 1 else f"ui_{area}_{number:02d}"
            catalog = {text: existing.get(text, "") for text, _ in chunk}
            placed.update(catalog)
            total += len(catalog)
            translated += sum(1 for value in catalog.values() if value)
            files += 1
            _write(locale_dir / f"{name}.json", catalog)
            _write(context_dir / f"{name}.sources.json", dict(chunk))
    orphans = {text: value for text, value in existing.items() if value and text not in placed}
    if orphans:
        _write(locale_dir / "ui_zz_retired.json", orphans)
    print(f"{total} strings in {files} files, {translated} translated, {len(orphans)} retired")


def _write(path: Path, data: dict[str, str]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
