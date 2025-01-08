

nodes = "Manhole"
pipes = "Sewer_Main"

nodeDict = {}
pipeDict = {}


#populate node dictionary with X,Y as the key and node ID as the value
print("populate node dictionary with X,Y as the key and node ID as the value")
for node in arcpy.da.SearchCursor(nodes, ["ManholeID", "SHAPE@XY"]):
    nodeDict[(node[1][0], node[1][1])] = node[0]

#populate pipe dictionary with pipe ID as the key and list of X,Y as values
#vertices populated in the order that the line was draw
#so that [0] is the first vertex and [-1] is the final vertex
print("Setting VERTICES")
for pipe in arcpy.da.SearchCursor(pipes, ["FID", "SHAPE@"]):
    for arrayOb in pipe[1]:
        for point in arrayOb:
            if pipe[0] in pipeDict:
                pipeDict[pipe[0]].append((point.X, point.Y))
            else:
                pipeDict[pipe[0]] = [(point.X, point.Y)]

#populate UNITID with the first vertex of the line
#populate UNITID2 with the final vertex of the line
print("populate UNITID2 with the final vertex of the line")
with arcpy.da.UpdateCursor(pipes, ["FID", "StartID", "EndID"]) as cur:
    for pipe in cur:
        if pipeDict[pipe[0]][0] in nodeDict:
            pipe[1] = nodeDict[pipeDict[pipe[0]][0]]
        if pipeDict[pipe[0]][-1] in nodeDict:
            pipe[2] = nodeDict[pipeDict[pipe[0]][-1]]
        cur.updateRow(pipe)
print("Process completed")