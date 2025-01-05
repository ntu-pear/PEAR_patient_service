from fastapi import FastAPI,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .database import engine, Base
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
)
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

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
    # Add other origins if needed
]


# middleware to connect to the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for Request Validations
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body},
    )


Base.metadata.create_all(bind=engine)

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
app.include_router(patient_mobility_router.router, prefix=f"{API_VERSION_PREFIX}", tags=["Mobility"])
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
    return {"message": "Welcome to the Patient API Testing"}
