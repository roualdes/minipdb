# MiniPDB

MiniPDB, AKA Mini-PosteriorDB, provides a
[SQLite](https://www.sqlite.org/index.html) database that contains reference
draws for a collection of [Stan](https://mc-stan.org/) programs, with the goal
of easing the comparison and evaluation of MCMC algorithms.

MiniPDB attempts to mimic the usefuleness of
[posteriordb](https://github.com/stan-dev/posteriordb), but uses a SQLite
database instead.  MiniPDB's most useful components are the database
`minipdb.sqlite` itself and a command line interface `minipdb.py` for managing
the entires of a MiniPDB database.

The database `minipdb.sqlite` consists of the tables `Program`, `Meta`, `x`,
`x_diagnostics`, and `x_metric`, where `x` represents a model name matching the
values in the column `model_name` of table `Program`.  Details of the tables are
described below.

## Database Tables

Table `Program` contains columns: `model_name`, `code`, and `data`.  Each row of
this table is a Stan program comprised of a name `model_name`, the Stan
file stored in `code`, and JSON dats stored in `data`.

Table `Meta` contains all the information necessary to recreate the reference
draws stored in table `x` (see below) when run in CmdStanR.  Table `Meta` has
columns: `model_name`, `iter_warmup`, `iter_sampling`, `chains`,
`parallel_chains`, `thin`, `seed`, `adapt_delta`, `max_treedepth`, and
`sig_figs`.

Table `x`, where `x` represents a model name matching the values in table
`Program`'s column `model_name`, contains the reference draws as sampled via
CmdStanR using the sampling parameters stored in table `Meta`.

N.B. Reference draws for all parameters and transformed parameters are stored
are on the constrained scale, even though Stan samples on the unconstrained
scale.  The user is responsible for conversion from the constrained scale to the
unconstrained scale.


Table `x_diagnostics` contains all the information output from CmdStanR's
function
[sampler_diagnostics()](https://mc-stan.org/cmdstanr/reference/fit-method-sampler_diagnostics.html),
namely columns: `accept_stat__`, `stepsize__`, `treedepth__`, `n_leapfrog__`,
`divergent__`, and `energy__`.

N.B. Once [CmdStanPy issue
676](https://github.com/stan-dev/cmdstanpy/issues/676) is in, this table will be
merged with the reference draws table.

Table `x_metric` contains the diagonal elements of (the diagonal) mass matrix as
output from CmdStanR's function
[inv_metric()](https://mc-stan.org/cmdstanr/reference/fit-method-inv_metric.html).
Rows of this table correspond to dimensions of the model and columns correspond
to chains.

## Dependencies

The Python packages used in the command line interface `minipdb.py` are
argparse, pathlib, sqlite3, tomllib, sys, random, string, json, cmdstanpy,
numpy, pandas, and multiprocessing

The package `cmdstanpy` itself has dependencies on
[CmdStan](https://mc-stan.org/docs/cmdstan-guide/index.html) and a suitable C++
toolchain.  Follow the [CmdStanPy documentation](https://mc-stan.org/cmdstanpy/)
to get this set up.

## Command Line Interface

The file `minipdb.py` is a Python 3.11 command line interface (CLI) for managing the
entries of a minipdb database.  The subsections below describe the main verbs of
the minipdb CLI, but skip the various flags/options.

### help

Run

```
python3 minipdb.py -h
```

for help

### init

Initialize a Stan program (source code and data only) into the database.
Initialization is separated from running/storing reference draws in case the
user wants to run CmdStanPy on their preferred machine.

```
python3 minipdb.py init stan_program.toml
```

where some `stan_program.toml` file looks like

```
model_name = "Bespoke-model" # starts with [A-Z], no spaces, the only special
characters allowed are _-
stan_file = "path/to/model.stan"
json_data = "path/to/data.json"

[meta]
iter_sampling = int # defaults 10_000
iter_warmup = int # defaults to iter_sampling
chains = int # defaults to 10
parallel_chains = int # defaults to chains
thin = int # defaults to 1
seed = int # defaults to a random positive integer
adapt_delta = float # defaults 0.8, must be in [0, 1]
max_treedepth = int # defaults to 10
sig_figs = int # defaults to 16
```

### run

Run specified

```
python3 minipdb.py run SomeModel
```

where `SomeModel` corresponds to the model name (`model_name`) of a unique Stan program.  Run
(maybe a poor verb choice) fits the model `SomeModel`, which has already been
`add`ed to `minipdb.sqlite`, using the associated meta data, and stores the
resulting reference draws in a table named `SomeModel`.

If the flag `--overwrite` is present, then `run` overwrites the reference draws
in the database.

TODO Note that `parallel_chains` will default to the minimum of whatever is in
Meta/`SomeModel.toml` and `multiprocessing.cpu_count() - 1`.

### update

Update the Stan program pointed to by and using the information contained in the
specified TOML file,

```
python3 minipdb.py update stan_program.toml
```

where `stan_program.toml` looks like the example above, except the defaults are
now set by the corresponding values in Meta for the specified model name.  Any
values not specified in `stan_program.toml` will not be updated.

Like `init`, this command does not `run` a model. TODO so maybe it needs a
better name.

### delete

Delete the table containing reference draws identified by a unique `model_name`, and the
corresponding rows in `Program` and `Meta`, with

```
python3 minipdb.py delete SomeModel
```
