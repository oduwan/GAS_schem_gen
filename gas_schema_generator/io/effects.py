from __future__ import annotations

import json
import logging
import os
from typing import Callable, Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdfcanvas

from ..core.config import config_path
from ..core.domain import select_equipment
from ..core.intents import Intent
from ..core.model import AppState, StaticConfig
from ..infra.logging import setup_logging
from .pdf_drawer import Drawer

log = logging.getLogger(__name__)



def effect_load_config(dispatch: Callable[[Intent, object | None], None]) -> None:
    setup_logging()
    p = config_path()
    cfg: Optional[StaticConfig] = None
    try:
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            cfg = StaticConfig(
                company_name=data.get("company_name", ""),
                phone=data.get("phone", ""),
                email=data.get("email", ""),
                output_dir=data.get("output_dir", ""),
            )
            ok, msg = cfg.validate()
            if not ok:
                log.warning("Invalid config removed: %s | reason: %s", p, msg)
                p.unlink(missing_ok=True)
                cfg = None
        else:
            log.info("Config not found: %s", p)
    except Exception as e:
        log.exception("Failed to load config: %s", e)
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass
        cfg = None
    dispatch(Intent.CONFIG_LOADED, cfg)


def effect_save_config(cfg: StaticConfig, dispatch: Callable[[Intent, object | None], None]) -> None:
    setup_logging()
    try:
        ok, msg = cfg.validate()
        if not ok:
            raise ValueError(msg)
        p = config_path()
        p.write_text(json.dumps({
            "company_name": cfg.company_name,
            "phone": cfg.phone,
            "email": cfg.email,
            "output_dir": cfg.output_dir,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        log.info("Config saved: %s", p)
        dispatch(Intent.SETTINGS_SAVED, (True, ""))
    except Exception as e:
        log.exception("Failed to save config: %s", e)
        dispatch(Intent.SETTINGS_SAVED, (False, f"Nepavyko išsaugoti nustatymų: {e}"))


def effect_generate_pdf(state: AppState, dispatch: Callable[[Intent, object | None], None]) -> None:
    setup_logging()
    assert state.config is not None
    dyn = state.dyn
    sel = select_equipment(dyn.inverter_powers_kw)
    base = f"GAS_schema_{dyn.inverter_count}inv_{int(sel.pmax_kw)}kW.pdf"
    out_path = os.path.join(state.config.output_dir, base)
    try:
        c = pdfcanvas.Canvas(out_path, pagesize=A4)
        Drawer(c).draw_schema(state.config, dyn, sel, out_path)
        log.info("PDF generated: %s", out_path)
        dispatch(Intent.GENERATED, (True, out_path))
    except Exception as e:
        log.exception("PDF generation failed: %s", e)
        dispatch(Intent.GENERATED, (False, f"PDF generavimo klaida: {e}"))
