import arcpy

# Set the path to your File Geodatabase
gdb_path = r"C:\Users\octav\POSM Software Dropbox\POSM Software Dropbox\POSM Customer Projects\Martinsburg\1. Mapreader from 102021\Data Package\data\MartinsburgWV.gdb"  # Ensure the string is properly closed

arcpy.env.workspace = gdb_path

# List all feature classes (layers) in the GDB
layers = arcpy.ListFeatureClasses()

# Check if there are layers in the GDB
if not layers:
    print("No layers found in the GDB.")
    exit()

# Display the available layers and let the user select one
print("Available layers:")
for i, layer in enumerate(layers):
    print(f"{i + 1}. {layer}")

try:
    # Get user input to select the layer
    choice = int(input("Enter the number of the layer to describe: ")) - 1

    # Validate the input
    if choice < 0 or choice >= len(layers):
        print("Invalid selection. Exiting.")
        exit()

    selected_layer = layers[choice]
    print(f"\nSelected Layer: {selected_layer}")
except ValueError:
    print("Invalid input. Please enter a valid number.")
    exit()

# Describe the selected layer to get its schema
desc = arcpy.Describe(selected_layer)

# Display schema information
print("\nField Schema:")
print("-" * 30)
for field in arcpy.ListFields(selected_layer):
    print(f"Field Name: {field.name}")
    print(f"Field Type: {field.type}")
    print(f"Field Alias: {field.aliasName}")
    print(f"Length: {field.length}" if field.type == 'String' else "")
    print("-" * 30)

# Optional: Save the schema info as a text file
with open(f"{selected_layer}_schema.txt", "w") as f:
    f.write(f"Schema for {selected_layer}\n")
    f.write("-" * 30 + "\n")
    for field in arcpy.ListFields(selected_layer):
        f.write(f"Field Name: {field.name}\n")
        f.write(f"Field Type: {field.type}\n")
        f.write(f"Field Alias: {field.aliasName}\n")
        if field.type == 'String':
            f.write(f"Length: {field.length}\n")
        f.write("-" * 30 + "\n")

print(f"\nSchema information has been saved to {selected_layer}_schema.txt")
