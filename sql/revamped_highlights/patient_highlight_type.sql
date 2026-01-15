-- Create table to define different types of patient highlights
CREATE TABLE PATIENT_HIGHLIGHT_TYPE (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    TypeName NVARCHAR(100) NOT NULL,
    TypeCode NVARCHAR(50) NOT NULL UNIQUE,
    Description NVARCHAR(500) NULL,
    IsEnabled INT NOT NULL DEFAULT 1,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NOT NULL DEFAULT GETDATE(),
    IsDeleted INT NOT NULL DEFAULT 0,
    CreatedById NVARCHAR(450) NOT NULL,
    ModifiedById NVARCHAR(450) NOT NULL,
);