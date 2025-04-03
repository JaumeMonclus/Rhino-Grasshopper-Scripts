#r: networkx
#r: matplotlib

import networkx as nx
import Rhino.Geometry as rg # type: ignore beaause using stubs
import matplotlib.pyplot as plt # type: ignore

def GetMeshFaceCentroid(mesh, mfi):

    mf = mesh.Faces[mfi]
    if mf.IsTriangle:
        v1 = mesh.Vertices[mf.A]
        v2 = mesh.Vertices[mf.B]
        v3 = mesh.Vertices[mf.C]

        return (v1 + v2 +v3) * (1/3)

    if mf.IsQuad:
        v1 = mesh.Vertices[mf.A]
        v2 = mesh.Vertices[mf.B]
        v3 = mesh.Vertices[mf.C]
        v4 = mesh.Vertices[mf.D]

        return (v1 + v2 +v3+ v4) * (1/4)

def getStartPoint(g):

    if nx.is_connected(g):
        Grapheccentricity=nx.algorithms.distance_measures.eccentricity(g)
        Maxeccentricity=max(list(Grapheccentricity.values()))
        MaxeccentricityIndex=(list(Grapheccentricity.values()).index(Maxeccentricity))
        realIndex=list(Grapheccentricity.keys())[MaxeccentricityIndex]
        startpoint=realIndex
    else:
        largest_cc = max(nx.connected_components(g), key=len)
        largest_graph=g.subgraph(largest_cc).copy()
        Grapheccentricity=nx.algorithms.distance_measures.eccentricity(largest_graph)
        Maxeccentricity=max(list(Grapheccentricity.values()))
        MaxeccentricityIndex=list(Grapheccentricity.values()).index(Maxeccentricity)
        realIndex=list(Grapheccentricity.keys())[MaxeccentricityIndex]
        startpoint=realIndex
    
    return startpoint

def DualGraphFromMesh(mesh):
    G=nx.Graph()

    dual_vertices = []
    dual_edges = []

    for i,mf in enumerate(mesh.Faces):

        faceCentroid = GetMeshFaceCentroid(mesh, i)
        dual_vertices.append(faceCentroid)
        
        G.add_node(i, point = faceCentroid, pos = faceCentroid)

        neighbours =   mesh.Faces.AdjacentFaces(i)

        # Add edges to graph
        for n in neighbours:

            if n > i:
                p1= faceCentroid

                p2= GetMeshFaceCentroid(mesh, n)

                line = rg.Line(p1,p2)
                dual_edges.append(line)

                G.add_edge(i,n, w = line.Length)

    return G, dual_vertices, dual_edges
    
def shortestPath(G, source, target):

    sp = nx.shortest_path(G, source, target, weight = "weight")
    
    pts = [G.nodes[i]["pos"] for i in sp]
    faceInd = [i for i in sp]

    return pts, faceInd, sp

def AllShortestPaths(g, startpoint):
    """Get the end point by getting the index of the point that has the longest shortest path"""

    end_point_index= startpoint #for single face islands
    initial_length=0 
    for i in list(g.nodes):          
        if nx.has_path(g,startpoint,i):
            Pathlength = nx.dijkstra_path_length(g,startpoint,i,weight = "weight")
            if Pathlength>initial_length :
                initial_length=Pathlength
                end_point_index=i
                s=i
            elif Pathlength < initial_length and i!=startpoint:
                end_point_index=s


    end=end_point_index
    
    # Check that start and end are not the same node
    if startpoint == end:
        pts = [g.nodes[startpoint]["point"]]
        indexes=[startpoint]
        sl=1
        to_be_removed=[startpoint]
        return [pts,indexes,sl,to_be_removed]
        
    else:
        # Check that a path exist between the two nodes
        if nx.has_path(g,startpoint,end):
            # Calculate shortest path
            
            sp = nx.dijkstra_path(g,startpoint,end,weight = "weight")

            # Make polyline through path
            pts = [g.nodes[i]["point"] for i in sp]
            #get points indexes 
            indexes=sp
            sl=len(sp)
            to_be_removed=sp

        
                    
        return [pts,indexes,sl,to_be_removed]
    
