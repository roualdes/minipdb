import pathlib
import json

import pandas as pd

def add_stan_programs(stan_dir):
    stan_dir = pathlib.Path(stan_dir)
    df = pd.read_parquet("minipdb.parquet")
    files = set([f.stem for f in stan_dir.glob("*") if f.suffix != ".so"])

    for f in files:
        pf = stan_dir / f
        stan_file = pf.with_suffix(".stan")
        code = stan_file.read_text()

        data_file = pf.with_suffix(".json")
        data = data_file.read_text()

        df_new = pd.DataFrame.from_dict({
            "model_name": [f],
            "code": [code],
            "data": [data],
            "inference_info": ["{}"],
            "summary_stats": ["{}"],
        })

        df = pd.concat([df, df_new], ignore_index = True)

    df.to_parquet("minipdb.parquet")

# add_stan_programs(pathlib.Path.home() / "adaptive-hmc" / "stan")
