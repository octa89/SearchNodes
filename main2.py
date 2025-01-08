import arcpy
import os


# Function to list feature classes in the GDB and select one by number
def select_feature_class(gdb_path, prompt):
    arcpy.env.workspace = gdb_path
    feature_classes = arcpy.ListFeatureClasses()

    if not feature_classes:
        print("No feature classes found in the provided geodatabase.")
        return None

    # Display the feature classes for selection
    print(f"\n{prompt}:")
    for index, fc in enumerate(feature_classes):
        print(f"{index + 1}: {fc}")

    # Prompt the user to select a feature class by number
    while True:
        selection = input("Enter the number of the feature class: ")
        try:
            selection_index = int(selection) - 1
            if 0 <= selection_index < len(feature_classes):
                return feature_classes[selection_index]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


# Function to list fields in a feature class and select one by number
def select_field(feature_class, prompt):
    fields = arcpy.ListFields(feature_class)

    # Display the fields for selection
    print(f"\n{prompt}:")
    for index, field in enumerate(fields):
        print(f"{index + 1}: {field.name}")

    # Prompt the user to select a field by number
    while True:
        selection = input("Enter the number of the field: ")
        try:
            selection_index = int(selection) - 1
            if 0 <= selection_index < len(fields):
                return fields[selection_index].name
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


# Main function
def main():
    # Prompt the user for the geodatabase path
    while True:
        gdb_path = input("Enter the path to your geodatabase (GDB): ")
        if os.path.exists(gdb_path) and gdb_path.endswith('.gdb'):
            break
        else:
            print("Invalid geodatabase path. Please provide a valid GDB path.")

    # Select the pipe layer
    pipe_layer = None
    while not pipe_layer:
        pipe_layer = select_feature_class(gdb_path, "Select the pipe layer (GM)")

    # Select the point layer
    point_layer = None
    while not point_layer:
        point_layer = select_feature_class(gdb_path, "Select the point layer (MH)")

    # Select the startID field from the pipe layer
    start_field = select_field(pipe_layer, "Select the startID field in the pipe layer")

    # Select the ENDID field from the pipe layer
    end_field = select_field(pipe_layer, "Select the ENDID field in the pipe layer")

    # Select the MHID field from the point layer
    mh_id_field = select_field(point_layer, "Select the MHID field in the point layer")

    # Start an editing session
    with arcpy.da.UpdateCursor(pipe_layer, ['SHAPE@', start_field, end_field]) as pipe_cursor:
        for pipe_row in pipe_cursor:
            line_geometry = pipe_row[0]
            start_point = line_geometry.firstPoint  # Get the start point of the line
            end_point = line_geometry.lastPoint  # Get the end point of the line

            # Variables to store the closest MHID for the start and end points
            closest_start_mhid = None
            closest_end_mhid = None

            # Minimum distances initialized to a large value
            min_start_dist = float("inf")
            min_end_dist = float("inf")

            # Search through all points in the MH layer
            with arcpy.da.SearchCursor(point_layer, ['SHAPE@', mh_id_field]) as mh_cursor:
                for mh_row in mh_cursor:
                    mh_geometry = mh_row[0]
                    mhid = mh_row[1]

                    # Calculate the distance from the line's start point to the current manhole
                    start_distance = mh_geometry.distanceTo(start_point)
                    if start_distance < min_start_dist:
                        min_start_dist = start_distance
                        closest_start_mhid = mhid

                    # Calculate the distance from the line's end point to the current manhole
                    end_distance = mh_geometry.distanceTo(end_point)
                    if end_distance < min_end_dist:
                        min_end_dist = end_distance
                        closest_end_mhid = mhid

            # Update the startID and ENDID fields with the closest MHIDs
            pipe_row[1] = closest_start_mhid
            pipe_row[2] = closest_end_mhid

            # Save the changes
            pipe_cursor.updateRow(pipe_row)

    print("StartID and ENDID fields have been successfully populated with MHIDs.")


# Run the script
if __name__ == "__main__":
    main()
