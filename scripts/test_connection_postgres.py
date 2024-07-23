import psycopg2
from psycopg2 import sql

# Connection details
host = "localhost"
port = 5432
database = "FYP"
user = "youruser"
password = "yourpassword"
# docker run --name postgres -e POSTGRES_PASSWORD=yourpassword -e POSTGRES_USER=youruser -e POSTGRES_DB=FYP -p 5432:5432 -d postgres:latest
try:
    # Establish the connection
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    
    # Create a cursor object
    cursor = conn.cursor()
    
    # Execute a simple query to test the connection
    cursor.execute("SELECT version();")
    
    # Fetch and print the result
    db_version = cursor.fetchone()
    print(f"PostgreSQL database version: {db_version}")
    
    # Close the cursor and connection
    cursor.close()
    conn.close()
    
    print("Connection successful.")
except Exception as error:
    print(f"Error: {error}")
