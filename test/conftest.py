import pytest
import sqlite3
import pathlib
import shutil

def pytest_configure(config):
    cwd = pathlib.Path().resolve() / 'test'
    database = cwd / 'test.sqlite'
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    db.execute('CREATE TABLE Program ("model_name" TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, data TEXT NOT NULL, "last_run" TIMESTAMP)')
    db.commit()

    db.execute('CREATE TABLE Meta ("model_name" TEXT PRIMARY KEY, "iter_sampling" INTEGER NOT NULL, "iter_warmup" INTEGER NOT NULL, chains INTEGER NOT NULL, "parallel_chains" INTEGER NOT NULL, thin INTEGER NOT NULL, seed INTEGER NOT NULL, "adapt_delta" REAL NOT NULL, "max_treedepth" INTEGER NOT NULL, "sig_figs" INTEGER NOT NULL)')
    db.commit()

    db.close()


def pytest_unconfigure(config):
    cwd = pathlib.Path().resolve() / 'test'
    database = cwd / 'test.sqlite'
    database.unlink()
    shutil.rmtree(str(cwd.parent / 'models'))
