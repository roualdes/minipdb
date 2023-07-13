import minipdb

import pytest
import pathlib
import sqlite3

import pandas as pd


def test_insert():
    cwd = pathlib.Path().resolve() / "test"
    args = {"yaml": cwd / "fake01.yml", "database": cwd / "test.sqlite"}
    minipdb.insert(args)

    args["yaml"] = cwd / "fake02.yml"
    minipdb.insert(args)

    database = args["database"]
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    dfp = pd.read_sql_query("SELECT * FROM Program", db)
    assert "Fake01" in dfp["model_name"].values
    assert "Fake02" in dfp["model_name"].values

    dfm = pd.read_sql_query("SELECT * FROM Meta", db)
    assert "Fake01" in dfm["model_name"].values
    assert "Fake02" in dfm["model_name"].values

    db.close()
