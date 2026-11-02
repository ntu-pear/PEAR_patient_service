-- PATIENT_MEDICATION_ADMINISTRATION: one row per dose actually given.
-- A dose slot is (MedicationId, AdministerDate, ScheduledTime). At most one live
-- (IsDeleted = '0') row per slot; a supervisor "undo" soft-deletes the row so the
-- slot can be marked given again.
--
-- Safe to run more than once: each step checks whether it has already been applied.
-- Run on the Patient service database (staging first, then production) BEFORE
-- switching MED_ADMIN_SYNC on in that environment.

-- Stop if connected to a system database (e.g. the editor defaulted to master).
IF DB_NAME() IN (N'master', N'model', N'msdb', N'tempdb') OR OBJECT_ID(N'dbo.PATIENT_MEDICATION', N'U') IS NULL
BEGIN
    DECLARE @db SYSNAME = DB_NAME();
    RAISERROR(N'Wrong database (%s): switch to the Patient service database, which has PATIENT_MEDICATION, then re-run.', 16, 1, @db);
    SET NOEXEC ON;
END
GO

IF OBJECT_ID(N'dbo.PATIENT_MEDICATION_ADMINISTRATION', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.PATIENT_MEDICATION_ADMINISTRATION (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        MedicationId INT NOT NULL,
        PatientId INT NOT NULL,
        AdministerDate DATE NOT NULL,              -- the dose's day, in Singapore time
        ScheduledTime VARCHAR(5) NOT NULL,         -- slot from the course's AdministerTime, e.g. '08:00'
        ActualAdministerTime DATETIME NOT NULL,    -- when it was given, stored in UTC
        AdministeredById NVARCHAR(450) NOT NULL,   -- user id from the login token
        IsDeleted NVARCHAR(1) NOT NULL DEFAULT '0',
        CreatedDateTime DATETIME NOT NULL DEFAULT GETUTCDATE(),
        UpdatedDateTime DATETIME NOT NULL DEFAULT GETUTCDATE(),
        CreatedById NVARCHAR(450) NOT NULL,
        ModifiedById NVARCHAR(450) NOT NULL,

        CONSTRAINT FK_PatientMedicationAdministration_Medication
            FOREIGN KEY (MedicationId) REFERENCES dbo.PATIENT_MEDICATION(Id),
        CONSTRAINT FK_PatientMedicationAdministration_Patient
            FOREIGN KEY (PatientId) REFERENCES dbo.PATIENT(id)
    );
END
GO

-- One live record per dose slot (soft-deleted rows don't count).
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = N'UX_PatientMedicationAdministration_Slot'
      AND object_id = OBJECT_ID(N'dbo.PATIENT_MEDICATION_ADMINISTRATION')
)
BEGIN
    CREATE UNIQUE NONCLUSTERED INDEX UX_PatientMedicationAdministration_Slot
        ON dbo.PATIENT_MEDICATION_ADMINISTRATION (MedicationId, AdministerDate, ScheduledTime)
        WHERE IsDeleted = '0';
END
GO

-- Patient History looks records up by patient and date.
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_PatientMedicationAdministration_Patient_Date'
      AND object_id = OBJECT_ID(N'dbo.PATIENT_MEDICATION_ADMINISTRATION')
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_PatientMedicationAdministration_Patient_Date
        ON dbo.PATIENT_MEDICATION_ADMINISTRATION (PatientId, AdministerDate);
END
GO

SET NOEXEC OFF;
GO
