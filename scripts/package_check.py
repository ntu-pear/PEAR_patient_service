import importlib.metadata

# List of packages to check
packages = [
    "fastapi",
    "pydantic",
    "psycopg2-binary",
    "databases",
    "sqlalchemy",
    "pyodbc",
    "uvicorn",
    "python-dotenv"
]

# Open requirements.txt in write mode
with open('requirements.txt', 'w') as f:
    for package in packages:
        try:
            # Get the version of the installed package
            version = importlib.metadata.version(package)
            # Write to requirements.txt
            f.write(f"{package}=={version}\n")
        except importlib.metadata.PackageNotFoundError:
            # If the package is not found, write an error message
            f.write(f"{package}==<not-installed>\n")
        except Exception as e:
            # Handle other exceptions
            f.write(f"{package}==<error: {str(e)}>\n")

print("Updated requirements.txt with current package versions.")
