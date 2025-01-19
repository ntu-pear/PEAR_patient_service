EXEC sp_rename '[dbo].[ALLERGY_REACTION_TYPE].createdById', 'CreatedById', 'COLUMN';
EXEC sp_rename '[dbo].[ALLERGY_REACTION_TYPE].modifiedById', 'ModifiedById', 'COLUMN';
EXEC sp_rename '[dbo].[ALLERGY_REACTION_TYPE].Active', 'IsDeleted', 'COLUMN';

ALTER TABLE dbo.ALLERGY_REACTION_TYPE
ADD CONSTRAINT DF_IsDeleted_Default3 DEFAULT (0) FOR IsDeleted;

UPDATE [dbo].[ALLERGY_REACTION_TYPE]
SET [IsDeleted] = 0
WHERE [IsDeleted] = 1;