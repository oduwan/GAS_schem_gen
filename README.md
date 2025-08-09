# GAS Schema Generator

Parametrinis GAS skydžio schemų generatorius (Python, Tkinter, ReportLab).

## Projekto tikslas
Programa generuoja PDF formato GAS elektros skydžio schemą pagal naudotojo įvestus parametrus.

---

## Naudojimas

### 1. Sistemos reikalavimai
- Python ≥ 3.10
- Veikianti `pip` aplinka
- OS: Windows / Linux / macOS

### 2. Įradimas
# Sukurkite virtualią aplinką
python -m venv .venv

# Aktyvuokite aplinką
# Linux / macOS:
source .venv/bin/activate
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Įdiekite naudotojo priklausomybes
pip install -r requirements.txt

# Jei dirbate su kodu (vystymo rėžimas) - įdiekite ir dev-priklausomybes
pip install -r requirements-dev.txt

### 3. Paleidimas
python -m gas_schema_generator.main

### 4. Testai
# Paleisti vien tik testus
pytest -q

# Paleisti testus su kodo padengimo ataskaita
pytest --cov=gas_schema_generator --cov-report=term-missing

### 5. Kodo kokybė
# Ruff (lint)
ruff check .

# Mypy (tipų tikrinimas)
mypy gas_schema_generator

### Projekto struktura

GAS_schem_gen/
├── gas_schema_generator/     # Pagrindinis paketas
│   ├── core/                  # Verslo logika, modeliai, validacija
│   ├── io/                    # PDF generavimas, failų įkėlimas/išsaugojimas
│   ├── ui/                    # Tkinter GUI
│   ├── infra/                 # Infrastruktūra (store, logging)
│   └── main.py                 # Paleidimo taškas
├── tests/                      # Unit ir integraciniai testai
├── requirements.txt            # Naudotojo priklausomybės
├── requirements-dev.txt        # Dev-priklausomybės
└── README.md                   # Dokumentacija

### Darpo jega

Konfigūracija saugoma naudotojo kataloge (~/.config/... arba %APPDATA% Windows).

# Prieš commit'ą:

Paleiskite ruff check . ir mypy gas_schema_generator

Paleiskite pytest --cov ir įsitikinkite, kad padengimas nenukrito

# Pakeitus UI logiką ar domeno modelius, pridėkite atitinkamus testus