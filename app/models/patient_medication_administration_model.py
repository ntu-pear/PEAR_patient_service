from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, Integer, String, Unicode, text

from app.database import Base


class PatientMedicationAdministration(Base):
    """One row per dose actually given. A slot is (MedicationId, AdministerDate, ScheduledTime);
    at most one live (IsDeleted='0') row per slot. Mirrors
    sql/17_patient_medication_administration_14_10_2026/01_create_table.sql."""

    __tablename__ = "PATIENT_MEDICATION_ADMINISTRATION"
    __table_args__ = (
        Index(
            "UX_PatientMedicationAdministration_Slot",
            "MedicationId", "AdministerDate", "ScheduledTime",
            unique=True,
            mssql_where=text("IsDeleted = '0'"),
        ),
        Index("IX_PatientMedicationAdministration_Patient_Date", "PatientId", "AdministerDate"),
    )

    Id = Column(Integer, primary_key=True)
    MedicationId = Column(Integer, ForeignKey("PATIENT_MEDICATION.Id"), nullable=False)
    PatientId = Column(Integer, ForeignKey("PATIENT.id"), nullable=False)
    AdministerDate = Column(Date, nullable=False)  # the dose's day, Singapore time
    ScheduledTime = Column(String(5), nullable=False)  # the course's slot spelling, e.g. "0800"
    ActualAdministerTime = Column(DateTime, nullable=False)  # UTC
    AdministeredById = Column(Unicode(450), nullable=False)
    IsDeleted = Column(Unicode(1), nullable=False, server_default=text("'0'"), default="0")
    CreatedDateTime = Column(DateTime, nullable=False, server_default=text("GETUTCDATE()"))
    UpdatedDateTime = Column(DateTime, nullable=False, server_default=text("GETUTCDATE()"))
    CreatedById = Column(Unicode(450), nullable=False)
    ModifiedById = Column(Unicode(450), nullable=False)