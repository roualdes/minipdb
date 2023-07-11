import minipdb

import pytest
import pathlib
import sqlite3

import pandas as pd

cwd = pathlib.Path().resolve() / 'test'

def test_run():
    args = {'toml': cwd / 'fake01.toml',
            'database': cwd / 'test.sqlite',
            'model_name': 'Fake01',
            'all_models': False,
            'overwrite': True,
            'yes': True,
            'cpus': 1}
    minipdb.run(args)

    database = args['database']
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    dfp = pd.read_sql_query('SELECT * FROM Program', db)
    assert 'Fake01' in dfp['model_name'].values

    dfm = pd.read_sql_query('SELECT * FROM Meta', db)
    assert 'Fake01' in dfm['model_name'].values

    df = pd.read_sql_query(f'SELECT * FROM Fake01', db)
    assert df.shape[0] == 4000

    dfmetric = pd.read_sql_query(f'SELECT * FROM "Fake01_metric"', db)

    db.close()


def test_update():
    args = {'toml': cwd / 'fake03.toml',
            'database': cwd / 'test.sqlite',
            'model_name': 'Fake01',
            'all_models': False,
            'overwrite': True,
            'yes': True,
            'cpus': 1}

    database = args['database']
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    dfm = pd.read_sql_query('SELECT * FROM Meta', db)
    assert 'Fake01' in dfm['model_name'].values
    idx = dfm['model_name'] == 'Fake01'
    assert dfm[idx]['iter_sampling'].values[0] == 2000
    assert dfm[idx]['thin'].values[0] == 1

    db.close()


def test_runall():
    args = {'database': cwd / 'test.sqlite',
            'overwrite': False,
            'yes': True,
            'cpus': 1}

    database = args['database']
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    # check does not overwrite Fake01 reference draws
    dfp = pd.read_sql_query('SELECT * FROM Program', db)
    assert 'Fake01' in dfp['model_name'].values

    idx = dfp['model_name'] == 'Fake01'
    t = pd.to_datetime(dfp[idx]['last_run'].values[0])

    db.close()

    minipdb.run_all(args)

    database = args['database']
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    dfp = pd.read_sql_query('SELECT * FROM Program', db)
    idx = dfp['model_name'] == 'Fake01'
    assert t == pd.to_datetime(dfp[idx]['last_run'].values[0])

    db.close()

    # check overwrites Fake01 and Fake 02
    args = {'database': cwd / 'test.sqlite',
            'overwrite': True,
            'yes': True,
            'cpus': 1}

    database = args['database']
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
    dfp = pd.read_sql_query('SELECT * FROM Program', db)

    idx01 = dfp['model_name'] == 'Fake01'
    t01 = pd.to_datetime(dfp[idx]['last_run'].values[0])

    idx02 = dfp['model_name'] == 'Fake02'
    t02 = pd.to_datetime(dfp[idx]['last_run'].values[0])

    db.close()

    minipdb.run_all(args)

    database = args['database']
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
    dfp = pd.read_sql_query('SELECT * FROM Program', db)

    idx01 = dfp['model_name'] == 'Fake01'
    assert t01 < pd.to_datetime(dfp[idx]['last_run'].values[0])

    idx02 = dfp['model_name'] == 'Fake02'
    assert t02 < pd.to_datetime(dfp[idx]['last_run'].values[0])

    db.close()
