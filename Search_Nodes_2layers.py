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

def find_closest_manholes(manholes_list, start_geom, end_geom, min_start_dist, min_end_dist, closest_start_mhid, closest_end_mhid, pipe_sr):
    """
    Finds the closest manholes for start and end points from a given list of manholes.
    Returns updated min distances and closest manhole IDs.
    """
    for mh_geometry, mhid in manholes_list:
        # Project if needed
        if mh_geometry.spatialReference.name != pipe_sr.name:
            mh_geometry = mh_geometry.projectAs(pipe_sr)

        # Calculate distances
        try:
            start_distance = start_geom.distanceTo(mh_geometry)
            end_distance = end_geom.distanceTo(mh_geometry)
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

    return min_start_dist, min_end_dist, closest_start_mhid, closest_end_mhid

# Prompt the user for the geodatabase path
geodatabase = input(Fore.CYAN + "Enter the path to your geodatabase: ")

# Set workspace to the provided geodatabase
arcpy.env.workspace = geodatabase
arcpy.env.overwriteOutput = True

# Select the pipes and primary nodes feature classes
pipe_layer = select_feature_class("Pipes")
point_layer = select_feature_class("Primary Nodes")

# Select the fields for Asset ID, StartID, EndID, and ManholeID
asset_id_field = select_field(pipe_layer, "Asset ID")
start_field = select_field(pipe_layer, "StartID")
end_field = select_field(pipe_layer, "EndID")
mh_id_field = select_field(point_layer, "Manhole ID (e.g., Asset_ID)")

# Optionally select a second point layer for backup manholes
use_backup = input(Fore.CYAN + "Do you want to select a second point layer for backup searching? (y/n): ").lower()

if use_backup == 'y':
    backup_point_layer = select_feature_class("Backup Nodes")
    backup_mh_id_field = select_field(backup_point_layer, "Backup Manhole ID (e.g., Asset_ID)")
else:
    backup_point_layer = None
    backup_mh_id_field = None

# Check and print the spatial references
pipe_sr = arcpy.Describe(pipe_layer).spatialReference
point_sr = arcpy.Describe(point_layer).spatialReference
print(Fore.YELLOW + "Pipe Layer Spatial Reference: {}".format(pipe_sr.name))
print(Fore.YELLOW + "Primary Point Layer Spatial Reference: {}".format(point_sr.name))

if backup_point_layer:
    backup_sr = arcpy.Describe(backup_point_layer).spatialReference
    print(Fore.YELLOW + "Backup Point Layer Spatial Reference: {}".format(backup_sr.name))

# Build a list of manhole geometries and IDs from the primary point layer
manholes = []
with arcpy.da.SearchCursor(point_layer, ['SHAPE@', mh_id_field]) as mh_cursor:
    for mh_row in mh_cursor:
        mh_geometry = mh_row[0]
        mhid = mh_row[1]

        if mh_geometry is None:
            print(Fore.MAGENTA + "Warning: Primary manhole with MHID '{}' has no geometry.".format(mhid))
            continue

        # Ensure manhole geometry has a spatial reference
        if mh_geometry.spatialReference is None:
            mh_geometry = arcpy.PointGeometry(mh_geometry.firstPoint, point_sr)

        manholes.append((mh_geometry, mhid))

print(Fore.BLUE + "Total primary manholes processed: {}".format(len(manholes)))

# If backup layer is selected, build a list of backup manholes
backup_manholes = []
if backup_point_layer:
    with arcpy.da.SearchCursor(backup_point_layer, ['SHAPE@', backup_mh_id_field]) as backup_cursor:
        for bm_row in backup_cursor:
            bm_geometry = bm_row[0]
            bm_id = bm_row[1]

            if bm_geometry is None:
                print(Fore.MAGENTA + "Warning: Backup manhole with MHID '{}' has no geometry.".format(bm_id))
                continue

            # Ensure backup manhole geometry has a spatial reference
            if bm_geometry.spatialReference is None:
                bm_geometry = arcpy.PointGeometry(bm_geometry.firstPoint, backup_sr)

            backup_manholes.append((bm_geometry, bm_id))

    print(Fore.BLUE + "Total backup manholes processed: {}".format(len(backup_manholes)))

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
        min_start_dist = float("inf")
        min_end_dist = float("inf")

        # First, try to find closest manholes from the primary list
        min_start_dist, min_end_dist, closest_start_mhid, closest_end_mhid = find_closest_manholes(
            manholes,
            start_point_geom,
            end_point_geom,
            min_start_dist,
            min_end_dist,
            closest_start_mhid,
            closest_end_mhid,
            pipe_sr
        )

        # Determine if we need backup
        start_need_backup = (closest_start_mhid is None or closest_start_mhid == 0)
        end_need_backup = (closest_end_mhid is None or closest_end_mhid == 0)

        if backup_point_layer and (start_need_backup or end_need_backup):
            print(Fore.MAGENTA + "Checking backup manholes for missing IDs...")

            if start_need_backup and end_need_backup:
                # Both need backup
                min_start_dist = float("inf")
                min_end_dist = float("inf")
                closest_start_mhid = None
                closest_end_mhid = None

                min_start_dist, min_end_dist, closest_start_mhid, closest_end_mhid = find_closest_manholes(
                    backup_manholes,
                    start_point_geom,
                    end_point_geom,
                    min_start_dist,
                    min_end_dist,
                    closest_start_mhid,
                    closest_end_mhid,
                    pipe_sr
                )

            elif start_need_backup and not end_need_backup:
                # Only start needs backup
                # Preserve the end manhole found from primary
                saved_end_mhid = closest_end_mhid
                saved_min_end_dist = min_end_dist

                min_start_dist = float("inf")
                closest_start_mhid = None

                # Find closest for start from backup
                new_min_start, new_min_end, new_start_mhid, new_end_mhid = find_closest_manholes(
                    backup_manholes,
                    start_point_geom,
                    end_point_geom,
                    min_start_dist,
                    float("inf"),  # we don't care about end this time
                    closest_start_mhid,
                    None,
                    pipe_sr
                )

                # Update only the start from backup search
                closest_start_mhid = new_start_mhid
                # Restore the original end from primary
                closest_end_mhid = saved_end_mhid
                min_end_dist = saved_min_end_dist

            elif end_need_backup and not start_need_backup:
                # Only end needs backup
                # Preserve the start manhole found from primary
                saved_start_mhid = closest_start_mhid
                saved_min_start_dist = min_start_dist

                min_end_dist = float("inf")
                closest_end_mhid = None

                # Find closest for end from backup
                new_min_start, new_min_end, new_start_mhid, new_end_mhid = find_closest_manholes(
                    backup_manholes,
                    start_point_geom,
                    end_point_geom,
                    float("inf"),  # we don't care about start this time
                    min_end_dist,
                    None,
                    closest_end_mhid,
                    pipe_sr
                )

                # Update only the end from backup search
                closest_end_mhid = new_end_mhid
                # Restore the original start from primary
                closest_start_mhid = saved_start_mhid
                min_start_dist = saved_min_start_dist

        # Update the fields
        pipe_row[2] = closest_start_mhid
        pipe_row[3] = closest_end_mhid

        # Print the assigned MHIDs:
        # AssetID in Magenta, StartID in Blue, EndID in Cyan
        print(
            Fore.YELLOW + "AssetID: " + Fore.MAGENTA + str(pipe_row[1]) +
            Fore.GREEN + " , Assigned StartID: " + Fore.BLUE + str(closest_start_mhid) +
            Fore.GREEN + " , Assigned EndID: " + Fore.CYAN + str(closest_end_mhid)
        )

        # Save the changes
        pipe_cursor.updateRow(pipe_row)

print(Fore.CYAN + "StartID and EndID fields have been successfully populated with MHIDs.")
