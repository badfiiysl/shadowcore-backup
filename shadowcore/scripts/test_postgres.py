import psycopg2
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",  # Try default first
        user="postgres",
        password=""
    )
    print("✅ PostgreSQL connected!")
    cursor = conn.cursor()
    cursor.execute("SELECT datname FROM pg_database;")
    dbs = cursor.fetchall()
    print(f"Databases: {[db[0] for db in dbs]}")
except Exception as e:
    print(f"❌ Error: {e}")
