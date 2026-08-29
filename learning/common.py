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
