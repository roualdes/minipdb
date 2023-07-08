using DataFrames
using SQLite
using Statistics

db = SQLite.DB("minipdb.sqlite");

model_name = "arK-arK";

df = DataFrame(DBInterface.execute(db, "SELECT * FROM '$(model_name)'"));

combine(df,
        Cols(x -> !startswith(x, ".")) .=> x -> [mean(x); std(x)],
        renamecols = false)

DBInterface.close(db)
