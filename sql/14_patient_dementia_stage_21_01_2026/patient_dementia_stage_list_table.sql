CREATE TABLE PATIENT_DEMENTIA_STAGE_LIST (
    id INT IDENTITY(1,1) PRIMARY KEY,
    DementiaStage NVARCHAR(50) NOT NULL,
    IsDeleted NVARCHAR(1) NOT NULL DEFAULT '0',
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NOT NULL DEFAULT GETDATE(),
    CreatedById NVARCHAR(255) NOT NULL,
    ModifiedById NVARCHAR(255) NOT NULL
);

INSERT INTO PATIENT_DEMENTIA_STAGE_LIST (DementiaStage, IsDeleted, CreatedDate, ModifiedDate, CreatedById, ModifiedById)
VALUES 
    ('Mild', '0', GETDATE(), GETDATE(), '1', '1'),
    ('Moderate', '0', GETDATE(), GETDATE(), '1', '1'),
    ('Severe', '0', GETDATE(), GETDATE(), '1', '1');