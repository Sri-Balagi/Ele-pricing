import sqlite3
conn = sqlite3.connect('elevator_config.db')
try:
    conn.execute("ALTER TABLE configurations ADD COLUMN customer_name VARCHAR DEFAULT ''")
    conn.commit()
    print("Migration successful")
except Exception as e:
    print(f"Error: {e}")
conn.close()
