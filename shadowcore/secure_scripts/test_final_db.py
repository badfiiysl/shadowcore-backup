import psycopg2
try:
    conn = psycopg2.connect(
        host="localhost",
        database="shadowcore",
        user="shadowcore",
        password="your_secure_password"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print("✅ PostgreSQL: Connected")
    print(f"   Version: {version.split()[0]}")
except Exception as e:
    print(f"❌ PostgreSQL: {e}")
