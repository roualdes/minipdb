import pathlib
import sqlite3
import sys
import json
import cmdstanpy
import datetime
import functools

import pandas as pd
import numpy as np

from multiprocessing import Pool, cpu_count

from .tools import table_exists

"""
Run a Stan program using CmdStanPy.  The Stan model code and data are pulled
from database table Program.  The sampling algorithm parameters are pulled from
database table Meta.  As such, the Stan program must be :command:`init` first.
"""


def run_model(model_name: str, models_dir: str = "", database_path: str = ""):

    db = sqlite3.connect(database_path, detect_types=sqlite3.PARSE_DECLTYPES)
    dfp = pd.read_sql_query("SELECT * FROM Program", db)
    dfm = pd.read_sql_query("SELECT * FROM Meta", db)

    idx = dfp["model_name"] == model_name
    code = dfp[idx]["code"].values[0]

    model_dir = pathlib.Path(models_dir) / model_name
    pathlib.Path(model_dir).mkdir(parents=True, exist_ok=True)
    stan_file_path = model_dir / (model_name + ".stan")
    with open(stan_file_path, "w") as f:
        f.write(code)

    data = json.loads(dfp[idx]["data"].values[0])
    data_file_path = model_dir / (model_name + ".json")
    cmdstanpy.write_stan_json(data_file_path, data)

    stan_file = str(stan_file_path)
    data_file = str(data_file_path)
    model = cmdstanpy.CmdStanModel(stan_file=stan_file)

    info = dfm[idx].to_dict(orient="index")
    k = list(info.keys())[0]
    info = info[k]
    fit = model.sample(
        data=data_file,
        iter_sampling=info["iter_sampling"],
        iter_warmup=info["iter_warmup"],
        chains=info["chains"],
        parallel_chains=min(cpu_count() - 1, info["parallel_chains"]),
        thin=info["thin"],
        seed=info["seed"],
        adapt_delta=info["adapt_delta"],
        max_treedepth=info["max_treedepth"],
        sig_figs=info["sig_figs"],
    )

    t = datetime.datetime.utcnow()
    db.execute(
        f'UPDATE Program SET "last_run" = "{t}" WHERE "model_name" = "{model_name}"'
    )
    db.commit()

    df = fit.draws_pd()
    df.to_sql(f"{model_name}", db, if_exists="replace", index=False)

    M = fit.metric.T
    col_names = ["chain_" + str(c + 1) for c in range(np.shape(M)[1])]
    dfmetric = pd.DataFrame(M, columns=col_names)
    dfmetric.to_sql(f"{model_name}_metric", db, if_exists="replace", index=False)

    db.close()


"""
Run an already :command:`init`ed Stan program and store the resulting reference draws.
"""


def run(args: dict):
    model_name = args["model_name"]
    print(f"Running model {model_name} and storing reference draws...")

    database = args["database"]
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    dfprogram = pd.read_sql_query("SELECT * FROM Program", db)
    exists_in_program = model_name in dfprogram["model_name"].values

    dfmeta = pd.read_sql_query("SELECT * FROM Meta", db)
    exists_in_meta = model_name in dfmeta["model_name"].values

    if sum([exists_in_program, exists_in_meta]) == 0:
        sys.exit(
            f"Program {model_name} does not exists in database, please init first."
        )

    if table_exists(args, db) and args["overwrite"]:
        print("overwrite turned on...")
        if not args["yes"]:
            ans = input(
                f"This operation will overwrite all previous reference draws.\n\nType Yes to continue: "
            )
            if ans != "Yes":
                sys.exit("Run canceled.")

    model_folder = pathlib.Path().resolve() / "models"
    run_model(model_name, models_dir=model_folder, database_path=database)

    db.close()
    print("Done.")


def run_all(args: dict):
    print(f"Running and storing reference draws for all models in database...")

    if not args["yes"] and args["overwrite"]:
        ans = input(
            f"This operation will overwrite all previous reference draws.\n\nType Yes to continue: "
        )
        if ans != "Yes":
            sys.exit("Run canceled.")

    database = args["database"]
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    dfprogram = pd.read_sql_query("SELECT * FROM Program", db)
    dfmeta = pd.read_sql_query("SELECT * FROM Meta", db)
    model_folder = pathlib.Path().resolve() / "models"

    model_names = dfprogram["model_name"].values

    if not args["overwrite"]:
        cursor = db.cursor()
        tables = cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        table_names = set([tbl[0] for tbl in tables])
        model_names = set(model_names).difference(table_names)

    with Pool(args["cpus"]) as p:
        f = functools.partial(
            run_model, models_dir=model_folder, database_path=database
        )
        p.map(f, model_names)

    db.close()
    print("Done.")
