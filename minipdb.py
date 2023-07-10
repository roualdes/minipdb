import argparse
import pathlib
import sqlite3
import tomllib
import sys
import random
import string
import pandas as pd


def error_message(var, toml, msg):
    return f'Variable {var} in {toml} must ' + msg

def init_checks(meta):
    if 'model_name' not in meta:
        sys.exit(f'No model name specified, please specify model_name in {args.toml} and add again.')
    else:
        if not meta['model_name'][0].isupper():
            raise TypeError(error_message('model_name', args.toml, 'begin with an upper case ACII character'))

        allowed_chars = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + '-' + '_')
        if not set(meta['model_name']) <= allowed_chars:
            raise ValueError(error_message('model_name', args.toml, 'contain only ACII characters, digits, _-'))


    if 'stan_file' not in meta:
        sys.exit(f'No Stan file specified, please specify stan_file in {args.toml} and add again.')
    else:
        if type(meta['stan_file']) is not str:
            raise TypeError(error_message('stan_file', args.toml, 'be a string.'))

        f = pathlib.Path(meta['stan_file'])
        if not f.is_file():
            raise ValueError(error_message('stan_file', args.toml, 'exist.'))


    if 'json_data' not in meta:
        sys.exit('No JSON data specified, please specify json_data in {args.toml} and add again.')
    else:
        if type(meta['json_data']) is not str:
            raise TypeError(error_message('json_data', args.toml, 'be a string.'))

        f = pathlib.Path(meta['json_data'])
        if not f.is_file():
            raise ValueError(error_message('json_data', args.toml, 'exist.'))


    if 'iter_sampling' not in meta:
        meta['iter_sampling'] = 10_000
    else:
        if meta['iter_sampling'] is not int:
            raise TypeError(error_message('iter_sampling', args.toml, 'be an integer.'))

        if not 2_000 <= meta['iter_sampling'] or not meta['iter_sampling'] <= 1_000_000:
            raise ValueError(error_message('iter_sampling', args.toml, 'be an integer in 2_000:1_000_000.'))


    if 'iter_warmup' not in meta:
        meta['iter_warmup'] = meta['iter_sampling']
    else:
        if type(meta['iter_warmup']) is not int:
            raise TypeError(error_message('iter_warmup', args.toml, 'be an integer.'))

        if not 2_000 <= meta['iter_warmup'] or not meta['iter_warmup'] <= 1_000_000:
            raise ValueError(error_message('iter_sampling', args.toml, 'be an integer in 2_000:1_000_000.'))


    if 'chains' not in meta:
        meta['chains'] = 10
    else:
        if type(meta['chains']) is not int:
            raise TypeError(error_message('chains', args.toml, 'be an integer.'))

        if not 1 <= meta['chains']:
            raise ValueError(error_message('chains', args.toml, 'be an integer greater than zero.'))


    if 'parallel_chains' not in meta:
        meta['parallel_chains'] = meta['chains']
    else:
        if type(meta['parallel_chains']) is not int:
            raise TypeError(error_message('chains', args.toml, 'be an integer.'))

        if not 1 <= meta['parallel_chains'] or not meta['parallel_chains'] <= meta['chains']:
            raise ValueError(error_message('parallel_chains', args.toml, f'be an integer in 1:{meta["chains"]}'))


    if 'thin' not in meta:
        meta['thin'] = 10
    else:
        if type(meta['thin']) is not int:
            raise TypeError(error_message('thin', args.toml, 'be an integer.'))

        if not 1 <= meta['thin'] or not meta['thin'] <= meta['iter_sampling']:
            raise ValueError(error_message('thin', args.toml, f'be an integer between 1 and {meta["iter_sampling"]}.'))


    if 'seed' not in meta:
        meta['seed'] = random.randint(0, 4_294_967_295)
    else:
        if type(meta['seed']) is not int:
            raise TypeError(error_message('seed', args.toml, 'be an integer.'))

        if not 0 <= meta['seed'] or not meta['seed'] <= 4_294_967_295:
            raise ValueError(error_message('seed', args.toml, 'be an integer in 0:4_294_967_295.'))


    if 'adapt_delta' not in meta:
        meta['adapt_delta'] = 0.8
    else:
        if type(meta['adapt_delta']) is not float:
            raise TypeError(error_message('adapt_delta', args.toml, 'be a float.'))

        if not 0 < meta['adapt_delta'] or not meta['adapt_delta'] < 1:
            raise ValueError(error_message('adapt_delta', args.toml, 'be a float in (0, 1).'))


    if 'max_treedepth' not in meta:
        meta['max_treedepth'] = 10
    else:
        if type(meta['max_treedepth']) is not int:
            raise TypeError(error_message('max_treedepth', args.toml, 'be an integer.'))

        if not 1 <= meta['max_treedepth'] or not meta['max_treedepth'] <= 20:
            raise ValueError(error_message('max_treedepth', args.toml, 'be an integer in 1:20.'))


    if 'sig_figs' not in meta:
        meta["sig_figs"] = 16
    else:
        if type(meta['sig_figs']) is not int:
            raise TypeError(error_message('sig_figs', args.toml, 'be an integer.'))

        if not 1 <= meta['sig_figs'] or not meta['sig_figs'] <= 18:
            raise ValueError(error_message('sig_figs', args.toml, 'be an integer in 1:18.'))

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
    with open(args.toml, 'rb') as f:
        meta = tomllib.load(f)

    init_checks(meta)

    print(f'Initializting {meta["model_name"]}...')
    database = args.database
    db = sqlite3.connect(database)

    dfprogram = pd.read_sql_query('SELECT * FROM Program', db)
    exists_in_program = meta['model_name'] in dfprogram['model_name']

    dfmeta = pd.read_sql_query('SELECT * FROM Meta', db)
    exists_in_meta = meta['model_name'] in dfmeta['model_name']

    dfdiagnostics = pd.read_sql_query(f'SELECT * FROM {args.model}_diagnostics', db)
    exists_in_diagnostics = meta['model_name'] in dfdiagnostics['model_name']

    dfmetric = pd.read_sql_query(f'SELECT * FROM {args.model}_metric', db)
    exists_in_metric = meta['model_name'] in dfmetric['model_name']

    exists = [exists_in_program, exists_in_meta, exists_in_diagnostics, exists_in_metric]
    if sum(exists) == 1:
        sys.exit(f'A Stan program with model name {meta["model_name"]} exists in some {args.database} table.  Something wrong happened.  Fix it.')

    if all(exists):
        sys.exit(f'A Stan program with model name {meta["model_name"]} already exists in minipdb.sqlite, please ensure you are adding a uniqur Stan program and if so change the nodel name.')

    with open(meta['stan_file'], 'r') as f:
        meta['code'] = f.readlines()

    with open(meta['json_data'], 'r') as f:
        meta['data'] = f.readlines()

    db.execute('INSERT INTO Program VALUES(:model_name, :code, :data)', meta)
    db.execute('INSERT INTO Meta VALUES(:model_name, :iter_warmup, :iter_sampling, :chains, :parallel_chains, :thin, :seed, :adapt_delta, :max_treedepth, :sig_figs)', meta)

    db.close()
    print('Done.')


"""
Run an already :command:`init`ed Stan program and store the resulting reference draws.
"""
def run(args):
    print(f'Run model {args.model} and store reference draws.')

    if args.overwrite:
        print('overwrite turned on')

    # TODO check about overwriting
    # TODO check model has been `init`ed.


def runall(args):
    print(f'Run model {args.model} and store reference draws.')
    # TODO print informative message and double check


def update(args):
    print(f'update the model specified by and using the information contained in TOML file {args.toml}')
    # TODO think through this better


def delete(args):
    ans = input(f'This operation will delete all reference draws for {args.model},\nand all corresponding information from minipdb.sqlite.\n\nThis operation can not be undone.\n\nAre you sure you want to proceed?\n\nType Yes to continue: ')

    if ans != 'Yes':
        sys.exit('Canceled delete.')

    database = args.database
    db = sqlite3.connect(database)
    print(f'deleting {args.model}...')

    dfprogram = pd.read_sql_query('SELECT * FROM Program', db)
    exists_in_program = meta['model_name'] in dfprogram['model_name']
    if exists_in_program:
        db.execute(f'DELETE FROM Program WHERE "model_name" = "{args.model}"')

    dfmeta = pd.read_sql_query('SELECT * FROM Meta', db)
    exists_in_meta = meta['model_name'] in dfprogram['model_name']
    if exists_in_meta:
        db.execute(f'DELETE FROM Meta WHERE "model_name" = "{args.model}"')

    dfdiagnostics = pd.read_sql_query(f'SELECT * FROM {args.model}_diagnostics', db)
    exists_in_diagnostics = meta['model_name'] in dfdiagnostics['model_name']
    if exists_in_diagnostics:
        db.execute(f'DELETE FROM {args.model}_diagnostics WHERE "model_name" = "{args.model}"')

    dfmetric = pd.read_sql_query(f'SELECT * FROM {args.model}_metric', db)
    exists_in_metric = meta['model_name'] in dfmetric['model_name']
    if exists_in_metric:
        db.execute(f'DELETE FROM {args.model}_metric WHERE "model_name" = "{args.model}"')

    table_exists = False
    cursor = db.cursor()
    tables = cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
    for table in tables:
        if args.model == table:
            table_exists = True
            break

    if table_exists:
        db.execute(f'DROP "{args.model}"')

    db.close()
    print('Done.')


parser = argparse.ArgumentParser(
    prog='minipdb',
    description='Command line tool for managing entries of minipdb.sqlite',
    epilog='what is an epilog for?')

parser.add_argument('-d',
                    '--database',
                    default = 'minipdb.sqlite',
                    help = 'Specify database to use; defaults to minipdb.sqlite')

subparsers = parser.add_subparsers(required = True)


cmd_init = subparsers.add_parser('init',
                                help = 'initialize a Stan program (source code and data only) into minipdb.sqlite')

cmd_init.add_argument('toml',
                      help = 'path to a TOML file, e.g. SomeModel.toml, which details information about the Stan program to be initialized')

cmd_init.set_defaults(func = init)


cmd_run = subparsers.add_parser('run',
                                help = 'run specified model and store reference draws')

cmd_run.add_argument('model',
                     help = 'unique model_name for an already added Stan program')

cmd_run.add_argument('--overwrite',
                    help='overwrite reference draws',
                    action='store_true')

cmd_run.set_defaults(func = run)


cmd_runall = subparsers.add_parser('run_all',
                                help = 'run specified model and store reference draws')

cmd_runall.set_defaults(func = runall)


cmd_update = subparsers.add_parser('update',
                                 help = 'update model pointed to by and using the information contained in TOML file')

cmd_update.add_argument('toml',
                        help = 'update model using the information contained in the specified TOML file')

cmd_update.set_defaults(func = update)

cmd_delete = subparsers.add_parser('delete',
                                   help = 'delete the table of reference draws and the corresponding entries in all tables; this operation can not be undone')

cmd_delete.add_argument('model',
                        help = 'unique model_name for an already added Stan program')

cmd_delete.set_defaults(func = delete)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
