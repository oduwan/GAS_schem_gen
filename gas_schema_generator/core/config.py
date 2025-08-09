from __future__ import annotations

import re
from pathlib import Path

APP_NAME = "GAS Schema Generator (MVI)"
CONFIG_FILENAME = ".gas_config.json"

# Validation regexes (liberal phone, standard email)
PHONE_RE = re.compile(r"^[+]?\d[\d\s\-()]{5,}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Selection sets (A)
BREAKER_SET = [25, 32, 40, 50, 63, 80, 100, 125]
MCCB_SET = [160, 200, 250]
CT_SET = [150, 200, 250]

# Drawing units in ReportLab are points; 1 pt ≈ 0.3528 mm
ICON = 36  # pt (~12.7 mm)
PADDING = 10  # pt

def config_path() -> Path:
    return Path.home() / CONFIG_FILENAME
