import pathlib
import random
import json
import datetime
import sqlite3

from posteriordb import PosteriorDatabase

pdb = PosteriorDatabase(pathlib.Path('/Users/ez/posteriordb/posterior_database'))
model_names = pdb.posterior_names()
db = sqlite3.connect('/Users/ez/.minipdb/minipdb_py.sqlite')

# create database here

for model_name in model_names:
    model = {}
    meta = {}
    posterior = pdb.posterior(model_name)

    reference_draws_exist = False
    try:
        posterior.reference_draws()
        reference_draws_exist = True
    except:
        pass

    if reference_draws_exist:
        model['model_name'] = posterior.name
        model['code'] = posterior.model.code('stan')
        model['last_run'] = datetime.datetime.min
        model['data'] = json.dumps(posterior.data.values())

        db.execute('INSERT INTO Program VALUES(:model_name, :description, :code, :data, :last_run)', model)
        db.commit()

        info = posterior.reference_draws_info()['inference']['method_arguments']
        meta['iter_sampling'] = info.get('iter', 10_000)
        meta['iter_warmup'] = info.get('warmup', meta['iter_sampling'])
        meta['chains'] = info.get('chains', 10)
        meta['parallel_chains'] = info.get('parallel_chains', meta['chains'])
        meta['thin'] = info.get('thin', 1)
        meta['seed'] = info.get('seed', random.randint(0, 4_294_967_295))
        meta['adapt_delta'] = info.get('control', 0.8).get('adapt_delta', 0.8)
        meta['max_treedepth'] = info.get('control', 10).get('max_treedepth', 10)

        db.execute('INSERT INTO Meta VALUES(:iter_sampling, :iter_warmup, :chains, :parallel_chains, :thin, :seed, :adapt_delta, :max_treedepth)', meta)
        db.commit()

db.close()
