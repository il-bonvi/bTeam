import sqlite3
from pathlib import Path

for db_file in ['bteam.db', '../../../bTeamData/bteam.db']:
    try:
        db_path = Path(db_file)
        if not db_path.exists():
            print(f'❌ {db_file}: Non esiste')
            continue
            
        size = db_path.stat().st_size
        print(f'\n📁 {db_file} ({size} bytes)')
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f'   Tables: {len(tables)}')
        
        # Check athletes
        if any(t[0] == 'athletes' for t in tables):
            cursor.execute('SELECT COUNT(*) FROM athletes')
            count = cursor.fetchone()[0]
            print(f'   ✓ Athletes table: {count} records')
            
            if count > 0:
                cursor.execute('SELECT id, first_name, last_name FROM athletes LIMIT 3')
                for row in cursor.fetchall():
                    print(f'      - {row[1]} {row[2]} (ID:{row[0]})')
        
        conn.close()
    except Exception as e:
        print(f'❌ {db_file}: {e}')
