# minipdb

`minipdb`, AKA Mini-PosteriorDB, provides a
[SQLite](https://www.sqlite.org/index.html) database that contains reference
draws for a collection of [Stan](https://mc-stan.org/) programs, with the goal
of easing the comparison and evaluation of MCMC algorithms.

`minipdb` attempts to mimic the usefuleness of
[posteriordb](https://github.com/stan-dev/posteriordb), but uses a SQLite
database via the R package
[RSQLite](https://cran.r-project.org/web/packages/RSQLite/).  `minipdb`'s most
useful component is the database `minipdb.sqlite`.

The database `minipdb.sqlite` consists of the tables `Program`, `Meta`, `x`,
`x_diagnostics`, and `x_metric`, where `x` represents a model name matching the
values in the column `model_name` of table `Program`.  Details of the tables
are described below.

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

Table `x_metric` contains the diagonal elements of (the diagonal) mass matrix as
output from CmdStanR's function
[inv_metric()](https://mc-stan.org/cmdstanr/reference/fit-method-inv_metric.html).

## Dependencies

The statistical programming language [R](https://www.r-project.org/), R packages
`posteriordb`, `dplyr`, `DBI`, `RSQLite`, `jsonlite`, `rlang`, `httr`,
`posterior`, `withr`, and `cmdstanr`.  The package `cmdstanr` itself has
dependencies on [CmdStan](https://mc-stan.org/docs/cmdstan-guide/index.html) and
a suitable C++ toolchain.  The documentation for a [CmdStan
Installation](https://mc-stan.org/docs/cmdstan-guide/cmdstan-installation.html)
has instructions for getting a suitable C++ toolchain setup.

## Looking Forward

This shouldn't be a set of R script files.  It should be a Python command line
tool with an API something like

### add

```
python3 minipdb.py add stan_program.toml
```

where some `stan_program.toml` file looks like

```
model_name = "Bespoke-model" # starts with [A-Z], no spaces, the only special
characters allowed are _-
stan_file = "path/to/model.stan"
json_data = "path/to/data.json"

[meta]
iter_sampling = Int # defaults 10_000
iter_warmup = Int # defaults to iter_sampling
chains = Int # defaults to 10
parallel_chains = Int # defaults to chains
thin = Int # defaults to 10
seed = Int # defaults to a random positive integer
adapt_delta = Float # defaults 0.8, must be in [0, 1]
max_treedepth = Int # defaults to 10
sig_figs = Int # defaults to 16
```

### run

```
python3 minipdb.py run "SomeModel" [--overwrite]
```

where `SomeModel` corresponds to the model name (`model_name`) of a unique Stan program.  Run
(maybe a poor verb choice) fits the model `SomeModel`, which has already been
`add`ed to `minipdb.sqlite`, using the associated meta data, and stores the
resulting reference draws in a table named `SomeModel`.

If the flag `--overwrite` is present, then `run` overwrites the reference draws
in the database.

TODO Should this be named store, instead of run?  Or maybe create?

### update

Update the meta data and/or model name of a uniquely identified Stan program.

```
python3 minipdb.py update stan_program.toml
```

where `stan_program.toml` looks like the example above, except the defaults are
now set by the corresponding values in Meta for the specified model name.

TODO what to do when a model's meta data is `update`ed, but not yet re-run?

If `update`ing the meta data of a model, maybe the user should consider if two
models with similar names and different meta data is more appropriate.

### delete

Delete the table containing reference draws identified by a unique `model_name`, and the
corresponding rows in `Program` and `Meta`, with

```
python3 minipdb.py delete "SomeModel"
```
