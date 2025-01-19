import logging
import os
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError  # For handling database-related errors
from sqlalchemy.orm import clear_mappers
from .database import engine, Base
from app.routers import (
    allergy_reaction_type_router,
    allergy_type_router,
    patient_allergy_mapping_router,
    patient_doctor_note_router,
    patient_guardian_router,
    patient_highlight_router,
    patient_list_router,
    patient_mobility_router,
    patient_photo_router,
    patient_prescription_router,
    patient_router,
    patient_social_history_router,
    patient_vital_router,
    patient_assigned_dementia_list_router,
    patient_assigned_dementia_mapping_router,
    patient_mobility_mapping_router,
)
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Logger Configuration
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)  # Create logs directory if it doesn't exist

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="NTU FYP PEAR PATIENT SERVICE",
    description="This is the patient service api docs",
    version="1.0.0",
    servers=[],  # This removes the servers dropdown in Swagger UI
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:5173",
    os.getenv("WEB_FE_ORIGIN"),
]

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to log requests and responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error occurred: {str(e)}", exc_info=True)
        raise
    logger.info(f"Response status: {response.status_code} for {request.method} {request.url}")
    return response

# Exception handler for request validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error at {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Exception handler for database errors
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error at {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please contact People in charge of servers."},
    )

# Database setup
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")
except Exception as db_init_error:
    logger.error(f"Failed to initialize database: {str(db_init_error)}", exc_info=True)

# Include the routers with prefixes and tags
app.include_router(patient_router.router, prefix="/api/v1", tags=["patients"])
app.include_router(patient_allergy_mapping_router.router, prefix="/api/v1", tags=["Patient Allergies"])
app.include_router(allergy_type_router.router, prefix="/api/v1", tags=["Allergy Types"])
app.include_router(allergy_reaction_type_router.router, prefix="/api/v1", tags=["Allergy Reaction Types"])
app.include_router(patient_assigned_dementia_list_router.router, prefix="/api/v1", tags=["Dementia List"])
app.include_router(patient_assigned_dementia_mapping_router.router, prefix="/api/v1", tags=["Patient Assigned Dementia"])
app.include_router(patient_doctor_note_router.router, prefix="/api/v1", tags=["doctor notes"])
app.include_router(patient_guardian_router.router, prefix="/api/v1", tags=["guardians"])
app.include_router(patient_highlight_router.router, prefix="/api/v1", tags=["highlights"])
app.include_router(patient_list_router.router, prefix="/api/v1", tags=["patient lists"])
app.include_router(patient_mobility_router.router, prefix="/api/v1", tags=["mobility"])
app.include_router(patient_mobility_mapping_router.router, prefix="/api/v1", tags=["Patient Mobility Mapping"])
app.include_router(patient_photo_router.router, prefix="/api/v1", tags=["photos"])
app.include_router(patient_prescription_router.router, prefix="/api/v1", tags=["prescriptions"])
app.include_router(patient_social_history_router.router, prefix="/api/v1", tags=["social history"])
app.include_router(patient_vital_router.router, prefix="/api/v1", tags=["vitals"])

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Patient API Testing"}
