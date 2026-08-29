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
