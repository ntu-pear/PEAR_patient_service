ALTER TABLE patient_service_dev.dbo.PATIENT_DOCTORNOTE
ADD isDeleted varchar(1) NOT NULL DEFAULT '0';

ALTER TABLE patient_service_dev.dbo.PATIENT_DOCTORNOTE
DROP COLUMN active;