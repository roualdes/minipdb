import pathlib
import sys
import cmdstanpy
import pathlib
import json
import string

import numpy as np

def error_message(var, toml, msg):
    return f'Variable {var} in {toml} must ' + msg


def model_name_check(toml, tomlfile):
    if 'model_name' not in toml:
        sys.exit(f'No model name specified, please specify model_name in {tomlfile} and add again.')
    else:
        if not toml['model_name'][0].isupper():
            raise ValueError(error_message('model_name', tomlfile, 'begin with an upper case ACII character'))

        allowed_chars = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + '-' + '_')
        if not set(toml['model_name']) <= allowed_chars:
            raise ValueError(error_message('model_name', tomlfile, 'contain only ACII characters, digits, _-'))


def stan_file_check(toml, tomlfile):
    if 'stan_file' not in toml:
        sys.exit(f'No Stan file specified, please specify stan_file in {tomlfile} and add again.')
    else:
        if type(toml['stan_file']) is not str:
            raise TypeError(error_message('stan_file', tomlfile, 'be a string.'))

        f = pathlib.Path(tomlfile).parent / toml['stan_file']
        if not f.is_file():
            raise ValueError(error_message('stan_file', tomlfile, 'exist.'))


def json_data_check(toml, tomlfile):
    if 'json_data' not in toml:
        sys.exit('No JSON data specified, please specify json_data in {tomlfile} and add again.')
    else:
        if type(toml['json_data']) is not str:
            raise TypeError(error_message('json_data', tomlfile, 'be a string.'))

        f = pathlib.Path(tomlfile).parent / toml['json_data']
        if not f.is_file():
            raise ValueError(error_message('json_data', tomlfile, 'exist.'))


def iter_sampling_check(toml, tomlfile):
    if 'iter_sampling' not in toml['meta']:
        toml['iter_sampling'] = 10_000
    else:
        if type(toml['meta']['iter_sampling']) is not int:
            raise TypeError(error_message('iter_sampling', tomlfile, 'be an integer.'))

        if not 2_000 <= toml['meta']['iter_sampling'] or not toml['meta']['iter_sampling'] <= 1_000_000:
            raise ValueError(error_message('iter_sampling', tomlfile, 'be an integer in 2_000:1_000_000.'))

        toml['iter_sampling'] = toml['meta']['iter_sampling']


def iter_warmup_check(toml, tomlfile):
    if 'iter_warmup' not in toml['meta']:
        toml['iter_warmup'] = toml['meta']['iter_sampling']
    else:
        if type(toml['meta']['iter_warmup']) is not int:
            raise TypeError(error_message('iter_warmup', tomlfile, 'be an integer.'))

        if not 2_000 <= toml['meta']['iter_warmup'] or not toml['meta']['iter_warmup'] <= 1_000_000:
            raise ValueError(error_message('iter_sampling', tomlfile, 'be an integer in 2_000:1_000_000.'))

        toml['iter_warmup'] = toml['meta']['iter_warmup']


def chains_check(toml, tomlfile):
    if 'chains' not in toml['meta']:
        toml['chains'] = 10
    else:
        if type(toml['meta']['chains']) is not int:
            raise TypeError(error_message('chains', tomlfile, 'be an integer.'))

        if not 1 <= toml['meta']['chains']:
            raise ValueError(error_message('chains', tomlfile, 'be an integer greater than zero.'))

        toml['chains'] = toml['meta']['chains']


def parallel_chains_check(toml, tomlfile):
    if 'parallel_chains' not in toml['meta']:
        toml['parallel_chains'] = toml['chains']
    else:
        if type(toml['meta']['parallel_chains']) is not int:
            raise TypeError(error_message('parallel_chains', tomlfile, 'be an integer.'))

        if not 1 <= toml['meta']['parallel_chains'] or not toml['meta']['parallel_chains'] <= toml['chains']:
            raise ValueError(error_message('parallel_chains', tomlfile, f'be an integer in 1:{toml["chains"]}'))

        toml['parallel_chains'] = toml['meta']['parallel_chains']


def thin_check(toml, tomlfile):
    if 'thin' not in toml['meta']:
        toml['thin'] = 1
    else:
        if type(toml['meta']['thin']) is not int:
            raise TypeError(error_message('thin', tomlfile, 'be an integer.'))

        if not 1 <= toml['meta']['thin'] or not toml['meta']['thin'] <= toml['iter_sampling']:
            raise ValueError(error_message('thin', tomlfile, f'be an integer between 1 and {toml["iter_sampling"]}.'))

        toml['thin'] = toml['meta']['thin']


def seed_check(toml, tomlfile):
    if 'seed' not in toml['meta']:
        toml['seed'] = random.randint(0, 4_294_967_295)
    else:
        if type(toml['meta']['seed']) is not int:
            raise TypeError(error_message('seed', tomlfile, 'be an integer.'))

        if not 0 <= toml['meta']['seed'] or not toml['meta']['seed'] <= 4_294_967_295:
            raise ValueError(error_message('seed', tomlfile, 'be an integer in 0:4_294_967_295.'))

        toml['seed'] = toml['meta']['seed']


def adapt_delta_check(toml, tomlfile):
    if 'adapt_delta' not in toml['meta']:
        toml['adapt_delta'] = 0.8
    else:
        if type(toml['meta']['adapt_delta']) is not float:
            raise TypeError(error_message('adapt_delta', tomlfile, 'be a float.'))

        if not 0 < toml['meta']['adapt_delta'] or not toml['meta']['adapt_delta'] < 1:
            raise ValueError(error_message('adapt_delta', tomlfile, 'be a float in (0, 1).'))

        toml['adapt_delta'] = toml['meta']['adapt_delta']


def max_treedepth_check(toml, tomlfile):
    if 'max_treedepth' not in toml['meta']:
        toml['max_treedepth'] = 10
    else:
        if type(toml['meta']['max_treedepth']) is not int:
            raise TypeError(error_message('max_treedepth', tomlfile, 'be an integer.'))

        if not 1 <= toml['meta']['max_treedepth'] or not toml['meta']['max_treedepth'] <= 20:
            raise ValueError(error_message('max_treedepth', tomlfile, 'be an integer in 1:20.'))

        toml['max_treedepth'] = toml['meta']['max_treedepth']


def sig_figs_check(toml, tomlfile):
    if 'sig_figs' not in toml['meta']:
        toml["sig_figs"] = 16
    else:
        if type(toml['meta']['sig_figs']) is not int:
            raise TypeError(error_message('sig_figs', tomlfile, 'be an integer.'))

        if not 1 <= toml['meta']['sig_figs'] or not toml['meta']['sig_figs'] <= 18:
            raise ValueError(error_message('sig_figs', tomlfile, 'be an integer in 1:18.'))

        toml['sig_figs'] = toml['meta']['sig_figs']


def init_checks(toml, tomlfile):
    model_name_check(toml, tomlfile)
    stan_file_check(toml, tomlfile)
    json_data_check(toml, tomlfile)
    iter_sampling_check(toml, tomlfile)
    iter_warmup_check(toml, tomlfile)
    chains_check(toml, tomlfile)
    parallel_chains_check(toml, tomlfile)
    thin_check(toml, tomlfile)
    seed_check(toml, tomlfile)
    adapt_delta_check(toml, tomlfile)
    max_treedepth_check(toml, tomlfile)
    sig_figs_check(toml, tomlfile)


def table_exists(args, database):
    tbl_exists = False
    try:
        cursor = database.cursor()
        tables = cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        for table in tables:
            if args['model_name'] == table:
                tbl_exists = True
                break
    except:
        return False
    return tbl_exists
