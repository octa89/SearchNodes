import arcpy

def list_feature_classes(geodatabase_path):
    """ Lists all feature classes in a given geodatabase. """
    arcpy.env.workspace = geodatabase_path
    feature_classes = []
    # Walk through the geodatabase and list all feature classes
    for dirpath, dirnames, filenames in arcpy.da.Walk(geodatabase_path, datatype="FeatureClass"):
        feature_classes.extend(filenames)
    return feature_classes

def print_fields(feature_class):
    """ Prints all fields in the selected feature class. """
    fields = arcpy.ListFields(feature_class)
    print(f"Fields in {feature_class}:")
    for field in fields:
        print(f"{field.name} (Type: {field.type})")

def main():
    geodatabase_path = input("Enter the path to the geodatabase: ")
    feature_classes = list_feature_classes(geodatabase_path)

    if not feature_classes:
        print("No feature classes found in the geodatabase.")
        return

    print("Available Feature Classes:")
    for i, fc in enumerate(feature_classes, 1):
        print(f"{i}. {fc}")

    try:
        choice = int(input("Select a feature class by number: ")) - 1
        if choice < 0 or choice >= len(feature_classes):
            print("Invalid selection. Exiting.")
            return
    except ValueError:
        print("Invalid input. Please enter a number. Exiting.")
        return

    selected_feature_class = feature_classes[choice]
    print_fields(selected_feature_class)

if __name__ == "__main__":
    main()
