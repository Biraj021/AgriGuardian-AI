import sqlite3
conn = sqlite3.connect("agri_guardian.db")
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
print("Tables:", [t[0] for t in tables])
for t in tables:
    name = t[0]
    if name == "alembic_version":
        continue
    count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    print(f"  {name}: {count} rows")
conn.close()
