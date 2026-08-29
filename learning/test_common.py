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
