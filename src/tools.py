import sqlite3
import yaml
import requests
import pathlib

"""
Check if table args['model_name'] exists in database
"""


def table_exists(args, database):
    tbl_exists = False
    try:
        cursor = database.cursor()
        tables = cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        for table in tables:
            if args["model_name"] == table:
                tbl_exists = True
                break
    except:
        return False
    return tbl_exists

"""
Initialize a MiniPDB database with empty tables Program and Meta
"""
def initialize_db(database: str):
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
    db.execute(
        'CREATE TABLE Program ("model_name" TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, data TEXT NOT NULL, "last_run" TIMESTAMP)'
    )
    db.commit()

    db.execute(
        'CREATE TABLE Meta ("model_name" TEXT PRIMARY KEY, "iter_sampling" INTEGER NOT NULL, "iter_warmup" INTEGER NOT NULL, chains INTEGER NOT NULL, "parallel_chains" INTEGER NOT NULL, thin INTEGER NOT NULL, seed INTEGER NOT NULL, "adapt_delta" REAL NOT NULL, "max_treedepth" INTEGER NOT NULL, "sig_figs" INTEGER NOT NULL)'
    )
    db.commit()
    db.close()

"""
Read a YAML config file
"""
def read_config(configfile: str):
    with open(configfile, "rb") as f:
        yml = yaml.load(f, Loader=yaml.Loader)
    return yml

"""
Download/stream minipdb.sqlite into path
"""
def download_db(path):
    url = 'https://roualdes.us/minipdb.sqlite'
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
