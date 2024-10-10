SET IDENTITY_INSERT patient_service_dev.dbo.PATIENT_GUARDIAN_RELATIONSHIP_MAPPING ON;
INSERT INTO patient_service_dev.dbo.PATIENT_GUARDIAN_RELATIONSHIP_MAPPING
(id, isDeleted , relationshipName , createdDate , modifiedDate , createdById , modifiedById)
VALUES
(1, 0, 'Husband', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1),
(2, 0, 'Wife', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1),
(3, 0, 'Child', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1),
(4, 0, 'Parent', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1),
(5, 0, 'Sibling', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1),
(6, 0, 'Grandchild', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1),
(7, 0, 'Friend', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1),
(8, 0, 'Nephew', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1),
(9, 0, 'Niece', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1),
(10, 0, 'Aunt', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1),
(11, 0, 'Uncle', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1),
(12, 0, 'Grandparent', '2024-01-01 00:00:00.000', '2024-01-01 00:00:00.000', 1, 1);

SET IDENTITY_INSERT patient_service_dev.dbo.PATIENT_GUARDIAN_RELATIONSHIP_MAPPING OFF;
