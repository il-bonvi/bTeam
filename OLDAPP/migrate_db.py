#!/usr/bin/env python3
"""Migrazione database per aggiungere colonne a race_athletes"""
import sqlite3
from pathlib import Path

# Cerca il database
db_paths = [
    Path.home() / '.bteam' / 'bteam.db',
    Path.cwd() / 'bteam.db',
]

db_path = None
for path in db_paths:
    if path.exists():
        db_path = path
        break

if not db_path:
    print('[!] Database non trovato')
    exit(1)

print(f'[bTeam] Database: {db_path}')

# Connetti e aggiungi le colonne
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE race_athletes ADD COLUMN kj_per_hour_per_kg REAL DEFAULT 10.0')
    print('[✓] Colonna kj_per_hour_per_kg aggiunta')
except sqlite3.OperationalError as e:
    print(f'[!] kj_per_hour_per_kg: {e}')

try:
    cursor.execute('ALTER TABLE race_athletes ADD COLUMN objective TEXT DEFAULT "C"')
    print('[✓] Colonna objective aggiunta')
except sqlite3.OperationalError as e:
    print(f'[!] objective: {e}')

conn.commit()
conn.close()
print('[✓] Database aggiornato con successo!')
