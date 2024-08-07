# PEAR Patient Service

## Overview

PEAR Patient Service is a microservice for managing patient-related data. This repository provides the setup and development instructions to get the service running locally.

## Getting Started

### Prerequisites
1. **Git**: Ensure Git is installed on your system.
2. **Docker**: Install Docker and Docker Compose for container management.
3. **Conda**: Install Conda for managing virtual environments.

### Cloning the Repository
Clone the repository using the following command:

```bash
git clone https://github.com/ntu-pear/PEAR_patient_service.git
cd PEAR_patient_service
```

### Setting Up Your Environment
1. Create a Conda Virtual Environment:
```bash
conda create -n pear_patient_service python=3.8
conda activate pear_patient_service
```

2. Docker Setup:
- **Docker Compose:** Ensure you have Docker Compose installed.

3. Run Docker Containers:
- Use Docker Compose to build and start the containers:

```bash
docker-compose up --build
```

This will start the Local MSSQL and the microservice, which should be accessible at `http://localhost:8000`.

### Notes for Windows Users
Ensure that Visual Studio Code uses LF (Line Feed) instead of CRLF (Carriage Return Line Feed) for line endings.

### Troubleshooting
If you encounter issues with Docker Compose, such as missing `.sh` files, you may need to adjust Git's line ending settings:
```bash
git config core.autocrlf false
git rm --cached -r .
git reset --hard
```

After running these commands, you should see:
```bash
Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

This indicates that the service is running successfully.

### Additional Information

- Local MSSQL Database Name: `fyp_patient_service_local_db`
- Microservice Name: `patient_service`