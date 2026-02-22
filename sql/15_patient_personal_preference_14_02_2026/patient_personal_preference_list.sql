-- ============================================================
-- PATIENT_PERSONAL_PREFERENCE_LIST
-- Reference/lookup table for preference types and items.
-- PreferenceType: 'LikesDislikes' | 'Habit' | 'Hobby'
-- ============================================================

CREATE TABLE PATIENT_PERSONAL_PREFERENCE_LIST (
    Id            INT            IDENTITY(1,1) PRIMARY KEY,
    PreferenceType NVARCHAR(50)  NOT NULL,          -- 'LikesDislikes', 'Habit', 'Hobby'
    PreferenceName NVARCHAR(255) NOT NULL,
    IsDeleted     VARCHAR(1)     NOT NULL DEFAULT '0',
    CreatedDate   DATETIME       NOT NULL DEFAULT GETDATE(),
    ModifiedDate  DATETIME       NOT NULL DEFAULT GETDATE(),
    CreatedByID   NVARCHAR(450)  NOT NULL,
    ModifiedByID  NVARCHAR(450)  NOT NULL,

    -- Prevent duplicate (type + name) combinations in active records
    CONSTRAINT UQ_PersonalPreferenceList_TypeName
        UNIQUE (PreferenceType, PreferenceName)
);

CREATE INDEX IX_PersonalPreferenceList_PreferenceType
    ON PATIENT_PERSONAL_PREFERENCE_LIST(PreferenceType);

CREATE INDEX IX_PersonalPreferenceList_IsDeleted
    ON PATIENT_PERSONAL_PREFERENCE_LIST(IsDeleted);

-- LikesDislikes
INSERT INTO PATIENT_PERSONAL_PREFERENCE_LIST
    (PreferenceType, PreferenceName, IsDeleted, CreatedDate, ModifiedDate, CreatedByID, ModifiedByID)
VALUES
    ('LikesDislikes', 'Animals/Pets/Wildlife',    '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Consume alcohol',           '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Cooking/Food',              '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Dance',                     '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Dirty environment',         '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Drama/Theatre',             '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Exercise/Sports',           '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Friends/Social activities', '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Gambling',                  '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Gardening/plants',          '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Movie/TV',                  '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Music/Singing',             '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Natural Scenery',           '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Noisy environment',         '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Reading',                   '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Religious activities',      '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Science/Technology',        '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Smoking',                   '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Travelling/Sightseeing',    '0', GETDATE(), GETDATE(), '1', '1'),
    ('LikesDislikes', 'Mannequin/Dolls',           '0', GETDATE(), GETDATE(), '1', '1');

-- Hobby
INSERT INTO PATIENT_PERSONAL_PREFERENCE_LIST
    (PreferenceType, PreferenceName, IsDeleted, CreatedDate, ModifiedDate, CreatedByID, ModifiedByID)
VALUES
    ('Hobby', 'Reading',       '0', GETDATE(), GETDATE(), '1', '1'),
    ('Hobby', 'Travelling',    '0', GETDATE(), GETDATE(), '1', '1'),
    ('Hobby', 'Fishing',       '0', GETDATE(), GETDATE(), '1', '1'),
    ('Hobby', 'Crafting',      '0', GETDATE(), GETDATE(), '1', '1'),
    ('Hobby', 'Television',    '0', GETDATE(), GETDATE(), '1', '1'),
    ('Hobby', 'Bird Watching', '0', GETDATE(), GETDATE(), '1', '1'),
    ('Hobby', 'Collecting',    '0', GETDATE(), GETDATE(), '1', '1'),
    ('Hobby', 'Music',         '0', GETDATE(), GETDATE(), '1', '1'),
    ('Hobby', 'Gardening',     '0', GETDATE(), GETDATE(), '1', '1'),
    ('Hobby', 'Video Games',   '0', GETDATE(), GETDATE(), '1', '1');

-- Habit
INSERT INTO PATIENT_PERSONAL_PREFERENCE_LIST
    (PreferenceType, PreferenceName, IsDeleted, CreatedDate, ModifiedDate, CreatedByID, ModifiedByID)
VALUES
    ('Habit', 'Biting Objects',        '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Licking Lips',          '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Crack Knuckles',        '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Daydreaming',           '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Fidget with Objects',   '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Frequent Toilet Visits','0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Hair Fiddling',         '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Talking to oneself',    '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Pick nose',             '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Skip meals',            '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Snacking',              '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Thumb Sucking',         '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Abnormal Sleep Cycle',  '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Worrying',              '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Scratch People',        '0', GETDATE(), GETDATE(), '1', '1'),
    ('Habit', 'Sleep Walking',         '0', GETDATE(), GETDATE(), '1', '1');