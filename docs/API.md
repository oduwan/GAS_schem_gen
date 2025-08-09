# GAS Schema Generator — API dokumentacija

Šis dokumentas aprašo pagrindines projekto programavimo sąsajas (API) kūrėjams.

---

## 1. Modeliai

### `StaticConfig`
```python
@dataclass(frozen=True)
class StaticConfig:
    company_name: str
    phone: str
    email: str
    output_dir: str

    def cleaned(self) -> StaticConfig
    def validate(self) -> tuple[bool, str]
```
Aprašo statinius nustatymus, kurie saugomi konfigūracijos faile.

### `DynamicParams`
```python
@dataclass(frozen=True)
class DynamicParams:
    inverter_count: int
    inverter_powers_kw: tuple[float, ...]

    def validate(self) -> tuple[bool, str]
```
Aprašo dinamiškus parametrus vienai schemos generavimo sesijai.

### `AppState`
```python
@dataclass(frozen=True)
class AppState:
    config: Optional[StaticConfig]
    dyn: Optional[DynamicParams]
```
Bendras aplikacijos būsenos objektas.

## 2. Intents (core/intents.py)
Naudojami MVI architektūroje veiksmams apibrėžti.
    LOAD_CONFIG – įkelti konfigūraciją iš failo
    SAVE_CONFIG – išsaugoti konfigūraciją
    SETTINGS_SAVED – nustatymai išsaugoti (sėkmė/klaida)
    CONFIG_LOADED – konfigūracija įkelta
    GENERATE – pradėti PDF generavimą
    GENERATED – PDF sugeneruotas (sėkmė/klaida)
    UPDATE_DYNAMIC – atnaujinti dinamiškus parametrus



