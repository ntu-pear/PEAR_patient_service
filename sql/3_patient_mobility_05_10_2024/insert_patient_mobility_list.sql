-- Insert realistic data into PATIENT_MOBILITY_LIST
INSERT INTO [dbo].[PATIENT_MOBILITY_LIST] (IsDeleted, Value, CreatedDateTime, ModifiedDateTime, CreatedById, ModifiedById)
VALUES 
    ('0', 'Cane', GETDATE(), GETDATE(), 1, 1),
    ('0', 'Crutches', GETDATE(), GETDATE(), 1, 1),
    ('0', 'Walkers', GETDATE(), GETDATE(), 1, 1),
    ('0', 'Gait trainers', GETDATE(), GETDATE(), 1, 1),
    ('0', 'Scooter', GETDATE(), GETDATE(), 1, 1),
    ('0', 'Wheelchairs', GETDATE(), GETDATE(), 1, 1);


