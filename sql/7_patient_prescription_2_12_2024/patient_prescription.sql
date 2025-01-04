INSERT INTO patient_service_dev.dbo.PATIENT_PRESCRIPTION (
    IsDeleted, PatientId, Dosage, FrequencyPerDay,
    Instruction, StartDate, EndDate, IsAfterMeal, PrescriptionRemarks,
    Status, CreatedDateTime, UpdatedDateTime, CreatedById, UpdatedById, PrescriptionListId
) VALUES
('1', 1, '500mg', 2, 'Take with water', '2024-12-01 08:00:00', '2024-12-15 08:00:00', '1', 'No remarks', 'Active', '2024-12-01 07:00:00', '2024-12-01 07:00:00', 1, 1, 1),
('1', 2, '250mg', 3, 'Before bed', '2024-12-02 09:00:00', '2024-12-16 09:00:00', '0', 'Take with care', 'Chronic', '2024-12-02 08:00:00', '2024-12-02 08:00:00', 1, 1, 2),
('1', 3, '1g', 1, 'Morning dose', '2024-12-03 10:00:00', '2024-12-17 10:00:00', '1', 'No remarks', 'Temporary', '2024-12-03 09:00:00', '2024-12-03 09:00:00', 1, 1, 3),
('1', 4, '2g', 4, 'Take with food', '2024-12-04 11:00:00', '2024-12-18 11:00:00', '0', 'Requires monitoring', 'Acute', '2024-12-04 10:00:00', '2024-12-04 10:00:00', 1, 1, 4),
('1', 5, '100mg', 2, 'At night', '2024-12-05 12:00:00', '2024-12-19 12:00:00', '1', 'Handle carefully', 'Chronic', '2024-12-05 11:00:00', '2024-12-05 11:00:00', 1, 1, 5);
