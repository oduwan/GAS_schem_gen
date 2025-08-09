from __future__ import annotations
from enum import Enum, auto

class Intent(Enum):
    APP_START = auto()
    CONFIG_LOADED = auto()          # payload: Optional[StaticConfig]

    OPEN_SETTINGS = auto()
    CLOSE_SETTINGS = auto()
    SETTINGS_EDIT = auto()          # payload: dict(fields)
    SETTINGS_SAVE = auto()          # payload: StaticConfig
    SETTINGS_SAVED = auto()         # payload: (ok: bool, msg: str)

    DYN_SET_COUNT = auto()          # payload: int
    DYN_SET_POWER = auto()          # payload: (index: int, value: Any)

    GENERATE = auto()
    GENERATED = auto()              # payload: (ok: bool, info: str)