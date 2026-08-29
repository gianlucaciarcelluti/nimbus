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
