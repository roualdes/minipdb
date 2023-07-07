library(posteriordb)
library(dplyr)
library(DBI)
library(RSQLite)
library(jsonlite)
library(rlang)
library(httr)

pdb <- posteriordb::pdb_github()
models <- posteriordb::posteriors_tbl_df(pdb)
db <- DBI::dbConnect(RSQLite::SQLite(), "minipdb.sqlite")

dfprograms <- data.frame()
dfmeta <- data.frame()
for (r in seq_len(nrow(models))) {
    model_name <- dplyr::pull(models[r, "name"])
    po <- posteriordb::posterior(model_name, pdb)
    model_draws <- tryCatch({
        posteriordb::reference_posterior_draws(po)
    },
        error = function(e) {})
    if (!is.null(model_draws)) {
        dfprograms <- bind_rows(dfprograms,
                                data.frame(model_name,
                                           code = as.character(posteriordb::stan_code(po)),
                                           data = as.character(jsonlite::toJSON(posteriordb::pdb_data(po)))
                                           ))

        info <- posteriordb::reference_posterior_draws_info(po)$inference$method_arguments

        iter_warmup <- info$warmup %||% 10000
        iter_sampling <- info$iter %||% 10000
        chains <- info$chains %||% 10
        parallel_chains <- chains
        thin <- info$thin %||% 10
        seed <- info$seed %||% 204
        adapt_delta <- info$control$adapt_delta %||% 0.8
        max_treedepth <- info$control$max_treedepth %||% 10
        sig_figs <- 16

        dfmeta <- dplyr::bind_rows(dfmeta,
                            data.frame(model_name = model_name,
                                       iter_warmup = iter_warmup,
                                       iter_sampling = iter_sampling,
                                       chains = chains,
                                       parallel_chains = parallel_chains,
                                       thin = thin,
                                       seed = seed,
                                       adapt_delta = adapt_delta,
                                       max_treedepth = max_treedepth,
                                       sig_figs = sig_figs
                                       ))
    }
}

dfprograms <- dplyr::distinct(dfprograms, model_name, .keep_all = TRUE)
DBI::dbWriteTable(db, "Program", dfprograms, overwrite = TRUE)

dfmeta <- dplyr::distinct(dfmeta, model_name, .keep_all = TRUE)
DBI::dbWriteTable(db, "Meta", dfmeta, overwrite = TRUE)
