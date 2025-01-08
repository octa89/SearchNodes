import arcpy

# Set overwrite output to True to allow for reruns of the script
arcpy.env.overwriteOutput = True

# Prompt for Geodatabase path and set it as the workspace
workspace = input("Enter the path to your geodatabase: ")

# Check if the workspace path exists
if not arcpy.Exists(workspace):
    raise ValueError("The specified geodatabase path does not exist.")

arcpy.env.workspace = workspace


# Function to list and select feature class
def list_and_select_feature_classes():
    feature_classes = arcpy.ListFeatureClasses()
    if not feature_classes:
        raise ValueError("No feature classes found in the specified geodatabase.")

    print("Available Feature Classes:")
    for idx, fc in enumerate(feature_classes, 1):
        print(f"{idx}. {fc}")

    while True:
        try:
            selected_index = int(input("Select a feature class by number: ")) - 1
            if 0 <= selected_index < len(feature_classes):
                return feature_classes[selected_index]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


# Selecting the feature class
in_table = list_and_select_feature_classes()
print(f"Selected feature class: {in_table}")

# Get the spatial reference of the input table
desc = arcpy.Describe(in_table)
input_spatial_ref = desc.spatialReference
print(f"Spatial reference: {input_spatial_ref.name}")

# Fields to add and their respective geometry calculations
fields_and_geometries = {
    "USX": "LINE_START_X",
    "USY": "LINE_START_Y",
    "DSX": "LINE_END_X",
    "DSY": "LINE_END_Y"
}

# Additional fields to ensure exist
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
        print(f"Adding field: {field_name}")
        arcpy.management.AddField(in_table, field_name, "DOUBLE")
    # Calculate geometry attribute for the field
    print(f"Calculating geometry for field: {field_name}")
    arcpy.management.CalculateGeometryAttributes(
        in_table,
        [[field_name, geometry_attribute]],
        coordinate_system=input_spatial_ref
    )

# Add additional fields if they do not exist
for field_name, field_type in additional_fields.items():
    if not field_exists(in_table, field_name):
        print(f"Adding field: {field_name}")
        arcpy.management.AddField(in_table, field_name, field_type)

print("Fields and geometry calculations completed.")
