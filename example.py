import sqlite3
import pandas as pd

db = sqlite3.connect('minipdb.sqlite')

model_name = 'arK-arK'

df = pd.read_sql_query(f'SELECT * FROM "{model_name}"', db)

dfp = df.iloc[:, ~df.columns.str.startswith('.')]

dfp.mean()

dfp.std()

db.close()
