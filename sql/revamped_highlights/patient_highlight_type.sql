-- Create table to define different types of patient highlights
CREATE TABLE PATIENT_HIGHLIGHT_TYPE (
    -- Primary Key
    Id INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Type Information
    TypeName NVARCHAR(100) NOT NULL,                  -- Human-readable name (e.g., "Vital Signs Alert")
    TypeCode NVARCHAR(50) NOT NULL UNIQUE,            -- Code for strategies (e.g., "VITAL", "ALLERGY")
    Description NVARCHAR(500) NULL,                   -- Optional description
    
    -- Configuration
    IsEnabled INT NOT NULL DEFAULT 1,                 -- Admin can enable/disable types
    
    -- Audit Fields
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NOT NULL DEFAULT GETDATE(),
    IsDeleted INT NOT NULL DEFAULT 0,
    CreatedById NVARCHAR(450) NOT NULL,
    ModifiedById NVARCHAR(450) NOT NULL,
);