from posteriordb import PosteriorDatabase
from run_tools import get_stan_files, summarize_pdb_draws

import pandas as pd
import numpy as np

import json
import pathlib
import random
import sys

def check_pdb(pdb_path):
    try:
        from posteriordb import PosteriorDatabase
    except:
        sys.exit("Install PosteriorDB Python package: $ pip install posteriordb")

    pdb = PosteriorDatabase(pdb_path)
    model_names = pdb.posterior_names()
    if not model_names:
        sys.exit(
            "No Stan programs available.  PosteriorDB requires the path to the sub-folder posterior_database of the git cloned repository."
        )

def has_reference_draws(pdb_model):
    reference_draws_exist = False
    try:
        pdb_model.reference_draws()
        reference_draws_exist = True
    except:
        pass
    return reference_draws_exist


def models_with_reference_draws(pdb_path):
    pdb = PosteriorDatabase(pdb_path)
    model_names = pdb.posterior_names()
    model_names_with_reference_draws = []
    for model_name in model_names:
        posterior = pdb.posterior(model_name)
        if has_reference_draws(posterior):
            model_names_with_reference_draws.append(model_name)
    return model_names_with_reference_draws


def create_minipdb(pdb_path: str):
    check_pdb(pdb_path)

    model_names = models_with_reference_draws(pdb_path)
    number_models = len(model_names)

    pdb = PosteriorDatabase(pdb_path)
    df = pd.DataFrame.from_dict({"model_name": model_names,
                                 "code": ["code"] * number_models,
                                 "data": ["data"] * number_models,
                                 "inference_info": ["defaults"] * number_models,
                                 "summary_stats": ["summary"] * number_models})

    for model_name in model_names:
        meta = {}
        idx = df["model_name"] == model_name
        posterior = pdb.posterior(model_name)

        df.loc[idx, "code"] = posterior.model.code("stan")
        df.loc[idx, "data"] = json.dumps(posterior.data.values())

        info = posterior.reference_draws_info()["inference"]["method_arguments"]
        meta["iter_sampling"] = info.get("iter", 10_000)
        meta["iter_warmup"] = info.get("warmup", meta["iter_sampling"])
        meta["chains"] = info.get("chains", 10)
        meta["parallel_chains"] = info.get("parallel_chains", meta["chains"])
        meta["thin"] = info.get("thin", 1)
        meta["seed"] = info.get("seed", random.randint(0, 4_294_967_295))
        meta["adapt_delta"] = info.get("control", 0.8).get("adapt_delta", 0.8)
        meta["max_treedepth"] = info.get("control", 10).get("max_treedepth", 10)
        meta["sig_figs"] = info.get("sig_figs", 16)
        df.loc[idx, "inference_info"] = json.dumps(meta)

        draws_df = pd.DataFrame(posterior.reference_draws())
        smry = summarize_pdb_draws(draws_df)
        df.loc[idx, "summary_stats"] = json.dumps(smry)

    df.to_parquet("minipdb.parquet")


# create_minipdb(pathlib.Path.home() / "posteriordb/posterior_database")
