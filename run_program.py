from run_tools import get_stan_files, summarize_pdb_draws

from pathlib import Path

import json

import cmdstanpy as csp
import pandas as pd

df = pd.read_parquet("minipdb.parquet")

model_name = "pkpd"
idx = df["model_name"] == model_name
stan_file = Path(model_name + ".stan")
data_file = Path(model_name + ".json")

stan_file.write_text(df.loc[idx, "code"].values[0])
data_file.write_text(df.loc[idx, "data"].values[0])

inference_info = df.loc[idx, "inference_info"]
if inference_info.values[0] == "{}":
    inference_info = df.loc[0, "inference_info"]
    df.loc[idx, "inference_info"] = inference_info
inference_info = json.loads(inference_info)

csp_model = csp.CmdStanModel(stan_file = stan_file,
                             compile = "force")

fit = csp_model.sample(data = data_file,
                       show_progress = True,
                       iter_warmup = inference_info["iter_warmup"],
                       iter_sampling = inference_info["iter_sampling"],
                       chains = inference_info["chains"],
                       parallel_chains = inference_info["parallel_chains"],
                       thin = inference_info["thin"],
                       seed = inference_info["seed"],
                       adapt_delta = inference_info["adapt_delta"],
                       max_treedepth = inference_info["max_treedepth"],
                       sig_figs = inference_info["sig_figs"])

ss = fit.summary()[["Mean", "StdDev", "5%", "50%", "95%"]]
ssdf = ss.iloc[1:, :]
ssdf.columns = ["mean", "std", "q05", "q50", "q95"]
df.loc[idx, "summary_stats"] = ssdf.to_json()

df.to_parquet("minipdb.parquet")

stan_file.unlink()
data_file.unlink()
Path(model_name).unlink()
