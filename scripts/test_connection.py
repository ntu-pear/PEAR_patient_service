import pyodbc

# Connection details
server = 'localhost,1433'  # Adjust the port if needed
database = 'master'  # Use 'master' to test the connection
username = 'sa'
password = 'ILOVEFYP123!'
driver = '{ODBC Driver 17 for SQL Server}'

try:
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT @@version;")
            row = cursor.fetchone()
            while row:
                print(row[0])
                row = cursor.fetchone()
    print("Connection successful.")
except Exception as e:
    print(f"Error: {e}")
