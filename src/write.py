import sqlite3
import pathlib
import sys

import pandas as pd
import numpy as np

from .tools import write_stan_model, write_stan_data

"""
Write Stan programs, model and data, to file.  The directory programs will be
created and each Stan program will get its own directory named after the model.

"""


def write(args: dict):
    database = args["database"]
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    dfp = pd.read_sql_query("SELECT * FROM Program", db)

    programs_path = pathlib.Path().resolve() / "programs"
    programs_path.mkdir(exist_ok=True)

    if args["programs"]:
        programs = [s.strip() for s in args["programs"].split(",")]
    else:
        programs = dfp["model_name"].values

    if not args["yes"]:
        ans = input(
            f'This operation will overwrite the Stan programs {", ".join(programs)}.\n\nThis operation can not be undone.\n\nAre you sure you want to proceed?\n\nType Yes to continue: '
        )
        if ans != "Yes":
            sys.exit("Canceled write.")

    print("Writing Stan programs...")
    for program in programs:
        idx = dfp["model_name"] == program
        if not np.any(idx):
            continue

        print(program)
        code = dfp[idx]["code"].values[0]
        stan_file_path = programs_path / program / (program + ".stan")
        write_stan_model(code, stan_file_path)

        data = dfp[idx]["data"].values[0]
        data_file_path = programs_path / program / (program + ".json")
        write_stan_data(data, data_file_path)

    print("Done.")
