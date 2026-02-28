#!/usr/bin/env python3
import sqlite3
import sys

sys.path.insert(0, 'webapp')

conn = sqlite3.connect('webapp/data/bteam.db')
cur = conn.cursor()

# Check if table exists
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='race_stages'")
table_exists = cur.fetchone() is not None
print(f'race_stages table exists: {table_exists}')

if table_exists:
    cur.execute('SELECT COUNT(*) FROM race_stages')
    count = cur.fetchone()[0]
    print(f'Stages count: {count}')
    
    if count > 0:
        cur.execute('SELECT id, race_id, stage_number, distance_km FROM race_stages LIMIT 5')
        for row in cur.fetchall():
            print(f'  Stage: {row}')

# Check races
cur.execute('SELECT id, name, num_stages FROM races LIMIT 3')
print('\nRaces:')
for row in cur.fetchall():
    print(f'  Race: {row}')

conn.close()
