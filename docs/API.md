# API

## Pagrindiniai tipai
- `StaticConfig.validate() -> tuple[bool, str]`
- `DynamicParams.validate() -> tuple[bool, str]`
- `compute_pmax_kw(powers_kw: tuple[float, ...]) -> float`
- `select_equipment(powers_kw: tuple[float, ...]) -> Selection`

## Intents
`APP_START`, `CONFIG_LOADED`, `OPEN_SETTINGS`, `CLOSE_SETTINGS`, `SETTINGS_EDIT`, `SETTINGS_SAVE`, `SETTINGS_SAVED`, `DYN_SET_COUNT`, `DYN_SET_POWER`, `GENERATE`, `GENERATED`.

## Store
`dispatch(intent: Intent, payload: Any | None)`; subscribe(callback: (AppState) -> None).