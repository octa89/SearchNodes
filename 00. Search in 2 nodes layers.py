import arcpy


def select_feature_class(message):
    feature_classes = arcpy.ListFeatureClasses()
    print(f"\nAvailable Feature Classes for {message}:")
    for idx, fc in enumerate(feature_classes, 1):
        print(f"{idx}. {fc}")
    selected_index = int(input(f"Select a feature class for {message} by number: ")) - 1
    return feature_classes[selected_index]


def select_field(feature_class, message):
    fields = arcpy.ListFields(feature_class)
    print(f"\nAvailable Fields in {feature_class} for {message}:")
    for idx, field in enumerate(fields, 1):
        print(f"{idx}. {field.name} (Type: {field.type})")
    selected_index = int(input(f"Select a field for {message} by number: ")) - 1
    return fields[selected_index].name


# Set the path to your geodatabase
gdb_path = input("Enter the path to your geodatabase: ")
arcpy.env.workspace = gdb_path
arcpy.env.overwriteOutput = True

# Select nodes, nodes2, and pipes feature classes
nodes = select_feature_class("Nodes")
nodes2 = select_feature_class("Nodes2")
pipes = select_feature_class("Pipes")

# Select the fields for manhole ID in nodes, nodes2, and pipe ID in pipes
ManholeID = select_field(nodes, "Manhole ID")
ManholeID2 = select_field(nodes2, "Manhole ID")
pipeID = select_field(pipes, "Pipe ID")

nodeDict = {}
nodeDict2 = {}

# Populate node dictionary with X,Y as the key and node ID as the value
print("\nPopulating node dictionary with X,Y as the key and node ID as the value")
for node in arcpy.da.SearchCursor(nodes, [ManholeID, "SHAPE@XY"]):
    if node[1]:  # Check if geometry is not None
        nodeDict[(node[1][0], node[1][1])] = node[0]

# Populate node2 dictionary similar to nodeDict
print("\nPopulating second node dictionary with X,Y as the key and node ID as the value")
for node in arcpy.da.SearchCursor(nodes2, [ManholeID2, "SHAPE@XY"]):
    if node[1]:  # Check if geometry is not None
        nodeDict2[(node[1][0], node[1][1])] = node[0]

pipeDict = {}

# Populate pipe dictionary with pipe ID as the key and list of X,Y as values
print("\nSetting vertices")
for pipe in arcpy.da.SearchCursor(pipes, [pipeID, "SHAPE@"]):
    if pipe[1]:  # Check if geometry is not None
        for arrayOb in pipe[1]:
            for point in arrayOb:
                if pipe[0] in pipeDict:
                    pipeDict[pipe[0]].append((point.X, point.Y))
                else:
                    pipeDict[pipe[0]] = [(point.X, point.Y)]

# Populate UNITID with the first vertex of the line, and UNITID2 with the final vertex
print("\nPopulating UNITID with the first vertex of the line, and UNITID2 with the final vertex")
with arcpy.da.UpdateCursor(pipes, [pipeID, "StartID", "EndID"]) as cur:
    for pipe in cur:
        start_key = pipeDict.get(pipe[0], [None])[0]
        end_key = pipeDict.get(pipe[0], [None])[-1]
        if start_key in nodeDict:
            pipe[1] = nodeDict[start_key]
        elif start_key in nodeDict2:  # Fallback to nodes2
            pipe[1] = nodeDict2[start_key]

        if end_key in nodeDict:
            pipe[2] = nodeDict[end_key]
        elif end_key in nodeDict2:  # Fallback to nodes2
            pipe[2] = nodeDict2[end_key]

        cur.updateRow(pipe)

print("\nProcess completed")
