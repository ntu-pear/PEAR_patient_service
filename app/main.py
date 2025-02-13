import logging
import os
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError  # For handling database-related errors
from sqlalchemy.orm import clear_mappers
from .database import engine, Base
from app.models import (
    patient_allergy_mapping_model,  # Import all models to ensure they are registered
    patient_allocation_model,
    patient_attendance_model,
    patient_doctor_note_model,
    patient_guardian_model,
    patient_highlight_model,
    patient_list_model,
    patient_mobility_mapping_model,
    patient_list_language_model,
    patient_model,
    patient_photo_list_model,
    patient_photo_model,
    patient_prescription_list_model,
    patient_prescription_model,
    patient_social_history_model,
    patient_social_history_list_mapping_model,
    patient_vital_model,
    patient_mobility_list_model,
    patient_guardian_relationship_mapping_model,
    patient_patient_guardian_model,
    patient_assigned_dementia_list_model,
    patient_assigned_dementia_mapping_model,
    patient_list_language_model,
)
from app.routers import (
    allergy_reaction_type_router,
    allergy_type_router,
    patient_allergy_mapping_router,
    patient_doctor_note_router,
    patient_guardian_router,
    patient_highlight_router,
    patient_highlight_type_router,
    patient_list_router,
    patient_mobility_router,
    patient_photo_router,
    patient_prescription_router,
    patient_router,
    patient_social_history_router,
    patient_vital_router,
    patient_assigned_dementia_list_router,
    patient_assigned_dementia_mapping_router,
    patient_list_language_router,
    patient_mobility_mapping_router,
)
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

logger = logging.getLogger("uvicorn")

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
    logger.info("Database initialized successfully.")
except Exception as db_init_error:
    logger.error(f"Failed to initialize database: {str(db_init_error)}", exc_info=True)

API_VERSION_PREFIX = "/api/v1"  

app.include_router(patient_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Patients"])

app.include_router(
    allergy_type_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Allergy Types"]
)
app.include_router(
    allergy_reaction_type_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Allergy Reaction Types"]
)
app.include_router(
    patient_assigned_dementia_list_router.router, prefix=f"{API_VERSION_PREFIX}",tags=["Dementia List"]
)
app.include_router(
    patient_assigned_dementia_mapping_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Patient Assigned Dementia"]
)
app.include_router(
    patient_allergy_mapping_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Patient Allergies"]
)
app.include_router(
    patient_doctor_note_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Doctor Notes"]
)
app.include_router(patient_guardian_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Guardians"])

# highlights
app.include_router(
    patient_highlight_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Highlights"]
)
app.include_router(
    patient_highlight_type_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Highlights Type"]
)

app.include_router(
    patient_list_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Patient Lists"]
)
app.include_router(patient_list_language_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Language List"])
app.include_router(patient_mobility_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Mobility"])
app.include_router(patient_mobility_mapping_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Patient Mobility Mapping"])
app.include_router(patient_photo_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Photos"])
app.include_router(
    patient_prescription_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Prescriptions"]
)
app.include_router(
    patient_social_history_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Social History"]
)
app.include_router(patient_vital_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Vitals"])

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Patient API Testing"}
