from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable, List, Tuple

from .intents import Intent
from .model import AppState, StaticConfig, UiFlags

Dispatcher = Callable[[Intent, object | None], None]
Effect = Callable[[Dispatcher], None]
Reducer = Callable[[AppState, Intent, object | None], Tuple[AppState, List[Effect]]]

def _recalc_can_generate(state: AppState) -> AppState:
    """
    Recalculate the `can_generate` flag based on the current state.
    """
    okd, _ = state.dyn.validate()
    can = (state.config is not None) and okd
    return replace(state, ui=replace(state.ui, can_generate=bool(can)))


def reducer(state: AppState, intent: Intent, payload: object | None) -> tuple[AppState, list[Effect]]:
    effects: list[Effect] = []

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
        fields = payload if isinstance(payload, dict) else {}
        cfg = state.config or StaticConfig()
        cfg = replace(
            cfg,
            company_name=str(fields.get("company_name", cfg.company_name)),
            phone=str(fields.get("phone", cfg.phone)),
            email=str(fields.get("email", cfg.email)),
            output_dir=str(fields.get("output_dir", cfg.output_dir)),
        )
        return replace(state, config=cfg), effects

    if intent is Intent.SETTINGS_SAVE:
        if not isinstance(payload, StaticConfig):
            return replace(state, ui=replace(state.ui, message="Neteisingi nustatymai")), effects
        from ..io.effects import effect_save_config

        def _eff_save_config(d: Dispatcher, c: Any = payload) -> None:
            effect_save_config(c, d)

        effects.append(_eff_save_config)
        return state, effects

    if intent is Intent.SETTINGS_SAVED:
        ok, msg = payload if isinstance(payload, tuple) else (False, "Nežinoma klaida")
        if ok:
            ui = replace(state.ui, settings_open=False, message="Nustatymai išsaugoti.")
            s2 = replace(state, ui=ui)
            s2 = _recalc_can_generate(s2)
            return s2, effects
        else:
            return replace(state, ui=replace(state.ui, message=f"Klaida: {msg}")), effects

    if intent is Intent.DYN_SET_COUNT:
        count = int(payload) if isinstance(payload, (int, str)) else state.dyn.inverter_count
        default_powers = tuple((state.dyn.inverter_powers_kw + (5.0,) * 3)[:count])
        dyn = replace(state.dyn, inverter_count=count, inverter_powers_kw=default_powers)
        s2 = replace(state, dyn=dyn)
        return _recalc_can_generate(s2), effects

    if intent is Intent.DYN_SET_POWER:
        if isinstance(payload, tuple) and len(payload) == 2:
            idx_raw, val_raw = payload
            try:
                idx = int(idx_raw)
                val = float(val_raw)
            except Exception:
                idx = -1
                val = 0.0
            powers = list(state.dyn.inverter_powers_kw)
            if 0 <= idx < len(powers):
                powers[idx] = val
            dyn = replace(state.dyn, inverter_powers_kw=tuple(powers))
            s2 = replace(state, dyn=dyn)
            return _recalc_can_generate(s2), effects
        return state, effects

    if intent is Intent.GENERATE:
        if state.config is None:
            return replace(state, ui=replace(state.ui, message="Pirmiausia užpildykite nustatymus.")), effects
        ok1, _ = state.dyn.validate()
        ok2, _ = state.config.validate()
        if ok1 and ok2:
            from ..io.effects import effect_generate_pdf

            snap = state
            def _eff_generate_pdf(d: Dispatcher, s: AppState = snap) -> None:
                effect_generate_pdf(s, d)

            effects.append(_eff_generate_pdf)
            return state, effects
        else:
            return replace(state, ui=replace(state.ui, message="Patikrinkite įvestis.")), effects

    if intent is Intent.GENERATED:
        ok, info = payload if isinstance(payload, tuple) else (False, "Nežinoma klaida")
        if ok:
            return replace(state, ui=replace(state.ui, message=f"PDF išsaugotas: {info}")), effects
        else:
            return replace(state, ui=replace(state.ui, message=f"Klaida: {info}")), effects

    return state, effects

