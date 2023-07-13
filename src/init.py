import pathlib
import sys

from .tools import download_db, initialize_db

"""
Initialize a MiniPDB database by downloading minipdb.sqlite or setting up an
empty database with the appropriate tables
"""


def init(args):
    database = pathlib.Path(args["database"])
    if args["download"]:
        print("Downloading database...")
        database.parent.mkdir(exist_ok = True)
        if database.is_file():
            if not args["yes"]:
                ans = input(
                    f"File {str(database)} already exists.\n\nDo you want to delete it and proceed?\n\nType Yes to continue: "
                )
                if ans != "Yes":
                    sys.exit("Canceled download.")
        database.unlink()
        download_db(database)
    else:
        print("Initializing database...")
        initialize_db(database)
    print("Done.")
