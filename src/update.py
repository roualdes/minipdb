import sqlite3

from .checks import init_checks
from .tools import read_config


def update(args: dict):
    configfile = args["yaml"]
    config = read_config(configfile)
    print(f"Updating meta information using information in {configfile}...")

    meta = {k: v for k, v in config["meta"].items()}
    init_checks(config, configfile)

    for k in meta.keys():
        meta[k] = config[k]

    changes = (
        str(meta).replace("'", '"').replace(":", " =").replace("{", "").replace("}", "")
    )

    database = args["database"]
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    model_name = config["model_name"]
    db.execute(f'UPDATE Meta SET {changes} WHERE "model_name" = "{model_name}"')
    db.commit()

    db.close()
    print("Done.")
