from fastapi import FastAPI
from .database import engine, Base
from app.routers import (
    patient_allergy_router,
    patient_assigned_dementia_router,
    patient_doctor_note_router,
    patient_guardian_router,
    patient_highlight_router,
    patient_list_router,
    patient_mobility_router,
    patient_photo_router,
    patient_prescription_router,
    patient_router,
    patient_social_history_router,
    patient_vital_router
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
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

Base.metadata.create_all(bind=engine)

# Include the routers with prefixes and tags
app.include_router(patient_router.router, prefix="/api/v1", tags=["patients"])
app.include_router(patient_allergy_router.router, prefix="/api/v1", tags=["allergies"])
# app.include_router(patient_assigned_dementia_router.router, prefix="/api/v1/", tags=["dementia"])
# app.include_router(patient_doctor_note_router.router, prefix="/api/v1/", tags=["doctor notes"])
# app.include_router(patient_guardian_router.router, prefix="/api/v1/", tags=["guardians"])
# app.include_router(patient_highlight_router.router, prefix="/api/v1/", tags=["highlights"])
# app.include_router(patient_list_router.router, prefix="/api/v1/", tags=["patient lists"])
# app.include_router(patient_mobility_router.router, prefix="/api/v1/", tags=["mobility"])
# app.include_router(patient_photo_router.router, prefix="/api/v1/", tags=["photos"])
# app.include_router(patient_prescription_router.router, prefix="/api/v1/", tags=["prescriptions"])
# app.include_router(patient_social_history_router.router, prefix="/api/v1/", tags=["social history"])
# app.include_router(patient_vital_router.router, prefix="/api/v1/", tags=["vitals"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Patient API hello"} 