from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.patient_vital_model import PatientVital
from ..schemas.patient_vital import PatientVitalCreate, PatientVitalUpdate, PatientVitalDelete
from ..config import Config

config = Config().Vital

def get_latest_vital(db: Session, patient_id: int):
    return db.query(PatientVital).filter(PatientVital.PatientId == patient_id).order_by(PatientVital.CreatedDateTime.desc()).first()

def get_vital_list(db: Session, patient_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(PatientVital)
        .filter(PatientVital.PatientId == patient_id)
        .order_by(PatientVital.CreatedDateTime.desc())  # Ensure ordering before OFFSET and LIMIT
        .offset(skip)
        .limit(limit)
        .all()
    )
    
def create_vital(db: Session, vital: PatientVitalCreate):
    try:
        validate_vital_threshold(vital)
        
        db_vital = PatientVital(**vital.model_dump())
        db.add(db_vital)
        db.commit()
        db.refresh(db_vital)
        return db_vital
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def update_vital(db: Session, vital_id: int, vital: PatientVitalUpdate):
    try:
        validate_vital_threshold(vital)
        
        db_vital = db.query(PatientVital).filter(PatientVital.Id == vital_id).first()
        if db_vital:
            for key, value in vital.model_dump().items():
                if key == "UpdatedDateTime":
                    setattr(db_vital, key, datetime.now())
                else:
                    setattr(db_vital, key, value)
            db.commit()
            db.refresh(db_vital)
        return db_vital
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def delete_vital(db: Session, vital_id: int):
    db_vital = db.query(PatientVital).filter(PatientVital.Id == vital_id).first()
    if db_vital:
        setattr(db_vital, "IsDeleted", "1")
        db.commit()
        db.refresh(db_vital)
    return db_vital

def validate_vital_threshold(vital: PatientVitalCreate):
    if (vital.Temperature < config.Temperature.MIN_VALUE) or (vital.Temperature > config.Temperature.MAX_VALUE):
        raise ValueError(f"Temperature must be between {config.Temperature.MIN_VALUE} and {config.Temperature.MAX_VALUE}")
    if (vital.SystolicBP < config.SystolicBP.MIN_VALUE) or (vital.SystolicBP > config.SystolicBP.MAX_VALUE):
        raise ValueError(f"Systolic blood pressure must be between {config.SystolicBP.MIN_VALUE} and {config.SystolicBP.MAX_VALUE}")
    if (vital.DiastolicBP < config.DiastolicBP.MIN_VALUE) or (vital.DiastolicBP > config.DiastolicBP.MAX_VALUE):
        raise ValueError(f"Diastolic blood pressure must be between {config.DiastolicBP.MIN_VALUE} and {config.DiastolicBP.MAX_VALUE}")
    if (vital.SpO2 < config.SpO2.MIN_VALUE) or (vital.SpO2 > config.SpO2.MAX_VALUE):
        raise ValueError(f"SpO2 must be between {config.SpO2.MIN_VALUE} and {config.SpO2.MAX_VALUE} breaths per minute")
    if (vital.BloodSugarLevel < config.BloodSugarLevel.MIN_VALUE) or (vital.BloodSugarLevel > config.BloodSugarLevel.MAX_VALUE):
        raise ValueError(f"Blood sugar level must be between {config.BloodSugarLevel.MIN_VALUE} and {config.BloodSugarLevel.MAX_VALUE}")
    # if (vital.BloodSugarLevel < config.BslBeforeMeal.MIN_VALUE) or (vital.BloodSugarLevel > config.BslBeforeMeal.MAX_VALUE):
    #     raise ValueError(f"Blood sugar level before meal must be between {config.BslBeforeMeal.MIN_VALUE} and {config.BslBeforeMeal.MAX_VALUE}")
    # if (vital.BloodSugarLevel < config.BslAfterMeal.MIN_VALUE) or (vital.BloodSugarLevel > config.BslAfterMeal.MAX_VALUE):
    #     raise ValueError(f"Blood sugar level after meal must be between {config.BslAfterMeal.MIN_VALUE} and {config.BslAfterMeal.MAX_VALUE}")
    # if (vital.HeartRate < config.HeartRate.MIN_VALUE) or (vital.HeartRate > config.HeartRate.MAX_VALUE):
        raise ValueError(f"Heart rate must be between {config.HeartRate.MIN_VALUE} and {config.HeartRate.MAX_VALUE}")