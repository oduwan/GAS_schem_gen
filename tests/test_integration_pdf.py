from gas_schema_generator.core.intents import Intent
from gas_schema_generator.core.model import AppState, DynamicParams, StaticConfig
from gas_schema_generator.core.reducer import reducer


def test_generate_pdf(tmp_path):
    st = AppState(
        config=StaticConfig("ACME", "+37060000000", "x@y.lt", str(tmp_path)),
        dyn=DynamicParams(1, (10.0,)),
    )
    st, effects = reducer(st, Intent.GENERATE, None)
    for eff in effects:
        eff(lambda *_: None)
    assert any(p.suffix == ".pdf" for p in tmp_path.iterdir())
