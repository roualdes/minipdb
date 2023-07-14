import sqlite3
import sys
import pathlib
import datetime

import pandas as pd

from .checks import insert_checks
from .tools import table_exists, read_config

"""
Insert a Stan program into the database, without storing reference draws.

A row is added to both of the database tables Program and Meta.  The row
inserted into Program will contain the model name, the .stan file code, and the
JSON data.  The row inserted into Meta will contain all the necessary sampling
parameters in order to create the reference draws.  The values within each row
is obtained from the YAML file specified at the command line.

Following the insertion of a Stan program, the command :command:`run` is
neccessary to store reference draws.  Separating `insert` and `run` allows one
to `run` a Stan program and on their preferred machine.

See also the `add` which will both `insert` and `run` in one step.
"""


def insert(args):
    configfile = args["yaml"]
    config = read_config(configfile)

    insert_checks(config, configfile)

    model_name = config["model_name"]
    print(f"Initializing {model_name}...")

    database = pathlib.Path(args["database"])
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    exists_in_program = False
    try:
        dfprogram = pd.read_sql_query("SELECT * FROM Program", db)
        exists_in_program = model_name in dfprogram["model_name"].values
    except pandas.errors.DatabaseError as e:
        print(e)
        sys.exit(f'args["database"] does not have table Program')

    exists_in_meta = False
    try:
        dfmeta = pd.read_sql_query("SELECT * FROM Meta", db)
        exists_in_meta = model_name in dfmeta["model_name"].values
    except pandas.errors.DatabaseError as e:
        print(e)
        sys.exit(f'args["database"] does not have table Meta')

    exists_in_diagnostics = False
    try:
        dfdiagnostics = pd.read_sql_query(f"SELECT * FROM {model_name}_diagnostics", db)
        exists_in_diagnostics = model_name in dfdiagnostics["model_name"].values
    except:
        pass

    exists_in_metric = False
    try:
        dfmetric = pd.read_sql_query(f"SELECT * FROM {model_name}_metric", db)
        exists_in_metric = model_name in dfmetric["model_name"].values
    except:
        pass

    exists = [
        exists_in_program,
        exists_in_meta,
        exists_in_diagnostics,
        exists_in_metric,
    ]
    if sum(exists) == 1:
        sys.exit(
            f'A Stan program with model name {model_name} exists in some {args["database"]} table.  Something wrong happened.  Fix it.'
        )

    if all(exists):
        sys.exit(
            f"A Stan program with model name {model_name} already exists in minipdb.sqlite, please ensure you are adding a uniqur Stan program and if so change the nodel name."
        )

    folder = configfile.parent

    with open(folder / config["stan_file"], "r") as f:
        config["code"] = "".join(f.readlines())

    with open(folder / config["json_data"], "r") as f:
        config["data"] = "".join(f.readlines())

    try:
        config["last_run"] = datetime.datetime.min
        db.execute(
            "INSERT INTO Program VALUES(:model_name, :code, :data, :last_run)", config
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        print(e)

    try:
        db.execute(
            "INSERT INTO Meta VALUES(:model_name, :iter_warmup, :iter_sampling, :chains, :parallel_chains, :thin, :seed, :adapt_delta, :max_treedepth, :sig_figs)",
            config,
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        print(e)

    db.close()
    print("Done.")
