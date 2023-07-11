CREATE TABLE Program (
       "model_name" TEXT PRIMARY KEY,
       code TEXT NOT NULL UNIQUE,
       data TEXT NOT NULL,
       "last_run" TIMESTAMP
       );

CREATE TABLE Meta (
       "model_name" TEXT PRIMARY KEY,
       "iter_sampling" INTEGER NOT NULL,
       "iter_warmup" INTEGER NOT NULL,
       chains INTEGER NOT NULL,
       "parallel_chains" INTEGER NOT NULL,
       thin INTEGER NOT NULL,
       seed INTEGER NOT NULL,
       "adapt_delta" REAL NOT NULL,
       "max_treedepth" INTEGER NOT NULL,
       "sig_figs" INTEGER NOT NULL
);
