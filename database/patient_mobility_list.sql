INSERT INTO [fyp_dev_john].[dbo].[PATIENT_MOBILITY_LIST] 
    (mobilityListId, IsDeleted, createdDate, modifiedDate, value) 
VALUES 
    (1, 0, '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 'Mobility List 1'),
    (2, 0, '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 'Mobility List 2'),
    (3, 0, '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 'Mobility List 3'),
    (4, 0, '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 'Mobility List 4'),
    (5, 0, '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 'Mobility List 5');
---
-- PATIENT_MOBILITY_PATIENT_MOBILITY_LIST
INSERT INTO [fyp_dev_john].[dbo].[PATIENT_MOBILITY_PATIENT_MOBILITY_LIST] 
    (patient_id, mobilityListId, createdDate, modifiedDate, createdById, modifiedById) 
VALUES 
    (1, 1, '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 1, 1),
    (2, 2, '2021-01-02 00:00:00.000', '2021-01-02 00:00:00.000', 2, 2),
    (3, 3, '2021-01-03 00:00:00.000', '2021-01-03 00:00:00.000', 3, 3),
    (4, 4, '2021-01-04 00:00:00.000', '2021-01-04 00:00:00.000', 4, 4),
    (5, 5, '2021-01-05 00:00:00.000', '2021-01-05 00:00:00.000', 5, 5);
