import pyodbc
import arcpy
import json
import urllib.request

# Prompt for user input
mdb_path = input("Enter the full path to the Access database (e.g., C:\\path\\to\\POSMGISdata.mdb): ")
arcgis_service_url = input("Enter the URL of the ArcGIS Online feature service: ")

# Fetch the layers from the ArcGIS Online feature service
response = urllib.request.urlopen(arcgis_service_url + "?f=json")
data = json.load(response)

print("\nAvailable Layers in Feature Service:")
layers = data['layers']
for i, layer in enumerate(layers):
    print(f"{i + 1}. {layer['name']}")

# Prompt user to select a layer
layer_index = int(input("\nEnter the number of the layer to use: ")) - 1
selected_layer = layers[layer_index]

print(f"\nSelected Layer: {selected_layer['name']}")

# Construct the URL for the selected layer
selected_layer_url = f"{arcgis_service_url}/{selected_layer['id']}"

# Load the selected layer
feature_layer = arcpy.FeatureSet()
feature_layer.load(selected_layer_url)

# Describe the feature layer to get its fields
desc = arcpy.Describe(feature_layer)
fields = desc.fields

# Connect to Access database
conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + mdb_path
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Delete current content of PosmGIS table
cursor.execute("DELETE FROM PosmGIS")
conn.commit()
print("Current content of PosmGIS table deleted.")

# Fetch and display fields from POSMGIS table
posmgis_fields = [column.column_name for column in cursor.columns(table='PosmGIS')]
print("\nPOSMGIS Table Fields:")
for field in posmgis_fields:
    print("- {}".format(field))

# Fetch and display fields from selected ArcGIS feature layer
print("\nSelected ArcGIS Feature Layer Fields:")
for field in fields:
    print("- {}".format(field.name))

# Define field mapping (manual mapping based on your requirements)
field_mapping = {
    "AssetID": "AssetID",
    "StartID": "StartID",
    "EndID": "EndID",
    "ManholeStartX": "USX",
    "ManholeStartY": "USY",
    "ManholeEndX": "DSX",
    "ManholeEndY": "DSY",
    "AssetLength": "Shape__Length",
    "AssetType": "Material"
}

# Insert data into POSMGIS table
with arcpy.da.SearchCursor(feature_layer, list(field_mapping.values())) as search_cursor:
    for row in search_cursor:
        try:
            asset_length = round(float(row[8]), 1)  # Shape_Length
        except (ValueError, TypeError):
            asset_length = 0.0  # Default value if conversion fails

        values = (
            row[0],  # AssetID
            row[1],  # StartID
            row[2],  # EndID
            row[3],  # USX
            row[4],  # USY
            row[5],  # DSX
            row[6],  # DSY
            asset_length,  # Shape_Length
            "Marina Coast",  # Static value for City
            row[7]  # Material
        )
        cursor.execute("INSERT INTO PosmGIS (AssetID, StartID, EndID, ManholeStartX, ManholeStartY, ManholeEndX, ManholeEndY, AssetLength, City, AssetType) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)

conn.commit()
conn.close()

print("Data successfully inserted into PosmGIS table.")
