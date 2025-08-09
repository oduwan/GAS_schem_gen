from gas_schema_generator.core.intents import Intent
from gas_schema_generator.core.model import StaticConfig
from gas_schema_generator.io.effects import effect_load_config, effect_save_config


def test_save_then_load(tmp_path):
    cfg = StaticConfig("ACME", "+37060000000", "x@y.lt", str(tmp_path))
    msgs = []
    effect_save_config(cfg, lambda i,p=None: msgs.append((i,p)))
    msgs.clear()
    effect_load_config(lambda i,p=None: msgs.append((i,p)))
    # должен прилететь CONFIG_LOADED с корректным StaticConfig
    assert any(i is Intent.CONFIG_LOADED and p for i,p in msgs)
