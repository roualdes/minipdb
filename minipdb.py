import argparse
import pathlib
import sqlite3
import tomllib
import sys
import random
import string
import json
import cmdstanpy

import numpy as np
import pandas as pd

from multiprocessing import Pool, cpu_count


def error_message(var, toml, msg):
    return f'Variable {var} in {toml} must ' + msg

def init_checks(toml, tomlfile):
    if 'model_name' not in toml:
        sys.exit(f'No model name specified, please specify model_name in {tomlfile} and add again.')
    else:
        if not toml['model_name'][0].isupper():
            raise TypeError(error_message('model_name', tomlfile, 'begin with an upper case ACII character'))

        allowed_chars = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + '-' + '_')
        if not set(toml['model_name']) <= allowed_chars:
            raise ValueError(error_message('model_name', tomlfile, 'contain only ACII characters, digits, _-'))


    if 'stan_file' not in toml:
        sys.exit(f'No Stan file specified, please specify stan_file in {tomlfile} and add again.')
    else:
        if type(toml['stan_file']) is not str:
            raise TypeError(error_message('stan_file', tomlfile, 'be a string.'))

        f = pathlib.Path(toml['stan_file'])
        if not f.is_file():
            raise ValueError(error_message('stan_file', tomlfile, 'exist.'))


    if 'json_data' not in toml:
        sys.exit('No JSON data specified, please specify json_data in {tomlfile} and add again.')
    else:
        if type(toml['json_data']) is not str:
            raise TypeError(error_message('json_data', tomlfile, 'be a string.'))

        f = pathlib.Path(toml['json_data'])
        if not f.is_file():
            raise ValueError(error_message('json_data', tomlfile, 'exist.'))


    if 'iter_sampling' not in toml['meta']:
        toml['iter_sampling'] = 10_000
    else:
        if type(toml['meta']['iter_sampling']) is not int:
            raise TypeError(error_message('iter_sampling', tomlfile, 'be an integer.'))

        if not 2_000 <= toml['meta']['iter_sampling'] or not toml['meta']['iter_sampling'] <= 1_000_000:
            raise ValueError(error_message('iter_sampling', tomlfile, 'be an integer in 2_000:1_000_000.'))

        toml['iter_sampling'] = toml['meta']['iter_sampling']


    if 'iter_warmup' not in toml['meta']:
        toml['iter_warmup'] = toml['meta']['iter_sampling']
    else:
        if type(toml['meta']['iter_warmup']) is not int:
            raise TypeError(error_message('iter_warmup', tomlfile, 'be an integer.'))

        if not 2_000 <= toml['meta']['iter_warmup'] or not toml['meta']['iter_warmup'] <= 1_000_000:
            raise ValueError(error_message('iter_sampling', tomlfile, 'be an integer in 2_000:1_000_000.'))

        toml['iter_warmup'] = toml['meta']['iter_warmup']


    if 'chains' not in toml['meta']:
        toml['chains'] = 10
    else:
        if type(toml['meta']['chains']) is not int:
            raise TypeError(error_message('chains', tomlfile, 'be an integer.'))

        if not 1 <= toml['meta']['chains']:
            raise ValueError(error_message('chains', tomlfile, 'be an integer greater than zero.'))

        toml['chains'] = toml['meta']['chains']


    if 'parallel_chains' not in toml['meta']:
        toml['parallel_chains'] = toml['chains']
    else:
        if type(toml['meta']['parallel_chains']) is not int:
            raise TypeError(error_message('chains', tomlfile, 'be an integer.'))

        if not 1 <= toml['meta']['parallel_chains'] or not toml['meta']['parallel_chains'] <= toml['meta']['chains']:
            raise ValueError(error_message('parallel_chains', tomlfile, f'be an integer in 1:{toml["meta"]["chains"]}'))

        toml['parallel_chains'] = toml['meta']['parallel_chains']


    if 'thin' not in toml['meta']:
        toml['thin'] = 1
    else:
        if type(toml['meta']['thin']) is not int:
            raise TypeError(error_message('thin', tomlfile, 'be an integer.'))

        if not 1 <= toml['meta']['thin'] or not toml['meta']['thin'] <= toml['meta']['iter_sampling']:
            raise ValueError(error_message('thin', tomlfile, f'be an integer between 1 and {toml["meta"]["iter_sampling"]}.'))

        toml['thin'] = toml['meta']['thin']


    if 'seed' not in toml['meta']:
        toml['seed'] = random.randint(0, 4_294_967_295)
    else:
        if type(toml['meta']['seed']) is not int:
            raise TypeError(error_message('seed', tomlfile, 'be an integer.'))

        if not 0 <= toml['meta']['seed'] or not toml['meta']['seed'] <= 4_294_967_295:
            raise ValueError(error_message('seed', tomlfile, 'be an integer in 0:4_294_967_295.'))

        toml['seed'] = toml['meta']['seed']


    if 'adapt_delta' not in toml['meta']:
        toml['adapt_delta'] = 0.8
    else:
        if type(toml['meta']['adapt_delta']) is not float:
            raise TypeError(error_message('adapt_delta', tomlfile, 'be a float.'))

        if not 0 < toml['meta']['adapt_delta'] or not toml['meta']['adapt_delta'] < 1:
            raise ValueError(error_message('adapt_delta', tomlfile, 'be a float in (0, 1).'))

        toml['adapt_delta'] = toml['meta']['adapt_delta']


    if 'max_treedepth' not in toml['meta']:
        toml['max_treedepth'] = 10
    else:
        if type(toml['meta']['max_treedepth']) is not int:
            raise TypeError(error_message('max_treedepth', tomlfile, 'be an integer.'))

        if not 1 <= toml['meta']['max_treedepth'] or not toml['meta']['max_treedepth'] <= 20:
            raise ValueError(error_message('max_treedepth', tomlfile, 'be an integer in 1:20.'))

        toml['max_treedepth'] = toml['meta']['max_treedepth']


    if 'sig_figs' not in toml['meta']:
        toml["sig_figs"] = 16
    else:
        if type(toml['meta']['sig_figs']) is not int:
            raise TypeError(error_message('sig_figs', tomlfile, 'be an integer.'))

        if not 1 <= toml['meta']['sig_figs'] or not toml['meta']['sig_figs'] <= 18:
            raise ValueError(error_message('sig_figs', tomlfile, 'be an integer in 1:18.'))

        toml['sig_figs'] = toml['meta']['sig_figs']

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
    tomlfile = args.toml
    with open(tomlfile, 'rb') as f:
        toml = tomllib.load(f)

    init_checks(toml, tomlfile)

    print(f'Initializting {toml["model_name"]}...')
    database = args.database
    db = sqlite3.connect(database)

    exists_in_program = False
    try:
        dfprogram = pd.read_sql_query('SELECT * FROM Program', db)
        exists_in_program = toml['model_name'] in dfprogram['model_name'].values
    except:
        pass

    exists_in_meta = False
    try:
        dfmeta = pd.read_sql_query('SELECT * FROM Meta', db)
        exists_in_meta = toml['model_name'] in dfmeta['model_name'].values
    except:
        pass

    exists_in_diagnostics = False
    try:
        dfdiagnostics = pd.read_sql_query(f'SELECT * FROM {toml["model_name"]}_diagnostics', db)
        exists_in_diagnostics = toml['model_name'] in dfdiagnostics['model_name'].values
    except:
        pass

    exists_in_metric = False
    try:
        dfmetric = pd.read_sql_query(f'SELECT * FROM {toml["model_name"]}_metric', db)
        exists_in_metric = toml['model_name'] in dfmetric['model_name'].values
    except:
        pass

    exists = [exists_in_program, exists_in_meta, exists_in_diagnostics, exists_in_metric]
    if sum(exists) == 1:
        sys.exit(f'A Stan program with model name {toml["model_name"]} exists in some {args.database} table.  Something wrong happened.  Fix it.')

    if all(exists):
        sys.exit(f'A Stan program with model name {toml["model_name"]} already exists in minipdb.sqlite, please ensure you are adding a uniqur Stan program and if so change the nodel name.')

    with open(toml['stan_file'], 'r') as f:
        toml['code'] = ''.join(f.readlines())

    with open(toml['json_data'], 'r') as f:
        toml['data'] = ''.join(f.readlines())

    db.execute('INSERT INTO Program VALUES(:model_name, :code, :data)', toml)
    db.execute('INSERT INTO Meta VALUES(:model_name, :iter_warmup, :iter_sampling, :chains, :parallel_chains, :thin, :seed, :adapt_delta, :max_treedepth, :sig_figs)', toml)

    db.commit()
    db.close()
    print('Done.')



def table_exists(database):
    tbl_exists = False
    try:
        cursor = database.cursor()
        tables = cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        for table in tables:
            if args.model == table:
                tbl_exists = True
                break
    except:
        return False
    return tbl_exists


"""
Run a Stan program using CmdStanPy.  The Stan model code and data are pulled
from database table Program.  The sampling algorithm parameters are pulled from
database table Meta.  As such, the Stan program must be :command:`init` first.
"""
def run_model(model_name: str, models_dir: str = "", dfp: str  = "", dfm: str = "", db: str = ""):

    idx = dfp['model_name'] == model_name
    code = dfp[idx]['code'][0]

    model_dir = pathlib.Path(models_dir) / model_name
    pathlib.Path(model_dir).mkdir(parents = True, exist_ok = True)
    stan_file_path = model_dir / (model_name + '.stan')
    with open(stan_file_path, 'w') as f:
        f.write(code)

    data = json.loads(dfp[idx]['data'][0])
    data_file_path = model_dir / (model_name + '.json')
    cmdstanpy.write_stan_json(data_file_path, data)

    stan_file = str(stan_file_path)
    data_file = str(data_file_path)
    model = cmdstanpy.CmdStanModel(stan_file = stan_file)

    info = dfm[idx].to_dict(orient = 'index')[0]
    fit = model.sample(data = data_file,
                       iter_sampling = info['iter_sampling'],
                       iter_warmup = info['iter_warmup'],
                       chains = info['chains'],
                       parallel_chains = info['parallel_chains'],
                       thin = info['thin'],
                       seed = info['seed'],
                       adapt_delta = info['adapt_delta'],
                       max_treedepth = info['max_treedepth'],
                       sig_figs = info['sig_figs'])

    df = fit.draws_pd()
    df.to_sql(f'{model_name}', db, if_exists = 'replace', index = False)

    M = fit.metric.T
    col_names = ['chain_' + str(c + 1) for c in range(np.shape(M)[1])]
    dfmetric = pd.DataFrame(M, columns = col_names)
    dfmetric.to_sql(f'{model_name}_metric', db, if_exists = 'replace', index = False)


"""
Run an already :command:`init`ed Stan program and store the resulting reference draws.
"""
def run(args: dict):
    model_name = args.model

    if args.all_models:
        print(f'Running and storing reference draws for all models in database...')
    else:
        print(f'Running model {model_name} and storing reference draws...')

    database = args.database
    db = sqlite3.connect(database)

    dfprogram = pd.read_sql_query('SELECT * FROM Program', db)
    exists_in_program = model_name in dfprogram['model_name'].values

    dfmeta = pd.read_sql_query('SELECT * FROM Meta', db)
    exists_in_meta = model_name in dfmeta['model_name'].values

    if sum([exists_in_program, exists_in_meta]) == 0:
        sys.exit(f'Program {args.model} does not exists in database, please init first.')

    if table_exists(db) and args.overwrite:
        print('overwrite turned on...')
        if not args.yes:
            ans = input(f'This operation will overwrite all previous reference draws.\n\nType Yes to continue: ')
            if ans != 'Yes':
                sys.exit('Run canceled.')

    model_folder = pathlib.Path().resolve() / 'models'

    def runmodel(model_name):
        run_model(model_name,
                  models_dir = model_folder,
                  dfp = dfprogram,
                  dfm = dfmeta,
                  db = db)

    if args.all_models:
        model_names = dfprogram['model_name']
        with Pool(args.cpus) as p:
            p.map(runmodel, model_names)
    else:
        runmodel(args.model)

    db.close()
    print('Done.')


def update(args: dict):
    print(f'Updating meta information using information in {args.toml}...')

    tomlfile = args.toml
    with open(tomlfile, 'rb') as f:
        toml = tomllib.load(f)

    meta = {k: v for k, v in toml['meta'].items()}
    init_checks(toml, tomlfile)

    for k in meta.keys():
        meta[k] = toml[k]

    changes = str(meta).replace('\'', '"').replace(":", " =").replace("{", "").replace("}", "")

    database = args.database
    db = sqlite3.connect(database)

    db.execute(f'UPDATE Meta SET {changes} WHERE "model_name" = "{toml["model_name"]}"')

    db.commit()
    db.close()
    print('Done.')


def delete(args: dict):
    ans = input(f'This operation will delete all reference draws for {args.model_name},\nand all corresponding information from minipdb.sqlite.\n\nThis operation can not be undone.\n\nAre you sure you want to proceed?\n\nType Yes to continue: ')

    if ans != 'Yes':
        sys.exit('Canceled delete.')

    database = args.database
    db = sqlite3.connect(database)
    print(f'deleting {args.model_name}...')

    exists_in_program = False
    try:
        dfprogram = pd.read_sql_query('SELECT * FROM Program', db)
        exists_in_program = args.model_name in dfprogram['model_name'].values
    except:
        pass
    if exists_in_program:
        print(f'deleing {args.model_name} from table Program')
        db.execute(f'DELETE FROM Program WHERE "model_name" = "{args.model_name}"')

    exists_in_meta = False
    try:
        dfmeta = pd.read_sql_query('SELECT * FROM Meta', db)
        exists_in_meta = args.model_name in dfprogram['model_name'].values
    except:
        pass
    if exists_in_meta:
        db.execute(f'DELETE FROM Meta WHERE "model_name" = "{args.model_name}"')

    exists_in_diagnostics = False
    try:
        dfdiagnostics = pd.read_sql_query(f'SELECT * FROM {args.model_name}_diagnostics', db)
        exists_in_diagnostics = args.model_name in dfdiagnostics['model_name'].values
    except:
        pass
    if exists_in_diagnostics:
        db.execute(f'DROP {args.model_name}_diagnostics')

    exists_in_metric = False
    try:
        dfmetric = pd.read_sql_query(f'SELECT * FROM {args.model_name}_metric', db)
        exists_in_metric = args.model_name in dfmetric['model_name'].values
    except:
        pass
    if exists_in_metric:
        db.execute(f'DROP {args.model}_metric')

    if table_exists(db):
        db.execute(f'DROP "{args.model}"')

    db.commit()
    db.close()
    print('Done.')


parser = argparse.ArgumentParser(
    prog='minipdb',
    description='Command line tool for managing entries of a minipdb database.')

parser.add_argument('-d',
                    '--database',
                    default = 'minipdb.sqlite',
                    help = 'Specify database to use; defaults to minipdb.sqlite')

parser.add_argument('-y',
                    '--yes',
                    default = False,
                    action = 'store_true',
                    help = 'Automatic yes to prompts. Assume "Yes" as answer to all prompts and run non-interactively. Defaults to No.')

parser.add_argument('-c',
                    '--cpus',
                    type = int,
                    default = cpu_count() - 1,
                    help = 'Number of CPU processes to use while running models.  Defaults to multiprocessing.cpu_count() - 1')

parser.add_argument('-a',
                    '--all_models',
                    default = False,
                    action = 'store_true',
                    help = 'Run all models in database.')

subparsers = parser.add_subparsers(required = True)


cmd_init = subparsers.add_parser('init',
                                help = 'initialize a Stan program (source code and data only) into database')

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


cmd_update = subparsers.add_parser('update',
                                 help = 'update model pointed to by and using the information contained in TOML file')

cmd_update.add_argument('toml',
                        help = 'update model using the information contained in the specified TOML file')

cmd_update.set_defaults(func = update)

cmd_delete = subparsers.add_parser('delete',
                                   help = 'delete the table of reference draws and the corresponding entries in all tables')

cmd_delete.add_argument('model_name',
                        help = 'unique model_name for an already added Stan program')

cmd_delete.set_defaults(func = delete)

cmd_reinit = subparsers.add_parser('re-init',
                                   help = 're-initialize the sampling algorithm information in Meta')

def reinit(args):
    print('do stuff')

cmd_reinit.set_defaults(func = reinit)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
