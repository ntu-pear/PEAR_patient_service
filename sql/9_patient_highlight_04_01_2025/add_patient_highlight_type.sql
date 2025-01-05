-- Create the HighlightType table
CREATE TABLE [dbo].[PATIENT_HIGHLIGHT_TYPE] (
    [HighlightTypeID] INT IDENTITY (1, 1) NOT NULL,
    [Value] NVARCHAR (32) NOT NULL,
    [IsDeleted] BIT NOT NULL,
    [CreatedDateTime] DATETIME2 (7) NOT NULL,
    [UpdatedDateTime] DATETIME2 (7) NOT NULL,
    CONSTRAINT [PK_HighlightType] PRIMARY KEY CLUSTERED ([HighlightTypeID] ASC)
);

-- Insert mock data into the HighlightType table
INSERT INTO [dbo].[PATIENT_HIGHLIGHT_TYPE] ([Value], [IsDeleted], [CreatedDateTime], [UpdatedDateTime])
VALUES
    ('newPrescription', 0, '2021-01-01T00:00:00', '2021-01-01T00:00:00'),
    ('newAllergy', 0, '2021-01-01T00:00:00', '2021-01-01T00:00:00'),
    ('newActivityExclusion', 0, '2021-01-01T00:00:00', '2021-01-01T00:00:00'),
    ('abnormalVital', 0, '2021-01-01T00:00:00', '2021-01-01T00:00:00'),
    ('problem', 0, '2021-01-01T00:00:00', '2021-01-01T00:00:00'),
    ('medicalHistory', 0, '2021-01-01T00:00:00', '2021-01-01T00:00:00');

  -- Add CreatedById column with default value 1
ALTER TABLE [dbo].[PATIENT_HIGHLIGHT_TYPE]
ADD CreatedById INT NOT NULL DEFAULT (1);

-- Add ModifiedById column with default value 1
ALTER TABLE [dbo].[PATIENT_HIGHLIGHT_TYPE]
ADD ModifiedById INT NOT NULL DEFAULT (1);

  -- Alter the isDeleted column to VARCHAR(1) from BIT
ALTER TABLE [dbo].[PATIENT_HIGHLIGHT_TYPE]
ALTER COLUMN [IsDeleted] VARCHAR(1) NOT NULL;

-- Add a default value for IsDeleted as '0'
ALTER TABLE [dbo].[PATIENT_HIGHLIGHT_TYPE]
ADD CONSTRAINT DF_IsDeleted_Default5 DEFAULT ('0') FOR [IsDeleted];

ALTER TABLE PATIENT_HIGHLIGHT ALTER COLUMN PatientId INT NOT NULL;
