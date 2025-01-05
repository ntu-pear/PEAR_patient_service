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
