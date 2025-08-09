from gas_schema_generator.core.model import DynamicParams, StaticConfig


def test_static_ok(tmp_path):
    ok, msg = StaticConfig("ACME", "+370 600 00000", "a@b.lt", str(tmp_path)).validate()
    assert ok, msg

def test_dynamic_ok():
    ok, msg = DynamicParams(2, (5.0, 150.0)).validate()
    assert ok, msg
