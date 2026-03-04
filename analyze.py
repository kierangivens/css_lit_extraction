import sqlite3
import pandas as pd

def basic_overview():
    print("Loading data from SQLite...\n")
    
    # Connect and load the data
    conn = sqlite3.connect('aigc_research_full.db')
    df = pd.read_sql_query("SELECT * FROM papers", conn)
    conn.close()

    print("="*40)
    print(" 📊 DATASET OVERVIEW")
    print("="*40)

    # 1. Size and Scope
    print(f"Total Papers: {len(df)}")
    print(f"Columns: {', '.join(df.columns)}\n")

    # 2. Publication Years
    print("--- BREAKDOWN BY YEAR ---")
    # Sorts the years from newest to oldest
    print(df['year'].value_counts().sort_index(ascending=False).to_string())
    print("\n")

    # 3. Top Topics
    print("--- TOP 5 PRIMARY TOPICS ---")
    print(df['primary_topic'].value_counts().head(5).to_string())
    print("\n")

if __name__ == "__main__":
    basic_overview()