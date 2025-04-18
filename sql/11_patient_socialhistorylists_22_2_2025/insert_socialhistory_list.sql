-- DROP TABLES
DROP TABLE [dbo].PATIENT_SOCIAL_HISTORY

DROP TABLE [dbo].PATIENT_LIST_DIET
DROP TABLE [dbo].PATIENT_LIST_EDUCATION
DROP TABLE [dbo].PATIENT_LIST_LIVEWITH
DROP TABLE [dbo].PATIENT_LIST_OCCUPATION
DROP TABLE [dbo].PATIENT_LIST_PET
DROP TABLE [dbo].PATIENT_LIST_RELIGION

-- DROP TABLES
DROP TABLE [dbo].PATIENT_SOCIAL_HISTORY

DROP TABLE [dbo].PATIENT_LIST_DIET
DROP TABLE [dbo].PATIENT_LIST_EDUCATION
DROP TABLE [dbo].PATIENT_LIST_LIVEWITH
DROP TABLE [dbo].PATIENT_LIST_OCCUPATION
DROP TABLE [dbo].PATIENT_LIST_PET
DROP TABLE [dbo].PATIENT_LIST_RELIGION

-- PATIENT_LIST_DIET
INSERT INTO [dbo].[PATIENT_LIST_DIET] (IsDeleted, Value, CreatedDateTime, UpdatedDateTime, CreatedById, ModifiedById)
VALUES
    ('0', 'Not Available', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Diabetic', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Halal', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Vegan', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Vegetarian', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Gluten-free', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Soft food', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'No Cheese', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'No Peanuts', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'No Seafood', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'No Vegetables', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'No Meat', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'No Dairy', GETDATE(), GETDATE(), "1", "1");

-- PATIENT_LIST_EDUCATION
INSERT INTO [dbo].[PATIENT_LIST_EDUCATION] (IsDeleted, Value, CreatedDateTime, UpdatedDateTime, CreatedById, ModifiedById)
VALUES
    ('0', 'Not Available', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Primary or lower', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Secondary', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Diploma', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Junior College', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Degree', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Master', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Doctorate', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Vocational', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'ITE', GETDATE(), GETDATE(), "1", "1");

-- PATIENT_LIST_LIVEWITH
INSERT INTO [dbo].[PATIENT_LIST_LIVEWITH] (IsDeleted, Value, CreatedDateTime, UpdatedDateTime, CreatedById, ModifiedById)
VALUES
    ('0', 'Not Available', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Alone', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Children', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Friend', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Relative', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Spouse', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Family', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Parents', GETDATE(), GETDATE(), "1", "1");

-- PATIENT_LIST_OCCUPATION
INSERT INTO [dbo].[PATIENT_LIST_OCCUPATION] (IsDeleted, Value, CreatedDateTime, UpdatedDateTime, CreatedById, ModifiedById)
VALUES
    ('0', 'Not Available', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Accountant', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Business owner', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Chef/Cook', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Cleaner', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Clerk', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Dentist', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Doctor', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Driver', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Engineer', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Fireman', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Gardener', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Hawker', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Homemaker', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Housekeeper', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Labourer', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Lawyer', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Manager', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Mechanic', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Nurse', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Professional sportsperson', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Receptionist', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Sales person', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Secretary', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Security guard', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Teacher', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Trader', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Unemployed', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Vet', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Waiter', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Zoo keeper', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Artist', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Scientist', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Singer', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Policeman', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Actor', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Professor', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Florist', GETDATE(), GETDATE(), "1", "1");

-- PATIENT_LIST_PET
INSERT INTO [dbo].[PATIENT_LIST_PET] (IsDeleted, Value, CreatedDateTime, UpdatedDateTime, CreatedById, ModifiedById)
VALUES
    ('0', 'Not Available', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Bird', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Cat', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Dog', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Fish', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Hamster', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Rabbit', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Guinea Pig', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Hedgehog', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Tortoise', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Spider', GETDATE(), GETDATE(), "1", "1");

-- PATIENT_LIST_RELIGION
INSERT INTO [dbo].[PATIENT_LIST_RELIGION] (IsDeleted, Value, CreatedDateTime, UpdatedDateTime, CreatedById, ModifiedById)
VALUES
    ('0', 'Not Available', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Atheist', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Buddhist', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Catholic', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Christian', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Free Thinker', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Hindu', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Islam', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Taoist', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Judaism', GETDATE(), GETDATE(), "1", "1"),
    ('0', 'Confucianism', GETDATE(), GETDATE(), "1", "1");
