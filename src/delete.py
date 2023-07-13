import sqlite3
import sys

import pandas as pd

from .tools import table_exists


def delete(args: dict):
    model_name = args['model_name']

    if not args['yes']:
        ans = input(
            f'This operation will delete all reference draws for {model_name},\nand all corresponding information from minipdb.sqlite.\n\nThis operation can not be undone.\n\nAre you sure you want to proceed?\n\nType Yes to continue: '
        )
        if ans != 'Yes':
            sys.exit('Canceled delete.')

    print(f'deleting {model_name}...')

    database = args['database']
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    exists_in_program = False
    try:
        dfprogram = pd.read_sql_query('SELECT * FROM Program', db)
        exists_in_program = model_name in dfprogram['model_name'].values
    except:
        pass
    if exists_in_program:
        print(f'deleting {model_name} from table Program')
        db.execute(f'DELETE FROM Program WHERE "model_name" = "{model_name}"')
        db.commit()

    exists_in_meta = False
    try:
        dfmeta = pd.read_sql_query('SELECT * FROM Meta', db)
        exists_in_meta = model_name in dfprogram['model_name'].values
    except:
        pass
    if exists_in_meta:
        print(f'deleting {model_name} from table Meta')
        db.execute(f'DELETE FROM Meta WHERE "model_name" = "{model_name}"')
        db.commit()

    exists_in_diagnostics = False
    try:
        dfdiagnostics = pd.read_sql_query(
            f'SELECT * FROM "{model_name}_diagnostics"', db
        )
        exists_in_diagnostics = model_name in dfdiagnostics['model_name'].values
    except:
        pass
    if exists_in_diagnostics:
        print(f'deleting table {model_name}_diagnostics')
        db.execute(f'DROP "{model_name}_diagnostics"')
        db.commit()

    exists_in_metric = False
    try:
        dfmetric = pd.read_sql_query(f'SELECT * FROM "{model_name}_metric"', db)
        exists_in_metric = model_name in dfmetric['model_name'].values
    except:
        pass
    if exists_in_metric:
        print(f'deleting table {model_name}_metric')
        db.execute(f'DROP "{model_name}_metric"')
        db.commit()

    if table_exists(args, db):
        print(f'deleting table {model_name}')
        db.execute(f'DROP "{model_name}"')
        db.commit()

    db.close()
    print('Done.')
