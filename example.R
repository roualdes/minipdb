cwd <- getwd()
model_dir <- file.path(cwd, "models")
dir.create(model_dir)

library(cmdstanr)
library(DBI)
library(RSQLite)
library(jsonlite)
library(dplyr)

## TODO simplify to highlight just extraction of reference draws and then compre



cmdstanr::install_cmdstan()

db <- DBI::dbConnect(RSQLite::SQLite(), "minipdb.sqlite")

dfprogram <- DBI::dbGetQuery(db, "SELECT * FROM Program")

model_index <- 1
model_name <- dfprograms$model[model_index]

dfmeta <- DBI::dbGetQuery(db, "SELECT * FROM Meta")
info <- dfmeta[model_index, ]

cmdstanr::write_stan_file(dfprogram[model_index, "code"],
                          dir = file.path(model_dir, model_name),
                          basename = model_name,
                          force_overwrite = TRUE)

cmdstanr::write_stan_json(jsonlite::fromJSON(dfprogram[model_index, "data"]),
                          file = file.path(model_dir, model_name, paste0(model_name, ".json")))

stan_file <- file.path(model_dir, model_name, paste0(model_name, ".stan"))
mod <- cmdstanr::cmdstan_model(stan_file)
stan_data <- file.path(model_dir, model_name, paste0(model_name, ".json"))

fit <- mod$sample(data = stan_data,
                  iter_warmup = 2000,
                  iter_sampling = 2000,
                  chains = 4,
                  parallel_chains = 2,
                  adapt_delta = info$adapt_delta,
                  max_treedepth = info$max_treedepth,
                  sig_figs = info$sig_figs)

## compare current fit
fit$summary()

## to minidb reference draws
## TODO doesn't quite work, but why not
dfdraws <- DBI::dbGetQuery(db,
                           'SELECT * FROM :model',
                           params = list(model = "arK-arK"))

dfdraws %>%
    select(-starts_with(".")) %>%
    colMeans
