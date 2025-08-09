from __future__ import annotations
from dataclasses import replace
from typing import Callable, Optional
from .model import AppState, UiFlags, StaticConfig
from .intents import Intent

Reducer = Callable[[AppState, Intent, Optional[object]], tuple[AppState, list[Callable]]]


def _recalc_can_generate(state: AppState) -> AppState:
    can = False
    if state.config is not None:
        okd, _ = state.dyn.validate()
        can = okd
    return replace(state, ui=replace(state.ui, can_generate=can))


def reducer(state: AppState, intent: Intent, payload: Optional[object]):
    effects: list[Callable] = []

    if intent is Intent.APP_START:
        from ..io.effects import effect_load_config
        effects.append(lambda d: effect_load_config(d))
        return state, effects

    if intent is Intent.CONFIG_LOADED:
        cfg = payload if isinstance(payload, (StaticConfig, type(None))) else None
        ui = UiFlags(settings_open=(cfg is None))
        new = replace(state, config=cfg, ui=ui)
        new = _recalc_can_generate(new)
        return new, effects

    if intent is Intent.OPEN_SETTINGS:
        return replace(state, ui=replace(state.ui, settings_open=True)), effects

    if intent is Intent.CLOSE_SETTINGS:
        return replace(state, ui=replace(state.ui, settings_open=False)), effects

    if intent is Intent.SETTINGS_EDIT:
        fields = payload or {}
        cfg = state.config or StaticConfig()
        cfg = replace(cfg,
            company_name=fields.get("company_name", cfg.company_name),
            phone=fields.get("phone", cfg.phone),
            email=fields.get("email", cfg.email),
            output_dir=fields.get("output_dir", cfg.output_dir),
        )
        return replace(state, config=cfg), effects

    if intent is Intent.SETTINGS_SAVE:
        cfg = payload
        from ..io.effects import effect_save_config
        effects.append(lambda d, c=cfg: effect_save_config(c, d))
        return state, effects

    if intent is Intent.SETTINGS_SAVED:
        ok, msg = payload
        if ok:
            ui = replace(state.ui, settings_open=False, message="Nustatymai išsaugoti.")
            s2 = replace(state, ui=ui)
            s2 = _recalc_can_generate(s2)
            return s2, effects
        else:
            return replace(state, ui=replace(state.ui, message=f"Klaida: {msg}")), effects

    if intent is Intent.DYN_SET_COUNT:
        count = int(payload)
        powers = tuple((state.dyn.inverter_powers_kw + (5.0,) * 3)[:count])
        dyn = replace(state.dyn, inverter_count=count, inverter_powers_kw=powers)
        s2 = replace(state, dyn=dyn)
        return _recalc_can_generate(s2), effects

    if intent is Intent.DYN_SET_POWER:
        idx, val = payload
        powers = list(state.dyn.inverter_powers_kw)
        if 0 <= idx < len(powers):
            try:
                powers[idx] = float(val)
            except Exception:
                pass
        dyn = replace(state.dyn, inverter_powers_kw=tuple(powers))
        s2 = replace(state, dyn=dyn)
        return _recalc_can_generate(s2), effects

    if intent is Intent.GENERATE:
        if state.config is None:
            return replace(state, ui=replace(state.ui, message="Pirmiausia užpildykite nustatymus.")), effects
        ok1, _ = state.dyn.validate()
        ok2, _ = state.config.validate()
        if ok1 and ok2:
            from ..io.effects import effect_generate_pdf
            snap = state
            effects.append(lambda d, s=snap: effect_generate_pdf(s, d))
            return state, effects
        else:
            return replace(state, ui=replace(state.ui, message="Patikrinkite įvestis.")), effects

    if intent is Intent.GENERATED:
        ok, info = payload
        if ok:
            return replace(state, ui=replace(state.ui, message=f"PDF išsaugotas: {info}")), effects
        else:
            return replace(state, ui=replace(state.ui, message=f"Klaida: {info}")), effects

    return state, effects