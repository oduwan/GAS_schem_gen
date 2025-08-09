from gas_schema_generator.core.intents import Intent
from gas_schema_generator.core.model import AppState, DynamicParams, StaticConfig
from gas_schema_generator.core.reducer import reducer


def test_settings_flow(tmp_path):
    st = AppState()
    # открыть настройки
    st, eff = reducer(st, Intent.OPEN_SETTINGS, None)
    assert st.ui.settings_open

    # сохранить валидные настройки
    cfg = StaticConfig("ACME", "+37060000000", "x@y.lt", str(tmp_path))
    st, eff = reducer(st, Intent.SETTINGS_SAVE, cfg)
    # выполнить эффекты синхронно
    for e in eff:
        e(lambda *_: None)

def test_dynamic_and_generate(tmp_path):
    st = AppState(
        config=StaticConfig("ACME", "+37060000000", "x@y.lt", str(tmp_path)),
        dyn=DynamicParams(2, (10.0, 12.0)),
    )
    st, eff = reducer(st, Intent.GENERATE, None)
    for e in eff:
        e(lambda *_: None)
