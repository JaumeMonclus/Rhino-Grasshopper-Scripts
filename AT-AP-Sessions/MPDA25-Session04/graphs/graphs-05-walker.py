#r: networkx
#r: matplotlib

from typing import cast, Any
import networkx as nx # type: ignore
import matplotlib.pyplot as plt # type: ignore
import Rhino.Geometry as rg # type: ignore beaause using stubs

import graph_helpers as graph 

# DECLARE INPUT VARIABLES OF PYTHON COMPONENT
m = cast(rg.Mesh, m)  # type: ignore
s = cast(int, s)  # type: ignore
t = cast(int, t)  # type: ignore

G, dv,de = graph.DualGraphFromMesh(m)

SP = graph.shortestPath(G, s, t)
pts = SP[0]
faceInd = SP[1]

a= dv
b = de
c = faceInd


#plot
# path= r"C:\Users\david\Desktop\Session02\session02\images\MDPA_plot5.png"
# ghelp.PlotGraph(G, path)