import sqlite3
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).parent.parent

db_path = project_folder / "SQL" / "churn_analysis.db"
data_path = project_folder / "Data"

conn = sqlite3.connect(db_path)

users_df = pd.read_csv(data_path / "users.csv")
usage_df = pd.read_csv(data_path / "usage.csv")
tickets_df = pd.read_csv(data_path / "tickets.csv")

users_df.to_sql("users", conn, if_exists="replace", index=False)
usage_df.to_sql("usage", conn, if_exists="replace", index=False)
tickets_df.to_sql("tickets", conn, if_exists="replace", index=False)

conn.close()

print("All 3 tables imported successfully.")