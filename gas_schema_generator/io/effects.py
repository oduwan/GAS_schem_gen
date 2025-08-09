from __future__ import annotations
import json
import os
from typing import Callable, Optional
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.pagesizes import A4
from ..core.config import config_path
from ..core.model import StaticConfig, AppState
from ..core.intents import Intent
from .pdf_drawer import Drawer
from ..core.domain import select_equipment


def effect_load_config(dispatch: Callable[[Intent, object | None], None]):
    cfg: Optional[StaticConfig] = None
    p = config_path()
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            cfg = StaticConfig(
                company_name=data.get("company_name", ""),
                phone=data.get("phone", ""),
                email=data.get("email", ""),
                output_dir=data.get("output_dir", ""),
            )
            ok, _ = cfg.validate()
            if not ok:
                p.unlink(missing_ok=True)
                cfg = None
        except Exception:
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass
            cfg = None
    dispatch(Intent.CONFIG_LOADED, cfg)


def effect_save_config(cfg: StaticConfig, dispatch: Callable[[Intent, object | None], None]):
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
        dispatch(Intent.SETTINGS_SAVED, (True, ""))
    except Exception as e:
        dispatch(Intent.SETTINGS_SAVED, (False, str(e)))


def effect_generate_pdf(state: AppState, dispatch: Callable[[Intent, object | None], None]):
    assert state.config is not None
    dyn = state.dyn
    sel = select_equipment(dyn.inverter_powers_kw)
    base = f"GAS_schema_{dyn.inverter_count}inv_{int(sel.pmax_kw)}kW.pdf"
    out_path = os.path.join(state.config.output_dir, base)
    try:
        c = pdfcanvas.Canvas(out_path, pagesize=A4)
        Drawer(c).draw_schema(state.config, dyn, sel, out_path)
        dispatch(Intent.GENERATED, (True, out_path))
    except Exception as e:
        dispatch(Intent.GENERATED, (False, str(e)))