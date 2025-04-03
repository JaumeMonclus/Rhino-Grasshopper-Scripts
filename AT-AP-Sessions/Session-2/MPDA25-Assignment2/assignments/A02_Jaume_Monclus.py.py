#r: networkx
#r: matplotlib

import networkx as nx #type: ignore
import matplotlib.pyplot as plt #type: ignore
import random

#create a Graph
G = nx.Graph()

# Create a dictionary of my skilset
categories = [
    {"id": "Complex Modelling", "color": "0", "tools": ["Rhino3D", "Grasshopper3D", "Blender3D", "Sketchup", "Dynamo", "Python","C#",".NET", "Microstation"] },
    {"id": "Software Dev", "color": "0", "tools": ["Python","C#",".NET", "Grasshopper3D", "Blender3D","Revit","Rhino.inside", "SQL"] },
    {"id": "Interoperability", "color": "0", "tools": ["ArchiCad", "Revit","Grasshopper3D", "Blender3D", "Rhino.inside", "IFCjs"] },
    {"id": "Fabrication", "color": "0", "tools": ["CAM/CNC","3D Printing", "Grasshopper3D"] },
    {"id": "Backend dev", "color": "#0", "tools": [ "SQL", "Node.js","Mongodb","Kubernetes", "Docker", "Openshift"] },
    {"id": "Frontend dev", "color": "0", "tools": ["HTML/CSS", "ThreeJS", "Python", "Unreal","ProcessingJS", "SQL", "C#"] },
    {"id": "Simulation", "color": "0", "tools": ["Grasshopper3D", "Energy +", "Ladybug", "Unreal", "Blender3D"] }
]

# We traverse the dictionary creatin, adding and connecting the nodes.
for cat in categories:
    
    cat_id = cat["id"]
    color = ((random.random(),random.random(),random.random()))
    G.add_node(cat_id, size=25, color = color)

    for tools in cat["tools"]:

        G.add_node(tools, size=15)
        G.add_edge(tools, cat_id)
        

# #add position to display
pos = nx.spring_layout(G, 1.5, iterations=100, seed= 42)


# alternative postition
# pos = nx.circular_layout(G)


#draw serttings
fig = plt.figure(figsize=(10,10))
ax = plt.subplot()
ax.set_title('Graph', fontsize=12)


# Colors for higher categories
node_colors =[]

for node in G.nodes:
    # this was tricky bcs we a are looking for the compartment named 'color', not for the color itself.
    if 'color' in G.nodes[node]:
        color = G.nodes[node]['color']
        node_colors.append(color)
    # and if that one doesnt exist we assign a new one.
    else:
        node_colors.append('lightgray')

nx.draw(G, pos, node_size=1500, node_color=node_colors, with_labels=True, font_size=10, font_color='black')

#draw the graph
plt.tight_layout()


# plot
path= r"C:\Users\jaume\Desktop\session_2\session02\images\MDPA_plot1.png"
plt.savefig(path, format="PNG")