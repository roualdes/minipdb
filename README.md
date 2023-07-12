# MiniPDB

MiniPDB, AKA Mini-PosteriorDB, provides a
[SQLite](https://www.sqlite.org/index.html) database that contains reference
draws for a collection of [Stan](https://mc-stan.org/) programs, with the goal
of easing the comparison and evaluation of MCMC algorithms.

MiniPDB attempts to mimic the usefuleness of
[posteriordb](https://github.com/stan-dev/posteriordb), but uses a SQLite
database instead.  MiniPDB's most useful components are the database
minipdb.sqlite itself and a command line interface minipdb for managing
the entires of a MiniPDB database (minipdb.sqlite or otherwise).

The database minipdb.sqlite consists of the tables Program, Meta, *x*,
*x*_diagnostics, and *x*_metric, where *x* represents a model name matching the
values in the column model_name of table Program.  Details of the tables are
described below.

## Database Tables

Table Program contains columns: model_name, code, data, and last_run.
Each row of this table is a Stan program comprised of a name model_name, the
Stan file stored in code, JSON dats stored in data, and the last run time
last_run for which minipdb stored referenced draws for the model
model_name.

Table Meta contains all the information necessary to recreate the reference
draws stored in table *x* (see below) when run in CmdStanPy.  Table Meta has
columns: model_name, iter_warmup, iter_sampling, chains,
parallel_chains, thin, seed, adapt_delta, max_treedepth, and
sig_figs.

Table *x*, where *x* represents a model name matching the values in table
Program's column model_name, contains the reference draws as sampled via
CmdStanPy using the sampling parameters stored in table Meta.

N.B. Reference draws for all parameters and all transformed parameters are stored
on the constrained scale, even though Stan samples on the unconstrained
scale.  The user is responsible for conversion from the constrained scale to the
unconstrained scale.

Table *x*_diagnostics will be phased out once [CmdStanPy issue
676](https://github.com/stan-dev/cmdstanpy/issues/676) is in.

Table *x*_metric contains the diagonal elements of (the diagonal) mass matrix as
output from CmdStanPy's property
[metric](https://mc-stan.org/cmdstanpy/api.html#cmdstanpy.CmdStanMCMC.metric)
Rows of this table correspond to dimensions of the model and columns correspond
to chains.

## Dependencies

MiniPDB requires Python 3.11.  The Python packages used in the command line
interface minipdb which are not part of the Python 3.11 standard library are
cmdstanpy, numpy, and pandas.

The package cmdstanpy itself has dependencies on
[CmdStan](https://mc-stan.org/docs/cmdstan-guide/index.html) and a suitable C++
toolchain.  Follow the [CmdStanPy documentation](https://mc-stan.org/cmdstanpy/)
to get this set up.

## Command Line Interface

minipdb is a Python 3.11 command line interface (CLI) for managing the
entries of a MiniPDB database.  To install minipdb, run the following

```
cd /path/to/minipdb
pip install .
```

The subsections below describe the main verbs of the CLI.

### help

Run

```
python3 minipdb.py -h
```

to print the help menu.

### init

MiniPDB stores Stan programs, the combination of code from a .stan file and
data from a .json file, in the table Program.  All Stan programs must be
`init`ialized into this table before the Stan program can be `run`.

To initialize a Stan program into the database use a command similar to the
following.

```
minipdb init stan_program.toml
```

where some `stan_program.toml` file looks similar to the follow TOML file

```
model_name = "Bespoke-model" # starts with [A-Z], no spaces, the only special characters allowed are _-
stan_file = "path/to/model.stan"
json_data = "path/to/data.json"

[meta]
iter_sampling = int     # defaults 10_000, must be in 2_000:1_000_000
iter_warmup = int       # defaults to iter_sampling
chains = int            # defaults to 10, must be >= 1
parallel_chains = int   # defaults to chains, must be in 1:chains
thin = int              # defaults to 1, must be in 1:iter_sampling
seed = int              # defaults to a random positive integer, must be in 1:2^32-1
adapt_delta = float     # defaults 0.8, must be in [0, 1]
max_treedepth = int     # defaults to 10, must be in 1:20
sig_figs = int          # defaults to 16, must be in 1:18
```

such that `int` and `float` are stand-ins for integer and float values.

### run

minipdb will generate and store reference draws for `SomeModel` via CmdStanPy
for an `init`ed Stan prgram named `SomeModel` with code as follows.

```
minipdb run SomeModel
```

The Stan program name `SomeModel` must match model name of a unique Stan program
stored in the table Program.  CmdStanPy will execute the Stan program
`SomeModel` using the sampling algorithm parameters stored in the table Meta
corresponding to the entry with model name `SomeModel`.

The minipdb actions `init` and `run` are separated to enable minipdb to be run
locally or remotely, e.g. on a larger machine.  To better accomodate this, the
sampling algorithm parameter parallel_chains defaults to the minimum of whatever
is in Meta and `multiprocessing.cpu_count() - 1`.  So if minipdb `run`s a Stan
program on a smaller laptop with fewer CPUs than parallel_chains, minipdb will
adapt.

If the flag `--overwrite` (or `-o`) is present, then `run` overwrites the reference draws
in the database.

If the flag `--yes` (or `-y`) is present, then `run` will run automatically
without stopping to prompt the user to double check their request.

### add

Combine `init` and `run` into one command with

```
minipdb add stan_program.toml
```

This only works for `run`ning one Stan program.

### run_all

To `run` all Stan programs contained in the table Program use

```
minipdb run_all
```

One can `run` all the Stan programs in parallel.  Use the flag `--cpus` (or
`-c`) to control the number of CPUs in use.  N.B. the number of parallel_chains
specified for each Stan program will also spawn separate processes, e.g. if
there are 3 Stan programs to `run` with `parallel_chains = 10` for each Stan
program, and `--cpus 3` is set, then minipdb will spawn 30 processes.

If the flag `--overwrite` (or `-o`) is present, then `run_all` overwrites the
reference draws in the database.  If `--overwrite` is not set, then only the
Stan programs which have previously been `init`ed but not `run` will be run, so
no previous draws will be overwritten.

If the flag `--yes` (or `-y`) is present, then `run_all` will run automatically
without stopping to prompt the user to double check their request.

### update

Update the Stan program pointed to by and using the information contained in the
specified TOML file,

```
minipdb update stan_program.toml
```

where `stan_program.toml` looks like the example above, except the defaults are
now set by the corresponding values in Meta for the specified model name.  Any
values not specified in `stan_program.toml` will not be updated.

Like `init`, this command does not `run` a model.  The user is responsible for
calling `run` following an update.

### delete

Delete the table containing reference draws identified by a unique model_name, and the
corresponding rows in Program, Meta, *x*_diagnostics, and *x*_metric, with

```
minipdb delete SomeModel
```

If the flag `--yes` (or `-y`) is present, then `delete` will run automatically
without stopping to prompt the user to double check their request.
