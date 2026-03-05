-- ============================================================
-- PATIENT_PERSONAL_PREFERENCE
-- Patient-level mapping to preference list items.
-- Includes an optional free-text "like/dislike" flag for
-- LikesDislikes type entries (IsLike: 'Y' | 'N' | NULL).
-- ============================================================

CREATE TABLE PATIENT_PERSONAL_PREFERENCE (
    Id                         INT           IDENTITY(1,1) PRIMARY KEY,
    PatientID                  INT           NOT NULL,
    PersonalPreferenceListID   INT           NOT NULL,
    IsLike                     VARCHAR(1)    NULL,       -- 'Y' = Like, 'N' = Dislike, NULL for Habit/Hobby
    PreferenceRemarks          NVARCHAR(500) NULL,
    IsDeleted                  VARCHAR(1)    NOT NULL DEFAULT '0',
    CreatedDate                DATETIME      NOT NULL DEFAULT GETDATE(),
    ModifiedDate               DATETIME      NOT NULL DEFAULT GETDATE(),
    CreatedByID                NVARCHAR(450) NOT NULL,
    ModifiedByID               NVARCHAR(450) NOT NULL,


    CONSTRAINT FK_PatientPersonalPreference_Patient
        FOREIGN KEY (PatientID)
        REFERENCES PATIENT(id)
        ON DELETE CASCADE,

    CONSTRAINT FK_PatientPersonalPreference_PreferenceList
        FOREIGN KEY (PersonalPreferenceListID)
        REFERENCES PATIENT_PERSONAL_PREFERENCE_LIST(Id)
);

CREATE INDEX IX_PatientPersonalPreference_PatientID
    ON PATIENT_PERSONAL_PREFERENCE(PatientID);

CREATE INDEX IX_PatientPersonalPreference_PreferenceListID
    ON PATIENT_PERSONAL_PREFERENCE(PersonalPreferenceListID);

CREATE INDEX IX_PatientPersonalPreference_IsDeleted
    ON PATIENT_PERSONAL_PREFERENCE(IsDeleted);