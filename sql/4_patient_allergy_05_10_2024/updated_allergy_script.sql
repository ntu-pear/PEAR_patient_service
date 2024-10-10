CREATE TABLE [dbo].[ALLERGY_TYPE] (
    [AllergyTypeID]    INT            IDENTITY (1, 1) NOT NULL,
    [Active]           VARCHAR(1)    NOT NULL,  -- Renaming IsDeleted to Active
    [CreatedDateTime]  DATETIME2 (7)  NOT NULL,
    [UpdatedDateTime]  DATETIME2 (7)  NOT NULL,
    [Value]            NVARCHAR (256) NOT NULL,
    CONSTRAINT [PK_ALLERGY_TYPE] PRIMARY KEY CLUSTERED ([AllergyTypeID] ASC)
);

INSERT INTO [dbo].[ALLERGY_TYPE] (Active, CreatedDateTime, UpdatedDateTime, Value)
VALUES
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'To be updated'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'None'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Corn'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Eggs'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Fish'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Meat'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Milk'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Peanuts'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Tree nuts'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Shellfish'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Soy'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Wheat'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Seafood');

CREATE TABLE [dbo].[ALLERGY_REACTION_TYPE] (
    [AllergyReactionTypeID] INT            IDENTITY (1, 1) NOT NULL,
    [Active]                VARCHAR(1)     NOT NULL,  -- Renaming IsDeleted to Active
    [CreatedDateTime]       DATETIME2 (7)  NOT NULL,
    [UpdatedDateTime]       DATETIME2 (7)  NOT NULL,
    [Value]                 NVARCHAR (256) NOT NULL,
    CONSTRAINT [PK_ALLERGY_REACTION_TYPE] PRIMARY KEY CLUSTERED ([AllergyReactionTypeID] ASC)
);

INSERT INTO [dbo].[ALLERGY_REACTION_TYPE] (Active, CreatedDateTime, UpdatedDateTime, Value)
VALUES
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Rashes'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Sneezing'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Vomiting'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Nausea'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Swelling'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Difficulty Breathing'),
    (1, '2021-01-01T00:00:00', '2021-01-01T00:00:00', 'Diarrhoea'),
    (1, '2021-01-01 00:00:00.0000000', '2021-01-01 00:00:00.0000000', 'Abdominal cramp or pain'),
    (1, '2021-01-01 00:00:00.0000000', '2021-01-01 00:00:00.0000000', 'Nasal Congestion'),
    (1, '2021-01-01 00:00:00.0000000', '2021-01-01 00:00:00.0000000', 'Itching');

CREATE TABLE [dbo].[PATIENT_ALLERGY_MAPPING] (
    [Patient_AllergyID]      INT            IDENTITY (1, 1) NOT NULL,
    [PatientID]              INT            NOT NULL,
    [AllergyListID]          INT            NOT NULL,
    [AllergyReactionListID]  INT            NOT NULL,
    [AllergyRemarks]         NVARCHAR (MAX) NULL,
    [Active]                 VARCHAR(1)     NOT NULL DEFAULT(1),
    [CreatedDateTime]        DATETIME2 (7)  NOT NULL,
    [UpdatedDateTime]        DATETIME2 (7)  NOT NULL,
    CONSTRAINT [PK_Patient_Allergy_Mapping] PRIMARY KEY CLUSTERED ([Patient_AllergyID] ASC),
    CONSTRAINT [FK_Patient_Allergy_Mapping_Allergy_Types] FOREIGN KEY ([AllergyListID]) REFERENCES [dbo].[ALLERGY_TYPE] ([AllergyTypeID]) ON DELETE CASCADE,
    CONSTRAINT [FK_Patient_Allergy_Mapping_Allergy_Reaction_Types] FOREIGN KEY ([AllergyReactionListID]) REFERENCES [dbo].[ALLERGY_REACTION_TYPE] ([AllergyReactionTypeID]) ON DELETE CASCADE,
    CONSTRAINT [FK_Patient_Allergy_Mapping_PatientID] FOREIGN KEY ([PatientID]) REFERENCES [dbo].[Patient] ([id]) ON DELETE CASCADE
);

INSERT INTO [patient_service_dev].[dbo].[PATIENT_ALLERGY_MAPPING] (PatientID, AllergyListID, AllergyReactionListID, AllergyRemarks, Active, CreatedDateTime, UpdatedDateTime)
VALUES
    (1, 3, 1, 'Not well', 1, '2021-01-01T00:00:00', '2021-01-01T00:00:00'),
    (1, 4, 1, 'See doctor', 1, '2021-01-01T00:00:00', '2021-01-01T00:00:00'),
    (2, 5, 2, 'In serious condition', 1, '2021-01-01T00:00:00', '2021-01-01T00:00:00'),
    (3, 6, 3, 'Ok', 1, '2021-01-01T00:00:00', '2021-01-01T00:00:00'),
    (4, 7, 4, 'See doctor', 1, '2021-01-01T00:00:00', '2021-01-01T00:00:00'),
    (5, 8, 5, 'Sick', 1, '2021-01-01T00:00:00', '2021-01-01T00:00:00');

DROP TABLE [dbo].[PATIENT_ALLERGY];
