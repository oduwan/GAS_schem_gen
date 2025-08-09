from __future__ import annotations

import re

_WS = re.compile(r"\s+")

def sanitize_str(s: str) -> str:
    """Схлопывает лишние пробелы и обрезает края."""
    return _WS.sub(" ", s or "").strip()

def normalize_phone(s: str) -> str:
    """Оставляет только ведущий '+' и цифры."""
    return re.sub(r"[^+\d]", "", s or "")

def field_error(field: str, msg: str) -> str:
    return f"[{field}] {msg}"

def range_error(field: str, lo: float, hi: float) -> str:
    return field_error(field, f"turi būti {lo}..{hi}")

def must_be_float(field: str) -> str:
    return field_error(field, "turi būti skaičius")
