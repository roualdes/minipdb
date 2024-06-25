# MiniPDB

MiniPDB (Mini-PosteriorDB) contains a subset of
[PosteriorDB](https://github.com/stan-dev/posteriordb) with similar
goals, namely easing the comparison and evaluation of MCMC algorithms,
but MiniPDB also aims to be smaller and simpler.

The subset consists of only those PosteriorDB Stan programs that
contain reference draws and only [Stan](https://mc-stan.org/) programs
(code and data) and inference information ([sample](https://cmdstanpy.readthedocs.io/en/v1.2.0/api.html#cmdstanpy.CmdStanModel.sample) settings and summary
statistics).  MiniPDB does not contain any reference draws, and
instead stores the information necessary to recreate (similar, albeit
not exactly) the reference draws.  The entire database (< 1MB) is one
[Parquet](https://parquet.apache.org) file hosted within this
repository: `minipdb.parquet`.

Since the MiniPDB database is just the one parquet file, you can
access and use it in any way you like.  This repository contains
Python code that engages with the database in two ways.

First, after cloning the repository, you could run the following code to
install a command line interface (cli).  The MiniPDB cli, named
`minipdb`, allows you `download`, `search`, and/or `write` parts of or
the entire database contents to file so as to use the Stan programs or
their summarized inference output.

```
cd /path/to/minipdb/
pip install .
```

Second, there is example Python code in the file `example.py` that
demonstrates querying `minipdb.parquet` using the [Python client for
DuckDB](https://duckdb.org/docs/api/python/overview.html).  This
project chose a parquet file for its simplicity, compressibility, and
coordination with DuckDB.  DuckDB was chosen because it can [query a
database via
HTTPS](https://duckdb.org/docs/guides/network_cloud_storage/duckdb_over_https_or_s3.html).

## databse

The MiniPDB database consists of the sole file `minipdb.parquet`.
This file is effectively one table with columns `model_name`, `code`,
`data`, `inference_info`, and `summary_stats`.  Each row of this table
is a particular Stan program (code and data), referenced by its model
name, and the inference info (sample settings and summary statistics).

The column `model_name` is the name of the Stan program as defined in
PosteriorDB.  The column `code` is a string which contains the Stan
code associated with `model_name`.  The column `data` is a JSON string
containing the data necessary to sample from the model.  Hence, `code`
and `data` contain the necessary information to run a Stan program.

The column `inference_info` is a JSON string that contains the
[sample](https://cmdstanpy.readthedocs.io/en/v1.2.0/api.html#cmdstanpy.CmdStanModel.sample)
settings necessary to recreate reference draws similar to what
PosteriorDB itself contains.  Any MiniPDB recreated reference draws
are not guaranteed to match, bit for bit, the reference draws in
PosteriorDB, but the summary information they contain should be quite
close.

The column `summary_stats` is a JSON string that contains summary
statistics calculated directly from the reference draws contained in
PosteriorDB.  Means, standard deviations, and 5%, 50%, and 95%
quantiles are stored for each parameter, averaged over all chains.


## cli

To install the MiniPDB cli, `minipdb`, clone this repository, and then run

```
cd /path/to/minipdb/
pip install .
```

After installing, try running

```
minipdb --help
```

There are three basic verbs associated with `minipdb`: `download`,
`search`, and `write`.

### `download`

To download the entire database `minipdb.parquet`, run

```
minipdb download path/to/destination/directory
```

### `search`

To search the database, without downloading it, for a model name
that contains a specified pattern, run

```
minipdb search pattern
```

Internally, this uses the [Pandas Series method
contains](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.contains.html),
so the user specified pattern can be a general pattern or even a
regex.

### `write`

To write a Stan program to file run

```
minipdb write program model_name path/to/destiniation/directory
```

This will write both the Stan code and data into the user specified
directory, naming the Stan code file `model_name.stan` and the data
file `model_name.json`.

To write the inference information to file run

```
minipdb write inference model_name path/to/destination/directory
```

This will write both the sample settings and the summary statistics
into the user specified directory.  The sample settings file will be
named `model_name_inference_info.json`, and the summary statistics
file will be named `model_name_summary_stats.json`.

If the keyword ALL is specified as the model name, then all Stan
programs in `minipdb.parquet` will be written as requested.  Hence,

```
minipdb write inference ALL path/to/destination/directory
```

will write the inference information for every Stan program in the
MiniPDB database.
