import arcpy


def list_feature_layers(geodatabase_path):
    arcpy.env.workspace = geodatabase_path
    feature_layers = arcpy.ListFeatureClasses()
    print("Available Feature Layers:")
    for idx, layer in enumerate(feature_layers, 1):
        print(f"{idx}. {layer}")
    return feature_layers


def get_selected_feature_layer(geodatabase_path):
    try:
        feature_layers = list_feature_layers(geodatabase_path)

        if not feature_layers:
            raise ValueError(f"No feature layers found in the geodatabase: {geodatabase_path}")

        selected_idx = int(input("Select the feature layer by number: ")) - 1
        selected_layer = feature_layers[selected_idx]
        return selected_layer
    except Exception as e:
        print(f"Error fetching feature layer: {e}")
        return None


def count_rows_in_layer(geodatabase_path):
    feature_layer = get_selected_feature_layer(geodatabase_path)

    if feature_layer is None:
        print("Failed to select a valid feature layer.")
        return

    layer_path = f"{geodatabase_path}\\{feature_layer}"
    result = arcpy.GetCount_management(layer_path)
    count = int(result.getOutput(0))

    print(f"The number of rows in the layer '{feature_layer}' is: {count}")


# Input geodatabase path from user
geodatabase_path = input("Enter the path to your local geodatabase (e.g., C:\\path\\to\\your\\geodatabase.gdb): ")

# Call the function to count rows in the selected layer
count_rows_in_layer(geodatabase_path)
