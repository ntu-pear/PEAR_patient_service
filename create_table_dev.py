from app.database import engine, Base
from app.models import (
    patient_allergy_model,  # Import all models to ensure they are registered
    patient_allocation_model,
    patient_assigned_dementia_model,
    patient_attendance_model,
    patient_doctor_note_model,
    patient_guardian_model,
    patient_highlight_model,
    patient_list_model,
    patient_mobility_model,
    patient_model,
    patient_photo_model,
    patient_prescription_model,
    patient_social_history_model,
    patient_social_history_list_mapping_model,
    patient_vital_model,
)

# Create all tables in the database using the engine
Base.metadata.create_all(bind=engine)

print("Tables created successfully in the DB_DATABASE_DEV database.")
