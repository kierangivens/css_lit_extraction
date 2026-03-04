import sqlite3
import pandas as pd

# 1. Connect to your database
conn = sqlite3.connect('aigc_research_full.db')

# 2. Write and execute the SQL query
query = "SELECT title FROM papers LIMIT 50"
titles_df = pd.read_sql_query(query, conn)

conn.close()

# 3. Print the titles in a numbered list
print("\n--- FIRST 50 PAPER TITLES ---")
for index, title in enumerate(titles_df['title'], start=1):
    print(f"{index}. {title}")