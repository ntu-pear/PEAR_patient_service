-- Insert realistic data into PATIENT_MOBILITY_MAPPING
INSERT INTO [dbo].[PATIENT_MOBILITY_MAPPING] (PatientID, MobilityListId, MobilityRemarks, IsRecovered, IsDeleted, CreatedDateTime, ModifiedDateTime, CreatedById, ModifiedById)
VALUES 
    (1, 1, 'Not Recovered', 0, '0', GETDATE(), GETDATE(), 1, 1), 
    (2, 2, 'Not Recovered', 0, '0', GETDATE(), GETDATE(), 1, 1), 
    (3, 3, 'Not Recovered', 0, '0', GETDATE(), GETDATE(), 1, 1), 
    (4, 4, 'Not Recovered', 0, '0', GETDATE(), GETDATE(), 1, 1), 
    (5, 5, 'Not Recovered', 0, '0', GETDATE(), GETDATE(), 1, 1);