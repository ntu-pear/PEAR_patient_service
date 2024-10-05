-- Turn IDENTITY_INSERT ON for the PATIENT_SOCIAL_HISTORY table
SET IDENTITY_INSERT fyp_dev_john.dbo.PATIENT_SOCIAL_HISTORY ON;

-- Insert data into the PATIENT_SOCIAL_HISTORY table
INSERT INTO fyp_dev_john.dbo.PATIENT_SOCIAL_HISTORY (
    id, 
    active, 
    patientId, 
    sexuallyActive, 
    secondHandSmoker, 
    alcoholUse, 
    caffeineUse, 
    tobaccoUse, 
    drugUse, 
    exercise, 
    createdDate, 
    modifiedDate, 
    createdById, 
    modifiedById
) VALUES
(1, '1', 1, '1', '1', '0', '1', '0', '1', '1', '2021-01-01 00:00:00.000', '2024-04-29 15:35:57.350', 6, 10),
(2, '0', 2, '0', '0', '1', '0', '0', '0', '1', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 1, 2),
(3, '1', 3, '1', '1', '0', '0', '0', '0', '0', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 2, 2),
(4, '0', 4, '0', '0', '0', '0', '0', '0', '0', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 4, 2),
(5, '1', 5, '0', '0', '0', '0', '1', '1', '1', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 5, 2);

-- Turn IDENTITY_INSERT OFF for the PATIENT_SOCIAL_HISTORY table
--SET IDENTITY_INSERT fyp_dev_john.dbo.PATIENT_SOCIAL_HISTORY OFF;
-- SELECT id FROM fyp_dev_john.dbo.PATIENT;
