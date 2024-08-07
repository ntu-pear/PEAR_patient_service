<!-- 
This is for the postgres
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=yourStrong@Password" -p 1435:1435 -d mcr.microsoft.com/mssql/server:2022-latest
go into the postgres and create your db 
-->

<!-- MSSQL -->
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=ILOVEFYP123!"    -p 1435:1433 --name sa --hostname sa    -d    mcr.microsoft.com/mssql/server:2022-latest

<!-- Run the patient service (FastAPI) -->
uvicorn app.main:app --reload