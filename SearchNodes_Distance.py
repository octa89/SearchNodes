import arcpy
from colorama import init, Fore, Style

# Initialize colorama for color output
init(autoreset=True)

def select_feature_class(message):
    feature_classes = arcpy.ListFeatureClasses()
    print(Fore.CYAN + f"\nAvailable Feature Classes for {message}:")
    for idx, fc in enumerate(feature_classes, 1):
        # Number in Yellow, Feature Class name in Green
        print(Fore.YELLOW + f"{idx}. " + Fore.GREEN + f"{fc}")
    selected_index = int(input(Fore.CYAN + f"Select a feature class for {message} by number: ")) - 1
    return feature_classes[selected_index]

def select_field(feature_class, message):
    fields = arcpy.ListFields(feature_class)
    print(Fore.CYAN + f"\nAvailable Fields in {feature_class} for {message}:")
    for idx, field in enumerate(fields, 1):
        # Number in Yellow, Field name in Green, Type in Red
        print(Fore.YELLOW + f"{idx}. " + Fore.GREEN + f"{field.name}" + Fore.RED + f" (Type: {field.type})")
    selected_index = int(input(Fore.CYAN + f"Select a field for {message} by number: ")) - 1
    return fields[selected_index].name

# Prompt the user for the geodatabase path
geodatabase = input(Fore.CYAN + "Enter the path to your geodatabase: ")

# Set workspace to the provided geodatabase
arcpy.env.workspace = geodatabase
arcpy.env.overwriteOutput = True

# Select the pipes and nodes feature classes
pipe_layer = select_feature_class("Pipes")
point_layer = select_feature_class("Nodes")

# Select the fields for Asset ID, StartID, EndID, and ManholeID
asset_id_field = select_field(pipe_layer, "Asset ID")
start_field = select_field(pipe_layer, "StartID")
end_field = select_field(pipe_layer, "EndID")
mh_id_field = select_field(point_layer, "Manhole ID (e.g., Asset_ID)")

# Check and print the spatial references of both layers
pipe_sr = arcpy.Describe(pipe_layer).spatialReference
point_sr = arcpy.Describe(point_layer).spatialReference
print(Fore.YELLOW + "Pipe Layer Spatial Reference: {}".format(pipe_sr.name))
print(Fore.YELLOW + "Point Layer Spatial Reference: {}".format(point_sr.name))

# Build a list of manhole geometries and IDs
manholes = []
with arcpy.da.SearchCursor(point_layer, ['SHAPE@', mh_id_field]) as mh_cursor:
    for mh_row in mh_cursor:
        mh_geometry = mh_row[0]
        mhid = mh_row[1]

        if mh_geometry is None:
            print(Fore.MAGENTA + "Warning: Manhole with MHID '{}' has no geometry.".format(mhid))
            continue

        # Ensure manhole geometry has a spatial reference
        if mh_geometry.spatialReference is None:
            mh_geometry = arcpy.PointGeometry(mh_geometry.firstPoint, point_sr)

        manholes.append((mh_geometry, mhid))

print(Fore.BLUE + "Total manholes processed: {}".format(len(manholes)))

# Start updating the pipe layer
with arcpy.da.UpdateCursor(pipe_layer, ['SHAPE@', asset_id_field, start_field, end_field]) as pipe_cursor:
    for pipe_row in pipe_cursor:
        line_geometry = pipe_row[0]

        # If line geometry is null, skip this feature
        if line_geometry is None:
            print(Fore.MAGENTA + "Skipping feature because it has a null geometry.")
            continue

        start_point = line_geometry.firstPoint
        end_point = line_geometry.lastPoint

        # Check if start and end points are valid
        if start_point is None or end_point is None:
            print(Fore.RED + "Invalid geometry encountered in pipe feature. Skipping.")
            continue

        # Convert start_point and end_point to PointGeometry objects
        start_point_geom = arcpy.PointGeometry(start_point, pipe_sr)
        end_point_geom = arcpy.PointGeometry(end_point, pipe_sr)

        # Variables to store the closest MHID for the start and end points
        closest_start_mhid = None
        closest_end_mhid = None

        # Minimum distances initialized to a large value
        min_start_dist = float("inf")
        min_end_dist = float("inf")

        # Iterate over the manholes
        for mh_geometry, mhid in manholes:
            if mh_geometry.spatialReference.name != pipe_sr.name:
                mh_geometry = mh_geometry.projectAs(pipe_sr)

            # Calculate distances
            try:
                start_distance = start_point_geom.distanceTo(mh_geometry)
                end_distance = end_point_geom.distanceTo(mh_geometry)
            except Exception as e:
                print(Fore.RED + f"Error calculating distance for MHID '{mhid}': {e}")
                continue

            # Update closest start manhole
            if start_distance < min_start_dist:
                min_start_dist = start_distance
                closest_start_mhid = mhid

            # Update closest end manhole
            if end_distance < min_end_dist:
                min_end_dist = end_distance
                closest_end_mhid = mhid

        # Update the fields
        pipe_row[2] = closest_start_mhid
        pipe_row[3] = closest_end_mhid

        # Print the assigned MHIDs:
        # Asset ID in Yellow, StartID and EndID in Green
        print(
            Fore.YELLOW + "AssetID: " + Fore.MAGENTA + str(pipe_row[1]) +
            Fore.GREEN + " , Assigned StartID: " + Fore.BLUE + str(closest_start_mhid) + Fore.RED +
            " , Assigned EndID: " + Fore.CYAN + str(closest_end_mhid)
        )

        # Save the changes
        pipe_cursor.updateRow(pipe_row)

print(Fore.CYAN + "StartID and EndID fields have been successfully populated with MHIDs.")
