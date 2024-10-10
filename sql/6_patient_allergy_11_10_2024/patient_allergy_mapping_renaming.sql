-- Rename the column AllergyReactionListID to AllergyReactionTypeID
EXEC sp_rename 'dbo.PATIENT_ALLERGY_MAPPING.AllergyReactionListID', 'AllergyReactionTypeID', 'COLUMN';

-- Rename the column AllergyListID to AllergyTypeID
EXEC sp_rename 'dbo.PATIENT_ALLERGY_MAPPING.AllergyListID', 'AllergyTypeID', 'COLUMN';

-- Add createdById and modifiedById fields with a default value of 1 (assuming a default user)
ALTER TABLE dbo.PATIENT_ALLERGY_MAPPING
ADD createdById INT NOT NULL DEFAULT (1),
    modifiedById INT NOT NULL DEFAULT (1);