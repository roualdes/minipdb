import pathlib
import random
import json
import datetime
import sqlite3

from posteriordb import PosteriorDatabase

pdb = PosteriorDatabase(Path('~/posteriordb'))
model_names = pdb.posterior_names()
db = sqlite3.connect(database)

# create database here

for model_name in model_names:
    model = {}
    meta = {}
    posterior = pdb.posterior(model_name)

    # does info below break if reference draws don't exist?
    # if not, need a way to check for reference draws
    if reference_draws_exist:
        model['model_name'] = posterior.name
        model['code'] = posterior.model.code('stan')
        model['last_run'] = datetime.datetime.min
        model['description'] = posterior.model.information['description']
        model['data'] = json.dumps(posterior.data.values())

        db.execute('INSERT INTO Program VALUES(:model_name, :description, :code, :data, :last_run)', model)
        db.commit()

        info = posterior.reference_draws_info()['method_arguments']
        meta['iter_sampling'] = info.get('iter', 10_000)
        meta['iter_warmup'] = info.get('warmup', meta['iter_sampling'])
        meta['chains'] = info.get('chains', 10)
        meta['parallel_chains'] = info.get('parallel_chains', meta['chains'])
        meta['thin'] = info.get('thin', 1)
        meta['seed'] = info.get('seed', random.randint(0, 4_294_967_295))
        meta['adapt_delta'] = info.get('control', 0.8).get('adapt_delta', 0.8)
        meta['max_treedepth'] = info.get('control', 10).get('adapt_delta', 10)

        db.execute('INSERT INTO Meta VALUES(:iter_sampling, :iter_warmup, :chains, :parallel_chains, :thin, :seed, :adapt_delta, :max_treedepth)', meta)
        db.commit()

db.close()
