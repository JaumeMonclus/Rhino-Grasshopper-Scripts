#r: networkx
#r: matplotlib

from typing import cast, Any
import networkx as nx # type: ignore
import matplotlib.pyplot as plt # type: ignore
import Rhino.Geometry as rg # type: ignore

# DECLARE INPUT VARIABLES
m = cast(rg.Mesh, m)  # type: ignore

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

def GraphFromMesh(mesh):

    G=nx.Graph()
    edges = mesh.TopologyEdges

    for e in range(edges.Count):
        v1 = edges.GetTopologyVertices(e)[0]
        v2 = edges.GetTopologyVertices(e)[1]
        G.add_node(v1)
        G.add_node(v2)
        G.add_edge(v1, v2)

    return G



G= GraphFromMesh(m)
print (G)

  
#plot
# path= r"C:\Users\david\Desktop\Session02\session02\images\MDPA_plot2.png"
# PlotGraph(G, path)