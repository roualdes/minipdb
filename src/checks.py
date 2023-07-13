import pathlib
import sys
import pathlib
import string
import random


def error_message(var, config, msg):
    return f"Variable {var} in {config} must " + msg


def model_name_check(config, configfile):
    if "model_name" not in config:
        sys.exit(
            f"No model name specified, please specify model_name in {configfile} and add again."
        )
    else:
        if not config["model_name"][0].isupper():
            raise ValueError(
                error_message(
                    "model_name", configfile, "begin with an upper case ACII character"
                )
            )

        allowed_chars = set(
            string.ascii_lowercase + string.ascii_uppercase + string.digits + "-" + "_"
        )
        if not set(config["model_name"]) <= allowed_chars:
            raise ValueError(
                error_message(
                    "model_name", configfile, "contain only ACII characters, digits, _-"
                )
            )


def stan_file_check(config, configfile):
    if "stan_file" not in config:
        sys.exit(
            f"No Stan file specified, please specify stan_file in {configfile} and add again."
        )
    else:
        if type(config["stan_file"]) is not str:
            raise TypeError(error_message("stan_file", configfile, "be a string."))

        f = pathlib.Path(configfile).parent / config["stan_file"]
        if not f.is_file():
            raise ValueError(error_message("stan_file", configfile, "exist."))


def json_data_check(config, configfile):
    if "json_data" not in config:
        sys.exit(
            "No JSON data specified, please specify json_data in {configfile} and add again."
        )
    else:
        if type(config["json_data"]) is not str:
            raise TypeError(error_message("json_data", configfile, "be a string."))

        f = pathlib.Path(configfile).parent / config["json_data"]
        if not f.is_file():
            raise ValueError(error_message("json_data", configfile, "exist."))


def iter_sampling_check(config, configfile):
    if "iter_sampling" not in config["meta"]:
        config["iter_sampling"] = 10_000
    else:
        if type(config["meta"]["iter_sampling"]) is not int:
            raise TypeError(
                error_message("iter_sampling", configfile, "be an integer.")
            )

        if (
            not 2_000 <= config["meta"]["iter_sampling"]
            or not config["meta"]["iter_sampling"] <= 1_000_000
        ):
            raise ValueError(
                error_message(
                    "iter_sampling", configfile, "be an integer in 2_000:1_000_000."
                )
            )

        config["iter_sampling"] = config["meta"]["iter_sampling"]


def iter_warmup_check(config, configfile):
    if "iter_warmup" not in config["meta"]:
        config["iter_warmup"] = config["meta"]["iter_sampling"]
    else:
        if type(config["meta"]["iter_warmup"]) is not int:
            raise TypeError(error_message("iter_warmup", configfile, "be an integer."))

        if (
            not 2_000 <= config["meta"]["iter_warmup"]
            or not config["meta"]["iter_warmup"] <= 1_000_000
        ):
            raise ValueError(
                error_message(
                    "iter_sampling", configfile, "be an integer in 2_000:1_000_000."
                )
            )

        config["iter_warmup"] = config["meta"]["iter_warmup"]


def chains_check(config, configfile):
    if "chains" not in config["meta"]:
        config["chains"] = 10
    else:
        if type(config["meta"]["chains"]) is not int:
            raise TypeError(error_message("chains", configfile, "be an integer."))

        if not 1 <= config["meta"]["chains"]:
            raise ValueError(
                error_message("chains", configfile, "be an integer greater than zero.")
            )

        config["chains"] = config["meta"]["chains"]


def parallel_chains_check(config, configfile):
    if "parallel_chains" not in config["meta"]:
        config["parallel_chains"] = config["chains"]
    else:
        if type(config["meta"]["parallel_chains"]) is not int:
            raise TypeError(
                error_message("parallel_chains", configfile, "be an integer.")
            )

        if (
            not 1 <= config["meta"]["parallel_chains"]
            or not config["meta"]["parallel_chains"] <= config["chains"]
        ):
            raise ValueError(
                error_message(
                    "parallel_chains",
                    configfile,
                    f'be an integer in 1:{config["chains"]}',
                )
            )

        config["parallel_chains"] = config["meta"]["parallel_chains"]


def thin_check(config, configfile):
    if "thin" not in config["meta"]:
        config["thin"] = 1
    else:
        if type(config["meta"]["thin"]) is not int:
            raise TypeError(error_message("thin", configfile, "be an integer."))

        if (
            not 1 <= config["meta"]["thin"]
            or not config["meta"]["thin"] <= config["iter_sampling"]
        ):
            raise ValueError(
                error_message(
                    "thin",
                    configfile,
                    f'be an integer between 1 and {config["iter_sampling"]}.',
                )
            )

        config["thin"] = config["meta"]["thin"]


def seed_check(config, configfile):
    if "seed" not in config["meta"]:
        config["seed"] = random.randint(0, 4_294_967_295)
    else:
        if type(config["meta"]["seed"]) is not int:
            raise TypeError(error_message("seed", configfile, "be an integer."))

        if (
            not 0 <= config["meta"]["seed"]
            or not config["meta"]["seed"] <= 4_294_967_295
        ):
            raise ValueError(
                error_message("seed", configfile, "be an integer in 0:4_294_967_295.")
            )

        config["seed"] = config["meta"]["seed"]


def adapt_delta_check(config, configfile):
    if "adapt_delta" not in config["meta"]:
        config["adapt_delta"] = 0.8
    else:
        if type(config["meta"]["adapt_delta"]) is not float:
            raise TypeError(error_message("adapt_delta", configfile, "be a float."))

        if (
            not 0 < config["meta"]["adapt_delta"]
            or not config["meta"]["adapt_delta"] < 1
        ):
            raise ValueError(
                error_message("adapt_delta", configfile, "be a float in (0, 1).")
            )

        config["adapt_delta"] = config["meta"]["adapt_delta"]


def max_treedepth_check(config, configfile):
    if "max_treedepth" not in config["meta"]:
        config["max_treedepth"] = 10
    else:
        if type(config["meta"]["max_treedepth"]) is not int:
            raise TypeError(
                error_message("max_treedepth", configfile, "be an integer.")
            )

        if (
            not 1 <= config["meta"]["max_treedepth"]
            or not config["meta"]["max_treedepth"] <= 20
        ):
            raise ValueError(
                error_message("max_treedepth", configfile, "be an integer in 1:20.")
            )

        config["max_treedepth"] = config["meta"]["max_treedepth"]


def sig_figs_check(config, configfile):
    if "sig_figs" not in config["meta"]:
        config["sig_figs"] = 16
    else:
        if type(config["meta"]["sig_figs"]) is not int:
            raise TypeError(error_message("sig_figs", configfile, "be an integer."))

        if not 1 <= config["meta"]["sig_figs"] or not config["meta"]["sig_figs"] <= 18:
            raise ValueError(
                error_message("sig_figs", configfile, "be an integer in 1:18.")
            )

        config["sig_figs"] = config["meta"]["sig_figs"]


def init_checks(config, configfile):
    model_name_check(config, configfile)
    stan_file_check(config, configfile)
    json_data_check(config, configfile)
    iter_sampling_check(config, configfile)
    iter_warmup_check(config, configfile)
    chains_check(config, configfile)
    parallel_chains_check(config, configfile)
    thin_check(config, configfile)
    seed_check(config, configfile)
    adapt_delta_check(config, configfile)
    max_treedepth_check(config, configfile)
    sig_figs_check(config, configfile)
