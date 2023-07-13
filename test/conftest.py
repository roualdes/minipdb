import pytest
import sqlite3
import pathlib
import shutil

import minipdb


def pytest_configure(config):
    cwd = pathlib.Path().resolve() / "test"
    database = cwd / "test.sqlite"
    minipdb.tools.initialize_db(database)


def pytest_unconfigure(config):
    cwd = pathlib.Path().resolve() / "test"
    database = cwd / "test.sqlite"
    database.unlink()
    shutil.rmtree(str(cwd.parent / "models"))
