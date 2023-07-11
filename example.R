library(DBI)
library(RSQLite)
library(dplyr)

db <- DBI::dbConnect(RSQLite::SQLite(), "minipdb.sqlite")

df <- DBI::dbGetQuery(db, "SELECT * FROM 'arK-arK'")

dfp <- df %>%
    select(-starts_with("."))

dfp %>%
    summarize_all(mean)

dfp %>%
    summarize_all(sd)

DBI::dbDisconnect(db)
