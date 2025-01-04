-- Drop the table if it exists
IF OBJECT_ID('dbo.PATIENT_ASSIGNED_DEMENTIA_LIST', 'U') IS NOT NULL
    DROP TABLE [dbo].[PATIENT_ASSIGNED_DEMENTIA_LIST];

-- Create the PATIENT_ASSIGNED_DEMENTIA_LIST table
CREATE TABLE [dbo].[PATIENT_ASSIGNED_DEMENTIA_LIST] (
    [DementiaTypeListId] INT IDENTITY(1, 1) NOT NULL,
    [IsDeleted]          VARCHAR(1) NOT NULL DEFAULT('0'), -- '0' for active, '1' for deleted
    [Value]              NVARCHAR(256) NOT NULL, -- Dementia type (e.g., Alzheimer's)
    [CreatedById]        INT NOT NULL,
    [ModifiedById]       INT NOT NULL,
    [CreatedDate]        DATETIME2(7) NOT NULL DEFAULT(GETDATE()),
    [ModifiedDate]       DATETIME2(7) NOT NULL DEFAULT(GETDATE()),
    CONSTRAINT [PK_PATIENT_ASSIGNED_DEMENTIA_LIST] PRIMARY KEY CLUSTERED ([DementiaTypeListId] ASC)
);

-- Insert realistic data into PATIENT_ASSIGNED_DEMENTIA_LIST
INSERT INTO [dbo].[PATIENT_ASSIGNED_DEMENTIA_LIST] (IsDeleted, Value, CreatedById, ModifiedById, CreatedDate, ModifiedDate)
VALUES 
    ('0', 'Alzheimer Disease', 1, 1, '2025-01-01T09:00:00.000', '2025-01-01T09:00:00.000'),
    ('0', 'Vascular Dementia', 2, 2, '2025-01-01T09:15:00.000', '2025-01-01T09:20:00.000'),
    ('0', 'Lewy Body Dementia', 3, 3, '2025-01-01T10:00:00.000', '2025-01-01T10:05:00.000'),
    ('0', 'Frontotemporal Dementia', 1, 2, '2025-01-01T11:00:00.000', '2025-01-01T11:10:00.000'),
    ('1', 'Mixed Dementia', 2, 3, '2025-01-01T12:00:00.000', '2025-01-01T12:30:00.000'); -- Marked as deleted

-- Create the PATIENT_ASSIGNED_DEMENTIA_MAPPING table
CREATE TABLE [dbo].[PATIENT_ASSIGNED_DEMENTIA_MAPPING] (
    [Id]                 INT IDENTITY(1, 1) NOT NULL,
    [IsDeleted]          VARCHAR(1) NOT NULL DEFAULT('0'), -- '0' for active, '1' for deleted
    [PatientId]          INT NOT NULL,
    [DementiaTypeListId] INT NOT NULL,
    [CreatedDate]        DATETIME2(7) NOT NULL DEFAULT(GETDATE()),
    [ModifiedDate]       DATETIME2(7) NOT NULL DEFAULT(GETDATE()),
    [CreatedById]        INT NOT NULL,
    [ModifiedById]       INT NOT NULL,
    CONSTRAINT [PK_PATIENT_ASSIGNED_DEMENTIA_MAPPING] PRIMARY KEY CLUSTERED ([Id] ASC),
    CONSTRAINT [FK_DementiaTypeListId] FOREIGN KEY ([DementiaTypeListId]) REFERENCES [dbo].[PATIENT_ASSIGNED_DEMENTIA_LIST] ([DementiaTypeListId]) ON DELETE CASCADE
);

-- Insert realistic data into PATIENT_ASSIGNED_DEMENTIA_MAPPING
INSERT INTO [dbo].[PATIENT_ASSIGNED_DEMENTIA_MAPPING] (IsDeleted, PatientId, DementiaTypeListId, CreatedDate, ModifiedDate, CreatedById, ModifiedById)
VALUES 
    ('0', 1, 1, '2025-01-02T09:00:00.000', '2025-01-02T09:15:00.000', 1, 1), -- Patient 101 assigned to Alzheimer's Disease
    ('0', 2, 2, '2025-01-02T10:00:00.000', '2025-01-02T10:20:00.000', 2, 2), -- Patient 102 assigned to Vascular Dementia
    ('0', 3, 3, '2025-01-03T11:00:00.000', '2025-01-03T11:30:00.000', 3, 3), -- Patient 103 assigned to Lewy Body Dementia
    ('0', 4, 4, '2025-01-03T12:00:00.000', '2025-01-03T12:45:00.000', 1, 2), -- Patient 104 assigned to Frontotemporal Dementia
    ('1', 5, 5, '2025-01-04T13:00:00.000', '2025-01-04T13:30:00.000', 2, 3); -- Patient 105 (deleted) assigned to Mixed Dementia
