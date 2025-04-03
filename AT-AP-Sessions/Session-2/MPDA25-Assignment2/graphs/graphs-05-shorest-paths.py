#r: networkx
#r: matplotlib

from typing import cast, Any
import networkx as nx # type: ignore
import matplotlib.pyplot as plt # type: ignore
import Rhino.Geometry as rg # type: ignore

# DECLARE INPUT VARIABLES
m = cast(rg.Mesh, m)  # type: ignore
s = cast(int, s)  # type: ignore
t = cast(int, t)  # type: ignore


def PlotGraph(G,filepath):
    # add position
    pos = nx.spring_layout(G)

    #draw serttings
    fig = plt.figure(figsize=(10,10))
    ax = plt.subplot()
    ax.set_title('Graph', fontsize=12)
    nx.draw(G, pos, node_size=1500, with_labels=True, node_color='pink', font_size=12)

    #draw the graph
    plt.tight_layout()

    # plt.show()
    plt.savefig(filepath, format="PNG")

def GetMeshFaceCentroid(mesh, mfi):

    mf = mesh.Faces[mfi]
    if mf.IsTriangle:
        v1 = m.Vertices[mf.A]
        v2 = m.Vertices[mf.B]
        v3 = m.Vertices[mf.C]

        return (v1 + v2 +v3) * (1/3)

    if mf.IsQuad:
        v1 = m.Vertices[mf.A]
        v2 = m.Vertices[mf.B]
        v3 = m.Vertices[mf.C]
        v4 = m.Vertices[mf.D]

        return (v1 + v2 +v3+ v4) * (1/4)


def DualGraphFromMesh(mesh):
    G=nx.Graph()

    dual_vertices = []
    dual_edges = []

    for i,mf in enumerate(mesh.Faces):

        faceCentroid = GetMeshFaceCentroid(mesh, i)
        dual_vertices.append(faceCentroid)
        
        G.add_node(i, pos = faceCentroid)

        neighbours =   mesh.Faces.AdjacentFaces(i)

        # Add edges to graph
        for n in neighbours:

            if n > i:
                p1= faceCentroid

                p2= GetMeshFaceCentroid(m, n)

                line = rg.Line(p1,p2)
                dual_edges.append(line)

                G.add_edge(i,n, w = line.Length)

    return G, dual_vertices, dual_edges

def shortestPath(G, source, target):

    sp = nx.shortest_path(G, source, target, weight = "weight")
    
    pts = [G.nodes[i]["pos"] for i in sp]
    faceInd = [i for i in sp]

    return pts, faceInd, sp


G, dv,de = DualGraphFromMesh(m)

SP = shortestPath(G, s, t)
pts = SP[0]
faceInd = SP[1]

a= dv
b = de
c = faceInd


#plot
# path= r"C:\Users\david\Desktop\Session02\session02\images\MDPA_plot5.png"
# PlotGraph(G, path)