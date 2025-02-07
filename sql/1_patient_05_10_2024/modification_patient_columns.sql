-- Rename columns to PascalCase
-- EXEC sp_rename 'patient_service_dev.dbo.PATIENT.Id', 'id', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.Id', 'id', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.active', 'Active', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.name', 'Name', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.nric', 'Nric', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.address', 'Address', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.tempAddress', 'TempAddress', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.homeNo', 'HomeNo', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.handphoneNo', 'HandphoneNo', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.gender', 'Gender', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.dateOfBirth', 'DateOfBirth', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.guardianId', 'GuardianId', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.isApproved', 'IsApproved', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.preferredName', 'PreferredName', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.preferredLanguageId', 'PreferredLanguageId', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.updateBit', 'UpdateBit', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.autoGame', 'AutoGame', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.startDate', 'StartDate', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.endDate', 'EndDate', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.isActive', 'IsActive', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.isRespiteCare', 'IsRespiteCare', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.terminationReason', 'TerminationReason', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.inActiveReason', 'InActiveReason', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.inActiveDate', 'InActiveDate', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.profilePicture', 'ProfilePicture', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.createdDate', 'CreatedDate', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.modifiedDate', 'ModifiedDate', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.createdById', 'CreatedById', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.modifiedById', 'ModifiedById', 'COLUMN';
EXEC sp_rename 'patient_service_dev.dbo.PATIENT.privacyLevel', 'PrivacyLevel', 'COLUMN';

-- Change CreatedById and ModifiedById data type to NVARCHAR(255) (string)
ALTER TABLE patient_service_dev.dbo.PATIENT 
ALTER COLUMN CreatedById NVARCHAR(255) NOT NULL;

ALTER TABLE patient_service_dev.dbo.PATIENT 
ALTER COLUMN ModifiedById NVARCHAR(255) NOT NULL;
