CREATE TABLE PATIENT_PROBLEM (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    PatientID INT NOT NULL,
    ProblemListID INT NOT NULL,
    DateOfDiagnosis DATE NULL,
    ProblemRemarks NVARCHAR(500) NULL,
    SourceOfInformation NVARCHAR(255) NULL,
    IsDeleted VARCHAR(1) NOT NULL DEFAULT '0',
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NOT NULL DEFAULT GETDATE(),
    CreatedByID NVARCHAR(450) NOT NULL,
    ModifiedByID NVARCHAR(450) NOT NULL,
    
    -- Foreign key constraints
    CONSTRAINT FK_PatientProblem_Patient 
        FOREIGN KEY (PatientID) REFERENCES PATIENT(id)
        ON DELETE CASCADE,
    CONSTRAINT FK_PatientProblem_ProblemList 
        FOREIGN KEY (ProblemListID) REFERENCES PATIENT_PROBLEM_LIST(Id)
);

-- Create indexes for better query performance
CREATE INDEX IX_PatientProblem_PatientID ON PATIENT_PROBLEM(PatientID);
CREATE INDEX IX_PatientProblem_ProblemListID ON PATIENT_PROBLEM(ProblemListID);
CREATE INDEX IX_PatientProblem_IsDeleted ON PATIENT_PROBLEM(IsDeleted);
CREATE INDEX IX_PatientProblemList_IsDeleted ON PATIENT_PROBLEM_LIST(IsDeleted);
