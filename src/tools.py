import sqlite3
import json
import datetime
import yaml
import requests
import pathlib
import random
import sys

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


def initialize_empty_db(database: str):
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
    db.execute(
        'CREATE TABLE Program ("model_name" TEXT PRIMARY KEY, code TEXT NOT NULL, data TEXT NOT NULL, "last_run" TIMESTAMP, UNIQUE(code, data) ON CONFLICT IGNORE)'
    )
    db.commit()

    db.execute(
        'CREATE TABLE Meta ("model_name" TEXT PRIMARY KEY, "iter_sampling" INTEGER NOT NULL, "iter_warmup" INTEGER NOT NULL, chains INTEGER NOT NULL, "parallel_chains" INTEGER NOT NULL, thin INTEGER NOT NULL, seed INTEGER NOT NULL, "adapt_delta" REAL NOT NULL, "max_treedepth" INTEGER NOT NULL, "sig_figs" INTEGER NOT NULL)'
    )
    db.commit()
    db.close()


"""
Insert Programs from cloned PosteriorDB repository
"""


def insert_posteriordb(pdb_path: str, database: str):
    try:
        from posteriordb import PosteriorDatabase
    except:
        sys.exit("please install PosteriorDB Python package: $ pip install posteriordb")

    pdb = PosteriorDatabase(pdb_path)
    model_names = pdb.posterior_names()
    if not model_names:
        sys.exit(
            "No Stan programs available. Maybe the path is incorrectly specified.  Recall, PosteriorDB requires the path to the sub-folder posterior_database of the git cloned repository."
        )

    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    for model_name in model_names:
        model = {}
        meta = {}
        posterior = pdb.posterior(model_name)

        reference_draws_exist = False
        try:
            posterior.reference_draws()
            reference_draws_exist = True
        except:
            pass

        if reference_draws_exist:
            model["model_name"] = posterior.name
            model["code"] = posterior.model.code("stan")
            model["last_run"] = datetime.datetime.min
            model["data"] = json.dumps(posterior.data.values())

            try:
                db.execute(
                    "INSERT INTO Program VALUES(:model_name, :code, :data, :last_run)",
                    model,
                )
                db.commit()
            except:
                continue

            meta["model_name"] = model["model_name"]
            info = posterior.reference_draws_info()["inference"]["method_arguments"]
            meta["iter_sampling"] = info.get("iter", 10_000)
            meta["iter_warmup"] = info.get("warmup", meta["iter_sampling"])
            meta["chains"] = info.get("chains", 10)
            meta["parallel_chains"] = info.get("parallel_chains", meta["chains"])
            meta["thin"] = info.get("thin", 1)
            meta["seed"] = info.get("seed", random.randint(0, 4_294_967_295))
            meta["adapt_delta"] = info.get("control", 0.8).get("adapt_delta", 0.8)
            meta["max_treedepth"] = info.get("control", 10).get("max_treedepth", 10)
            meta["sig_figs"] = info.get("sig_figs", 16)

            db.execute(
                "INSERT INTO Meta VALUES(:model_name, :iter_sampling, :iter_warmup, :chains, :parallel_chains, :thin, :seed, :adapt_delta, :max_treedepth, :sig_figs)",
                meta,
            )
            db.commit()

    db.close()


"""
Read a YAML config file
"""


def read_config(configfile):
    with open(configfile, "rb") as f:
        yml = yaml.load(f, Loader=yaml.Loader)
    return yml


"""
Download/stream minipdb.sqlite into path
"""


def download_db(path):
    url = "https://roualdes.us/minipdb.sqlite"
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
