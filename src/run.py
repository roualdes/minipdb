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

from .tools import table_exists, write_stan_model, write_stan_data

"""
Run a Stan program using CmdStanPy.  The Stan program, model code and data, are
pulled from table Program.  The sampling algorithm parameters are pulled from
table Meta.  As such, the Stan program must be `insert`ed first.
"""


def run_model(model_name: str, programs_dir: str = "", database_path: str = ""):

    programs_dir = pathlib.Path(programs_dir)

    db = sqlite3.connect(database_path, detect_types=sqlite3.PARSE_DECLTYPES)
    dfp = pd.read_sql_query("SELECT * FROM Program", db)
    dfm = pd.read_sql_query("SELECT * FROM Meta", db)

    idx = dfp["model_name"] == model_name

    code = dfp[idx]["code"].values[0]
    stan_file_path = programs_dir / model_name / (model_name + ".stan")
    write_stan_model(code, stan_file_path)

    data = dfp[idx]["data"].values[0]
    data_file_path = programs_dir / model_name / (model_name + ".json")
    write_stan_data(data, data_file_path)

    stan_file = str(stan_file_path)
    data_file = str(data_file_path)
    model = cmdstanpy.CmdStanModel(stan_file=stan_file)

    info = dfm[idx].to_dict(orient="index")
    k = list(info.keys())[0]
    info = info[k]
    fit = model.sample(
        data=data_file,
        iter_sampling=int(info["iter_sampling"]),
        iter_warmup=int(info["iter_warmup"]),
        chains=int(info["chains"]),
        parallel_chains=int(min(cpu_count() - 1, info["parallel_chains"])),
        thin=int(info["thin"]),
        seed=int(info["seed"]),
        adapt_delta=info["adapt_delta"],
        max_treedepth=int(info["max_treedepth"]),
        sig_figs=int(info["sig_figs"]),
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

    programs_folder = pathlib.Path().resolve() / "programs"
    run_model(model_name, programs_dir=programs_folder, database_path=database)

    db.close()
    print("Done.")


def run_all(args: dict):
    print(f"Running and storing reference draws for all programs in database...")

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
    programs_folder = pathlib.Path().resolve() / "programs"

    model_names = dfprogram["model_name"].values

    if not args["overwrite"]:
        cursor = db.cursor()
        tables = cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        table_names = set([tbl[0] for tbl in tables])
        model_names = set(model_names).difference(table_names)

    with Pool(args["cpus"]) as p:
        f = functools.partial(
            run_model, programs_dir=programs_folder, database_path=database
        )
        p.map(f, model_names)

    db.close()
    print("Done.")
