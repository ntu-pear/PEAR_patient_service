EXEC sp_rename '[dbo].[PATIENT_HIGHLIGHT].[id]', 'Id', 'COLUMN';
EXEC sp_rename '[dbo].[PATIENT_HIGHLIGHT].[active]', 'IsDeleted', 'COLUMN';
EXEC sp_rename '[dbo].[PATIENT_HIGHLIGHT].[patientId]', 'PatientId', 'COLUMN';
EXEC sp_rename '[dbo].[PATIENT_HIGHLIGHT].[type]', 'Type', 'COLUMN';
EXEC sp_rename '[dbo].[PATIENT_HIGHLIGHT].[highlightJSON]', 'HighlightJSON', 'COLUMN';
EXEC sp_rename '[dbo].[PATIENT_HIGHLIGHT].[startDate]', 'StartDate', 'COLUMN';
EXEC sp_rename '[dbo].[PATIENT_HIGHLIGHT].[endDate]', 'EndDate', 'COLUMN';
EXEC sp_rename '[dbo].[PATIENT_HIGHLIGHT].[createdDate]', 'CreatedDate', 'COLUMN';
EXEC sp_rename '[dbo].[PATIENT_HIGHLIGHT].[modifiedDate]', 'ModifiedDate', 'COLUMN';
EXEC sp_rename '[dbo].[PATIENT_HIGHLIGHT].[createdById]', 'CreatedById', 'COLUMN';
EXEC sp_rename '[dbo].[PATIENT_HIGHLIGHT].[modifiedById]', 'ModifiedById', 'COLUMN';

-- Drop any existing default constraint on IsDeleted
DECLARE @ConstraintName NVARCHAR(128);
SELECT @ConstraintName = name
FROM sys.default_constraints
WHERE parent_object_id = OBJECT_ID('dbo.PATIENT_HIGHLIGHT') 
  AND col_name(parent_object_id, parent_column_id) = 'IsDeleted';

IF @ConstraintName IS NOT NULL
BEGIN
    EXEC('ALTER TABLE dbo.PATIENT_HIGHLIGHT DROP CONSTRAINT ' + @ConstraintName);
END

-- Add a new default constraint for IsDeleted
ALTER TABLE dbo.PATIENT_HIGHLIGHT
ADD CONSTRAINT DF_IsDeleted_Default4 DEFAULT (0) FOR IsDeleted;

INSERT INTO [dbo].[PATIENT_HIGHLIGHT] (
    IsDeleted, PatientId, Type, HighlightJSON, StartDate, EndDate, CreatedDate, ModifiedDate, CreatedById, ModifiedById
)
VALUES
    (0, 1, 'Allergy', '{"id":1,"value":"Shellfish"}', '2024-03-03T00:00:00', '2024-03-06T00:00:00', GETDATE(), GETDATE(), 1, 1),
    (0, 2, 'Prescription', '{"id":2,"value":"Paracetamol"}', '2024-03-11T00:00:00', '2024-03-14T00:00:00', GETDATE(), GETDATE(), 1, 1),
    (0, 3, 'VitalSign', '{"id":3,"value":"Details"}', '2024-03-11T00:00:00', '2024-03-14T00:00:00', GETDATE(), GETDATE(), 1, 1),
    (0, 4, 'Problem', '{"id":4,"value":"Behavior"}', '2024-03-12T00:00:00', '2024-03-15T00:00:00', GETDATE(), GETDATE(), 1, 1),
    (0, 5, 'ActivityExclusion', '{"id":5,"value":"Brisk Walking"}', '2024-03-12T00:00:00', '2024-03-15T00:00:00', GETDATE(), GETDATE(), 1, 1);
