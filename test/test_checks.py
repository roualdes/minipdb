import minipdb

import pytest
import pathlib

cwd = pathlib.Path().resolve() / "test"
tomlfile = str(cwd / "fake01.toml")


def test_model_name_check():
    # good: leads with capital letter, only contains ASCII, _-
    toml = {"model_name": "Good-Name_"}
    minipdb.checks.model_name_check(toml, tomlfile)

    toml = {"model_name": "lOWERCASE"}
    with pytest.raises(ValueError):
        minipdb.checks.model_name_check(toml, tomlfile)

    toml = {"model_name": "UpperCase!"}
    with pytest.raises(ValueError):
        minipdb.checks.model_name_check(toml, tomlfile)


def test_iter_sampling_check():
    # good
    toml = {"meta": {"iter_sampling": 10_000}}
    minipdb.checks.iter_sampling_check(toml, tomlfile)

    # not an int
    toml = {"meta": {"iter_sampling": 1.0}}
    with pytest.raises(TypeError):
        minipdb.checks.iter_sampling_check(toml, tomlfile)

    # unreasonably low
    toml = {"meta": {"iter_sampling": 100}}
    with pytest.raises(ValueError):
        minipdb.checks.iter_sampling_check(toml, tomlfile)

    # unreasonably high
    toml = {"meta": {"iter_sampling": 100_000_000}}
    with pytest.raises(ValueError):
        minipdb.checks.iter_sampling_check(toml, tomlfile)


def test_iter_warmup_check():
    # good
    toml = {"meta": {"iter_warmup": 10_000}}
    minipdb.checks.iter_warmup_check(toml, tomlfile)

    # not an int
    toml = {"meta": {"iter_warmup": 1.0}}
    with pytest.raises(TypeError):
        minipdb.checks.iter_warmup_check(toml, tomlfile)

    # unreasonably low
    toml = {"meta": {"iter_warmup": 100}}
    with pytest.raises(ValueError):
        minipdb.checks.iter_warmup_check(toml, tomlfile)

    # unreasonably high
    toml = {"meta": {"iter_warmup": 100_000_000}}
    with pytest.raises(ValueError):
        minipdb.checks.iter_warmup_check(toml, tomlfile)


def test_chains_check():
    # good
    toml = {"meta": {"chains": 10}}
    minipdb.checks.chains_check(toml, tomlfile)

    # not an int
    toml = {"meta": {"chains": 10.0}}
    with pytest.raises(TypeError):
        minipdb.checks.chains_check(toml, tomlfile)

    # unreasonably low
    toml = {"meta": {"chains": 0}}
    with pytest.raises(ValueError):
        minipdb.checks.chains_check(toml, tomlfile)


def test_parallel_chains_check():
    # good
    toml = {"meta": {"parallel_chains": 10}, "chains": 10}
    minipdb.checks.parallel_chains_check(toml, tomlfile)

    # good: defaults to chains
    toml = {"meta": {"other": 0}, "chains": 10}
    minipdb.checks.parallel_chains_check(toml, tomlfile)

    # not an int
    toml = {"meta": {"parallel_chains": 10.0}, "chains": 10}
    with pytest.raises(TypeError):
        minipdb.checks.parallel_chains_check(toml, tomlfile)

    # unreasonably low
    toml = {"meta": {"parallel_chains": 0}, "chains": 10}
    with pytest.raises(ValueError):
        minipdb.checks.parallel_chains_check(toml, tomlfile)


def test_thin_check():
    # good
    toml = {"meta": {"thin": 10}, "iter_sampling": 100}
    minipdb.checks.thin_check(toml, tomlfile)

    # not an int
    toml = {"meta": {"thin": 1.0}, "iter_sampling": 100}
    with pytest.raises(TypeError):
        minipdb.checks.thin_check(toml, tomlfile)

    # unreasonably low
    toml = {"meta": {"thin": 0}, "iter_sampling": 100}
    with pytest.raises(ValueError):
        minipdb.checks.thin_check(toml, tomlfile)

    # unreasonably high
    toml = {"meta": {"thin": 101}, "iter_sampling": 100}
    with pytest.raises(ValueError):
        minipdb.checks.thin_check(toml, tomlfile)


def test_seed_check():
    # good
    toml = {"meta": {"seed": 10}}
    minipdb.checks.seed_check(toml, tomlfile)

    # not an int
    toml = {"meta": {"seed": 10.0}}
    with pytest.raises(TypeError):
        minipdb.checks.seed_check(toml, tomlfile)

    # negative
    toml = {"meta": {"seed": -10}}
    with pytest.raises(ValueError):
        minipdb.checks.seed_check(toml, tomlfile)

    # unreasonably high
    toml = {"meta": {"seed": 2**32 + 1}}
    with pytest.raises(ValueError):
        minipdb.checks.seed_check(toml, tomlfile)


def test_adapt_delta_check():
    # good
    toml = {"meta": {"adapt_delta": 0.8}}
    minipdb.checks.adapt_delta_check(toml, tomlfile)

    # not an float
    toml = {"meta": {"adapt_delta": 1}}
    with pytest.raises(TypeError):
        minipdb.checks.adapt_delta_check(toml, tomlfile)

    # unreasonably low
    toml = {"meta": {"adapt_delta": -0.5}}
    with pytest.raises(ValueError):
        minipdb.checks.adapt_delta_check(toml, tomlfile)

    # unreasonably high
    toml = {"meta": {"adapt_delta": 1.5}}
    with pytest.raises(ValueError):
        minipdb.checks.adapt_delta_check(toml, tomlfile)


def test_max_treedepth_check():
    # good
    toml = {"meta": {"max_treedepth": 10}}
    minipdb.checks.max_treedepth_check(toml, tomlfile)

    # not an int
    toml = {"meta": {"max_treedepth": 10.0}}
    with pytest.raises(TypeError):
        minipdb.checks.max_treedepth_check(toml, tomlfile)

    # unreasonably low
    toml = {"meta": {"max_treedepth": 0}}
    with pytest.raises(ValueError):
        minipdb.checks.max_treedepth_check(toml, tomlfile)

    # unreasonably high
    toml = {"meta": {"max_treedepth": 25}}
    with pytest.raises(ValueError):
        minipdb.checks.max_treedepth_check(toml, tomlfile)


def test_sig_figs_check():
    # good
    toml = {"meta": {"sig_figs": 10}}
    minipdb.checks.sig_figs_check(toml, tomlfile)

    # not an int
    toml = {"meta": {"sig_figs": 10.0}}
    with pytest.raises(TypeError):
        minipdb.checks.sig_figs_check(toml, tomlfile)

    # unreasonably low
    toml = {"meta": {"sig_figs": 0}}
    with pytest.raises(ValueError):
        minipdb.checks.sig_figs_check(toml, tomlfile)

    # unreasonably high
    toml = {"meta": {"sig_figs": 21}}
    with pytest.raises(ValueError):
        minipdb.checks.sig_figs_check(toml, tomlfile)
