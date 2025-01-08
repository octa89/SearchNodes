import arcpy

# Set the path to your geodatabase
gdb_path = r"C:\Users\octav\POSM Software Dropbox\POSM Software Dropbox\POSM Customer Projects\Marina Coast Water District  CA\GIS\1.ONline Mapreader 052924\MXD\Marina Coast\Marina Coast.gdb"

# Set the arcpy workspace
arcpy.env.workspace = gdb_path

arcpy.env.overwriteOutput = True

# Specify the feature class
feature_class = "Sewer_Gravity_Main"  # Replace with the name of your feature class

# List of field names to be deleted
fields_to_delete = ["USX", "USY", "DSX", "DSY", "StartID", "EndID"]  # Adjust this list to match the exact field names

# Delete the fields
arcpy.DeleteField_management(feature_class, fields_to_delete)

print(f"Fields {', '.join(fields_to_delete)} have been deleted from the feature class '{feature_class}'.")
