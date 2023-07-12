import sqlite3
import tomllib

from .checks import init_checks


def update(args: dict):
    tomlfile = args["toml"]
    print(f"Updating meta information using information in {tomlfile}...")

    with open(tomlfile, "rb") as f:
        toml = tomllib.load(f)

    meta = {k: v for k, v in toml["meta"].items()}
    init_checks(toml, tomlfile)

    for k in meta.keys():
        meta[k] = toml[k]

    changes = (
        str(meta).replace("'", '"').replace(":", " =").replace("{", "").replace("}", "")
    )

    database = args["database"]
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    model_name = toml["model_name"]
    db.execute(f'UPDATE Meta SET {changes} WHERE "model_name" = "{model_name}"')
    db.commit()

    db.close()
    print("Done.")
