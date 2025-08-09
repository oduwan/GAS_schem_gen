from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple
import os
from .config import PHONE_RE, EMAIL_RE

@dataclass(frozen=True)
class StaticConfig:
    company_name: str = ""
    phone: str = ""
    email: str = ""
    output_dir: str = ""

    def validate(self) -> tuple[bool, str]:
        if not self.company_name.strip():
            return False, "Organizacijos pavadinimas yra privalomas."
        if not PHONE_RE.match(self.phone.strip()):
            return False, "Telefono numerio formatas neteisingas."
        if not EMAIL_RE.match(self.email.strip()):
            return False, "El. pašto formatas neteisingas."
        if not self.output_dir or not os.path.isdir(self.output_dir):
            return False, "Neteisingas išsaugojimo kelias."
        return True, ""

@dataclass(frozen=True)
class DynamicParams:
    inverter_count: int = 1
    inverter_powers_kw: Tuple[float, ...] = (5.0,)

    def validate(self) -> tuple[bool, str]:
        if not (1 <= self.inverter_count <= 3):
            return False, "Inverterių skaičius turi būti 1..3."
        if len(self.inverter_powers_kw) != self.inverter_count:
            return False, "Nurodykite galią kiekvienam inverteriui."
        for p in self.inverter_powers_kw:
            try:
                v = float(p)
            except Exception:
                return False, "Galia turi būti skaičius."
            if not (5 <= v <= 150):
                return False, "Kiekvieno inverterio galia turi būti 5..150 kW."
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