import sqlite3
import tomllib
import sys
import pathlib
import datetime

from .tools import init_checks, table_exists

"""
Initialize a Stan program into the database, without storing reference draws.

A row is added to both of the database tables Program and Meta.  The row
inserted into Program will contain the model name, the .stan file code, and the
JSON data.  The row inserted into Meta will contain all the necessary sampling
parameters in order to create the reference draws.  The values within each row
is obtained from the TOML file specified at the command line.

Following initialization of a Stan program, the command :command:`run` is
neccessary to store reference draws.  Separating :command:`init` and
:command:`run` allows one to :command:`run` a Stan program and on their
preferred machine.

See also the :command:`add` which will both :command:`init` and :command:`run`
in one step.
"""
def init(args):
    tomlfile = args['toml']
    with open(tomlfile, 'rb') as f:
        toml = tomllib.load(f)

    init_checks(toml, tomlfile)

    model_name = toml['model_name']
    print(f'Initializing {model_name}...')

    parent_dir = pathlib.Path(tomlfile).parent
    database = parent_dir / args['database']
    db = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    exists_in_program = False
    try:
        dfprogram = pd.read_sql_query('SELECT * FROM Program', db)
        exists_in_program = model_name in dfprogram['model_name'].values
    except:
        pass

    exists_in_meta = False
    try:
        dfmeta = pd.read_sql_query('SELECT * FROM Meta', db)
        exists_in_meta = model_name in dfmeta['model_name'].values
    except:
        pass

    exists_in_diagnostics = False
    try:
        dfdiagnostics = pd.read_sql_query(f'SELECT * FROM {model_name}_diagnostics', db)
        exists_in_diagnostics = model_name in dfdiagnostics['model_name'].values
    except:
        pass

    exists_in_metric = False
    try:
        dfmetric = pd.read_sql_query(f'SELECT * FROM {model_name}_metric', db)
        exists_in_metric = model_name in dfmetric['model_name'].values
    except:
        pass

    exists = [exists_in_program, exists_in_meta, exists_in_diagnostics, exists_in_metric]
    if sum(exists) == 1:
        sys.exit(f'A Stan program with model name {model_name} exists in some {args["database"]} table.  Something wrong happened.  Fix it.')

    if all(exists):
        sys.exit(f'A Stan program with model name {model_name} already exists in minipdb.sqlite, please ensure you are adding a uniqur Stan program and if so change the nodel name.')

    f = parent_dir / toml['stan_file']
    with open(f, 'r') as f:
        toml['code'] = ''.join(f.readlines())

    f = parent_dir / toml['json_data']
    with open(f, 'r') as f:
        toml['data'] = ''.join(f.readlines())

    try:
        toml['last_run'] = datetime.datetime.min
        db.execute('INSERT INTO Program VALUES(:model_name, :code, :data, :last_run)', toml)
        db.commit()
    except sqlite3.IntegrityError as e:
        print(e)

    try:
        db.execute('INSERT INTO Meta VALUES(:model_name, :iter_warmup, :iter_sampling, :chains, :parallel_chains, :thin, :seed, :adapt_delta, :max_treedepth, :sig_figs)', toml)
        db.commit()
    except sqlite3.IntegrityError as e:
        print(e)

    db.close()
    print('Done.')
