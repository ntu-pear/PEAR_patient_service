CREATE TABLE PATIENT_MEDICAL_HISTORY (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    PatientID INT NOT NULL,
    MedicalDiagnosisID INT NOT NULL,
    DateOfDiagnosis DATE NULL,
    Remarks NVARCHAR(500) NULL,
    SourceOfInformation NVARCHAR(255) NULL,
    IsDeleted VARCHAR(1) NOT NULL DEFAULT '0',
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NOT NULL DEFAULT GETDATE(),
    CreatedByID NVARCHAR(255) NOT NULL,
    ModifiedByID NVARCHAR(255) NOT NULL,
    
    -- Foreign key constraints
    CONSTRAINT FK_PatientMedicalHistory_Patient 
        FOREIGN KEY (PatientID) REFERENCES PATIENT(id),
    CONSTRAINT FK_PatientMedicalHistory_Diagnosis 
        FOREIGN KEY (MedicalDiagnosisID) REFERENCES PATIENT_MEDICAL_DIAGNOSIS_LIST(Id)
);