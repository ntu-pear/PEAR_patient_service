ALTER TABLE patient_service_dev.dbo.PATIENT_GUARDIAN
DROP CONSTRAINT FK__PATIENT_G__relat__3B40CD36;

ALTER TABLE patient_service_dev.dbo.PATIENT_GUARDIAN
DROP CONSTRAINT FK__PATIENT_G__patie__3C34F16F;

ALTER TABLE patient_service_dev.dbo.PATIENT_GUARDIAN
DROP COLUMN patientId;

ALTER TABLE patient_service_dev.dbo.PATIENT_GUARDIAN
DROP COLUMN relationshipId;

ALTER TABLE patient_service_dev.dbo.PATIENT_GUARDIAN
DROP COLUMN status

ALTER TABLE patient_service_dev.dbo.PATIENT_GUARDIAN
ADD status varchar(255);

ALTER TABLE patient_service_dev.dbo.PATIENT_GUARDIAN
ADD isDeleted varchar(1) not null default '0'

SET IDENTITY_INSERT patient_service_dev.dbo.PATIENT_GUARDIAN ON;
INSERT INTO patient_service_dev.dbo.PATIENT_GUARDIAN
(id, active, status, firstName, lastName, preferredName, gender, contactNo, nric, email, dateOfBirth, address, tempAddress, guardianApplicationUserId, isDeleted, createdDate, modifiedDate, createdById, modifiedById)
VALUES
(
	1, -- id
	'1', -- active
	NULL, -- status
	'Tommy', --firstName
	'Lee', -- lastName
	'Tommy', -- preferredName
	'M', -- gender
	'97753383', -- contactNo
	'S7719748F', -- nric
	'tommylee111@gmail.com', -- email
	'1980-01-01 00:00:00.000', --dateOfBirth
	'235 Thomson Road #13-07 NOVENA SQUARE - TOWER A, 307684, Singapore', -- address
	'235 Thomson Road #13-07 NOVENA SQUARE - TOWER A, 307684, Singapore', -- tempAddress
	NULL, -- guardianApplicationUserId
	'0', --isDeleted
	'2021-01-01 00:00:00.000', -- createdDate
	'2021-01-01 00:00:00.000', -- modifiedDate
	'1', -- createdById
	'1' --modifiedById
),
(
	2, -- id
	'1', -- active
	NULL, -- status
	'Ying', --firstName
	'Yi', -- lastName
	'Ying', -- preferredName
	'F', -- gender
	'91234568', -- contactNo
	'S5157772H', -- nric
	'yingyi222@gmail.com', -- email
	'1980-01-01 00:00:00.000', --dateOfBirth
	'235 Thomson Road #13-07 NOVENA SQUARE - TOWER A, 307684, Singapore', -- address
	'235 Thomson Road #13-07 NOVENA SQUARE - TOWER A, 307684, Singapore', -- tempAddress
	NULL, -- guardianApplicationUserId
	'0', --isDeleted
	'2021-01-01 00:00:00.000', -- createdDate
	'2021-01-01 00:00:00.000', -- modifiedDate
	'1', -- createdById
	'1' --modifiedById
),
(
	3, -- id
	'1', -- active
	NULL, -- status
	'Dawn', --firstName
	'Ong', -- lastName
	'Dawn', -- preferredName
	'M', -- gender
	'98123912', -- contactNo
	'S1295237F', -- nric
	'dawnong333@gmail.com', -- email
	'1980-01-01 00:00:00.000', --dateOfBirth
	'235 Thomson Road #13-07 NOVENA SQUARE - TOWER A, 307684, Singapore', -- address
	'235 Thomson Road #13-07 NOVENA SQUARE - TOWER A, 307684, Singapore', -- tempAddress
	NULL, -- guardianApplicationUserId
	'0', --isDeleted
	'2021-01-01 00:00:00.000', -- createdDate
	'2021-01-01 00:00:00.000', -- modifiedDate
	'1', -- createdById
	'1' --modifiedById
),
(
	4, -- id
	'1', -- active
	NULL, -- status
	'Hilda', --firstName
	'Gong', -- lastName
	'Hilda', -- preferredName
	'F', -- gender
	'98123912', -- contactNo
	'S1295237F', -- nric
	'dawnong333@gmail.com', -- email
	'1980-01-01 00:00:00.000', --dateOfBirth
	'235 Thomson Road #13-07 NOVENA SQUARE - TOWER A, 307684, Singapore', -- address
	'235 Thomson Road #13-07 NOVENA SQUARE - TOWER A, 307684, Singapore', -- tempAddress
	NULL, -- guardianApplicationUserId
	'0', --isDeleted
	'2021-01-01 00:00:00.000', -- createdDate
	'2021-01-01 00:00:00.000', -- modifiedDate
	'1', -- createdById
	'1' --modifiedById
),
(
	5, -- id
	'1', -- active
	NULL, -- status
	'Charissaaa', --firstName
	'Mao', -- lastName
	'Charissaaa', -- preferredName
	'F', -- gender
	'98231391', -- contactNo
	'S4201328E', -- nric
	'charissamao555@gmail.com', -- email
	'1980-01-01 00:00:00.000', --dateOfBirth
	'235 Thomson Road #13-07 NOVENA SQUARE - TOWER A, 307684, Singapore', -- address
	'235 Thomson Road #13-07 NOVENA SQUARE - TOWER A, 307684, Singapore', -- tempAddress
	NULL, -- guardianApplicationUserId
	'0', --isDeleted
	'2021-01-01 00:00:00.000', -- createdDate
	'2021-01-01 00:00:00.000', -- modifiedDate
	'1', -- createdById
	'1' --modifiedById
);

SET IDENTITY_INSERT patient_service_dev.dbo.PATIENT_GUARDIAN OFF;