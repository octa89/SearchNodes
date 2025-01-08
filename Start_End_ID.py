import arcpy

# Set overwrite output to True to allow for reruns of the script
arcpy.env.overwriteOutput = True

# Set the workspace to your Geodatabase path
arcpy.env.workspace = r"C:\Users\octav\POSM Software Dropbox\POSM Software Dropbox\POSM Customer Projects\South Jordan UT\GIS\1.Mapreader from 111822\Data Package\data\POSM_DATA.gdb"

# Specify the name of your input table
in_table = "Lines"

# Get the spatial reference of the input table
input_spatial_ref = arcpy.Describe(in_table).spatialReference

# Fields to add and their respective geometry calculations
fields_and_geometries = {
    "USX": "LINE_START_X",
    "USY": "LINE_START_Y",
    "DSX": "LINE_END_X",
    "DSY": "LINE_END_Y"
}

# Additional fields to add without geometry calculations
additional_fields = {
    "StartID": "TEXT",
    "EndID": "TEXT"
}

# Function to check if a field exists
def field_exists(table, field_name):
    return any(field.name == field_name for field in arcpy.ListFields(table))

# Loop through the fields and geometries to add and calculate them
for field_name, geometry_attribute in fields_and_geometries.items():
    if not field_exists(in_table, field_name):
        arcpy.management.AddField(in_table, field_name, "FLOAT")
    # Calculate geometry attribute for the field using the input table's spatial reference
    arcpy.management.CalculateGeometryAttributes(
        in_table,
        [[field_name, geometry_attribute]],
        coordinate_system=input_spatial_ref
    )

# Add additional fields (StartID and EndID)
for field_name, field_type in additional_fields.items():
    if not field_exists(in_table, field_name):
        # Assuming a maximum character length of 50 for the IDs; adjust as necessary
        arcpy.management.AddField(in_table, field_name, field_type, field_length=50)

print("Fields and geometry calculations completed.")
