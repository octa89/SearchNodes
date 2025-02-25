import arcpy

# Define the path to the geodatabase and the feature class/table
gdb_path = r"C:\Users\octav\POSM Software Dropbox\POSM Software Dropbox\POSM Customer Projects\Guilford Township\1. MapReader 110520\Data Package\data\dp00.gdb"
feature_class = "Sewers"  # Replace with your feature class or table name

# Set the full path to the feature class
fc_path = f"{gdb_path}\\{feature_class}"

# Add a new field for AssetID if it doesn't already exist
field_name = "AssetID"
if field_name not in [field.name for field in arcpy.ListFields(fc_path)]:
    arcpy.AddField_management(fc_path, field_name, "TEXT", field_length=255)

# Use an update cursor to calculate the AssetID field
with arcpy.da.UpdateCursor(fc_path, ["StartID", "EndID", field_name]) as cursor:
    for row in cursor:
        # Get StartID and EndID
        start_id = row[0]
        end_id = row[1]

        # Handle null values and concatenate
        start_id_str = str(start_id) if start_id is not None else ""
        end_id_str = str(end_id) if end_id is not None else ""
        row[2] = f"{start_id_str}_{end_id_str}"

        # Update the row
        cursor.updateRow(row)

print(f"AssetID field has been successfully calculated for {feature_class}.")
