import click
import pathlib

import duckdb as dk

DBURL = "https://github.com/roualdes/minipdb/raw/duckdb/minipdb/minipdb.parquet"

def get_model_row_as_df(model_name):
    df = dk.sql(f"SELECT * FROM '{DBURL}' where model_name = '{model_name}'").df()
    return df


def get_models_as_df():
    df = dk.sql(f"SELECT * FROM '{DBURL}'").df()
    return df


def write_program(Path_no_ext, code, data):
    path = str(Path_no_ext)
    with open(path + ".stan", "w") as stan_file:
        stan_file.write(code)

    with open(path + ".json", "w") as stan_data:
        stan_data.write(data)


def write_inference(Path_no_ext, inference_info, summary_stats):
    path = str(Path_no_ext)
    with open(path + "_inference_info.json", "w") as info_file:
        info_file.write(inference_info)

    with open(path + "_summary_stats.json", "w") as stat_file:
        stat_file.write(summary_stats)


@click.group()
@click.option("-y", "--yes",
              is_flag=True,
              default=False,
              show_default=True,
              help="If True, then WRITE will not prompt user to double check action.")
@click.option("-v", "--verbose", default=False, count=True, show_default=True)
@click.option("-d", "--dry", is_flag=True, default=False, show_default=True, help="Dry run")
@click.pass_context
def cli(ctx, yes, verbose, dry):
    ctx.ensure_object(dict)
    ctx.obj["YES"] = yes
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["DRY"] = dry
    if ctx.obj["DRY"]:
        ctx.obj["VERBOSE"] += 1


@cli.command()
@click.argument("phrase", nargs=1)
@click.pass_context
def search(ctx, phrase):
    """Search minipdb model names for PHRASE."""
    if ctx.obj["VERBOSE"] > 0:
        click.echo(f"Searching minipdb for {phrase} ...")
    if not ctx.obj["DRY"]:
        df = dk.sql(f"SELECT model_name FROM '{DBURL}'").df()
        click.echo(df.loc[df["model_name"].str.contains(phrase)])


@cli.command()
@click.argument("directory", type=click.Path(exists=True, path_type=pathlib.Path), nargs=1)
@click.pass_context
def download(ctx, directory):
    """Download minipdb to DIRECTORY"""
    if not ctx.obj["YES"]:
        click.confirm(f"Downloading will overwrite the file minipdb.parquet in {directory}.\n\nReverting download can not be undone.\n\nAre you sure you want to proceed?\n\n",
                      abort=True)
    if ctx.obj["VERBOSE"] > 0:
        click.echo(f"Downloading minipdb.parquet into {directory} ...")
    if not ctx.obj["DRY"]:
        df = dk.sql(f"SELECT * FROM '{DBURL}'").df()
        df.to_parquet(directory / "minipdb.parquet")


@cli.group()
@click.pass_context
def write(ctx):
    """
    Write inference info or summary statistics.

    Inference information contains the sample settings.  Summary
    statistics includes means, standard deviations, and quantiles
    averaged across all chains for each parameter.

    See minipdb write {inference, program} --help for more details
    """
    pass


@write.command()
@click.argument("model_name", nargs=1)
@click.argument("directory", type=click.Path(exists=True, path_type=pathlib.Path), nargs=1)
@click.pass_context
def program(ctx, model_name, directory):
    """Write program (Stan code and data) to DIRECTORY.

    If MODEL_NAME is ALL, write Stan program for every model in minipdb.
    """
    if not ctx.obj["YES"]:
        click.confirm(f"Writing will overwrite the files in {directory}.\n\nReverting write can not be undone.\n\nAre you sure you want to proceed?\n\n",
                      abort=True)
    if model_name == "ALL":
        if ctx.obj["VERBOSE"] > 0:
            click.echo(f"Writing all programs of minipdb into {directory} ...")
        if not ctx.obj["DRY"]:
            df = get_model_as_df()
    else:
        if ctx.obj["VERBOSE"] > 0:
            click.echo(f"Writing program {model_name} into {directory} ...")
        if not ctx.obj["DRY"]:
            df = get_model_row_as_df(model_name)

    if not ctx.obj["DRY"]:
        for index, row in df.iterrows():
            dirpath = directory / row["model_name"]
            write_program(dirpath, row["code"], row["data"])


@write.command()
@click.argument("model_name", nargs=1)
@click.argument("directory", type=click.Path(exists=True, path_type=pathlib.Path), nargs=1)
@click.pass_context
def inference(ctx, model_name, directory):
    """Write inference info (sample settings and summary stats) to DIRECTORY.

    If MODEL_NAME is ALL, write inference info for every model in minipdb.
    """
    if not ctx.obj["YES"]:
        click.confirm(f"Writing will overwrite the inference info files in {directory}.\n\nReverting write can not be undone.\n\nAre you sure you want to proceed?\n\n",
                          abort=True)
    if model_name == "ALL":
        if ctx.obj["VERBOSE"] > 0:
            click.echo(f"Writing all inference info of minipdb into {directory} ...")
        if not ctx.obj["DRY"]:
            df = get_model_as_df()
    else:
        if ctx.obj["VERBOSE"] > 0:
            click.echo(f"Writing inference info for program {model_name} into {directory} ...")
        if not ctx.obj["DRY"]:
            df = get_model_row_as_df(model_name)

    if not ctx.obj["DRY"]:
        for index, row in df.iterrows():
            dirpath = directory / row["model_name"]
            write_inference(dirpath, row["inference_info"], row["summary_stats"])
