from sqlalchemy.orm import clear_mappers
from app.database import engine, Base

clear_mappers()

from app.models import (
    allergy_reaction_type_model,
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
    patient_list_diet_model,
    patient_list_education_model,
    patient_list_livewith_model,
    patient_list_occupation_model,
    patient_list_religion_model,
    patient_list_pet_model,
    patient_vital_model,
    patient_mobility_list_model,
    patient_guardian_relationship_mapping_model,
    patient_patient_guardian_model,
    patient_assigned_dementia_list_model,
    patient_assigned_dementia_mapping_model,
)

# Create all tables in the database using the engine
Base.metadata.create_all(bind=engine)

print("Tables created successfully in the DB_DATABASE_DEV database.")
