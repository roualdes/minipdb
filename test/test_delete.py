import minipdb

import pytest
import pathlib
import sqlite3

import pandas as pd

def test_delete():
    cwd = pathlib.Path().resolve() / 'test'
    args = {'database': cwd / 'test.sqlite',
            'model_name': 'Fake01',
            'yes': True}
    minipdb.delete(args)

    args = {'database': cwd / 'test.sqlite',
            'model_name': 'Fake02',
            'yes': True}
    minipdb.delete(args)

    database = args['database']
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    dfp = pd.read_sql_query('SELECT * FROM Program', db)
    assert 'Fake01' not in dfp['model_name'].values
    assert 'Fake02' not in dfp['model_name'].values

    dfm = pd.read_sql_query('SELECT * FROM Meta', db)
    assert 'Fake01' not in dfm['model_name'].values
    assert 'Fake02' not in dfm['model_name'].values

    db.close()
