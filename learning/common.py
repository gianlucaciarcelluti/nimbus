"""Supporto al percorso didattico Nimbus.

Questo modulo contiene soltanto cio' che e' ripetitivo e non didattico:
percorsi, bounding box regionali e download con cache. Ogni contenuto
meteorologico o statistico resta visibile nelle celle dei notebook.

Non fa parte della pipeline Nimbus: vedere learning/README.md.
"""
import hashlib
from pathlib import Path

import requests

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
