SET IDENTITY_INSERT patient_service_dev.dbo.PATIENT ON;
INSERT INTO patient_service_dev.dbo.PATIENT
(id, active, name, nric, address, tempAddress, homeNo, handphoneNo, gender, dateOfBirth, guardianId, isApproved, preferredName, preferredLanguageId, updateBit, autoGame, startDate, endDate, isActive , isRespiteCare , terminationReason, inActiveReason , inActiveDate, profilePicture, createdDate, modifiedDate, createdById, modifiedById, privacyLevel)
VALUES
(
1,  -- id (was PatientID)
'1',  -- active (using '1' to represent active)
'Alice Lee',  -- name
'S1234567D',  -- nric
'71 KAMPONG BAHR ROAD 169373, SINGAPORE',  -- address
'WOODLANDS',  -- tempAddress
'63699859',  -- homeNo
'88888808',  -- handphoneNo
'F', --gender
'2001-01-01 00:00:00.000',  -- dateOfBirth (using a valid minimum date)
NULL,  -- guardianId (no corresponding data)
'1',  -- isApproved (assuming similar to active)
'ALICEE',  -- preferredName
3,  -- preferredLanguageId (was PreferredLanguageListID)
0,  -- updateBit
0,  -- autoGame
'2001-01-01 00:00:00.000',  -- startDate (using a valid minimum date)
NULL,  -- endDate
1,  -- isActive
1, -- isRespiteCare
NULL,  -- terminationReason (no corresponding data)
NULL,  -- inActiveReason (no corresponding data)
NULL,  -- inActiveDate (no corresponding data)
'https://res.cloudinary.com/dbpearfyp/image/upload/v1640487405/Patient/Alice_Lee_Sxxxx567D/ProfilePicture/zsw7dyprsvn0bjmatofg.jpg',  -- profilePicture
'2001-01-01 00:00:00.000',  -- createdDate (using a valid minimum date)
'2024-01-01 00:00:00.000',  -- modifiedDate (set to a specific date and time)
1,  -- createdById (assuming this to be 1)
1,   -- modifiedById (assuming this to be 1)
1 -- privacyLevel
),


(
2,  -- id (was PatientID)
'1',  -- active (using '1' to represent active)
'Yan Yi',  -- firstName
'S5090148C',  -- nric
'1000 ANSON ROAD #30-08 INTERNATIONAL PLAZA, 079903, SINGAPORE',  -- address
NULL,  -- tempAddress
'62260000',  -- homeNo
'90908563',  -- handphoneNo
'F', --gender
'1980-02-02 00:00:00.000',  -- dateOfBirth (using a valid minimum date)
NULL,  -- guardianId (no corresponding data)
'1',  -- isApproved (assuming similar to active)
'YY',  -- preferredName
2,  -- preferredLanguageId (was PreferredLanguageListID)
1,  -- updateBit
0,  -- autoGame
'2021-01-01 00:00:00.000',  -- startDate (using a valid minimum date)
NULL,  -- endDate
1,  -- isActive
0, -- isRespiteCare
NULL,  -- terminationReason (no corresponding data)
NULL,  -- inActiveReason (no corresponding data)
NULL,  -- inActiveDate (no corresponding data)
'https://res.cloudinary.com/dbpearfyp/image/upload/v1634521792/Patient/Yan_Yi_Sxxxx148C/ProfilePicture/g5gnecfsoc8igp56dwnb.jpg',  -- profilePicture
'2021-01-01 00:00:00.000',  -- createdDate (using a valid minimum date)
'2021-01-01 00:00:00.000',  -- modifiedDate (set to a specific date and time)
1,  -- createdById (assuming this to be 1)
1,   -- modifiedById (assuming this to be 1)
1 -- privacyLevel
),


(
3,  -- id (was PatientID)
'1',  -- active (using '1' to represent active)
'Jon Ong',  -- name
'S6421300H',  -- nric
'Blk 3007 Ubi Rd 1 05-412, 406701, Singapore',  -- address
NULL,  -- tempAddress
'67485000',  -- homeNo
'67489859',  -- handphoneNo
'M', --gender
'1980-03-03 00:00:00.000',  -- dateOfBirth (using a valid minimum date)
NULL,  -- guardianId (no corresponding data)
'1',  -- isApproved (assuming similar to active)
'Jon',  -- preferredName
3,  -- preferredLanguageId (was PreferredLanguageListID)
1,  -- updateBit
0,  -- autoGame
'2021-01-01 00:00:00.000',  -- startDate (using a valid minimum date)
NULL,  -- endDate
1,  -- isActive
0, -- isRespiteCare
NULL,  -- terminationReason (no corresponding data)
NULL,  -- inActiveReason (no corresponding data)
NULL,  -- inActiveDate (no corresponding data)
'https://res.cloudinary.com/dbpearfyp/image/upload/v1634522355/Patient/Jon_Ong_Sxxxx300H/ProfilePicture/arkceots9px0niro7iwh.jpg',  -- profilePicture
'2021-01-01 00:00:00.000',  -- createdDate (using a valid minimum date)
'2021-01-01 00:00:00.000',  -- modifiedDate (set to a specific date and time)
1,  -- createdById (assuming this to be 1)
1,   -- modifiedById (assuming this to be 1)
1 -- privacyLevel
),


(
4,  -- id (was PatientID)
'0',  -- active (using '1' to represent active)
'Bi Gong',  -- name
'S7866443F',  -- nric
'41 Sungei Kadut Loop S 729509, Singapore',  -- address
'42 Sungei Kadut Loop S 729509, Singapore',  -- tempAddress
'60608123',  -- homeNo
'98123144',  -- handphoneNo
'M', --gender
'1980-04-04 00:00:00.000',  -- dateOfBirth (using a valid minimum date)
NULL,  -- guardianId (no corresponding data)
'0',  -- isApproved (assuming similar to active)
'Bi',  -- preferredName
4,  -- preferredLanguageId (was PreferredLanguageListID)
0,  -- updateBit
0,  -- autoGame
'2021-01-01 00:00:00.000',  -- startDate (using a valid minimum date)
NULL,  -- endDate
1,  -- isActive
0, -- isRespiteCare
NULL,  -- terminationReason (no corresponding data)
NULL,  -- inActiveReason (no corresponding data)
NULL,  -- inActiveDate (no corresponding data)
'https://res.cloudinary.com/dbpearfyp/image/upload/v1634522583/Patient/Bi_Gong_Sxxxx443F/ProfilePicture/dwo0axohyhur5mp16lep.jpg',  -- profilePicture
'2021-01-01 00:00:00.000',  -- createdDate (using a valid minimum date)
'2021-01-01 00:00:00.000',  -- modifiedDate (set to a specific date and time)
1,  -- createdById (assuming this to be 1)
1,   -- modifiedById (assuming this to be 1)
1 -- privacyLevel
),


(
5,  -- id (was PatientID)
'1',  -- active (using '1' to represent active)
'Jeline Mao',  -- firstName
'S5862481J',  -- nric
'20 CECIL STREET #16-04 EQUITY PLAZA, 049705, SINGAPOR',  -- address
NULL,  -- tempAddress
'62312811',  -- homeNo
'92222811',  -- handphoneNo
'F', --gender
'1980-05-05 00:00:00.000',  -- dateOfBirth (using a valid minimum date)
NULL,  -- guardianId (no corresponding data)
'1',  -- isApproved (assuming similar to active)
'Jeline',  -- preferredName
5,  -- preferredLanguageId (was PreferredLanguageListID)
1,  -- updateBit
0,  -- autoGame
'2021-01-01 00:00:00.000',  -- startDate (using a valid minimum date)
NULL,  -- endDate
1,  -- isActive
0, -- isRespiteCare
NULL,  -- terminationReason (no corresponding data)
NULL,  -- inActiveReason (no corresponding data)
NULL,  -- inActiveDate (no corresponding data)
'https://res.cloudinary.com/dbpearfyp/image/upload/v1634522737/Patient/Jeline_Mao_Sxxxx481J/ProfilePicture/gm99nra8qfbc0dsnfrcu.jpg',  -- profilePicture
'2021-01-01 00:00:00.000',  -- createdDate (using a valid minimum date)
'2021-01-01 00:00:00.000',  -- modifiedDate (set to a specific date and time)
1,  -- createdById (assuming this to be 1)
1,   -- modifiedById (assuming this to be 1)
1 -- privacyLevel
)
;
SET IDENTITY_INSERT patient_service_dev.dbo.PATIENT OFF;

ALTER TABLE patient_service_dev.dbo.PATIENT ADD CONSTRAINT PATIENT_PATIENT_LIST_LANGUAGE_FK FOREIGN KEY (preferredLanguageId) REFERENCES patient_service_dev.dbo.PATIENT_LIST_LANGUAGE(id);