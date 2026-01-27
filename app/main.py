import asyncio
import logging
import os
import threading
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError  # For handling database-related errors
from sqlalchemy.orm import clear_mappers

from app.messaging.consumer_manager import create_patient_consumer_manager
from app.models import (
    patient_allergy_mapping_model,  # Import all models to ensure they are registered
)
from app.models import (
    outbox_model,
    patient_allocation_model,
    patient_assigned_dementia_list_model,
    patient_assigned_dementia_mapping_model,
    patient_dementia_stage_list_model,
    patient_attendance_model,
    patient_doctor_note_model,
    patient_guardian_model,
    patient_guardian_relationship_mapping_model,
    patient_highlight_model,
    patient_list_diet_model,
    patient_list_education_model,
    patient_list_language_model,
    patient_list_livewith_model,
    patient_list_model,
    patient_list_occupation_model,
    patient_list_pet_model,
    patient_list_religion_model,
    patient_medication_model,
    patient_mobility_list_model,
    patient_mobility_mapping_model,
    patient_model,
    patient_patient_guardian_model,
    patient_photo_list_model,
    patient_photo_model,
    patient_prescription_list_model,
    patient_prescription_model,
    patient_social_history_model,
    patient_vital_model,
)
from app.routers import (
    allergy_reaction_type_router,
    allergy_type_router,
    integrity_router,
    outbox_router,
    patient_allergy_mapping_router,
    patient_allocation_router,
    patient_assigned_dementia_list_router,
    patient_assigned_dementia_mapping_router,
    patient_dementia_stage_list_router,
    patient_doctor_note_router,
    patient_guardian_router,
    patient_highlight_router,
    patient_highlight_type_router,
    patient_list_diet_router,
    patient_list_education_router,
    patient_list_language_router,
    patient_list_livewith_router,
    patient_list_occupation_router,
    patient_list_pet_router,
    patient_list_religion_router,
    patient_list_router,
    patient_medical_diagnosis_list_router,
    patient_medical_history_router,
    patient_medication_router,
    patient_mobility_mapping_router,
    patient_mobility_router,
    patient_photo_router,
    patient_prescription_list_router,
    patient_prescription_router,
    patient_privacy_level_router,
    patient_router,
    patient_social_history_router,
    patient_vital_router,
    social_history_sensitive_mapping_router,
)
from app.services.background_processor import get_processor

from .database import Base, engine

load_dotenv()

logger = logging.getLogger("uvicorn")

# Global consumer manager instance
consumer_manager = None
shutdown_event = threading.Event()


def start_consumers():
    """Start RabbitMQ consumers"""
    global consumer_manager
    
    # Check if messaging is enabled (can be controlled via environment variable)
    enable_messaging = os.getenv('ENABLE_MESSAGING', 'true').lower() == 'true'
    
    if not enable_messaging:
        logger.info("Drift consumer disabled via ENABLE_MESSAGING environment variable")
        return
    
    try:
        logger.info("Starting RabbitMQ drift consumer...")
        consumer_manager = create_patient_consumer_manager()
        
        # Pass shutdown event to consumer manager
        consumer_manager.set_shutdown_event(shutdown_event)
        
        # Start all registered consumers
        consumer_manager.start_all_consumers()
        
        logger.info("Drift consumer started successfully")
        
        # Log consumer status
        status = consumer_manager.get_consumer_status()
        for name, state in status.items():
            logger.info(f"Consumer {name}: {state}")
            
    except Exception as e:
        logger.error(f"Failed to start drift consumer: {str(e)}", exc_info=True)
        # Don't fail the entire application if messaging fails
        logger.warning("Application will continue without drift consumer")


def stop_consumers():
    """Stop RabbitMQ consumers"""
    global consumer_manager
    
    if consumer_manager:
        try:
            logger.info("Stopping RabbitMQ drift consumer...")
            consumer_manager.stop_all_consumers()
            logger.info("Drift consumer stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping drift consumer: {str(e)}")
    else:
        logger.info("No drift consumer to stop")


@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    """
    Combined lifespan manager that handles both:
    1. Outbox processor
    2. Drift consumer
    """
    # Startup phase
    logger.info("=== Application Startup ===")
    
    # Start outbox processor
    logger.info("Starting outbox processor...")
    processor = get_processor()
    processor_task = asyncio.create_task(processor.start())
    logger.info("Outbox processor started")
    
    # Start drift consumer
    logger.info("Starting drift consumer...")
    await asyncio.get_event_loop().run_in_executor(None, start_consumers)
    
    try:
        # Application is now running - yield control
        logger.info("=== Application Running ===")
        yield
    finally:
        # Shutdown phase
        logger.info("=== Application Shutdown ===")
        
        # Stop drift consumer first
        logger.info("Stopping drift consumer...")
        shutdown_event.set()
        await asyncio.get_event_loop().run_in_executor(None, stop_consumers)
        logger.info("Drift consumer stopped")
        
        # Stop outbox processor
        logger.info("Stopping outbox processor...")
        await processor.stop()
        if not processor_task.done():
            processor_task.cancel()
            try:
                await processor_task
            except asyncio.CancelledError:
                pass
        logger.info("Outbox processor stopped")


app = FastAPI(
    title="NTU FYP PEAR PATIENT SERVICE",
    description="This is the patient service api docs",
    version="1.0.0",
    servers=[],  # This removes the servers dropdown in Swagger UI
    lifespan=combined_lifespan,  # Use combined lifespan manager
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
        content={
            "detail": "Internal server error. Please contact People in charge of servers."
        },
    )


# Database setup
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully.")
except Exception as db_init_error:
    logger.error(f"Failed to initialize database: {str(db_init_error)}", exc_info=True)

API_VERSION_PREFIX = "/api/v1"

app.include_router(
    patient_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Patients"]
)
app.include_router(
    patient_allocation_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Patient Allocation"]
)
app.include_router(
    allergy_type_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Allergy Types"]
)
app.include_router(
    allergy_reaction_type_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Allergy Reaction Types"],
)
app.include_router(
    patient_assigned_dementia_list_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Dementia List"],
)
app.include_router(
    patient_assigned_dementia_mapping_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Patient Assigned Dementia"],
)
app.include_router(
    patient_allergy_mapping_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Patient Allergies"],
)
app.include_router(
    patient_doctor_note_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Doctor Notes"],
)
app.include_router(
    patient_guardian_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Guardians"]
)

# highlights
app.include_router(
    patient_highlight_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Highlights"]
)
app.include_router(
    patient_highlight_type_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Highlights Type"],
)

app.include_router(
    patient_list_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Patient Lists"]
)

# Social History
app.include_router(
    patient_social_history_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Social History"],
)
app.include_router(
    patient_list_diet_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Diet List"]
)
app.include_router(
    patient_list_education_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Education List"],
)
app.include_router(
    patient_list_livewith_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Live With List"],
)
app.include_router(
    patient_list_occupation_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Occupation List"],
)
app.include_router(
    patient_list_pet_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Pet List"]
)
app.include_router(
    patient_list_religion_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Religion List"],
)

app.include_router(
    patient_vital_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Vitals"]
)

app.include_router(
    patient_list_language_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Language List"],
)
app.include_router(
    patient_mobility_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Mobility"]
)
app.include_router(
    patient_mobility_mapping_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Patient Mobility Mapping"],
)

app.include_router(
    patient_prescription_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Prescriptions"],
)

app.include_router(
    patient_prescription_list_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Prescription List"],
)

app.include_router(
    patient_medication_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Medications"],
)

app.include_router(
    patient_privacy_level_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Privacy"],
)

app.include_router(
    social_history_sensitive_mapping_router.router,
    prefix=f"{API_VERSION_PREFIX}",
    tags=["Social History Sensitive Mapping"],
)
app.include_router(
    patient_medical_diagnosis_list_router.router, 
    prefix=f"{API_VERSION_PREFIX}", 
    tags=["Medical Diagnosis List"]
)

app.include_router(
    patient_medical_history_router.router, 
    prefix=f"{API_VERSION_PREFIX}", 
    tags=["Medical History"]
)

app.include_router(
    patient_dementia_stage_list_router.router, 
    prefix=f"{API_VERSION_PREFIX}", 
    tags=["Dementia Stage List"]
)

app.include_router(
    integrity_router.router,
    prefix=f"{API_VERSION_PREFIX}/integrity",
    tags=["Integrity"],
)

app.include_router(
    outbox_router.router
)

# Shift Photos route to below. Photos route catches / routes which interferes with most GET ALL routes.
app.include_router(
    patient_photo_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Photos"]
)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Patient API"}


@app.get("/health")
def health_check():
    """Health check endpoint that includes consumer status"""
    global consumer_manager
    
    health_status = {
        "status": "healthy",
        "database": "connected",
        "outbox_processor": "unknown",
        "drift_consumer": "unknown"
    }
    
    # Check outbox processor status
    try:
        processor = get_processor()
        if processor.is_running():
            health_status["outbox_processor"] = "running"
            health_status["outbox_stats"] = processor.get_stats()
        else:
            health_status["outbox_processor"] = "stopped"
    except Exception as e:
        health_status["outbox_processor"] = f"error: {str(e)}"
    
    # Check drift consumer status
    if consumer_manager:
        try:
            status = consumer_manager.get_consumer_status()
            if status:
                # Check if any consumer has errors
                has_errors = any(s.startswith("Error") for s in status.values())
                health_status["drift_consumer"] = "error" if has_errors else "running"
                health_status["consumer_details"] = status
            else:
                health_status["drift_consumer"] = "not_registered"
        except Exception as e:
            health_status["drift_consumer"] = f"error: {str(e)}"
    else:
        health_status["drift_consumer"] = "not_started"
    
    # Determine overall status
    if (health_status["drift_consumer"] == "error" or 
        health_status["outbox_processor"] == "error"):
        health_status["status"] = "degraded"
    
    return health_status
