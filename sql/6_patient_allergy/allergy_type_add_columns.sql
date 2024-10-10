-- Add createdById and modifiedById fields with a default value of 1 (assuming a default user)
ALTER TABLE dbo.ALLERGY_TYPE
ADD createdById INT NOT NULL DEFAULT (1),
    modifiedById INT NOT NULL DEFAULT (1);