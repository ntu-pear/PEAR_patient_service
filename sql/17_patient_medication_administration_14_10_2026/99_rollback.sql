-- Rollback for 01_create_table.sql. Only run if the feature is being removed:
-- this permanently deletes every recorded dose administration.
-- Switch MED_ADMIN_SYNC off in that environment first.

IF OBJECT_ID(N'dbo.PATIENT_MEDICATION_ADMINISTRATION', N'U') IS NOT NULL
    DROP TABLE dbo.PATIENT_MEDICATION_ADMINISTRATION;
GO
