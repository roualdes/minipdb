# minipdb

`minipdb`, AKA Mini-PosteriorDB, provides a
[SQLite](https://www.sqlite.org/index.html) database that contains reference
draws for a collection of [Stan](https://mc-stan.org/) programs, with the hope
to ease the comparison and evaluation of MCMC algorithms.

`minipdg` attemps to mimic the usefuleness of
[posteriordb](https://github.com/stan-dev/posteriordb), but uses a SQLite
database via the R package
[RSQLite](https://cran.r-project.org/web/packages/RSQLite/).  `minipdb`'s most
useful feature is the database `minipdb.sqlite`.

The database `minipdb.sqlite` consists of three tables Program, $x$_draws,
$x$_diagnostics, $x$_metric, and Meta.  Details of the tables are described below.

## Database Tables

**Program** ...

$x$**_draws** ...

$x$**_draws** ...

$x$**_diagnostics** ...

$x$**_metric** ...

**Meta** ...


## Dependencies

R packages `posteriordb`, `dplyr`, `DBI`, `RSQLite`, `jsonlite`, `rlang`,
`httr`, and `cmdstanr`.  The package `cmdstanr` itself has dependencies on
[CmdStan](https://mc-stan.org/docs/cmdstan-guide/index.html) and a suitable C++
toolchain.  The documentation for a [CmdStan
Installation](https://mc-stan.org/docs/cmdstan-guide/cmdstan-installation.html)
has instructions for getting a suitable C++ toolchain setup.
