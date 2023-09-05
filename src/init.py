import pathlib
import sys

from .tools import download_db, initialize_empty_db, insert_posteriordb

"""
Initialize a MiniPDB database by downloading minipdb.sqlite or setting up an
empty database with the appropriate tables
"""


def init(args):
    database = pathlib.Path(args["database"])
    database.parent.mkdir(exist_ok=True)
    if database.is_file():
        if not args["yes"]:
            ans = input(
                f"File {str(database)} already exists.\n\nDo you want to delete it and proceed?\n\nType Yes to continue: "
            )
            if ans != "Yes":
                sys.exit("Canceled download.")
        database.unlink()

    if args["download"]:
        print("Downloading database...")
        download_db(database)
    elif args["posteriordb"]:
        print("Initializing database from PosteriorDB...")

        initialize_empty_db(database)
        insert_posteriordb(args["posteriordb"], database)
    else:
        print("Initializing empty database...")
        initialize_empty_db(database)
    print("Done.")
