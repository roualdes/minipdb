import duckdb as dk
import pandas as pd

import json

DBURL = "https://github.com/roualdes/minipdb/raw/duckdb/minipdb/minipdb.parquet"

df = dk.sql(f"SELECT * FROM '{DBURL}'").df()

print(json.loads(df["summary_stats"][0]))
