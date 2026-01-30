import sqlite3
from pathlib import Path

db_path = Path("H:\\bFactor Project\\bTeam\\bteam.db")
print(f"📁 Database: {db_path}")
print(f"   Size: {db_path.stat().st_size} bytes\n")

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f"📊 Tables ({len(tables)}):")

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"   ✓ {table}: {count} records")

# Show athletes details
if 'athletes' in tables:
    print("\n👥 Athletes:")
    cursor.execute('SELECT id, first_name, last_name, kj_per_hour_per_kg FROM athletes')
    for row in cursor.fetchall():
        print(f"   - {row[1]} {row[2]} (ID:{row[0]}, kJ/h/kg:{row[3]})")

conn.close()
