# Percorso didattico `learning/` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Costruire in `learning/` un percorso formativo in cinque notebook che porti da zero fino a una stima di previsione elementare, insegnando anche i limiti di ciò che si è ottenuto.

**Architecture:** Cinque notebook sequenziali che comunicano esclusivamente tramite file in `learning/data/`, più un modulo `common.py` che contiene solo ciò che è ripetitivo e non didattico (path, bbox regionali, download con cache e checksum). Il contenuto meteorologico e statistico resta visibile nelle celle.

**Tech Stack:** Python 3.12, xarray + cfgrib/eccodes per GRIB, pandas + pyarrow per tabelle, matplotlib + cartopy per mappe, requests per download, pytest per i test di `common.py`.

**Spec:** `docs/superpowers/specs/2026-08-29-learning-path-design.md`

## Global Constraints

- **Python 3.12** (`/opt/homebrew/bin/python3.12`, verificato 3.12.12). NON usare il Python di sistema `/usr/bin/python3`, che è 3.9.6 e non regge lo stack.
- Venv locale a `learning/.venv`. Già coperto da `.gitignore` (`.venv/`), come `learning/data/` (`data/`).
- **Nessun dato committato**: né CSV, né Parquet, né GRIB, né output di cella dei notebook.
- Commenti professionali **in italiano** per ogni funzione di `common.py`; anche la narrazione dei notebook è in italiano.
- Tutti i timestamp sono UTC e tz-aware. Usare `datetime.now(timezone.utc)`, mai `utcnow()` (deprecato).
- Gli intervalli temporali sono half-open `[start, end)`.
- Ogni notebook chiude con una sezione **"Il limite di quello che hai fatto"**.
- Ogni notebook si apre con un controllo degli input che nomina il notebook mancante, mai un `FileNotFoundError` nudo.

## Fatti verificati il 2026-08-29 (non riverificare, usare così)

Questi valori sono stati misurati durante la stesura del piano. Sono la base del codice sotto.

- **Wheel disponibili per tutte le dipendenze binarie**: `pip install cfgrib eccodes cartopy` funziona in un venv 3.12 **senza Homebrew**. Versioni risolte: cfgrib 0.9.15.1, eccodes 2.48.0 (+ `eccodeslib` 2.48.0.26 come dipendenza automatica), Cartopy 0.25.0, xarray 2026.7.0, pandas 3.0.5, pyarrow 25.0.1, matplotlib 3.11.1, numpy 2.5.2, requests 2.34.2. Import a runtime verificati tutti OK.
- **Inventario ISD**: `https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv`, HTTP 200, ~2,91 MB. Colonne esatte: `USAF, WBAN, STATION NAME, CTRY, STATE, ICAO, LAT, LON, ELEV(M), BEGIN, END`. Date in formato `%Y%m%d`.
- **Numeri riproducibili**: `CTRY=IT` → **318** record; candidate con `BEGIN<=2021-01-01` e `END>=2025-08-01` → **124**; per quota: **89** sotto 300 m, **22** fra 300 e 999 m, **13** da 1.000 m. Coincidono con il doc 05.
- **Discrepanza nota**: le stazioni con LAT/LON valorizzate sono **311**, non 317 come afferma il doc 05. Va gestita nel Task 8, non nascosta.
- **NOMADS GFS**: endpoint `https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25_1hr.pl`, parametro `dir=/gfs.YYYYMMDD/CC/atmos`, `file=gfs.tCCz.pgrb2.0p25.fFFF`. Un subset T2m su bbox Piemonte restituisce un GRIB2 valido di ~300 byte che `xarray.open_dataset(..., engine="cfgrib")` apre come griglia **11×11** con variabile `t2m`. La piccolezza del file è legittima: una variabile, area ridotta, packing GRIB2.
- **Il bbox Piemonte pesca fuori regione**: include Milano Linate, Malpensa, Cameri (Lombardia) e Genova Sestri (Liguria). È la prova concreta che la mappa dell'area è necessaria; va usata come esempio didattico esplicito nel Task 8.

---

## File Structure

| File | Responsabilità |
| --- | --- |
| `learning/README.md` | Cos'è e cosa NON è il percorso; setup; ordine dei notebook |
| `learning/requirements.txt` | Dipendenze pinnate alle versioni verificate |
| `learning/common.py` | Path, bbox regionali, download con cache+checksum, controllo prerequisiti |
| `learning/test_common.py` | Test del solo `common.py` |
| `learning/notebooks/01-setup-e-fondamenti.ipynb` | Verifica ambiente + nozioni base |
| `learning/notebooks/02-osservazioni-isd.ipynb` | Inventario, scelta area, stazioni, osservazioni |
| `learning/notebooks/03-forecast-gfs-grib.ipynb` | Download GFS, lettura GRIB, mappe, griglia→punto |
| `learning/notebooks/04-join-e-anti-leakage.ipynb` | Join temporale, leakage dimostrato, split |
| `learning/notebooks/05-baseline-e-previsione.ipynb` | Baseline, bias correction, metriche, limiti |

I Task 1-5 costruiscono e testano `common.py` in TDD. I Task 6-10 producono README/requirements e i notebook.

---

### Task 1: Scaffolding e requirements

**Files:**
- Create: `learning/requirements.txt`
- Create: `learning/notebooks/.gitkeep`

**Interfaces:**
- Consumes: niente
- Produces: un venv funzionante in `learning/.venv` con lo stack completo installato

- [ ] **Step 1: Creare la struttura e il file requirements**

```bash
mkdir -p learning/notebooks && touch learning/notebooks/.gitkeep
cat > learning/requirements.txt <<'EOF'
# Percorso didattico Nimbus - versioni verificate il 2026-08-29 su Python 3.12.
# Installare in un venv dedicato: vedere learning/README.md.

# Dati tabellari e formati colonnari
pandas==3.0.5
pyarrow==25.0.1
numpy==2.5.2

# Lettura GRIB dei forecast NWP.
# eccodes/eccodeslib sono le librerie binarie ECMWF: arrivano come wheel,
# quindi su questa piattaforma NON serve installare eccodes via Homebrew.
xarray==2026.7.0
cfgrib==0.9.15.1
eccodes==2.48.0

# Grafici e mappe. Cartopy porta con se' GEOS/PROJ come wheel.
matplotlib==3.11.1
Cartopy==0.25.0

# Download da NOMADS e NCEI
requests==2.34.2

# Ambiente notebook
jupyterlab==4.4.7

# Test del solo common.py
pytest==8.4.2
EOF
```

- [ ] **Step 2: Creare il venv e installare**

```bash
/opt/homebrew/bin/python3.12 -m venv learning/.venv
learning/.venv/bin/pip install --upgrade pip
learning/.venv/bin/pip install -r learning/requirements.txt
```

Se una versione pinnata non fosse più risolvibile, installare senza pin, poi rigenerare i pin con `learning/.venv/bin/pip freeze | grep -iE 'pandas|pyarrow|numpy|xarray|cfgrib|eccodes|matplotlib|Cartopy|requests|jupyterlab|pytest'` e aggiornare il file.

- [ ] **Step 3: Verificare che gli import critici funzionino**

```bash
learning/.venv/bin/python -c "
import eccodes, cfgrib, cartopy, xarray, pandas, pyarrow, matplotlib
print('eccodes', eccodes.codes_get_api_version())
print('cfgrib', cfgrib.__version__)
print('cartopy', cartopy.__version__)
print('xarray', xarray.__version__)
"
```

Expected: quattro righe di versione, nessuna eccezione.

- [ ] **Step 4: Commit**

```bash
git add learning/requirements.txt learning/notebooks/.gitkeep
git commit -m "feat: add learning path scaffolding and pinned requirements"
```

---

### Task 2: `common.py` — path e struttura dati

**Files:**
- Create: `learning/common.py`
- Test: `learning/test_common.py`

**Interfaces:**
- Consumes: niente
- Produces:
  - `LEARNING_DIR: Path`, `DATA_DIR: Path`, `RAW_DIR: Path`
  - `data_path(nome: str) -> Path`
  - `ensure_dirs() -> None`

- [ ] **Step 1: Scrivere i test che falliscono**

```python
# learning/test_common.py
"""Test del modulo di supporto del percorso didattico."""
from pathlib import Path

import common


def test_data_dir_e_dentro_learning():
    assert common.DATA_DIR.parent == common.LEARNING_DIR
    assert common.DATA_DIR.name == "data"


def test_raw_dir_e_dentro_data():
    assert common.RAW_DIR.parent == common.DATA_DIR
    assert common.RAW_DIR.name == "raw"


def test_data_path_compone_il_percorso():
    assert common.data_path("02_observations.parquet") == common.DATA_DIR / "02_observations.parquet"


def test_ensure_dirs_crea_le_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(common, "RAW_DIR", tmp_path / "data" / "raw")
    common.ensure_dirs()
    assert (tmp_path / "data").is_dir()
    assert (tmp_path / "data" / "raw").is_dir()


def test_ensure_dirs_e_idempotente(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(common, "RAW_DIR", tmp_path / "data" / "raw")
    common.ensure_dirs()
    common.ensure_dirs()
    assert (tmp_path / "data" / "raw").is_dir()
```

- [ ] **Step 2: Eseguire i test e verificare che falliscano**

```bash
cd learning && .venv/bin/pytest test_common.py -v
```

Expected: FAIL con `ModuleNotFoundError: No module named 'common'`.

- [ ] **Step 3: Implementazione minima**

```python
# learning/common.py
"""Supporto al percorso didattico Nimbus.

Questo modulo contiene soltanto cio' che e' ripetitivo e non didattico:
percorsi, bounding box regionali e download con cache. Ogni contenuto
meteorologico o statistico resta visibile nelle celle dei notebook.

Non fa parte della pipeline Nimbus: vedere learning/README.md.
"""
from pathlib import Path

# Radice del percorso didattico, dedotta dalla posizione di questo file.
LEARNING_DIR = Path(__file__).resolve().parent

# Directory degli artefatti prodotti dai notebook. E' gitignorata.
DATA_DIR = LEARNING_DIR / "data"

# Sottodirectory dei file grezzi (GRIB) a retention breve.
RAW_DIR = DATA_DIR / "raw"


def data_path(nome: str) -> Path:
    """Restituisce il percorso completo di un artefatto dentro DATA_DIR.

    Args:
        nome: nome del file, ad esempio "02_observations.parquet".

    Returns:
        Il percorso assoluto del file dentro la directory dei dati.
    """
    return DATA_DIR / nome


def ensure_dirs() -> None:
    """Crea le directory dei dati se non esistono.

    L'operazione e' idempotente: chiamarla piu' volte non produce errori.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

```bash
cd learning && .venv/bin/pytest test_common.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add learning/common.py learning/test_common.py
git commit -m "feat: add learning path common module with data paths"
```

---

### Task 3: `common.py` — bounding box regionali

**Files:**
- Modify: `learning/common.py`
- Modify: `learning/test_common.py`

**Interfaces:**
- Consumes: niente dal Task 2
- Produces:
  - `BBOX_REGIONI: dict[str, tuple[float, float, float, float]]` con chiavi in minuscolo e valori `(lon_min, lon_max, lat_min, lat_max)`
  - `BBOX_MACROAREE: dict[str, tuple[float, float, float, float]]`
  - `BBOX_ITALIA: tuple[float, float, float, float]`
  - `get_bbox(nome: str) -> tuple[float, float, float, float]` — accetta regione o macroarea, case-insensitive, solleva `KeyError` con messaggio che elenca i nomi validi
  - `REGIONE_DEFAULT: str = "piemonte"`

- [ ] **Step 1: Scrivere i test che falliscono**

Aggiungere in coda a `learning/test_common.py`:

```python
import pytest


def test_tutte_le_regioni_italiane_sono_presenti():
    attese = {
        "abruzzo", "basilicata", "calabria", "campania", "emilia-romagna",
        "friuli-venezia giulia", "lazio", "liguria", "lombardia", "marche",
        "molise", "piemonte", "puglia", "sardegna", "sicilia", "toscana",
        "trentino-alto adige", "umbria", "valle d'aosta", "veneto",
    }
    assert attese == set(common.BBOX_REGIONI)


def test_ogni_bbox_e_coerente():
    tutti = {**common.BBOX_REGIONI, **common.BBOX_MACROAREE, "italia": common.BBOX_ITALIA}
    for nome, (lon_min, lon_max, lat_min, lat_max) in tutti.items():
        assert lon_min < lon_max, f"{nome}: longitudini invertite"
        assert lat_min < lat_max, f"{nome}: latitudini invertite"
        assert 6.0 <= lon_min and lon_max <= 19.0, f"{nome}: longitudini fuori Italia"
        assert 35.0 <= lat_min and lat_max <= 47.5, f"{nome}: latitudini fuori Italia"


def test_get_bbox_e_case_insensitive():
    assert common.get_bbox("Piemonte") == common.BBOX_REGIONI["piemonte"]
    assert common.get_bbox("PIEMONTE") == common.BBOX_REGIONI["piemonte"]


def test_get_bbox_accetta_una_macroarea():
    assert common.get_bbox("nord-ovest") == common.BBOX_MACROAREE["nord-ovest"]


def test_get_bbox_su_nome_ignoto_elenca_i_validi():
    with pytest.raises(KeyError) as err:
        common.get_bbox("catalogna")
    assert "piemonte" in str(err.value)


def test_regione_default_esiste():
    assert common.REGIONE_DEFAULT in common.BBOX_REGIONI
```

- [ ] **Step 2: Eseguire i test e verificare che falliscano**

```bash
cd learning && .venv/bin/pytest test_common.py -v
```

Expected: FAIL con `AttributeError: module 'common' has no attribute 'BBOX_REGIONI'`.

- [ ] **Step 3: Implementazione**

Aggiungere in coda a `learning/common.py`:

```python
# Bounding box approssimative, in gradi decimali WGS84.
# Formato: (lon_min, lon_max, lat_min, lat_max).
#
# ATTENZIONE DIDATTICA: un rettangolo non e' un confine amministrativo.
# Il bbox del Piemonte, per esempio, include anche Milano Linate, Malpensa,
# Cameri e Genova Sestri. E' un limite voluto e accettato: filtrare un
# inventario di stazioni non richiede un point-in-polygon, e la mappa
# disegnata nel notebook 02 rende l'imprecisione visibile invece che nascosta.
BBOX_REGIONI: dict[str, tuple[float, float, float, float]] = {
    "abruzzo": (13.0, 14.8, 41.7, 42.9),
    "basilicata": (15.3, 16.9, 39.9, 41.1),
    "calabria": (15.6, 17.2, 37.9, 40.2),
    "campania": (13.7, 15.8, 39.9, 41.5),
    "emilia-romagna": (9.2, 12.8, 43.7, 45.1),
    "friuli-venezia giulia": (12.3, 13.9, 45.5, 46.7),
    "lazio": (11.4, 14.1, 40.7, 42.9),
    "liguria": (7.5, 10.1, 43.7, 44.7),
    "lombardia": (8.5, 11.5, 44.6, 46.7),
    "marche": (12.1, 13.9, 42.6, 43.9),
    "molise": (14.0, 15.2, 41.3, 42.1),
    "piemonte": (6.6, 9.3, 44.0, 46.5),
    "puglia": (14.9, 18.6, 39.7, 42.3),
    "sardegna": (8.1, 9.9, 38.8, 41.4),
    "sicilia": (12.3, 15.7, 36.6, 38.4),
    "toscana": (9.6, 12.4, 42.2, 44.5),
    "trentino-alto adige": (10.3, 12.5, 45.6, 47.1),
    "umbria": (11.8, 13.3, 42.3, 43.7),
    "valle d'aosta": (6.7, 7.9, 45.4, 46.0),
    "veneto": (10.6, 13.2, 44.7, 46.7),
}

# Aggregazioni piu' ampie, proposte quando una regione ha troppe poche stazioni.
BBOX_MACROAREE: dict[str, tuple[float, float, float, float]] = {
    "nord-ovest": (6.6, 11.5, 43.7, 46.7),
    "nord-est": (10.3, 13.9, 43.7, 47.1),
    "centro": (9.6, 14.1, 40.7, 44.5),
    "sud": (13.7, 18.6, 37.9, 42.3),
    "isole": (8.1, 15.7, 36.6, 41.4),
}

# Italia con un piccolo margine, usata per le mappe di inquadramento.
BBOX_ITALIA: tuple[float, float, float, float] = (6.0, 19.0, 35.0, 47.5)

# Default coerente con il pilota prioritario dei documenti 03 e 04.
REGIONE_DEFAULT: str = "piemonte"


def get_bbox(nome: str) -> tuple[float, float, float, float]:
    """Restituisce il bounding box di una regione o di una macroarea.

    Args:
        nome: nome della regione o della macroarea, senza distinzione
            fra maiuscole e minuscole.

    Returns:
        La tupla (lon_min, lon_max, lat_min, lat_max) in gradi WGS84.

    Raises:
        KeyError: se il nome non corrisponde ad alcuna area conosciuta.
            Il messaggio elenca i nomi accettati.
    """
    chiave = nome.strip().lower()
    if chiave in BBOX_REGIONI:
        return BBOX_REGIONI[chiave]
    if chiave in BBOX_MACROAREE:
        return BBOX_MACROAREE[chiave]
    if chiave == "italia":
        return BBOX_ITALIA
    validi = ", ".join(sorted(BBOX_REGIONI) + sorted(BBOX_MACROAREE) + ["italia"])
    raise KeyError(f"Area '{nome}' non riconosciuta. Aree valide: {validi}")
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

```bash
cd learning && .venv/bin/pytest test_common.py -v
```

Expected: 11 passed.

- [ ] **Step 5: Commit**

```bash
git add learning/common.py learning/test_common.py
git commit -m "feat: add regional bounding boxes to learning common module"
```

---

### Task 4: `common.py` — download con cache e checksum

**Files:**
- Modify: `learning/common.py`
- Modify: `learning/test_common.py`

**Interfaces:**
- Consumes: `RAW_DIR`, `ensure_dirs` dal Task 2
- Produces:
  - `sha256_file(percorso: Path) -> str`
  - `scarica_con_cache(url: str, destinazione: Path, *, params: dict | None = None, checksum_atteso: str | None = None, forza: bool = False) -> Path`
  - `ChecksumError(Exception)`

Comportamento: se il file esiste e il checksum (quando fornito) coincide, non tocca la rete. Se il checksum non coincide, il file scaricato viene rimosso e viene sollevato `ChecksumError`.

- [ ] **Step 1: Scrivere i test che falliscono**

Aggiungere in coda a `learning/test_common.py`:

```python
import hashlib


class _RispostaFinta:
    """Risposta HTTP simulata, sufficiente per il download a blocchi."""

    def __init__(self, contenuto: bytes):
        self._contenuto = contenuto
        self.status_code = 200

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size=8192):
        for i in range(0, len(self._contenuto), chunk_size):
            yield self._contenuto[i:i + chunk_size]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_sha256_file_calcola_il_digest(tmp_path):
    f = tmp_path / "x.bin"
    f.write_bytes(b"nimbus")
    assert common.sha256_file(f) == hashlib.sha256(b"nimbus").hexdigest()


def test_scarica_scrive_il_file(tmp_path, monkeypatch):
    chiamate = []

    def finto_get(url, params=None, stream=False, timeout=None):
        chiamate.append(url)
        return _RispostaFinta(b"contenuto")

    monkeypatch.setattr(common.requests, "get", finto_get)
    dest = tmp_path / "out.bin"
    ris = common.scarica_con_cache("http://esempio/x", dest)
    assert ris.read_bytes() == b"contenuto"
    assert len(chiamate) == 1


def test_cache_hit_non_tocca_la_rete(tmp_path, monkeypatch):
    dest = tmp_path / "out.bin"
    dest.write_bytes(b"gia-presente")

    def esplodi(*args, **kwargs):
        raise AssertionError("la rete non doveva essere usata")

    monkeypatch.setattr(common.requests, "get", esplodi)
    ris = common.scarica_con_cache("http://esempio/x", dest)
    assert ris.read_bytes() == b"gia-presente"


def test_forza_ignora_la_cache(tmp_path, monkeypatch):
    dest = tmp_path / "out.bin"
    dest.write_bytes(b"vecchio")
    monkeypatch.setattr(
        common.requests, "get",
        lambda url, params=None, stream=False, timeout=None: _RispostaFinta(b"nuovo"),
    )
    ris = common.scarica_con_cache("http://esempio/x", dest, forza=True)
    assert ris.read_bytes() == b"nuovo"


def test_checksum_corretto_e_accettato(tmp_path, monkeypatch):
    atteso = hashlib.sha256(b"buono").hexdigest()
    monkeypatch.setattr(
        common.requests, "get",
        lambda url, params=None, stream=False, timeout=None: _RispostaFinta(b"buono"),
    )
    dest = tmp_path / "out.bin"
    ris = common.scarica_con_cache("http://esempio/x", dest, checksum_atteso=atteso)
    assert ris.exists()


def test_checksum_errato_rimuove_il_file_e_solleva(tmp_path, monkeypatch):
    monkeypatch.setattr(
        common.requests, "get",
        lambda url, params=None, stream=False, timeout=None: _RispostaFinta(b"cattivo"),
    )
    dest = tmp_path / "out.bin"
    with pytest.raises(common.ChecksumError):
        common.scarica_con_cache("http://esempio/x", dest, checksum_atteso="0" * 64)
    assert not dest.exists(), "il file corrotto non deve restare sul disco"


def test_cache_con_checksum_diverso_riscarica(tmp_path, monkeypatch):
    dest = tmp_path / "out.bin"
    dest.write_bytes(b"vecchio")
    atteso = hashlib.sha256(b"nuovo").hexdigest()
    monkeypatch.setattr(
        common.requests, "get",
        lambda url, params=None, stream=False, timeout=None: _RispostaFinta(b"nuovo"),
    )
    ris = common.scarica_con_cache("http://esempio/x", dest, checksum_atteso=atteso)
    assert ris.read_bytes() == b"nuovo"
```

- [ ] **Step 2: Eseguire i test e verificare che falliscano**

```bash
cd learning && .venv/bin/pytest test_common.py -v
```

Expected: FAIL con `AttributeError: module 'common' has no attribute 'sha256_file'`.

- [ ] **Step 3: Implementazione**

In testa a `learning/common.py`, accanto agli import esistenti, aggiungere:

```python
import hashlib

import requests
```

Poi aggiungere in coda al file:

```python
class ChecksumError(Exception):
    """Il file scaricato non corrisponde al checksum atteso."""


def sha256_file(percorso: Path) -> str:
    """Calcola il digest SHA-256 di un file, leggendolo a blocchi.

    Args:
        percorso: file da leggere.

    Returns:
        Il digest esadecimale.
    """
    digest = hashlib.sha256()
    with percorso.open("rb") as f:
        for blocco in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(blocco)
    return digest.hexdigest()


def scarica_con_cache(
    url: str,
    destinazione: Path,
    *,
    params: dict | None = None,
    checksum_atteso: str | None = None,
    forza: bool = False,
) -> Path:
    """Scarica un file solo se non e' gia' presente e integro.

    E' la funzione che rende ripetibili i notebook: rieseguire una cella
    non riscarica nulla. E' anche la versione didatticamente minima di
    cio' che nella pipeline Nimbus e' il download idempotente con manifest.

    Args:
        url: indirizzo da scaricare.
        destinazione: percorso del file locale.
        params: parametri di query, usati dal filtro GRIB di NOMADS.
        checksum_atteso: digest SHA-256 atteso. Se presente, un file in
            cache che non corrisponde viene riscaricato, e un download
            che non corrisponde viene rimosso.
        forza: se True ignora la cache e riscarica comunque.

    Returns:
        Il percorso del file scaricato o gia' presente.

    Raises:
        ChecksumError: se il file scaricato non corrisponde al checksum.
    """
    destinazione.parent.mkdir(parents=True, exist_ok=True)

    if destinazione.exists() and not forza:
        if checksum_atteso is None or sha256_file(destinazione) == checksum_atteso:
            return destinazione

    with requests.get(url, params=params, stream=True, timeout=300) as risposta:
        risposta.raise_for_status()
        with destinazione.open("wb") as f:
            for blocco in risposta.iter_content(chunk_size=1024 * 1024):
                if blocco:
                    f.write(blocco)

    if checksum_atteso is not None:
        effettivo = sha256_file(destinazione)
        if effettivo != checksum_atteso:
            destinazione.unlink(missing_ok=True)
            raise ChecksumError(
                f"Checksum non corrispondente per {url}: "
                f"atteso {checksum_atteso}, ottenuto {effettivo}"
            )

    return destinazione
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

```bash
cd learning && .venv/bin/pytest test_common.py -v
```

Expected: 18 passed.

- [ ] **Step 5: Commit**

```bash
git add learning/common.py learning/test_common.py
git commit -m "feat: add cached download with checksum verification"
```

---

### Task 5: `common.py` — controllo prerequisiti fra notebook

**Files:**
- Modify: `learning/common.py`
- Modify: `learning/test_common.py`

**Interfaces:**
- Consumes: `data_path` dal Task 2
- Produces:
  - `PrerequisitoMancante(Exception)`
  - `richiede(*nomi_file: str) -> None` — solleva `PrerequisitoMancante` con un messaggio che nomina il notebook da eseguire
  - `NOTEBOOK_DI_ORIGINE: dict[str, str]`

- [ ] **Step 1: Scrivere i test che falliscono**

Aggiungere in coda a `learning/test_common.py`:

```python
def test_richiede_passa_se_i_file_esistono(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "DATA_DIR", tmp_path)
    (tmp_path / "01_stations.csv").write_text("x")
    common.richiede("01_stations.csv")


def test_richiede_nomina_il_notebook_mancante(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "DATA_DIR", tmp_path)
    with pytest.raises(common.PrerequisitoMancante) as err:
        common.richiede("01_stations.csv")
    messaggio = str(err.value)
    assert "01_stations.csv" in messaggio
    assert "02-osservazioni-isd" in messaggio


def test_richiede_elenca_tutti_i_file_mancanti(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "DATA_DIR", tmp_path)
    with pytest.raises(common.PrerequisitoMancante) as err:
        common.richiede("02_observations.parquet", "03_forecast_points.parquet")
    messaggio = str(err.value)
    assert "02_observations.parquet" in messaggio
    assert "03_forecast_points.parquet" in messaggio


def test_ogni_file_noto_ha_un_notebook_di_origine():
    for nome in common.NOTEBOOK_DI_ORIGINE.values():
        assert nome.startswith("0")
```

- [ ] **Step 2: Eseguire i test e verificare che falliscano**

```bash
cd learning && .venv/bin/pytest test_common.py -v
```

Expected: FAIL con `AttributeError: module 'common' has no attribute 'richiede'`.

- [ ] **Step 3: Implementazione**

Aggiungere in coda a `learning/common.py`:

```python
# Mappa fra artefatto e notebook che lo produce. Serve a trasformare un
# FileNotFoundError anonimo in un'istruzione comprensibile.
NOTEBOOK_DI_ORIGINE: dict[str, str] = {
    "00_env_report.json": "01-setup-e-fondamenti",
    "01_stations.csv": "02-osservazioni-isd",
    "02_observations.parquet": "02-osservazioni-isd",
    "03_forecast_points.parquet": "03-forecast-gfs-grib",
    "04_dataset.parquet": "04-join-e-anti-leakage",
    "05_metrics.json": "05-baseline-e-previsione",
}


class PrerequisitoMancante(Exception):
    """Manca un artefatto prodotto da un notebook precedente."""


def richiede(*nomi_file: str) -> None:
    """Verifica che gli artefatti richiesti esistano prima di proseguire.

    Ogni notebook chiama questa funzione nella prima cella. Se un file
    manca, il messaggio dice quale notebook eseguire, invece di lasciare
    che il notebook fallisca piu' avanti con un errore oscuro.

    Args:
        *nomi_file: nomi degli artefatti attesi dentro DATA_DIR.

    Raises:
        PrerequisitoMancante: se almeno un artefatto non esiste.
    """
    mancanti = [nome for nome in nomi_file if not data_path(nome).exists()]
    if not mancanti:
        return

    righe = ["Mancano artefatti prodotti da notebook precedenti:", ""]
    for nome in mancanti:
        origine = NOTEBOOK_DI_ORIGINE.get(nome, "sconosciuto")
        righe.append(f"  - {nome}  ->  eseguire il notebook {origine}")
    righe.append("")
    righe.append("I notebook vanno eseguiti in ordine: 01, 02, 03, 04, 05.")
    raise PrerequisitoMancante("\n".join(righe))
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

```bash
cd learning && .venv/bin/pytest test_common.py -v
```

Expected: 22 passed.

- [ ] **Step 5: Commit**

```bash
git add learning/common.py learning/test_common.py
git commit -m "feat: add prerequisite checks between notebooks"
```

---

### Task 6: README del percorso

**Files:**
- Create: `learning/README.md`
- Modify: `README.md` (radice, sezione Documentazione)

**Interfaces:**
- Consumes: i comandi di setup del Task 1
- Produces: niente di programmatico

- [ ] **Step 1: Scrivere `learning/README.md`**

```markdown
# Percorso didattico Nimbus

Un percorso in cinque notebook che parte da zero e arriva a una stima di
previsione elementare: scarico di dati pubblici, lettura di mappe
meteorologiche, unione fra previsione e osservazione, valutazione.

## Cosa NON e'

Va letto prima di tutto il resto.

- **Non e' la pipeline Nimbus** ne' un suo prototipo. La pipeline vera
  comincia da M0 del [piano MVP](../docs/08-mvp-implementation-plan.md).
- **Non e' autorevole sui contratti dati.** La fonte di verita' resta `docs/`.
  Dove i notebook semplificano, lo dichiarano.
- **Non produce previsioni pubblicabili.** Nessun output di `learning/` puo'
  essere presentato come forecast Nimbus.
- **Il suo codice non confluisce nel package `nimbus`** e le sue dipendenze
  non vincolano quelle della pipeline.

## Setup

Serve Python 3.12. Su macOS con Homebrew:

```bash
brew install python@3.12
```

Poi, dalla radice del repository:

```bash
/opt/homebrew/bin/python3.12 -m venv learning/.venv
learning/.venv/bin/pip install --upgrade pip
learning/.venv/bin/pip install -r learning/requirements.txt
```

Le dipendenze binarie (eccodes per il GRIB, GEOS/PROJ per le mappe) arrivano
come wheel: su questa piattaforma **non** serve installarle a parte.

Avviare i notebook:

```bash
learning/.venv/bin/jupyter lab learning/notebooks
```

## Ordine dei notebook

Vanno eseguiti in sequenza: ognuno legge i file prodotti dal precedente.
Saltarne uno fa fallire il successivo con un messaggio che dice quale
eseguire.

| # | Notebook | Cosa impari | Durata indicativa |
| --- | --- | --- | --- |
| 01 | `01-setup-e-fondamenti` | Ambiente, griglia, run/valid time, UTC, cos'e' un GRIB | ~30 min |
| 02 | `02-osservazioni-isd` | Inventario NOAA, scelta dell'area, stazioni, dati sporchi | ~45 min |
| 03 | `03-forecast-gfs-grib` | Download GFS, lettura GRIB, mappe, dalla griglia al punto | ~45 min |
| 04 | `04-join-e-anti-leakage` | Join temporale, leakage mostrato dal vivo, split corretti | ~40 min |
| 05 | `05-baseline-e-previsione` | Baseline, bias correction, metriche e loro limiti | ~40 min |

Le durate sono stime di pianificazione, non misure: dipendono soprattutto
dalla velocita' del download.

## Dati

Tutto quello che i notebook scaricano o producono finisce in `learning/data/`,
che e' gitignorata. Non committare dati, GRIB, Parquet, ne' gli output delle
celle dei notebook.

I GRIB grezzi restano in `learning/data/raw/`. Rispecchiano la politica di
retention breve del [documento di fattibilita'](../docs/05-mvp-data-feasibility.md):
si possono cancellare quando i Parquet sono stati prodotti.

## Test

Il solo componente con logica non didattica e' `common.py`, ed e' l'unico
testato:

```bash
cd learning && .venv/bin/pytest test_common.py -v
```

I notebook non hanno test automatici: la loro verifica e' l'esecuzione
completa in ordine su un ambiente pulito.
```

- [ ] **Step 2: Aggiungere il rimando nel README di radice**

Nella sezione `## Documentazione` del `README.md` di radice, aggiungere in coda all'elenco:

```markdown
- [Percorso didattico interattivo](learning/README.md) — materiale formativo, non fa parte della pipeline
```

- [ ] **Step 3: Verificare i link relativi**

```bash
grep -o '](\.\./docs/[^)]*)' learning/README.md | sed 's/](//;s/)$//' | while read p; do
  [ -f "learning/$p" ] && echo "OK $p" || echo "ROTTO $p"
done
```

Expected: due righe `OK`.

- [ ] **Step 4: Commit**

```bash
git add learning/README.md README.md
git commit -m "docs: add learning path README"
```

---

### Task 7: Notebook 01 — Setup e fondamenti

**Files:**
- Create: `learning/notebooks/01-setup-e-fondamenti.ipynb`

**Interfaces:**
- Consumes: `common.ensure_dirs`, `common.data_path`
- Produces: `learning/data/00_env_report.json` con chiavi `python`, `pacchetti` (dict nome→versione), `eccodes_api`, `cartopy_ok` (bool), `generato_il` (ISO UTC)

**Struttura del notebook.** Alternare celle markdown e celle di codice secondo lo schema: cosa impari → contesto → codice → cosa hai ottenuto → il limite.

- [ ] **Step 1: Celle introduttive (markdown)**

Titolo, e in apertura il blocco "Cosa NON e' questo percorso" ripreso dal README: non e' la pipeline, non e' autorevole, non produce previsioni pubblicabili.

Poi le nozioni minime, una cella markdown ciascuna:

1. **Cos'e' un modello NWP e perche' ha una griglia.** Il GFS risolve equazioni fisiche su celle di circa 0,25° (~25 km alle nostre latitudini). Dentro una cella il modello ha un solo valore: la sua "montagna" e' una media, non la montagna vera.
2. **Run time, valid time, lead.** Il modello parte da uno stato iniziale a `run_time` e proietta in avanti; `lead_hours` e' quanto avanti; `valid_time = run_time + lead_hours`. Il GFS gira alle 00/06/12/18 UTC.
3. **Perche' UTC.** L'ora locale ha fusi e ora legale: due timestamp identici possono essere istanti diversi. Tutta la meteorologia lavora in UTC. In questo percorso ogni timestamp e' tz-aware.
4. **Cos'e' un GRIB e perche' non e' un CSV.** Formato binario compresso per campi grigliati, con metadati per messaggio. Va aperto con una libreria dedicata; e' il motivo per cui serve `eccodes`.

- [ ] **Step 2: Cella di verifica ambiente**

```python
import json
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

sys.path.insert(0, str(Path.cwd().parent))  # per importare common.py
import common

common.ensure_dirs()

report = {
    "python": sys.version.split()[0],
    "pacchetti": {},
    "eccodes_api": None,
    "cartopy_ok": False,
    "generato_il": datetime.now(timezone.utc).isoformat(),
}

problemi = []

for pacchetto in ["pandas", "pyarrow", "numpy", "xarray", "cfgrib",
                  "eccodes", "matplotlib", "Cartopy", "requests"]:
    try:
        report["pacchetti"][pacchetto] = metadata.version(pacchetto)
    except metadata.PackageNotFoundError:
        report["pacchetti"][pacchetto] = None
        problemi.append(f"{pacchetto} non installato")

print("Python:", report["python"])
if not report["python"].startswith("3.12"):
    problemi.append(
        f"Python {report['python']}: il percorso e' verificato su 3.12. "
        "Ricreare il venv con /opt/homebrew/bin/python3.12 -m venv learning/.venv"
    )
for nome, versione in report["pacchetti"].items():
    print(f"  {nome:12s} {versione or 'MANCANTE'}")
```

- [ ] **Step 3: Cella di verifica delle due dipendenze binarie**

Preceduta da una cella markdown che spiega perche' queste due meritano un trattamento a parte: sono wrapper di librerie C, quindi possono installarsi e poi non importarsi.

```python
# eccodes: la libreria ECMWF che legge il GRIB.
try:
    import eccodes
    report["eccodes_api"] = eccodes.codes_get_api_version()
    print("eccodes OK, versione libreria:", report["eccodes_api"])
    import cfgrib  # noqa: F401
    print("cfgrib OK: xarray potra' aprire i GRIB")
except Exception as errore:
    problemi.append(f"eccodes/cfgrib non utilizzabili: {type(errore).__name__}: {errore}")
    print("PROBLEMA con eccodes/cfgrib:", errore)
    print("Rimedio: learning/.venv/bin/pip install --force-reinstall eccodes cfgrib")
    print("Se persiste su macOS: brew install eccodes, poi reinstallare i pacchetti.")

# cartopy: confini e proiezioni per le mappe.
try:
    import cartopy.crs as ccrs  # noqa: F401
    report["cartopy_ok"] = True
    print("cartopy OK: le mappe avranno coste e confini")
except Exception as errore:
    print("cartopy non disponibile:", errore)
    print("Il percorso resta eseguibile: le mappe perderanno i contorni,")
    print("ma stazioni e griglia restano leggibili.")
```

- [ ] **Step 4: Cella che scrive il report e riepiloga**

```python
with common.data_path("00_env_report.json").open("w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

if problemi:
    print("AMBIENTE INCOMPLETO:")
    for p in problemi:
        print("  -", p)
else:
    print("Ambiente verificato. Puoi passare al notebook 02.")
print("\nReport scritto in:", common.data_path("00_env_report.json"))
```

- [ ] **Step 5: Cella finale "Il limite di quello che hai fatto" (markdown)**

Contenuto: hai verificato che le librerie si importano, non che i dati siano scaricabili — le fonti remote possono essere irraggiungibili o aver cambiato formato, e lo scoprirai nel notebook 02. Il report registra un ambiente in un istante: se reinstalli qualcosa, va rieseguito.

- [ ] **Step 6: Eseguire il notebook per intero e verificare l'output**

```bash
cd learning/notebooks && ../.venv/bin/jupyter nbconvert --to notebook --execute \
  --inplace 01-setup-e-fondamenti.ipynb
cat ../data/00_env_report.json
```

Expected: esecuzione senza eccezioni; il JSON contiene `python` che inizia con `3.12`, `eccodes_api` valorizzato e `cartopy_ok: true`.

- [ ] **Step 7: Ripulire gli output e committare**

```bash
cd learning/notebooks && ../.venv/bin/jupyter nbconvert --clear-output \
  --inplace 01-setup-e-fondamenti.ipynb
cd ../.. && git add learning/notebooks/01-setup-e-fondamenti.ipynb
git commit -m "feat: add notebook 01 environment setup and fundamentals"
```

---

### Task 8: Notebook 02 — Osservazioni ISD e scelta dell'area

**Files:**
- Create: `learning/notebooks/02-osservazioni-isd.ipynb`

**Interfaces:**
- Consumes: `common.richiede`, `common.scarica_con_cache`, `common.get_bbox`, `common.REGIONE_DEFAULT`, `common.data_path`, `common.RAW_DIR`
- Produces:
  - `learning/data/01_stations.csv` — colonne `station_id, usaf, wban, nome, lat, lon, elev_m, begin, end, regione_scelta`
  - `learning/data/02_observations.parquet` — colonne `station_id, valid_time_utc (tz-aware), t2m_c, qa_flag`

- [ ] **Step 1: Cella di prerequisiti e scelta dell'area**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))
import common

common.richiede("00_env_report.json")
common.ensure_dirs()

# ---- SCEGLI QUI LA TUA AREA ----------------------------------------
# Puoi indicare una regione italiana ("lombardia", "sicilia", ...),
# una macroarea ("nord-ovest", "centro", "isole") oppure "italia".
REGIONE = common.REGIONE_DEFAULT
# --------------------------------------------------------------------

lon_min, lon_max, lat_min, lat_max = common.get_bbox(REGIONE)
print(f"Area scelta: {REGIONE}")
print(f"  longitudine {lon_min} -> {lon_max}")
print(f"  latitudine  {lat_min} -> {lat_max}")
```

- [ ] **Step 2: Cella markdown sull'inventario, poi download e riproduzione dei numeri del progetto**

La cella markdown spiega che l'inventario e' un elenco di stazioni con periodo di attivita', **non** i dati osservati, e che stiamo per riprodurre numeri che compaiono in `docs/05-mvp-data-feasibility.md`.

```python
import pandas as pd

URL_INVENTARIO = "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv"
percorso = common.scarica_con_cache(URL_INVENTARIO, common.RAW_DIR / "isd-history.csv")

inv = pd.read_csv(percorso, dtype=str)
print("Colonne:", list(inv.columns))
print("Record totali nel mondo:", len(inv))

it = inv[inv["CTRY"] == "IT"].copy()
it["lat"] = pd.to_numeric(it["LAT"], errors="coerce")
it["lon"] = pd.to_numeric(it["LON"], errors="coerce")
it["elev_m"] = pd.to_numeric(it["ELEV(M)"], errors="coerce")
it["begin"] = pd.to_datetime(it["BEGIN"], format="%Y%m%d", errors="coerce")
it["end"] = pd.to_datetime(it["END"], format="%Y%m%d", errors="coerce")

print("\nRecord con CTRY=IT:", len(it))          # atteso 318
geoloc = it[["lat", "lon"]].notna().all(axis=1).sum()
print("Con coordinate valorizzate:", geoloc)      # atteso 311

candidate = it[(it["begin"] <= "2021-01-01") & (it["end"] >= "2025-08-01")].copy()
print("Candidate 2021 -> ago 2025:", len(candidate))   # atteso 124
print("  sotto 300 m:", int((candidate["elev_m"] < 300).sum()))                                  # 89
print("  fra 300 e 999 m:", int(candidate["elev_m"].between(300, 999.999).sum()))                # 22
print("  da 1000 m:", int((candidate["elev_m"] >= 1000).sum()))                                  # 13
```

- [ ] **Step 3: Cella markdown — i numeri e una discrepanza onesta**

Contenuto obbligatorio:

- I valori 318, 124, 89/22/13 coincidono con la Misura 1 del documento di fattibilita': lo stesso file, lo stesso filtro, lo stesso risultato. E' cosi' che si verifica un dato invece di fidarsi.
- **Discrepanza da dichiarare:** il documento riporta 317 stazioni geolocalizzate, il conteggio odierno ne trova 311. L'inventario e' aggiornato di continuo, quindi divergere di qualche unita' a distanza di mesi e' atteso. La lezione: un numero misurato va sempre accompagnato dalla sua data. Se la differenza fosse grande, andrebbe indagata prima di proseguire.
- `END` non significa che la stazione sia spenta: molte righe si fermano ad agosto 2025 perche' l'inventario e' aggiornato a blocchi.

- [ ] **Step 4: Cella di selezione con la soglia delle 3 stazioni**

```python
SOGLIA_MINIMA = 3

sel = candidate[
    candidate["lat"].between(lat_min, lat_max)
    & candidate["lon"].between(lon_min, lon_max)
].copy()
sel["station_id"] = sel["USAF"].str.strip() + "-" + sel["WBAN"].str.strip()
sel["nome"] = sel["STATION NAME"].str.strip()

print(f"Stazioni candidate dentro '{REGIONE}': {len(sel)}")
if len(sel):
    fasce = pd.cut(sel["elev_m"], [-100, 300, 1000, 9000],
                   labels=["<300 m", "300-999 m", ">=1000 m"], right=False)
    print(fasce.value_counts().sort_index().to_string())

if len(sel) < SOGLIA_MINIMA:
    print(f"\nTROPPO POCHE (minimo {SOGLIA_MINIMA}). Il percorso non prosegue con questo campione.")
    print("Scegli una macroarea piu' ampia e riesegui da questa cella:")
    print("  ", ", ".join(sorted(common.BBOX_MACROAREE)))
else:
    print("\nCampione sufficiente per proseguire.")
```

- [ ] **Step 5: Cella markdown + mappa dell'area (requisito della spec)**

La cella markdown avverte: un bbox non e' un confine amministrativo, e la mappa serve a vedere cosa e' stato davvero preso. **Esempio da citare esplicitamente**: il bbox del Piemonte include Milano Linate, Malpensa, Cameri e Genova Sestri, che in Piemonte non sono. E' un limite accettato, reso visibile invece che nascosto.

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    proiezione = ccrs.PlateCarree()
except Exception:
    ccrs = None

fig = plt.figure(figsize=(9, 9))
if ccrs is not None:
    ax = plt.axes(projection=proiezione)
    ax.set_extent(common.BBOX_ITALIA, crs=proiezione)
    ax.add_feature(cfeature.LAND, facecolor="#f2f2f2")
    ax.add_feature(cfeature.OCEAN, facecolor="#dceaf5")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4, linestyle=":")
    kw = {"transform": proiezione}
else:
    ax = plt.axes()
    lo0, lo1, la0, la1 = common.BBOX_ITALIA
    ax.set_xlim(lo0, lo1); ax.set_ylim(la0, la1); ax.set_aspect("equal")
    kw = {}

ax.scatter(candidate["lon"], candidate["lat"], s=14, c="#999999",
           label=f"candidate ISD ({len(candidate)})", **kw)
ax.add_patch(mpatches.Rectangle(
    (lon_min, lat_min), lon_max - lon_min, lat_max - lat_min,
    fill=False, edgecolor="#c0392b", linewidth=2, label=f"bbox {REGIONE}", **kw))
ax.scatter(sel["lon"], sel["lat"], s=70, c="#c0392b", edgecolor="white",
           zorder=5, label=f"selezionate ({len(sel)})", **kw)
for _, r in sel.iterrows():
    ax.annotate(f"{r['nome']}\n{r['elev_m']:.0f} m", (r["lon"], r["lat"]),
                fontsize=7, xytext=(4, 4), textcoords="offset points", **kw)

ax.set_title(f"Stazioni ISD candidate e area scelta: {REGIONE}")
ax.legend(loc="lower left", fontsize=8)
plt.show()
```

- [ ] **Step 6: Scrivere `01_stations.csv`**

```python
colonne = ["station_id", "usaf", "wban", "nome", "lat", "lon", "elev_m", "begin", "end"]
out = sel.rename(columns={"USAF": "usaf", "WBAN": "wban"})[colonne].copy()
out["regione_scelta"] = REGIONE
out.to_csv(common.data_path("01_stations.csv"), index=False)
print("Scritte", len(out), "stazioni in", common.data_path("01_stations.csv"))
```

- [ ] **Step 7: Scaricare le osservazioni di poche stazioni**

Preceduta da una cella markdown che spiega: si scaricano pochi mesi e poche stazioni perche' il percorso deve restare eseguibile in una sessione; il comando per l'archivio pluriennale e' mostrato ma non eseguito.

```python
ANNO = 2024
MAX_STAZIONI = 5
scelte = out.sort_values("elev_m", ascending=False).head(MAX_STAZIONI)

frames = []
for _, r in scelte.iterrows():
    nome_file = f"{r['usaf']}-{r['wban']}-{ANNO}.gz"
    url = f"https://www.ncei.noaa.gov/pub/data/noaa/{ANNO}/{nome_file}"
    try:
        p = common.scarica_con_cache(url, common.RAW_DIR / nome_file)
    except Exception as e:
        print(f"  {r['nome']}: non disponibile ({e})")
        continue
    # ISD lite/full e' a larghezza fissa: qui leggiamo i campi obbligatori
    # posizionali del record (data, ora, temperatura e relativo flag QA).
    righe = []
    import gzip
    with gzip.open(p, "rt", errors="ignore") as f:
        for linea in f:
            try:
                data = linea[15:23]          # AAAAMMGG
                ora = linea[23:27]           # HHMM
                t_raw = linea[87:92]         # temperatura in decimi di C
                t_qa = linea[92]             # flag qualita'
                if t_raw == "+9999":
                    continue
                righe.append((f"{data}{ora}", int(t_raw) / 10.0, t_qa))
            except (ValueError, IndexError):
                continue
    if not righe:
        print(f"  {r['nome']}: nessuna temperatura utilizzabile")
        continue
    df = pd.DataFrame(righe, columns=["stamp", "t2m_c", "qa_flag"])
    df["valid_time_utc"] = pd.to_datetime(df["stamp"], format="%Y%m%d%H%M", utc=True)
    df["station_id"] = r["station_id"]
    frames.append(df[["station_id", "valid_time_utc", "t2m_c", "qa_flag"]])
    print(f"  {r['nome']}: {len(df)} osservazioni")

oss = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(
    columns=["station_id", "valid_time_utc", "t2m_c", "qa_flag"])
```

- [ ] **Step 8: Cella markdown + QA e scrittura del Parquet**

La cella markdown introduce i dati sporchi: `+9999` e' il sentinella di assente e non una temperatura; il flag QA distingue valori validati da valori sospetti; i buchi esistono e non vanno riempiti in silenzio.

```python
print("Osservazioni totali:", len(oss))
print("\nDistribuzione dei flag QA:")
print(oss["qa_flag"].value_counts().to_string())

# I flag "2", "3", "6", "7" indicano valori sospetti o errati nel formato ISD.
sospetti = oss["qa_flag"].isin(list("2367"))
print(f"\nValori marcati sospetti: {int(sospetti.sum())} su {len(oss)}")

print("\nCompletezza oraria per stazione:")
for sid, g in oss.groupby("station_id"):
    attese = pd.date_range(g["valid_time_utc"].min(), g["valid_time_utc"].max(),
                           freq="h", tz="UTC")
    presenti = g["valid_time_utc"].dt.floor("h").nunique()
    print(f"  {sid}: {presenti}/{len(attese)} ore = {100*presenti/len(attese):.1f}%")

oss.to_parquet(common.data_path("02_observations.parquet"), index=False)
print("\nScritto", common.data_path("02_observations.parquet"))
```

- [ ] **Step 9: Cella finale "Il limite di quello che hai fatto" (markdown)**

Contenuto obbligatorio:

- **Completezza della stazione ≠ completezza della variabile**: l'inventario dice che la stazione era attiva, non che la temperatura ci sia ogni ora. Il conteggio appena stampato lo dimostra.
- Il campione e' di poche stazioni e un anno: sufficiente per imparare, insufficiente per concludere.
- Il flag QA di ISD e' automatico. Come ricorda `docs/03-italy-observation-source-census.md`, validazione automatica non equivale a validazione finale.
- Il bbox include stazioni fuori regione: le hai viste sulla mappa.

- [ ] **Step 10: Eseguire, verificare, ripulire e committare**

```bash
cd learning/notebooks && ../.venv/bin/jupyter nbconvert --to notebook --execute \
  --inplace 02-osservazioni-isd.ipynb
../.venv/bin/python -c "
import pandas as pd
s = pd.read_csv('../data/01_stations.csv'); print('stazioni:', len(s))
o = pd.read_parquet('../data/02_observations.parquet'); print('osservazioni:', len(o))
assert len(s) >= 3
assert str(o['valid_time_utc'].dtype).endswith('UTC]'), 'i timestamp devono essere tz-aware'
print('OK')
"
../.venv/bin/jupyter nbconvert --clear-output --inplace 02-osservazioni-isd.ipynb
cd ../.. && git add learning/notebooks/02-osservazioni-isd.ipynb
git commit -m "feat: add notebook 02 ISD observations and area selection"
```

---

### Task 9: Notebook 03 — Forecast GFS e GRIB

**Files:**
- Create: `learning/notebooks/03-forecast-gfs-grib.ipynb`

**Interfaces:**
- Consumes: `01_stations.csv`, `common.scarica_con_cache`, `common.get_bbox`
- Produces: `learning/data/03_forecast_points.parquet` — colonne `station_id, run_time_utc, publication_time_utc, lead_hours, valid_time_utc, t2m_c_forecast, model_elev_m, metodo_interpolazione`

- [ ] **Step 1: Prerequisiti e ricostruzione dell'area dalla staffetta**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))
import common
import pandas as pd

common.richiede("01_stations.csv")
stazioni = pd.read_csv(common.data_path("01_stations.csv"))
REGIONE = stazioni["regione_scelta"].iloc[0]
lon_min, lon_max, lat_min, lat_max = common.get_bbox(REGIONE)
print(f"Area ereditata dal notebook 02: {REGIONE} ({len(stazioni)} stazioni)")
```

- [ ] **Step 2: Cella markdown + download del subset GFS**

La markdown spiega: NOMADS espone un filtro che ritaglia variabili e area, quindi si scaricano megabyte invece di gigabyte; e' la stessa procedura della Misura 2 del documento di fattibilita'.

```python
from datetime import datetime, timedelta, timezone

# Si sceglie un run recente ma gia' pubblicato: NOMADS impiega qualche ora
# a rendere disponibile un ciclo completo.
adesso = datetime.now(timezone.utc) - timedelta(hours=8)
run = adesso.replace(hour=(adesso.hour // 6) * 6, minute=0, second=0, microsecond=0)
LEADS = [3, 6, 9, 12, 24, 36, 48]

BASE = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25_1hr.pl"
percorsi = {}
for lead in LEADS:
    params = {
        "file": f"gfs.t{run:%H}z.pgrb2.0p25.f{lead:03d}",
        "lev_2_m_above_ground": "on",
        "var_TMP": "on",
        "subregion": "",
        "leftlon": lon_min, "rightlon": lon_max,
        "toplat": lat_max, "bottomlat": lat_min,
        "dir": f"/gfs.{run:%Y%m%d}/{run:%H}/atmos",
    }
    dest = common.RAW_DIR / f"gfs_{run:%Y%m%d_%H}_f{lead:03d}.grib2"
    try:
        p = common.scarica_con_cache(BASE, dest, params=params)
        if p.read_bytes()[:4] != b"GRIB":
            print(f"  lead {lead:3d}h: risposta non GRIB, run forse non ancora pubblicato")
            p.unlink(missing_ok=True)
            continue
        percorsi[lead] = p
        print(f"  lead {lead:3d}h: {p.stat().st_size/1024:.1f} KB")
    except Exception as e:
        print(f"  lead {lead:3d}h: fallito ({e})")

print(f"\nRun {run:%Y-%m-%d %H} UTC, {len(percorsi)} lead scaricati")
```

Se nessun lead viene scaricato, la cella markdown successiva istruisce a riprovare con `adesso - timedelta(hours=14)`.

- [ ] **Step 3: Cella markdown + apertura del GRIB**

La markdown: un GRIB e' un contenitore di messaggi, ognuno con variabile, livello e istante. `xarray` lo presenta come array con coordinate; `time` e' il run, `step` il lead, `valid_time` la loro somma.

```python
import xarray as xr

lead_demo = sorted(percorsi)[0]
ds = xr.open_dataset(percorsi[lead_demo], engine="cfgrib")
print(ds)
print("\nRun (time):      ", pd.Timestamp(ds.time.values, tz="UTC"))
print("Lead (step):     ", pd.Timedelta(ds.step.values))
print("Valid time:      ", pd.Timestamp(ds.valid_time.values, tz="UTC"))
print("Forma della griglia:", ds.t2m.shape)
print("Passo in gradi:  ",
      float(abs(ds.latitude[1] - ds.latitude[0])),
      float(abs(ds.longitude[1] - ds.longitude[0])))
```

- [ ] **Step 4: Prima mappa — Italia intera, poi zoom (requisito della spec)**

La markdown annuncia che questa e' la prima mappa vera del percorso, e che si guarda prima l'Italia intera per non perdere la percezione della griglia.

```python
import matplotlib.pyplot as plt
try:
    import cartopy.crs as ccrs, cartopy.feature as cfeature
    proj = ccrs.PlateCarree()
except Exception:
    ccrs = None

t2m_c = ds.t2m - 273.15  # da kelvin a gradi Celsius

fig, assi = plt.subplots(1, 2, figsize=(15, 6),
                         subplot_kw={"projection": proj} if ccrs else None)

for ax, estensione, titolo in [
    (assi[0], common.BBOX_ITALIA, "Inquadramento: Italia"),
    (assi[1], (lon_min, lon_max, lat_min, lat_max), f"Zoom: {REGIONE}"),
]:
    kw = {"transform": proj} if ccrs else {}
    if ccrs:
        ax.set_extent(estensione, crs=proj)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.7)
        ax.add_feature(cfeature.BORDERS, linewidth=0.4, linestyle=":")
    else:
        ax.set_xlim(estensione[0], estensione[1]); ax.set_ylim(estensione[2], estensione[3])
    m = ax.pcolormesh(ds.longitude, ds.latitude, t2m_c, shading="nearest",
                      cmap="RdYlBu_r", **kw)
    ax.scatter(stazioni["lon"], stazioni["lat"], s=60, c="black", marker="^",
               zorder=5, label="stazioni", **kw)
    ax.set_title(titolo)
    ax.legend(loc="lower left", fontsize=8)
    plt.colorbar(m, ax=ax, label="T2m (C)", shrink=0.8)

plt.suptitle(f"GFS run {run:%Y-%m-%d %H} UTC, lead +{lead_demo}h")
plt.tight_layout(); plt.show()
```

- [ ] **Step 5: Cella markdown — dalla griglia al punto**

E' il passaggio concettuale centrale del percorso. Contenuto obbligatorio:

- La stazione e' un punto; il modello ha valori solo sui nodi della griglia. Serve interpolare.
- **Nearest**: prende il nodo piu' vicino, non inventa valori, ma salta bruscamente.
- **Bilineare**: media pesata dei quattro nodi circostanti, piu' liscia, ma puo' produrre valori che nessun nodo aveva.
- La differenza che conta di piu' e' un'altra: la quota. Il modello ha una sua orografia mediata sulla cella; una stazione a 3.488 m dentro una cella la cui quota media e' molto piu' bassa avra' un errore sistematico. **E' esattamente la ragione fisica per cui il post-processing statistico funziona**: quell'errore e' ripetibile, quindi apprendibile.

- [ ] **Step 6: Interpolazione ed estrazione dei punti-stazione**

```python
PUBBLICAZIONE_STIMATA_ORE = 4  # ritardo tipico fra run e disponibilita' su NOMADS

righe = []
for lead, percorso in sorted(percorsi.items()):
    d = xr.open_dataset(percorso, engine="cfgrib")
    t_c = d.t2m - 273.15
    for _, s in stazioni.iterrows():
        nearest = float(t_c.sel(latitude=s["lat"], longitude=s["lon"], method="nearest"))
        bilin = float(t_c.interp(latitude=s["lat"], longitude=s["lon"]))
        righe.append({
            "station_id": s["station_id"],
            "run_time_utc": pd.Timestamp(d.time.values, tz="UTC"),
            "publication_time_utc": pd.Timestamp(d.time.values, tz="UTC")
                                    + pd.Timedelta(hours=PUBBLICAZIONE_STIMATA_ORE),
            "lead_hours": lead,
            "valid_time_utc": pd.Timestamp(d.valid_time.values, tz="UTC"),
            "t2m_c_forecast": bilin,
            "t2m_c_forecast_nearest": nearest,
            "station_elev_m": s["elev_m"],
            "metodo_interpolazione": "bilineare",
        })

fc = pd.DataFrame(righe)
print(fc.head(10).to_string(index=False))
print("\nDifferenza fra nearest e bilineare (C):")
print((fc["t2m_c_forecast"] - fc["t2m_c_forecast_nearest"]).describe().to_string())

fc.to_parquet(common.data_path("03_forecast_points.parquet"), index=False)
print("\nScritto", common.data_path("03_forecast_points.parquet"))
```

- [ ] **Step 7: Cella markdown "Il limite di quello che hai fatto"**

Contenuto obbligatorio:

- **NOMADS conserva circa dieci giorni.** Quello che hai scaricato non e' un archivio storico: fra un mese quel run non ci sara' piu'. Per il vero storico serve l'archivio S3 `noaa-gfs-bdp-pds`, mostrato sotto ma non eseguito perche' richiede tempo e spazio molto maggiori.
- `publication_time_utc` qui e' **stimato** con un ritardo fisso di 4 ore. Nella pipeline vera va registrato quando il file e' stato davvero visto disponibile, perche' e' il campo su cui si fonda tutta la regola anti-leakage.
- Hai una sola variabile (T2m) e un solo run: sufficiente per il metodo, non per una valutazione.

```python
# Non eseguire ora: e' il modo di prendere lo storico vero.
#   aws s3 ls --no-sign-request s3://noaa-gfs-bdp-pds/gfs.20240115/00/atmos/
# Ordini di grandezza nel documento docs/05-mvp-data-feasibility.md.
```

- [ ] **Step 8: Eseguire, verificare, ripulire e committare**

```bash
cd learning/notebooks && ../.venv/bin/jupyter nbconvert --to notebook --execute \
  --inplace 03-forecast-gfs-grib.ipynb
../.venv/bin/python -c "
import pandas as pd
f = pd.read_parquet('../data/03_forecast_points.parquet')
print('righe:', len(f)); assert len(f) > 0
for c in ['run_time_utc','publication_time_utc','valid_time_utc']:
    assert str(f[c].dtype).endswith('UTC]'), c + ' non tz-aware'
assert (f['valid_time_utc'] - f['run_time_utc']).dt.total_seconds().div(3600).eq(f['lead_hours']).all()
print('OK: valid_time = run_time + lead')
"
../.venv/bin/jupyter nbconvert --clear-output --inplace 03-forecast-gfs-grib.ipynb
cd ../.. && git add learning/notebooks/03-forecast-gfs-grib.ipynb
git commit -m "feat: add notebook 03 GFS download and GRIB reading"
```

---

### Task 10: Notebook 04 — Join e anti-leakage

**Files:**
- Create: `learning/notebooks/04-join-e-anti-leakage.ipynb`

**Interfaces:**
- Consumes: `02_observations.parquet`, `03_forecast_points.parquet`
- Produces: `learning/data/04_dataset.parquet` — colonne `station_id, run_time_utc, publication_time_utc, lead_hours, valid_time_utc, t2m_c_forecast, t2m_c_osservato, errore, split`

- [ ] **Step 1: Prerequisiti e join temporale**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))
import common
import pandas as pd

common.richiede("02_observations.parquet", "03_forecast_points.parquet")
oss = pd.read_parquet(common.data_path("02_observations.parquet"))
fc = pd.read_parquet(common.data_path("03_forecast_points.parquet"))

# Il forecast e' orario: si arrotonda l'osservazione all'ora piena e si
# uniscono le due tabelle su (stazione, istante di validita').
oss["ora_utc"] = oss["valid_time_utc"].dt.floor("h")
oss_oraria = (oss[~oss["qa_flag"].isin(list("2367"))]
              .groupby(["station_id", "ora_utc"], as_index=False)["t2m_c"].mean()
              .rename(columns={"t2m_c": "t2m_c_osservato", "ora_utc": "valid_time_utc"}))

ds = fc.merge(oss_oraria, on=["station_id", "valid_time_utc"], how="inner")
ds["errore"] = ds["t2m_c_forecast"] - ds["t2m_c_osservato"]
print(f"Coppie forecast-osservazione: {len(ds)} su {len(fc)} forecast")
print(ds[["station_id", "lead_hours", "t2m_c_forecast", "t2m_c_osservato", "errore"]].head(10).to_string(index=False))
```

- [ ] **Step 2: Cella markdown sugli intervalli half-open**

Contenuto: per una temperatura istantanea basta un istante, ma per una quantita' accumulata come la pioggia il target e' un intervallo `[inizio, fine)`, ed estremo destro escluso evita di contare due volte il confine. Il documento `docs/02-historical-forecast-observation-protocol.md` lo impone perche' un disallineamento di un'ora fra intervallo previsto e osservato produce un errore che non e' del modello ma del join.

- [ ] **Step 3: Il leakage, dimostrato facendolo**

La cella markdown che precede deve contenere un avviso inequivocabile: **il codice che segue e' deliberatamente sbagliato**, serve a mostrare un sintomo, e non va copiato.

```python
# =====================================================================
# ATTENZIONE: CODICE DELIBERATAMENTE SBAGLIATO.
# Serve solo a mostrare come si manifesta il leakage. NON COPIARLO.
# =====================================================================
import numpy as np

sbagliato = ds.copy()

# L'ERRORE: si usa come feature l'osservazione dell'ora successiva, che al
# momento della previsione NON ERA ANCORA ACCADUTA.
sbagliato = sbagliato.sort_values(["station_id", "valid_time_utc"])
sbagliato["feature_SBAGLIATA_non_usare"] = (
    sbagliato.groupby("station_id")["t2m_c_osservato"].shift(-1)
)
sbagliato = sbagliato.dropna(subset=["feature_SBAGLIATA_non_usare"])

# Una "correzione" che sfrutta la feature proibita.
previsione_barata = (sbagliato["t2m_c_forecast"] + sbagliato["feature_SBAGLIATA_non_usare"]) / 2
mae_barato = float(np.abs(previsione_barata - sbagliato["t2m_c_osservato"]).mean())
mae_onesto = float(np.abs(sbagliato["t2m_c_forecast"] - sbagliato["t2m_c_osservato"]).mean())

print(f"MAE del GFS grezzo:            {mae_onesto:.2f} C")
print(f"MAE del modello 'migliorato':  {mae_barato:.2f} C   <-- sembra fantastico")
print("\nE' una bugia: quella feature non esisteva al momento della previsione.")
```

- [ ] **Step 4: Cella markdown che spiega il sintomo**

Contenuto obbligatorio:

- Il miglioramento e' vistoso e arriva senza sforzo. **Un salto di qualita' improvviso e inspiegabile e' il sintomo tipico del leakage**, non un successo.
- La regola violata: nessuna feature puo' usare informazione non disponibile entro `publication_time_utc` (documento 02, regola 1).
- In produzione l'errore non si vede finche' non e' troppo tardi: in backtest il modello brilla, dal vivo l'osservazione futura non esiste e crolla.
- Il controllo automatico: per ogni feature, chiedersi da quale istante proviene e confrontarlo con `publication_time_utc`.

```python
# Il controllo che va eseguito su ogni feature.
istante_feature = sbagliato.groupby("station_id")["valid_time_utc"].shift(-1)
violazioni = (istante_feature > sbagliato["publication_time_utc"]).sum()
print(f"Feature che usano informazione successiva alla pubblicazione: {violazioni} su {len(sbagliato)}")
assert violazioni > 0, "l'esempio deve violare la regola, altrimenti non dimostra nulla"
print("Confermato: la feature e' inammissibile.")
```

- [ ] **Step 5: Split temporale contro split casuale**

```python
ds = ds.sort_values("valid_time_utc").reset_index(drop=True)

# CORRETTO: taglio nel tempo. Il test e' il futuro rispetto al train.
taglio = ds["valid_time_utc"].quantile(0.7)
ds["split"] = np.where(ds["valid_time_utc"] <= taglio, "train", "test")
print("Split temporale:")
print(f"  train fino a {taglio}  -> {(ds['split']=='train').sum()} righe")
print(f"  test  dopo       -> {(ds['split']=='test').sum()} righe")

# SBAGLIATO, per confronto: mescolare le righe.
rng = np.random.default_rng(42)
split_casuale = rng.permutation(np.where(np.arange(len(ds)) < len(ds) * 0.7, "train", "test"))
sovrapposizione = (
    pd.Series(ds["valid_time_utc"][split_casuale == "test"]).min()
    < pd.Series(ds["valid_time_utc"][split_casuale == "train"]).max()
)
print(f"\nCon lo split casuale il test contiene istanti anteriori al train: {sovrapposizione}")
print("Su serie autocorrelate questo gonfia le metriche: ore adiacenti si somigliano,")
print("quindi il modello ritrova nel test cio' che ha gia' visto nel train.")
```

- [ ] **Step 6: Scrivere il dataset**

```python
colonne = ["station_id", "run_time_utc", "publication_time_utc", "lead_hours",
           "valid_time_utc", "t2m_c_forecast", "t2m_c_osservato", "errore", "split"]
ds[colonne].to_parquet(common.data_path("04_dataset.parquet"), index=False)
print("Scritto", common.data_path("04_dataset.parquet"))
print("Lo split e' una COLONNA, non tre file: nel notebook 05 il test resta")
print("visibile e va lasciato intatto fino alla valutazione finale.")
```

- [ ] **Step 7: Cella markdown "Il limite di quello che hai fatto"**

Contenuto: il dataset copre un solo run e pochi lead, quindi il taglio temporale separa ore, non stagioni — il vero split del progetto separa anni interi (documento 04). Qui manca la validation: con cosi' pochi dati sarebbe illusoria. Il leakage mostrato e' il piu' evidente; ne esistono di piu' sottili, come una climatologia calcolata sull'intero periodo compreso il test.

- [ ] **Step 8: Eseguire, verificare, ripulire e committare**

```bash
cd learning/notebooks && ../.venv/bin/jupyter nbconvert --to notebook --execute \
  --inplace 04-join-e-anti-leakage.ipynb
../.venv/bin/python -c "
import pandas as pd
d = pd.read_parquet('../data/04_dataset.parquet')
print('righe:', len(d)); assert len(d) > 0
assert set(d['split']) <= {'train','test'}
tr, te = d[d.split=='train'], d[d.split=='test']
assert tr['valid_time_utc'].max() <= te['valid_time_utc'].min(), 'split non temporale'
print('OK: il test e posteriore al train')
"
../.venv/bin/jupyter nbconvert --clear-output --inplace 04-join-e-anti-leakage.ipynb
cd ../.. && git add learning/notebooks/04-join-e-anti-leakage.ipynb
git commit -m "feat: add notebook 04 temporal join and leakage demonstration"
```

---

### Task 11: Notebook 05 — Baseline e previsione basic

**Files:**
- Create: `learning/notebooks/05-baseline-e-previsione.ipynb`

**Interfaces:**
- Consumes: `04_dataset.parquet`, `01_stations.csv`
- Produces: `learning/data/05_metrics.json` con struttura `{"baseline": {nome: {"mae": float, "rmse": float, "bias": float, "n": int}}, "bootstrap": {...}, "generato_il": ISO}`

- [ ] **Step 1: Prerequisiti e ordine obbligatorio delle baseline (markdown + codice)**

La markdown ricorda l'ordine imposto dal progetto: climatologia → persistenza → GFS grezzo → bias correction → e solo dopo, eventualmente, ML. Il senso e' che un modello complesso va confrontato con quello che si ottiene quasi gratis.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))
import common
import numpy as np
import pandas as pd

common.richiede("04_dataset.parquet", "01_stations.csv")
ds = pd.read_parquet(common.data_path("04_dataset.parquet"))
stazioni = pd.read_csv(common.data_path("01_stations.csv"))
train = ds[ds["split"] == "train"].copy()
test = ds[ds["split"] == "test"].copy()
print(f"train: {len(train)} righe | test: {len(test)} righe")

def metriche(previsto, osservato) -> dict:
    """Calcola MAE, RMSE e bias di una previsione contro l'osservazione."""
    e = np.asarray(previsto) - np.asarray(osservato)
    return {"mae": float(np.abs(e).mean()), "rmse": float(np.sqrt((e ** 2).mean())),
            "bias": float(e.mean()), "n": int(len(e))}
```

- [ ] **Step 2: Le quattro baseline, tutte sullo stesso campione**

```python
risultati = {}

# 1. Climatologia: la media per stazione calcolata SOLO sul train.
clim = train.groupby("station_id")["t2m_c_osservato"].mean()
risultati["climatologia"] = metriche(test["station_id"].map(clim), test["t2m_c_osservato"])

# 2. Persistenza: l'ultima osservazione disponibile nel train per quella stazione.
ultima = train.sort_values("valid_time_utc").groupby("station_id")["t2m_c_osservato"].last()
risultati["persistenza"] = metriche(test["station_id"].map(ultima), test["t2m_c_osservato"])

# 3. GFS grezzo, con la stessa interpolazione usata da tutto il resto.
risultati["gfs_grezzo"] = metriche(test["t2m_c_forecast"], test["t2m_c_osservato"])

# 4. Bias correction: la correzione media per stazione, stimata SOLO sul train
#    e applicata al test senza rifare il fit.
correzione = train.groupby("station_id")["errore"].mean()
corretto = test["t2m_c_forecast"] - test["station_id"].map(correzione).fillna(0.0)
risultati["bias_correction"] = metriche(corretto, test["t2m_c_osservato"])

confronto = pd.DataFrame(risultati).T[["mae", "rmse", "bias", "n"]]
print(confronto.round(3).to_string())
print("\nATTENZIONE: tutte le baseline usano lo stesso campione, lo stesso filtro")
print("e la stessa interpolazione. Un confronto fra campioni diversi non vale nulla.")
```

- [ ] **Step 3: Grafici — errore per lead e mappa dell'errore (requisito della spec)**

```python
import matplotlib.pyplot as plt
try:
    import cartopy.crs as ccrs, cartopy.feature as cfeature
    proj = ccrs.PlateCarree()
except Exception:
    ccrs = None

fig = plt.figure(figsize=(15, 6))

# A sinistra: errore assoluto medio in funzione del lead.
ax1 = fig.add_subplot(1, 2, 1)
per_lead = test.assign(ae=test["errore"].abs()).groupby("lead_hours")["ae"].mean()
ax1.plot(per_lead.index, per_lead.values, marker="o")
ax1.set_xlabel("lead (ore)"); ax1.set_ylabel("MAE (C)")
ax1.set_title("L'errore cresce con l'orizzonte di previsione")
ax1.grid(alpha=0.3)

# A destra: dove sbaglia, sulla mappa.
mae_staz = test.assign(ae=test["errore"].abs()).groupby("station_id")["ae"].mean()
st = stazioni.set_index("station_id").loc[mae_staz.index]
ax2 = fig.add_subplot(1, 2, 2, projection=proj) if ccrs else fig.add_subplot(1, 2, 2)
kw = {"transform": proj} if ccrs else {}
if ccrs:
    margine = 0.5
    ax2.set_extent([st["lon"].min()-margine, st["lon"].max()+margine,
                    st["lat"].min()-margine, st["lat"].max()+margine], crs=proj)
    ax2.add_feature(cfeature.COASTLINE, linewidth=0.7)
    ax2.add_feature(cfeature.BORDERS, linewidth=0.4, linestyle=":")
sc = ax2.scatter(st["lon"], st["lat"], c=mae_staz.values, s=220,
                 cmap="YlOrRd", edgecolor="black", zorder=5, **kw)
for sid, r in st.iterrows():
    ax2.annotate(f"{r['nome']}\n{r['elev_m']:.0f} m ; MAE {mae_staz[sid]:.1f}",
                 (r["lon"], r["lat"]), fontsize=7,
                 xytext=(6, 6), textcoords="offset points", **kw)
plt.colorbar(sc, ax=ax2, label="MAE (C)", shrink=0.8)
ax2.set_title("Dove sbaglia il modello")
plt.tight_layout(); plt.show()

print("\nMAE per quota:")
print(pd.DataFrame({"mae": mae_staz, "quota_m": st["elev_m"]}).sort_values("quota_m").round(2).to_string())
```

- [ ] **Step 4: Cella markdown — leggere il grafico**

Contenuto: l'errore cresce col lead perche' l'incertezza iniziale si amplifica. Sulla mappa, tipicamente le stazioni in quota hanno l'errore maggiore: la cella del modello ha un'orografia mediata che non conosce la vetta. **Questo errore e' sistematico, quindi apprendibile: e' la ragione per cui il post-processing statistico ha senso.**

- [ ] **Step 5: Bootstrap — quanto e' solido il risultato**

```python
def bootstrap_mae(previsto, osservato, gruppi, n=1000, seed=42):
    """Intervallo di confidenza del MAE, ricampionando per stazione-giorno.

    Si ricampionano i gruppi, non i singoli record: due ore consecutive
    non sono osservazioni indipendenti, e ricampionarle come tali
    restringerebbe artificiosamente l'intervallo.
    """
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({"e": np.abs(np.asarray(previsto) - np.asarray(osservato)), "g": list(gruppi)})
    per_gruppo = df.groupby("g")["e"].mean()
    chiavi = per_gruppo.index.to_numpy()
    campioni = [per_gruppo[rng.choice(chiavi, len(chiavi), replace=True)].mean() for _ in range(n)]
    return float(np.percentile(campioni, 2.5)), float(np.percentile(campioni, 97.5))

gruppi = test["station_id"] + "|" + test["valid_time_utc"].dt.date.astype(str)
ic_gfs = bootstrap_mae(test["t2m_c_forecast"], test["t2m_c_osservato"], gruppi)
ic_bc = bootstrap_mae(corretto, test["t2m_c_osservato"], gruppi)

print(f"GFS grezzo      MAE {risultati['gfs_grezzo']['mae']:.2f} C  IC95% [{ic_gfs[0]:.2f}, {ic_gfs[1]:.2f}]")
print(f"Bias correction MAE {risultati['bias_correction']['mae']:.2f} C  IC95% [{ic_bc[0]:.2f}, {ic_bc[1]:.2f}]")

sovrapposti = not (ic_bc[1] < ic_gfs[0] or ic_gfs[1] < ic_bc[0])
print(f"\nGli intervalli si sovrappongono: {sovrapposti}")
if sovrapposti:
    print("=> La differenza NON e' distinguibile dal rumore su questo campione.")
    print("   Qualunque conclusione sul fatto che la correzione 'funzioni' sarebbe abusiva.")
```

- [ ] **Step 6: Scrivere le metriche**

```python
import json
from datetime import datetime, timezone

uscita = {
    "baseline": risultati,
    "bootstrap": {"gfs_grezzo_ic95": list(ic_gfs), "bias_correction_ic95": list(ic_bc),
                  "intervalli_sovrapposti": bool(sovrapposti)},
    "campione": {"stazioni": int(test["station_id"].nunique()),
                 "righe_train": int(len(train)), "righe_test": int(len(test))},
    "generato_il": datetime.now(timezone.utc).isoformat(),
}
with common.data_path("05_metrics.json").open("w") as f:
    json.dump(uscita, f, indent=2, ensure_ascii=False)
print("Scritto", common.data_path("05_metrics.json"))
```

- [ ] **Step 7: Cella markdown finale — il limite, e cosa servirebbe davvero**

E' la conclusione dell'intero percorso e la parte che gli da' onesta'. Contenuto obbligatorio:

**Quello che hai ottenuto:** il ciclo completo, dal download alla metrica, con un metodo corretto — split temporale, fit solo sul train, confronto equo, incertezza dichiarata.

**Quello che NON hai ottenuto:** una prova che il post-processing funzioni. Poche stazioni, un run, pochi lead, nessuna copertura stagionale. Se gli intervalli bootstrap si sovrappongono — e con questo campione e' probabile — il risultato **non e' conclusivo**, e dirlo non e' un fallimento: e' il risultato.

**Cosa servirebbe** (dal `docs/04-mvp-benchmark-validation-plan.md`): le 124 stazioni candidate invece di cinque; anni interi con train 2021-2024, validation 2025 e test congelato; tutti i lead 1-72 h su quattro run al giorno; segmentazione per macro-area, stagione, ora locale, fascia altimetrica e classe di evento; e per la precipitazione un target ad accumulo, che e' un problema piu' difficile.

**Il seguito serio** e' M0 del `docs/08-mvp-implementation-plan.md`: contratti dati, catalogo, idempotenza. Non e' un notebook, ed e' questa la differenza fra imparare e costruire.

- [ ] **Step 8: Eseguire, verificare, ripulire e committare**

```bash
cd learning/notebooks && ../.venv/bin/jupyter nbconvert --to notebook --execute \
  --inplace 05-baseline-e-previsione.ipynb
../.venv/bin/python -c "
import json
m = json.load(open('../data/05_metrics.json'))
for nome in ['climatologia','persistenza','gfs_grezzo','bias_correction']:
    assert nome in m['baseline'], 'manca la baseline ' + nome
    print(f\"{nome:16s} MAE {m['baseline'][nome]['mae']:.2f}\")
assert 'intervalli_sovrapposti' in m['bootstrap']
print('OK: tutte le baseline obbligatorie sono presenti')
"
../.venv/bin/jupyter nbconvert --clear-output --inplace 05-baseline-e-previsione.ipynb
cd ../.. && git add learning/notebooks/05-baseline-e-previsione.ipynb
git commit -m "feat: add notebook 05 baselines and honest evaluation"
```

---

### Task 12: Verifica end-to-end su ambiente pulito

**Files:**
- Modify: nessuno (solo verifica; correzioni se emergono difetti)

**Interfaces:**
- Consumes: tutto
- Produces: la conferma che il percorso e' eseguibile da zero

- [ ] **Step 1: Cancellare gli artefatti e rieseguire tutto in ordine**

```bash
rm -rf learning/data
cd learning/notebooks
for nb in 01-setup-e-fondamenti 02-osservazioni-isd 03-forecast-gfs-grib \
          04-join-e-anti-leakage 05-baseline-e-previsione; do
  echo "=== $nb ==="
  ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace "$nb.ipynb" || {
    echo "FALLITO: $nb"; break; }
done
```

Expected: cinque esecuzioni senza eccezioni.

- [ ] **Step 2: Verificare che tutti gli artefatti attesi esistano**

```bash
cd learning && for f in 00_env_report.json 01_stations.csv 02_observations.parquet \
  03_forecast_points.parquet 04_dataset.parquet 05_metrics.json; do
  [ -f "data/$f" ] && echo "OK   $f" || echo "MANCANTE $f"
done
```

Expected: sei righe `OK`.

- [ ] **Step 3: Verificare che il controllo dei prerequisiti funzioni davvero**

```bash
cd learning && mv data/02_observations.parquet /tmp/backup.parquet
.venv/bin/python -c "
import sys; sys.path.insert(0,'.')
import common
try:
    common.richiede('02_observations.parquet','03_forecast_points.parquet')
    print('ERRORE: doveva sollevare un errore')
except common.PrerequisitoMancante as e:
    assert '02-osservazioni-isd' in str(e)
    print('OK, messaggio corretto:'); print(e)
"
mv /tmp/backup.parquet data/02_observations.parquet```

Expected: il messaggio nomina `02-osservazioni-isd`.

- [ ] **Step 4: Eseguire i test di `common.py` un'ultima volta**

```bash
cd learning && .venv/bin/pytest test_common.py -v
```

Expected: 22 passed.

- [ ] **Step 5: Verificare che nulla di generato stia per essere committato**

```bash
git status --short learning/
git check-ignore -v learning/data/05_metrics.json learning/.venv/bin/python
```

Expected: `git status` non elenca `learning/data/` ne' `learning/.venv/`; `check-ignore` conferma entrambi ignorati.

- [ ] **Step 6: Verificare che i notebook committati non contengano output**

```bash
learning/.venv/bin/python - <<'PY'
import json, pathlib
for p in sorted(pathlib.Path("learning/notebooks").glob("*.ipynb")):
    nb = json.loads(p.read_text())
    sporche = [i for i, c in enumerate(nb["cells"])
               if c.get("cell_type") == "code" and (c.get("outputs") or c.get("execution_count"))]
    print(("SPORCO " if sporche else "PULITO "), p.name, sporche or "")
PY
```

Expected: cinque righe `PULITO`. Se una e' sporca, rieseguire `jupyter nbconvert --clear-output --inplace` su quel file.

- [ ] **Step 7: Commit finale (solo se i passi precedenti hanno prodotto correzioni)**

```bash
git add -u learning/
git commit -m "fix: correct issues found in end-to-end learning path run"
```

Se nessuna correzione e' stata necessaria, non c'e' nulla da committare: il percorso e' completo.

---

## Note per chi esegue il piano

**Le fonti remote possono cambiare.** I Task 8 e 9 dipendono da NCEI e NOMADS. Se un download fallisce:

- verificare l'URL nel browser prima di modificare il codice;
- per NOMADS, la causa piu' probabile e' un run non ancora pubblicato: aumentare lo scarto orario nel Task 9 Step 2;
- non sostituire silenziosamente una fonte con un'altra: l'onesta' sulle fonti e' parte di cio' che il percorso insegna.

**I numeri riprodotti dal documento 05 possono divergere.** L'inventario ISD e' aggiornato di continuo. Una divergenza di qualche unita' e' attesa e va dichiarata, come gia' previsto nel Task 8 Step 3. Una divergenza grande va indagata prima di proseguire.

**Le durate nel README sono stime di pianificazione, non misure.** Se l'esecuzione reale del Task 12 mostra durate molto diverse, aggiornare la tabella del README.

**Ordine dei task.** I Task 2-5 costruiscono `common.py` in TDD e vanno eseguiti in sequenza. I Task 7-11 dipendono l'uno dall'output dell'altro. Il Task 6 (README) puo' essere anticipato o posticipato liberamente.
