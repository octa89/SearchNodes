import arcpy

# Path to your MXD file
mxd_path = r"C:\Users\octav\POSM Software Dropbox\POSM Software Dropbox\POSM Customer Projects\JCSA James City Service Authority VA\GIS\1. Mapreader from 050624\MXD\JCMUA_new.mxd"

# Open the MXD file
mxd = arcpy.mapping.MapDocument(mxd_path)

# Open the MXD file
mxd = arcpy.mapping.MapDocument(mxd_path)

# List all layers in the MXD
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.isBroken:
        print("Broken layer found: {}".format(lyr.name))
    elif lyr.supports("SERVICEPROPERTIES"):
        service_properties = lyr.serviceProperties
        if service_properties.get('ConnectionType', '').lower() == 'ags':
            print("Online layer found: {} - {}".format(lyr.name, service_properties['URL']))
            # Remove the online layer
            arcpy.mapping.RemoveLayer(arcpy.mapping.ListDataFrames(mxd)[0], lyr)
# Save the updated MXD
mxd.saveACopy(r"C:\Users\octav\POSM Software Dropbox\POSM Software Dropbox\POSM Customer Projects\JCSA James City Service Authority VA\GIS\1. Mapreader from 050624\MXD\JCMUA_updated.mxd")
del mxd
