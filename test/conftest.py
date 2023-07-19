import pytest
import sqlite3
import pathlib
import shutil

import minipdb

cwd = pathlib.Path().resolve() / "test"
database = cwd / "test.sqlite"


def pytest_configure(config):
    minipdb.tools.initialize_empty_db(database)


def pytest_unconfigure(config):
    database.unlink()
    shutil.rmtree(str(cwd.parent / "programs"))
