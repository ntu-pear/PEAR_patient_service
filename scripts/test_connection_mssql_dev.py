import pyodbc

# Connection details to the DEV environment
server = '172.21.148.179,1433'  # Adjust the port if needed
database = 'patient_service_dev'  # Use 'master' to test the connection
username = 'fypcom_fypcom'
password = 'Fyppear@1'
driver = '{ODBC Driver 17 for SQL Server}'

try:
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    print(connection_string)
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
