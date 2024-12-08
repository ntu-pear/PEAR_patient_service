ALTER TABLE patient_service_dev.dbo.PATIENT_DOCTORNOTE
ADD isDeleted varchar(1) NOT NULL DEFAULT '0';

SET IDENTITY_INSERT patient_service_dev.dbo.PATIENT_DOCTORNOTE ON;
INSERT INTO patient_service_dev.dbo.PATIENT_DOCTORNOTE
(id, active, patientId, doctorId, doctorRemarks, isDeleted, createdDate, modifiedDate, createdById, modifiedById) 
VALUES
(1, 'Y', 1, 2, 'Patient is recovering well.', '0', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1),
(2, 'Y', 2, 1, 'Follow-up required in 2 weeks.', '0', '2024-01-02 00:00:00.000', '2024-01-02 00:00:00.000', 1, 1),
(3, 'Y', 3, 4, 'Prescribed medication adjustment.', '0', '2024-01-03 00:00:00.000', '2024-01-03 00:00:00.000', 1, 1),
(4, 'Y', 4, 3, 'Patient reported mild side effects.', '0', '2024-01-04 00:00:00.000', '2024-01-04 00:00:00.000', 1, 1),
(5, 'Y', 5, 5, 'Routine check-up completed.', '0', '2024-01-05 00:00:00.000', '2024-01-05 00:00:00.000', 1, 1);

SET IDENTITY_INSERT patient_service_dev.dbo.PATIENT_DOCTORNOTE OFF;