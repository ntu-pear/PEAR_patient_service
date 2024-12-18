INSERT INTO patient_service_dev.dbo.PATIENT_VITAL (
    PatientId,
    IsDeleted,
    IsAfterMeal,
    Temperature,
    SystolicBP,
    DiastolicBP,
    HeartRate,
    SpO2,
    BloodSugarlevel,
    Height,
    Weight,
    VitalRemarks,
    CreatedById,
    UpdatedById,
    CreatedDateTime,
    UpdatedDateTime
)
VALUES
    (1, '1', '1', 22.0, 22, 20, 23, 29, 60, 1.65, 60.5, 'well', 1, 1,GETDATE(), GETDATE()),
    (2, '0', '1', 24.5, 24, 22, 25, 30, 65, 1.70, 62.0, 'good', 1, 1,GETDATE(), GETDATE()),
    (3, '1', '1', 21.0, 21, 19, 22, 28, 58, 1.60, 59.0, 'average', 1, 1,GETDATE(), GETDATE()),
    (4, '0', '1', 23.5, 23, 21, 24, 31, 64, 1.68, 61.0, 'poor', 1, 1,GETDATE(), GETDATE()),
    (5, '1', '1', 20.0, 20, 18, 20, 27, 55, 1.75, 63.0, 'excellent', 1, 1,GETDATE(), GETDATE());
