import argparse
import pathlib
import sqlite3
import tomllib
import sys
import random
import string
import pandas as pd

def check_type_error(expr, var, toml, msg):
    if not expr:
        raise TypeError(f'Variable {var} in {toml} must ' + msg)

def check_value_error(expr, var, toml, msg):
    if not expr:
        raise ValueError(f'Variable {var} in {toml} must ' + msg)

def add_checks(meta):
    if 'model_name' not in meta:
        sys.exit(f'No model name specified, please specify model_name in {args.toml} and add again.')
    else:
        check_type_error(meta['model_name'][0].isupper(),
                         'model_name',
                         args.toml,
                         'begin with an upper case ACII character')

        allowed_chars = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + '-' + '_')
        check_value_error(set(meta['model_name']) <= allowed_chars,
                          'model_name',
                          args.toml,
                          'contain only ACII characters, digits, _-')

    if 'stan_file' not in meta:
        sys.exit(f'No Stan file specified, please specify stan_file in {args.toml} and add again.')
    else:
        check_type_error(type(meta['stan_file']) is str,
                         'stan_file',
                         args.toml,
                         'be a string.')

        f = pathlib.Path(meta['stan_file'])
        check_value_error(f.is_file(),
                          'stan_file',
                          args.toml,
                          'exist.')

    if 'json_data' not in meta:
        sys.exit('No JSON data specified, please specify json_data in {args.toml} and add again.')
    else:
        check_type_error(type(meta['json_data']) is str,
                         'json_data',
                         args.toml,
                         'be a string.')

        f = pathlib.Path(meta['json_data'])
        check_value_error(f.is_file(),
                          'json_data',
                          args.toml,
                          'exist.')

    if 'iter_sampling' not in meta:
        meta['iter_sampling'] = 10_000
    else:
        check_type_error(type(meta['iter_sampling']) is int,
                         'iter_sampling',
                         args.toml,
                         'be an integer.')

        check_value_error(2_000 <= meta['iter_sampling'] and meta['iter_sampling'] <= 1_000_000,
                          'iter_sampling',
                          args.toml,
                          'be an integer in 2_000:1_000_000.')

    if 'iter_warmup' not in meta:
        meta['iter_warmup'] = meta['iter_sampling']
    else:
        check_type_error(type(meta['iter_warmup']) is int,
                         'iter_warmup',
                         args.toml,
                         'be an integer.')

        check_value_error(2_000 <= meta['iter_warmup'] and meta['iter_warmup'] <= 1_000_000,
                          'iter_sampling',
                          args.toml,
                          'be an integer in 2_000:1_000_000.')

    if 'chains' not in meta:
        meta['chains'] = 10
    else:
        check_type_error(type(meta['chains']) is int,
                         'chains',
                         args.toml,
                         'be an integer.')

        check_value_error(1 <= meta['chains'],
                          'chains',
                          args.toml,
                          'be an integer greater than zero.')

    if 'parallel_chains' not in meta:
        meta['parallel_chains'] = meta['chains']
    else:
        check_type_error(type(meta['parallel_chains']) is int,
                         'chains',
                         args.toml,
                         'be an integer.')

        check_value_error(1 <= meta['parallel_chains'] and meta['parallel_chains'] <= meta['chains'],
                          'parallel_chains',
                          args.toml,
                          f'be an integer in 1:{meta["chains"]}')

    if 'thin' not in meta:
        meta['thin'] = 10
    else:
        check_type_error(type(meta['thin']) is int,
                         'thin',
                         args.toml,
                         'be an integer.')

        check_value_error(1 <= meta['thin'] and meta['thin'] <= meta['iter_sampling'],
                          'thin',
                          args.toml,
                          f'be an integer between 1 and {meta["iter_sampling"]}.')

    if 'seed' not in meta:
        meta['seed'] = random.randint(0, 4_294_967_295)
    else:
        check_type_error(type(meta['seed']) is int,
                         'seed',
                         args.toml,
                         'be an integer.')

        check_value_error(0 <= meta['seed'] and meta['seed'] <= 4_294_967_295,
                          'seed',
                          args.toml,
                          'be an integer in 0:4_294_967_295.')

    if 'adapt_delta' not in meta:
        meta['adapt_delta'] = 0.8
    else:
        check_type_error(type(meta['adapt_delta']) is float,
                         'adapt_delta',
                         args.toml,
                         'be a float.')

        check_value_error(0 < meta['adapt_delta'] and meta['adapt_delta'] < 1,
                         'adapt_delta',
                         args.toml,
                         'be a float in (0, 1).')

    if 'max_treedepth' not in meta:
        meta['max_treedepth'] = 10
    else:
        check_type_error(type(meta['max_treedepth']) is int,
                         'max_treedepth',
                         args.toml,
                         'be an integer.')

        check_value_error(1 <= meta['max_treedepth'] and meta['max_treedepth'] <= 20,
                          'max_treedepth',
                          args.toml,
                          'be an integer in 1:20.')

    if 'sig_figs' not in meta:
        meta["sig_figs"] = 16
    else:
        check_type_error(type(meta['sig_figs']) is int,
                         'sig_figs',
                         args.toml,
                         'be an integer.')

        check_value_error(type(meta['sig_figs']) is int,
                          'sig_figs',
                          args.toml,
                          'be an integer in 1:18.')


def add(args):

    with open(args.toml, 'rb') as f:
        meta = tomllib.load(f)

    add_checks(meta)

    print(f'adding {meta["model_name"]}...')
    db = sqlite3.connect('minipdb.sqlite')

    dfprogram = pd.read_sql_query('SELECT * FROM Program', db)
    exists_in_program = meta['model_name'] in dfprogram['model_name']

    dfmeta = pd.read_sql_query('SELECT * FROM Meta', db)
    exists_in_meta = meta['model_name'] in dfprogram['model_name']

    if (exists_in_program and not exists_in_meta) or (not exists_in_program and exists_in_meta):
        sys.exit(f'A Stan program with model name {meta["model_name"]} exists in Program or Meta, but not the other.  Something wrong happened.  Fix it.')

    exists_in_both = exists_in_program and exists_in_meta:
    if exists_in_both:
        sys.exit(f'A Stan program with model name {meta["model_name"]} already exists in minipdb.sqlite, please ensure you are adding a uniqur Stan program and if so change the nodel name.')

    with open(meta['stan_file'], 'r') as f:
        meta['code'] = f.readlines()

    with open(meta['json_data'], 'r') as f:
        meta['data'] = f.readlines()

    db.execute('INSERT INTO Program VALUES(:model_name, :code, :data)', meta)
    db.execute('INSERT INTO Meta VALUES(:model_name, :iter_warmup, :iter_sampling, :chains, :parallel_chains, :thin, :seed, :adapt_delta, :max_treedepth, :sig_figs)', meta)

    db.close()
    print('Done.')

def run(args):
    print(f'run model {args.model} and store reference draws')

    if args.overwrite:
        print('overwrite turned on')

def update(args):
    print(f'update the model specified by and using the information contained in TOML file {args.toml}')

def delete(args):
    ans = input(f'This operation will delete all reference draws for {args.model},\nand all corresponding information from minipdb.sqlite.\n\nThis operation can not be undone.\n\nAre you sure you want to proceed?\n\nType Yes to continue: ')

    if ans == 'Yes':
        db = sqlite3.connect('minipdb.sqlite')
        print(f'deleting {args.model}...')

        dfprogram = pd.read_sql_query('SELECT * FROM Program', db)
        exists_in_program = meta['model_name'] in dfprogram['model_name']
        if exists_in_program:
            db.execute(f'DELETE FROM Program WHERE "model_name" = "{args.model}"')

        dfmeta = pd.read_sql_query('SELECT * FROM Meta', db)
        exists_in_meta = meta['model_name'] in dfprogram['model_name']
        if exists_in_meta:
            db.execute(f'DELETE FROM Meta WHERE "model_name" = "{args.model}"')

        table_exists = False
        cursor = db.cursor()
        tables = cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        for table in tables:
            if args.model == table:
                table_exists = True
        if table_exists:
            db.execute(f'DROP "{args.model}"')

        db.close()
        print('Done.')
    else:
        print('cancelled delete')


parser = argparse.ArgumentParser(
    prog='minipdb',
    description='Command line tool for managing entries of minipdb.sqlite',
    epilog='what is an epilog for?')

subparsers = parser.add_subparsers(required = True)


cmd_add = subparsers.add_parser('add',
                                help = 'add a Stan program to minipdb.sqlite')

cmd_add.add_argument('toml',
                     help = 'path to a TOML file, e.g. SomeModel.toml, which details information about the Stan program to be added')

cmd_add.set_defaults(func = add)


cmd_run = subparsers.add_parser('run',
                                help = 'run specified model and store reference draws')

cmd_run.add_argument('model',
                     help = 'unique model_name for an already added Stan program')

cmd_run.add_argument('--overwrite',
                    help='overwrite reference draws',
                    action='store_true')

cmd_run.set_defaults(func = run)

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

args = parser.parse_args()
args.func(args)
