SET IDENTITY_INSERT patient_service_dev.dbo.PATIENT ON;

INSERT INTO PATIENT_MOBILITY (
    id, 
    active, 
    mobilityListId, 
    status, 
    createdDate, 
    modifiedDate, 
    createdById, 
    modifiedById
) VALUES
(1, 'Y', 1, 1, 'Not Recovered', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 0, 0),
(2, 'Y', 2, 2, 'Not Recovered', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 0, 0),
(3, 'Y', 3, 3, 'Not Recovered', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 0, 0),
(4, 'Y', 4, 4, 'Not Recovered', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 0, 0),
(5, 'Y', 5, 5, 'Not Recovered', '2021-01-01 00:00:00.000', '2021-01-01 00:00:00.000', 0, 0);

