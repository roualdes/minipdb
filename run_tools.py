def get_stan_files(path, model_name):
    stan_file = f"{path}/{model_name}.stan"
    data_file = f"{path}/{model_name}.json"
    return stan_file, data_file

def summarize_pdb_draws(df):
    stats = ["mean", "std", "q05", "q50", "q95"]
    params = [col for col in df.columns]
    summary = {st: {p: 0.0 for p in params} for st in stats}
    for p in params:
        data = df[p].explode()
        summary["mean"][p] = np.mean(data)
        summary["std"][p] = np.std(data, ddof = 1)
        q05, q50, q95 = np.quantile(data, [0.05, 0.50, 0.95])
        summary["q05"][p] = q05
        summary["q50"][p] = q50
        summary["q95"][p] = q95
    return summary
