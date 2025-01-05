EXEC sp_rename '[dbo].[ALLERGY_TYPE].createdById', 'CreatedById', 'COLUMN';
EXEC sp_rename '[dbo].[ALLERGY_TYPE].modifiedById', 'ModifiedById', 'COLUMN';
EXEC sp_rename '[dbo].[ALLERGY_TYPE].Active', 'IsDeleted', 'COLUMN';

ALTER TABLE dbo.ALLERGY_TYPE
ADD CONSTRAINT DF_IsDeleted_Default2 DEFAULT (0) FOR IsDeleted;

UPDATE [dbo].[ALLERGY_TYPE]
SET [IsDeleted] = 0
WHERE [IsDeleted] = 1;