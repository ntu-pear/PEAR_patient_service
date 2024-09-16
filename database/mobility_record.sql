SET IDENTITY_INSERT [fyp_dev_john].[dbo].[PATIENT_MOBILITY] ON;

INSERT INTO [fyp_dev_john].[dbo].[PATIENT_MOBILITY] 
    (id, active, patient_id, mobilityListId, status, createdDate, modifiedDate, createdById, modifiedById) 
VALUES 
    (1, 'Y', 1, 1, 'Active', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 1, 1),
    (2, 'Y', 2, 2, 'Active', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 2, 2),
    (3, 'N', 3, 3, 'Inactive', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 3, 3),
    (4, 'Y', 4, 4, 'Active', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 4, 4),
    (5, 'N', 5, 5, 'Inactive', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 5, 5);

SET IDENTITY_INSERT [fyp_dev_john].[dbo].[PATIENT_MOBILITY] OFF;
