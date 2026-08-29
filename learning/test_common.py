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
