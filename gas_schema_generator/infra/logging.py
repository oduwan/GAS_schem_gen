from __future__ import annotations
import logging

_configured = False
_FMT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logging once."""
    global _configured
    if _configured:
        return
    logging.basicConfig(level=level, format=_FMT)
    _configured = True