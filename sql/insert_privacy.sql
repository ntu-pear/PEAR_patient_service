INSERT INTO patient_service_dev.dbo.PRIVACY_LEVEL_SETTING
(patientId, active, privacyLevelSensitive, createdDate, modifiedDate, createdById, modifiedById)
VALUES
(
1, -- patientId
1, -- active
'LOW', -- privacyLevelSensitive
'2001-01-01 00:00:00.000',  -- createdDate (using a valid minimum date)
'2024-01-01 00:00:00.000',  -- modifiedDate (set to a specific date and time)
1,  -- createdById (assuming this to be 1)
1   -- modifiedById (assuming this to be 1)
),

(
2, -- patientId
1, -- active
'LOW', -- privacyLevelSensitive
'2001-01-01 00:00:00.000',  -- createdDate (using a valid minimum date)
'2024-01-01 00:00:00.000',  -- modifiedDate (set to a specific date and time)
1,  -- createdById (assuming this to be 1)
1   -- modifiedById (assuming this to be 1)
),

(
3, -- patientId
1, -- active
'MEDIUM', -- privacyLevelSensitive
'2001-01-01 00:00:00.000',  -- createdDate (using a valid minimum date)
'2024-01-01 00:00:00.000',  -- modifiedDate (set to a specific date and time)
1,  -- createdById (assuming this to be 1)
1   -- modifiedById (assuming this to be 1)
),

(
4, -- patientId
1, -- active
'HIGH', -- privacyLevelSensitive
'2001-01-01 00:00:00.000',  -- createdDate (using a valid minimum date)
'2024-01-01 00:00:00.000',  -- modifiedDate (set to a specific date and time)
1,  -- createdById (assuming this to be 1)
1   -- modifiedById (assuming this to be 1)
)