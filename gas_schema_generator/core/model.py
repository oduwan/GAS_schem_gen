from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Tuple

from .config import EMAIL_RE, PHONE_RE
from .validation import field_error, must_be_float, normalize_phone, range_error, sanitize_str


@dataclass(frozen=True)
class StaticConfig:
    company_name: str = ""
    phone: str = ""
    email: str = ""
    output_dir: str = ""

    def cleaned(self) -> "StaticConfig":
        return StaticConfig(
            company_name=sanitize_str(self.company_name),
            phone=normalize_phone(self.phone),
            email=sanitize_str(self.email),
            output_dir=sanitize_str(self.output_dir),
        )

    def validate(self) -> tuple[bool, str]:
        c = self.cleaned()
        if not c.company_name:
            return False, field_error("Organizacija", "privalomas laukas")
        if not PHONE_RE.match(c.phone):
            return False, field_error("Telefonas", "neteisingas formatas")
        if not EMAIL_RE.match(c.email):
            return False, field_error("El. paštas", "neteisingas formatas")
        if not c.output_dir or not os.path.isdir(c.output_dir):
            return False, field_error("Kelias", "neteisingas arba nepasiekiamas")
        return True, ""

@dataclass(frozen=True)
class DynamicParams:
    inverter_count: int = 1
    inverter_powers_kw: Tuple[float, ...] = (5.0,)

    def validate(self) -> tuple[bool, str]:
        if not (1 <= self.inverter_count <= 3):
            return False, range_error("Inverterių skaičius", 1, 3)
        if len(self.inverter_powers_kw) != self.inverter_count:
            return False, field_error("Galia", "nurodykite kiekvienam inverteriui")
        for idx, p in enumerate(self.inverter_powers_kw, 1):
            try:
                v = float(p)
            except Exception:
                return False, must_be_float(f"Inverteris {idx} galia")
            if not (5 <= v <= 150):
                return False, range_error(f"Inverteris {idx} galia (kW)", 5, 150)
        return True, ""

@dataclass(frozen=True)
class Selection:
    pmax_kw: float
    direct_metering: bool
    per_inv_breaker_a: int
    main_breaker_a: int
    ct_rating_a: Optional[int]

@dataclass(frozen=True)
class UiFlags:
    settings_open: bool = False
    can_generate: bool = False
    message: str = ""

@dataclass(frozen=True)
class AppState:
    config: Optional[StaticConfig] = None
    dyn: DynamicParams = DynamicParams()
    sel: Optional[Selection] = None
    ui: UiFlags = UiFlags()
