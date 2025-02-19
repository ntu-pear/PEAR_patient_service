-- Changing of types from int to STR

-- NOTE: I CHANGED TABLE NAME FOR EACH TABLE THAT NEEDED MODIFICATION AND RAN IT MULTIPLE TIMES.

DECLARE @TableName NVARCHAR(128) = 'ALLERGY_TYPE'; -- Change this to your table name

-- Step 1: Find and Drop the Default Constraints (if they exist)
DECLARE @sql NVARCHAR(MAX) = '';

-- Generate DROP CONSTRAINT commands dynamically
SELECT @sql += 'ALTER TABLE ' + QUOTENAME(@TableName) + ' DROP CONSTRAINT ' + QUOTENAME(dc.name) + ';' + CHAR(13)
FROM sys.default_constraints dc
JOIN sys.tables t ON dc.parent_object_id = t.object_id
WHERE t.name = @TableName
AND (dc.parent_column_id = COLUMNPROPERTY(OBJECT_ID(t.name), 'CreatedById', 'ColumnId')
     OR dc.parent_column_id = COLUMNPROPERTY(OBJECT_ID(t.name), 'ModifiedById', 'ColumnId'));

-- Execute the drop constraint statements
IF @sql <> ''
    EXEC sp_executesql @sql;

-- Step 2: Add new columns with VARCHAR type
SET @sql = '
ALTER TABLE ' + QUOTENAME(@TableName) + ' ADD CreatedByIdNew VARCHAR(50);
ALTER TABLE ' + QUOTENAME(@TableName) + ' ADD ModifiedByIdNew VARCHAR(50);';
EXEC sp_executesql @sql;

-- Step 3: Copy data from old INT columns to new VARCHAR columns
SET @sql = '
UPDATE ' + QUOTENAME(@TableName) + '
SET CreatedByIdNew = CAST(CreatedById AS VARCHAR(50)),
    ModifiedByIdNew = CAST(ModifiedById AS VARCHAR(50));';
EXEC sp_executesql @sql;

-- Step 4: Drop old columns
SET @sql = '
ALTER TABLE ' + QUOTENAME(@TableName) + ' DROP COLUMN CreatedById;
ALTER TABLE ' + QUOTENAME(@TableName) + ' DROP COLUMN ModifiedById;';
EXEC sp_executesql @sql;

-- Step 5: Rename new columns to the original column names
SET @sql = '
EXEC sp_rename ''' + @TableName + '.CreatedByIdNew'', ''CreatedById'', ''COLUMN'';
EXEC sp_rename ''' + @TableName + '.ModifiedByIdNew'', ''ModifiedById'', ''COLUMN'';';
EXEC sp_executesql @sql;


-- IF ANY CAMEL CASE COLUMN, RENAME TO PASCAL CASE COLUMNS

EXEC sp_rename 'PATIENT_ALLOCATION.createdById', 'CreatedById', 'COLUMN';
EXEC sp_rename 'PATIENT_ALLOCATION.modifiedById', 'ModifiedById', 'COLUMN';