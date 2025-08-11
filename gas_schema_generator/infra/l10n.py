from __future__ import annotations

import importlib.resources as pkgres
import json
from typing import Dict, cast

_CACHE_UI: Dict[str, Dict[str, str]] = {}
_CACHE_PDF: Dict[str, Dict[str, str]] = {}

def _load_json(package: str, resource: str) -> Dict[str, str]:
    with pkgres.files(package).joinpath(resource).open("r", encoding="utf-8") as f:
        return cast(dict[str, str], json.load(f))

def get_ui(lang: str = "lt") -> Dict[str, str]:
    if lang not in _CACHE_UI:
        try:
            _CACHE_UI[lang] = _load_json("gas_schema_generator.locales", f"{lang}.json")
        except FileNotFoundError:
            _CACHE_UI[lang] = _load_json("gas_schema_generator.locales", "lt.json")
    return _CACHE_UI[lang]

def get_labels(lang: str = "lt") -> Dict[str, str]:
    if lang not in _CACHE_PDF:
        try:
            _CACHE_PDF[lang] = _load_json("gas_schema_generator.labels", f"{lang}.json")
        except FileNotFoundError:
            _CACHE_PDF[lang] = _load_json("gas_schema_generator.labels", "lt.json")
    return _CACHE_PDF[lang]

def t(key: str, lang: str = "lt", default: str | None = None) -> str:
    return get_ui(lang).get(key, default or key)

def get_pdf_label(key: str, lang: str = "lt", default: str | None = None) -> str:
    return get_labels(lang).get(key, default or key)
