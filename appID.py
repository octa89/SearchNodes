from arcgis.gis import GIS
from arcgis.mapping import WebMap
from arcgis.features import FeatureLayer
import arcpy

# Connect to GIS
gis = GIS("pro")  # Use "pro" for ArcGIS Pro credentials

# Define the App ID
app_id = "679671419a20484fa8e22f377820b0a8"

# Get the Web Application Item
app_item = gis.content.get(app_id)
print(f"Application Title: {app_item.title}")
print(f"Application Type: {app_item.type}")

# Access the Application Data
app_data = app_item.get_data()

# Retrieve the Web Map ID
webmap_id = None
if 'map' in app_data and 'itemId' in app_data['map']:
    webmap_id = app_data['map']['itemId']
elif 'values' in app_data and 'webmap' in app_data['values']:
    webmap_id = app_data['values']['webmap']
else:
    print("Web map ID not found in application data.")

if webmap_id:
    print(f"Web Map ID: {webmap_id}")
else:
    raise Exception("Web Map ID could not be found.")

# Get the Web Map Item
webmap_item = gis.content.get(webmap_id)
print(f"Web Map Title: {webmap_item.title}")
print(f"Web Map Type: {webmap_item.type}")

# Create a WebMap object
webmap = WebMap(webmap_item)

# List and Access Layers
layers = []
for layer_info in webmap.layers:
    print(f"Layer Title: {layer_info['title']}")
    print(f"Layer URL: {layer_info['url']}")
    print(f"Layer Type: {layer_info['layerType']}")
    print("-------------------------")
    # Access the Feature Layer
    fl = FeatureLayer(layer_info['url'], gis=gis)
    layers.append(fl)

# Optional: Add Layers to ArcGIS Pro Map
aprx = arcpy.mp.ArcGISProject("CURRENT")
map = aprx.activeMap

for fl in layers:
    map.addDataFromPath(fl.url)

arcpy.RefreshActiveView()
