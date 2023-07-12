import minipdb

import pytest
import pathlib

cwd = pathlib.Path().resolve() / "test"
configfile = str(cwd / "fake01.yml")


def test_model_name_check():
    # good: leads with capital letter, only contains ASCII, _-
    config = {"model_name": "Good-Name_"}
    minipdb.checks.model_name_check(config, configfile)

    config = {"model_name": "lOWERCASE"}
    with pytest.raises(ValueError):
        minipdb.checks.model_name_check(config, configfile)

    config = {"model_name": "UpperCase!"}
    with pytest.raises(ValueError):
        minipdb.checks.model_name_check(config, configfile)


def test_iter_sampling_check():
    # good
    config = {"meta": {"iter_sampling": 10_000}}
    minipdb.checks.iter_sampling_check(config, configfile)

    # not an int
    config = {"meta": {"iter_sampling": 1.0}}
    with pytest.raises(TypeError):
        minipdb.checks.iter_sampling_check(config, configfile)

    # unreasonably low
    config = {"meta": {"iter_sampling": 100}}
    with pytest.raises(ValueError):
        minipdb.checks.iter_sampling_check(config, configfile)

    # unreasonably high
    config = {"meta": {"iter_sampling": 100_000_000}}
    with pytest.raises(ValueError):
        minipdb.checks.iter_sampling_check(config, configfile)


def test_iter_warmup_check():
    # good
    config = {"meta": {"iter_warmup": 10_000}}
    minipdb.checks.iter_warmup_check(config, configfile)

    # not an int
    config = {"meta": {"iter_warmup": 1.0}}
    with pytest.raises(TypeError):
        minipdb.checks.iter_warmup_check(config, configfile)

    # unreasonably low
    config = {"meta": {"iter_warmup": 100}}
    with pytest.raises(ValueError):
        minipdb.checks.iter_warmup_check(config, configfile)

    # unreasonably high
    config = {"meta": {"iter_warmup": 100_000_000}}
    with pytest.raises(ValueError):
        minipdb.checks.iter_warmup_check(config, configfile)


def test_chains_check():
    # good
    config = {"meta": {"chains": 10}}
    minipdb.checks.chains_check(config, configfile)

    # not an int
    config = {"meta": {"chains": 10.0}}
    with pytest.raises(TypeError):
        minipdb.checks.chains_check(config, configfile)

    # unreasonably low
    config = {"meta": {"chains": 0}}
    with pytest.raises(ValueError):
        minipdb.checks.chains_check(config, configfile)


def test_parallel_chains_check():
    # good
    config = {"meta": {"parallel_chains": 10}, "chains": 10}
    minipdb.checks.parallel_chains_check(config, configfile)

    # good: defaults to chains
    config = {"meta": {"other": 0}, "chains": 10}
    minipdb.checks.parallel_chains_check(config, configfile)

    # not an int
    config = {"meta": {"parallel_chains": 10.0}, "chains": 10}
    with pytest.raises(TypeError):
        minipdb.checks.parallel_chains_check(config, configfile)

    # unreasonably low
    config = {"meta": {"parallel_chains": 0}, "chains": 10}
    with pytest.raises(ValueError):
        minipdb.checks.parallel_chains_check(config, configfile)


def test_thin_check():
    # good
    config = {"meta": {"thin": 10}, "iter_sampling": 100}
    minipdb.checks.thin_check(config, configfile)

    # not an int
    config = {"meta": {"thin": 1.0}, "iter_sampling": 100}
    with pytest.raises(TypeError):
        minipdb.checks.thin_check(config, configfile)

    # unreasonably low
    config = {"meta": {"thin": 0}, "iter_sampling": 100}
    with pytest.raises(ValueError):
        minipdb.checks.thin_check(config, configfile)

    # unreasonably high
    config = {"meta": {"thin": 101}, "iter_sampling": 100}
    with pytest.raises(ValueError):
        minipdb.checks.thin_check(config, configfile)


def test_seed_check():
    # good
    config = {"meta": {"seed": 10}}
    minipdb.checks.seed_check(config, configfile)

    # not an int
    config = {"meta": {"seed": 10.0}}
    with pytest.raises(TypeError):
        minipdb.checks.seed_check(config, configfile)

    # negative
    config = {"meta": {"seed": -10}}
    with pytest.raises(ValueError):
        minipdb.checks.seed_check(config, configfile)

    # unreasonably high
    config = {"meta": {"seed": 2**32 + 1}}
    with pytest.raises(ValueError):
        minipdb.checks.seed_check(config, configfile)


def test_adapt_delta_check():
    # good
    config = {"meta": {"adapt_delta": 0.8}}
    minipdb.checks.adapt_delta_check(config, configfile)

    # not an float
    config = {"meta": {"adapt_delta": 1}}
    with pytest.raises(TypeError):
        minipdb.checks.adapt_delta_check(config, configfile)

    # unreasonably low
    config = {"meta": {"adapt_delta": -0.5}}
    with pytest.raises(ValueError):
        minipdb.checks.adapt_delta_check(config, configfile)

    # unreasonably high
    config = {"meta": {"adapt_delta": 1.5}}
    with pytest.raises(ValueError):
        minipdb.checks.adapt_delta_check(config, configfile)


def test_max_treedepth_check():
    # good
    config = {"meta": {"max_treedepth": 10}}
    minipdb.checks.max_treedepth_check(config, configfile)

    # not an int
    config = {"meta": {"max_treedepth": 10.0}}
    with pytest.raises(TypeError):
        minipdb.checks.max_treedepth_check(config, configfile)

    # unreasonably low
    config = {"meta": {"max_treedepth": 0}}
    with pytest.raises(ValueError):
        minipdb.checks.max_treedepth_check(config, configfile)

    # unreasonably high
    config = {"meta": {"max_treedepth": 25}}
    with pytest.raises(ValueError):
        minipdb.checks.max_treedepth_check(config, configfile)


def test_sig_figs_check():
    # good
    config = {"meta": {"sig_figs": 10}}
    minipdb.checks.sig_figs_check(config, configfile)

    # not an int
    config = {"meta": {"sig_figs": 10.0}}
    with pytest.raises(TypeError):
        minipdb.checks.sig_figs_check(config, configfile)

    # unreasonably low
    config = {"meta": {"sig_figs": 0}}
    with pytest.raises(ValueError):
        minipdb.checks.sig_figs_check(config, configfile)

    # unreasonably high
    config = {"meta": {"sig_figs": 21}}
    with pytest.raises(ValueError):
        minipdb.checks.sig_figs_check(config, configfile)
