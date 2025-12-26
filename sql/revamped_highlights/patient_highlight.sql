CREATE TABLE PATIENT_HIGHLIGHT (
    -- Primary Key
    Id INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Core Fields
    PatientId INT NOT NULL,                           -- FK to PATIENT table
    HighlightTypeId INT NOT NULL,                     -- FK to PATIENT_HIGHLIGHT_TYPE
    HighlightText NVARCHAR(500) NOT NULL,             -- Display text (e.g., "High BP: 180/110 mmHg")
    
    -- Source Tracking (links back to original record)
    SourceTable NVARCHAR(50) NOT NULL,                -- Table name (e.g., "PATIENT_VITAL")
    SourceRecordId INT NOT NULL,                      -- ID in source table
    
    -- Audit Fields
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NOT NULL DEFAULT GETDATE(),
    IsDeleted NVARCHAR(1) NOT NULL DEFAULT '0',       -- Soft delete ('0' = active, '1' = deleted)
    CreatedById NVARCHAR(450) NOT NULL,
    ModifiedById NVARCHAR(450) NOT NULL,
    
    -- Foreign Keys
    CONSTRAINT FK_PatientHighlight_Patient 
        FOREIGN KEY (PatientId) REFERENCES PATIENT(id)
        ON DELETE CASCADE,
    
    CONSTRAINT FK_PatientHighlight_Type 
        FOREIGN KEY (HighlightTypeId) REFERENCES PATIENT_HIGHLIGHT_TYPE(Id)
        ON DELETE CASCADE,
);