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
