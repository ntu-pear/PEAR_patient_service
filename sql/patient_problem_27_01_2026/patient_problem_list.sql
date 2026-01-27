CREATE TABLE PATIENT_PROBLEM_LIST (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    ProblemName NVARCHAR(255) NOT NULL,
    IsDeleted VARCHAR(1) NOT NULL DEFAULT '0',
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NOT NULL DEFAULT GETDATE(),
    CreatedByID NVARCHAR(450) NOT NULL,
    ModifiedByID NVARCHAR(450) NOT NULL
);

-- Insert initial problem types
INSERT INTO PATIENT_PROBLEM_LIST (ProblemName, IsDeleted, CreatedDate, ModifiedDate, CreatedByID, ModifiedByID)
VALUES 
    ('Behavior', '0', GETDATE(), GETDATE(), '1', '1'),
    ('Communication', '0', GETDATE(), GETDATE(), '1', '1'),
    ('Delusion', '0', GETDATE(), GETDATE(), '1', '1'),
    ('Emotion', '0', GETDATE(), GETDATE(), '1', '1'),
    ('Health', '0', GETDATE(), GETDATE(), '1', '1'),
    ('Memory', '0', GETDATE(), GETDATE(), '1', '1'),
    ('Sleep', '0', GETDATE(), GETDATE(), '1', '1');