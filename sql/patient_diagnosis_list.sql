CREATE TABLE PATIENT_MEDICAL_DIAGNOSIS_LIST (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    DiagnosisName NVARCHAR(255) NOT NULL,
    IsDeleted VARCHAR(1) NOT NULL DEFAULT '0',
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NOT NULL DEFAULT GETDATE(),
    CreatedByID NVARCHAR(255) NOT NULL,
    ModifiedByID NVARCHAR(255) NOT NULL
);


-- Insertion codes for initial data
INSERT INTO PATIENT_MEDICAL_DIAGNOSIS_LIST
    (DiagnosisName, IsDeleted, CreatedByID, ModifiedByID)
VALUES
    ('Cardiovascular', '0', '1', '1'),
    ('Endocrine / Metabolic', '0', '1', '1'),
    ('Gastrointestinal', '0', '1', '1'),
    ('Mental Health', '0', '1', '1'),
    ('Musculoskeletal', '0', '1', '1'),
    ('Neurological', '0', '1', '1'),
    ('Renal / Urological', '0', '1', '1'),
    ('Respiratory', '0', '1', '1');