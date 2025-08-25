import sqlite3

conn = sqlite3.connect('bible_verses.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)

# If no tables, the database might not be initialized
if not tables:
    print("Database is empty. Need to initialize with Bible verses data.")

conn.close()