# 运行时界面翻译目录：按中文原文查找译文，支持带占位符的模板与逐行回退。
"""Runtime translation catalog keyed by the original Chinese source text.

The catalog is display-only: program logic keeps working with the Chinese
source strings, and `translate()` is applied where text reaches a Qt widget
(see `src.i18n.qt_patch`). Untranslated text falls back to the original.

Catalog files live in `locales/<language>/*.json`. Each file is a flat JSON
object mapping source text to translation. Keys containing `{...}` fields are
templates: `"已保存{0}件"` matches `"已保存12件"`, and the captured values are
themselves translated before being substituted into the translation, so game
names embedded in sentences are translated too. Empty values mean "not yet
translated" and are ignored.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_CJK = re.compile(r"[　-〿㐀-鿿＀-￯]")
_IDEOGRAPH = re.compile(r"[\u3400-\u9fff]")
_FIELD = re.compile(r"\{([^{}]*)\}")
# Templates with fewer literal ideographs only match when every captured value
# was fully translated.
_WEAK_TEMPLATE = 3


@dataclass(frozen=True)
class _Template:
    pattern: re.Pattern[str]
    fields: tuple[str, ...]
    translation: str
    anchor: str
    # Chinese characters in the literal parts; weak templates such as "{0}型"
    # would otherwise match unrelated text.
    strength: int


class Catalog:
    """Immutable lookup over one language's exact strings and templates."""

    def __init__(self, entries: dict[str, str]) -> None:
        self._exact: dict[str, str] = {}
        templates: list[_Template] = []
        for source, translation in entries.items():
            if not translation or source == translation:
                continue
            template = _compile_template(source, translation)
            if template is None:
                self._exact[source] = translation
                # "\n额外形状：…" is appended to other text, then looked up line by line.
                stripped = source.strip()
                if stripped != source and stripped not in entries:
                    self._exact.setdefault(stripped, translation.strip())
            else:
                templates.append(template)
        # Longer anchors are more specific; try them first.
        templates.sort(key=lambda item: len(item.anchor), reverse=True)
        self._templates = tuple(templates)
        self._translate = lru_cache(maxsize=50_000)(self._translate_uncached)

    def __len__(self) -> int:
        return len(self._exact) + len(self._templates)

    def translate(self, text: str) -> str:
        if not text or not _CJK.search(text):
            return text
        return self._translate(text)

    def _translate_uncached(self, text: str, depth: int = 0) -> str:
        exact = self._exact.get(text)
        if exact is not None:
            return exact
        if "\r" in text:
            return self._translate_uncached(text.replace("\r\n", "\n").replace("\r", "\n"), depth)
        stripped = text.strip()
        if stripped != text and stripped:
            inner = self._exact.get(stripped)
            if inner is not None:
                start = text.index(stripped)
                return text[:start] + inner + text[start + len(stripped):]
        by_line = None
        if "\n" in text:
            lines = text.split("\n")
            translated = [self.translate(line) for line in lines]
            if translated != lines:
                by_line = "\n".join(translated)
                if not _IDEOGRAPH.search(by_line):
                    return by_line
        # Multi-line templates ("当前{0}模式不允许此功能。\n{1}") can finish what lines could not.
        templated = self._translate_templates(text, depth)
        if templated is not None and (by_line is None or not _IDEOGRAPH.search(templated)):
            return templated
        if by_line is not None:
            return by_line
        if depth < 2:
            composed = self._translate_segments(text, depth)
            if composed is not None:
                return composed
        return text

    def _translate_templates(self, text: str, depth: int) -> str | None:
        if depth < 3:
            for template in self._templates:
                if template.anchor not in text:
                    continue
                match = template.pattern.fullmatch(text)
                if match is None:
                    continue
                values = {
                    field: _english_punctuation(self._translate_uncached(value, depth + 1), value, trim=False)
                    if value and _IDEOGRAPH.search(value) else value
                    for field, value in zip(template.fields, match.groups())
                }
                if template.strength < _WEAK_TEMPLATE and any(
                    _IDEOGRAPH.search(value) for value in values.values()
                ):
                    continue
                return _FIELD.sub(
                    lambda field: values.get(field.group(1).split(":")[0].split("!")[0], field.group(0)),
                    template.translation,
                )
        return None

    def _translate_segments(self, text: str, depth: int) -> str | None:
        """Translate text assembled from known pieces ("1. " + name, label + "：").

        Splits on separators, translates each piece, and only succeeds when no
        Chinese is left, so a half-translated mix is never shown.
        """
        for splitter in _SEGMENT_SPLITTERS:
            pieces = splitter.split(text)
            if len(pieces) < 2:
                continue
            translated = [
                piece if splitter.fullmatch(piece) or not _IDEOGRAPH.search(piece)
                else self._translate_uncached(piece, depth + 1)
                for piece in pieces
            ]
            if not any(_IDEOGRAPH.search(piece) for piece in translated):
                joined = "".join(translated)
                # Nested pieces keep Chinese punctuation; the outermost call converts it once.
                return _english_punctuation(joined, text) if depth == 0 else joined
        return None


# Coarse separators first (keeps "（同类型）" whole), then brackets and sentence ends.
_SEGMENT_SPLITTERS = (
    # List joins ("、", " > ") split before names that contain "：" or "，" are cut apart.
    re.compile(r"(\s*[·｜|、]\s*|\s+>\s+|\s{2,})"),
    re.compile(r"(\s+)"),
    re.compile(r"(\s+|[｜|：:，,；;、·/→]+)"),
    re.compile(r"(\s+|[｜|：:，,；;、·/→（）()【】\[\]「」“”。]+)"),
)
_PUNCTUATION = {
    "：": ": ", "，": ", ", "；": "; ", "、": ", ", "｜": " | ", "（": " (", "）": ")",
    "【": "[", "】": "]", "「": "\"", "」": "\"", "“": "\"", "”": "\"", "。": ". ", "　": " ",
}


def _english_punctuation(text: str, source: str, trim: bool = True) -> str:
    for chinese, english in _PUNCTUATION.items():
        text = text.replace(chinese, english)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r" ([),.:;\]])", r"\1", text)
    text = re.sub(r"\( ", "(", text)
    if trim and not source[:1].isspace():
        text = text.lstrip(" ")
    if trim and not source[-1:].isspace():
        text = text.rstrip(" ")
    return text


def _compile_template(source: str, translation: str) -> _Template | None:
    """Build a matcher for a `{field}` template, or None for plain strings."""
    parts = _FIELD.split(source)
    if len(parts) == 1:
        return None
    literals = parts[0::2]
    fields = tuple(name.split(":")[0].split("!")[0] for name in parts[1::2])
    if not any(_CJK.search(literal) for literal in literals):
        return None
    regex = "".join(
        re.escape(literal) if index % 2 == 0 else "(.*?)"
        for index, literal in enumerate(parts)
    )
    return _Template(
        pattern=re.compile(regex, re.DOTALL),
        fields=fields,
        translation=translation,
        anchor=max(literals, key=len),
        strength=sum(len(_IDEOGRAPH.findall(literal)) for literal in literals),
    )


def load_catalog(locale_dir: Path) -> Catalog:
    """Merge every `*.json` in `locale_dir`; later files (sorted) win on conflicts."""
    entries: dict[str, str] = {}
    if locale_dir.is_dir():
        for path in sorted(locale_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                entries.update(
                    (str(key), value) for key, value in data.items() if isinstance(value, str) and value
                )
    return Catalog(entries)
