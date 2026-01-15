import psycopg2
try:
    # Test with the shadowcore user and new password
    conn = psycopg2.connect(
        host="localhost",
        database="shadowcore",
        user="shadowcore",
        password="your_secure_password"  # Use the password you just set
    )
    print("✅ SUCCESS: Connected to PostgreSQL as 'shadowcore' user!")
    
    # Test basic queries
    cursor = conn.cursor()
    
    # Check current user and database
    cursor.execute("SELECT current_user, current_database();")
    user, db = cursor.fetchone()
    print(f"   User: {user}, Database: {db}")
    
    # Check tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    if tables:
        print(f"   Tables found: {', '.join(tables)}")
    else:
        print("   No tables found in 'public' schema.")
        print("   Creating a test table 'iocs'...")
        cursor.execute("""
            CREATE TABLE iocs (
                id SERIAL PRIMARY KEY,
                type VARCHAR(50),
                value TEXT,
                risk_level VARCHAR(20)
            )
        """)
        conn.commit()
        print("   ✅ Test table created.")
    
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"❌ CONNECTION FAILED: {e}")
    print("\nPossible solutions:")
    print("1. Double-check the password you just set")
    print("2. Check PostgreSQL authentication method:")
    print("   sudo grep -A5 'local.*shadowcore' /etc/postgresql/*/main/pg_hba.conf")
    print("3. Try connecting as 'postgres' user with no password:")
    print("   python3 -c \"import psycopg2; conn=psycopg2.connect(host='localhost',dbname='shadowcore',user='postgres',password=''); print('Postgres user works')\"")
except Exception as e:
    print(f"❌ OTHER ERROR: {e}")
