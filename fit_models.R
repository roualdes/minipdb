cwd <- getwd()
packages <- file.path(cwd, "packages")
dir.create(packages)

r <- getOption("repos")
r["CRAN"] <- "https://cloud.r-project.org"
install.packages(c("DBI", "RSQLite", "jsonlite"),
                 repos = r, lib = packages, destdir = packages)

install.packages("cmdstanr",
                 repos = "https://mc-stan.org/r-packages/",
                 lib = packages, destdir = packages)



library(cmdstanr, lib.loc = packages)
library(DBI, lib.loc = packages)
library(RSQLite, lib.loc = packages)
library(jsonlite, lib.loc = packages)

cmdstanr::install_cmdstan(dir = packages)
cmdstanr::set_cmdstan_path(path = packages)

db <- DBI::dbConnect(RSQLite::SQLite(), "minipdb.sqlite")

dfprograms <- DBI::dbGetQuery(db, "SELECT * FROM Program")
model_names <- dfprograms$model

dfmeta <- DBI::dbGetQuery(db, "SELECT * FROM Meta")

## possibly filter/reduce model_names, e.g.
## model_names <- model_names[1]

for (model_index in seq_along(model_names)) {
    model_name <- model_names[model_index]

    cmdstanr::write_stan_file(dfprograms[model_index, "code"],
                              dir = file.path(cwd, model_name),
                              basename = model_name,
                              force_overwrite = TRUE)

    cmdstanr::write_stan_json(jsonlite::fromJSON(dfprograms[model_index, "data"]),
                              file = file.path(cwd, model_name, paste0(model_name, ".json")))

    stan_file <- file.path(cwd, model_name, paste0(model_name, ".stan"))
    mod <- cmdstanr::cmdstan_model(stan_file)
    stan_data <- file.path(cwd, model_name, paste0(model_name, ".json"))

    info <- dfmeta[model_index, ]

    ## draws
    fit <- mod$sample(data = stan_data,
                      iter_warmup = info$iter_warmup,
                      iter_sampling = info$iter_sampling,
                      chains = info$chains,
                      parallel_chains = info$parallel_chains,
                      thin = info$thin,
                      seed = info$seed,
                      adapt_delta = info$adapt_delta,
                      max_treedepth = info$max_treedepth,
                      sig_figs = info$sig_figs)

    dfdraws <- as.data.frame(fit$draws(format = "draws_df"))
    DBI::dbWriteTable(db, model_name, dfdraws, overwrite = TRUE)

    ## diagnostics
    dfdiagnostics <- as.data.frame(fit$sampler_diagnostics())
    DBI::dbWriteTable(db, paste0(model_name, "_diagnostics"), dfdiagnostics, overwrite = TRUE)

    ## metric
    ## dims X chains
    dfmetric <- as.data.frame(lapply(fit$inv_metric(), diag))
    DBI::dbWriteTable(db, paste0(model_name, "_metric"), dfmetric, overwrite = TRUE)
}
