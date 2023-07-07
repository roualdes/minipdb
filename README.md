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
CmdStanR using the sampling parameters stored in table `Meta`.  Reference draws
for all parameters and transformed parameters are stored are on the constrained
scale, even though Stan samples on the unconstrained scale.

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
