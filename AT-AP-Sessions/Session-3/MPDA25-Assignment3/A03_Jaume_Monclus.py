#r: networkx
#r: matplotlib

from typing import cast, Any
import networkx as nx # type: ignore
import matplotlib.pyplot as plt # type: ignore
import ghpythonlib.treehelpers as th # type: ignore
import System # type: ignore
import Rhino # type: ignore
import Rhino.Geometry as rg # type: ignore
import rhinoscriptsyntax as rs # type: ignore
import math # type: ignore
import ghpythonlib.components as comps # type: ignore
import KangarooSolver as KS # type: ignore

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



def mirrored_face(m,source,G):
    mesh_indexes = []

    # Get the face index of the source face

    ray_vector_reversed = -m.FaceNormals[source]

    ray_initial_face = m.Faces[source]
    
    vr1 = m.Vertices[ray_initial_face.A]
    vr2 = m.Vertices[ray_initial_face.B]
    vr3 = m.Vertices[ray_initial_face.C]
    vr4 = m.Vertices[ray_initial_face.D]

    ray_initial_point = (vr1 + vr2 +vr3+ vr4) * (1/4)

    # mesh curve intersectiion

    mesh_line = rg.Line(ray_initial_point, ray_vector_reversed, 200)

    Face_point_intersection = rg.Intersect.Intersection.MeshLine(m, mesh_line)
    
    Mesh_index_list = m.ClosestPoint(Face_point_intersection[0],20)

    # this is the mesh index

    Mesh_index = Mesh_index_list[0]

    # extract the shortest path of the oposite point
    
    sp = nx.shortest_path(G, source, Mesh_index, weight = "weight")
    
    pts = [G.nodes[i]["pos"] for i in sp]
    faceInd = [i for i in sp]

    # next face index

    next_faces = m.Faces.GetConnectedFaces(
        source,
        0.5,
        True)


class TorusStripes:
    def __init__(self, m, G):
        self.m = m
        self.G = G
        return 
    def mesh_faces(self):

        mesh_indexes = []
        self.striped_mesh_faces = []
        processed_faces = set()
        for i in range(0, len(m.Faces)):
            if i in processed_faces:
                continue
            else:
                next_faces = m.Faces.GetConnectedFaces(
                    i,
                    0.5,
                    True)
                stripe_faces = []
                
                # si vas a hacer un list(), siempre en append.
                for idx in next_faces:
                    mesh_face = m.Faces.GetFace(idx)
                    stripe_faces.append(mesh_face)

                self.striped_mesh_faces.append(stripe_faces)
                mesh_indexes.append(list(next_faces))
                processed_faces.update(next_faces)

    
        return self.striped_mesh_faces
            
    def torus_stripes(self):

        self.nested_face_meshes = []
        
        for stripe in self.striped_mesh_faces:
            stripe_meshes = []  # Lista para almacenar los mini meshes de este stripe
            for face in stripe:
                new_mesh = rg.Mesh()
                v_indices = []
                # Agregar los 4 vértices de la cara (quad)
                for orig_idx in [face.A, face.B, face.C, face.D]:
                    v_indices.append(new_mesh.Vertices.Add(m.Vertices[orig_idx]))
                new_mesh.Faces.AddFace(v_indices[0], v_indices[1], v_indices[2], v_indices[3])
                new_mesh.Normals.ComputeNormals()
                new_mesh.Compact()
                stripe_meshes.append(new_mesh)
            self.nested_face_meshes.append(stripe_meshes)

        return self.nested_face_meshes

    def sorting_mesh_faces(self):

        # create the initial group of centroids
        self.centroids = []
        self.average_middle_point = []
        keys = []  

        # Recorremos cada grupo en nested_face_meshes
        for nested_face in self.nested_face_meshes:

            # create the subgroups of centroids
            centroids_group = []
            
            for face in nested_face:
                amp = rg.AreaMassProperties.Compute(face)
                if amp: 
                    # double append
                    centroids_group.append(amp.Centroid)
                    
            # average point of the group
            if len(centroids_group) > 0:
                avg = rg.Point3d(0, 0, 0)
                for pt in centroids_group:
                    avg += pt
                avg /= len(centroids_group)
            
            
            # Guardamos el punto promedio individualmente (por grupo)
            self.average_middle_point.append(avg)
            
            
            sorting_circle = rg.Circle(1)
            result = comps.CurveClosestPoint(avg, sorting_circle)
            t_value = list(result)[1]
            
            # outputs: agregamos el grupo completo y su promedio ya calculado
            self.centroids.append(centroids_group)

            # Agregamos la key (un solo float) para este grupo
            keys.append(t_value)
        
        zipped_data = list(zip(keys, self.centroids))
        zipped_data.sort(key=lambda x: x[0])
        keys_sorted_cent = []
        centroids_sorted = []
        for k, g in zipped_data:
            keys_sorted_cent.append(k)
            centroids_sorted.append(g)

        sorted_keys = keys_sorted_cent
        self.centroids = centroids_sorted

        zipped_data_average = list(zip(keys, self.average_middle_point))
        zipped_data_average.sort(key=lambda x: x[0])

        # keys for the vectors and polyline

        keys_sorted_avg = []
        self.average_middle_point_sorted = []
        for k, g in zipped_data_average:
            keys_sorted_avg.append(k)
            self.average_middle_point_sorted.append(g)


        # order the mesh stripes

        zipped_data = list(zip(keys, self.nested_face_meshes))
        zipped_data.sort(key=lambda x: x[0])
        keys_sorted_cent = []
        self.striped_mesh_faces_sorted = []
        for k, g in zipped_data:
            keys_sorted_cent.append(k)
            self.striped_mesh_faces_sorted.append(g)

       

        # Devuelve las stripes ordenadas
        return self.striped_mesh_faces_sorted
    
    def sorted_stripes (self):
    
        # here we are going to get a plane, a coplanar cirlce and sort the points accordingly for each grou`p
        
        self.average_middle_point_sorted
        self.centroids

        # get the connecting vectors between i and i * 1 for the average_middle_point_sorted
        connecting_vectors = []
        cross_vectors = []
        stripes_plane = []
        circles = []
        t_values = []
        sorted_keys_all = []
        self.sorted_mesh_faces = []
        
        for i in range(len(self.average_middle_point_sorted)):
            next_index = (i + 1) % len(self.average_middle_point_sorted)
            vector = self.average_middle_point_sorted[next_index] - self.average_middle_point_sorted[i]
            connecting_vectors.append(vector)
        
            # calculating the cross product

            cross_vector = rg.Vector3d.CrossProduct(vector, rg.Vector3d.ZAxis)
            cross_vectors.append(cross_vector)

            # create the plane for the stripe

            plane = rg.Plane(self.average_middle_point_sorted[i], rg.Vector3d.ZAxis, cross_vector)
            stripes_plane.append(plane)

            # create a circle in each plane

            circle = rg.Circle(plane, 1)
            circles.append(circle)

            # order all the centroid correspondingly

            result = comps.CurveClosestPoint(self.centroids[i], circle)
            t_value = list(result)[1]
            t_values.append(list(t_value))

        # order the centroids correspondingly zip them first
        # this is a working method for embeded list sorting

        for ex_t_values, ex_mesh_faces in zip(t_values, self.striped_mesh_faces_sorted):
            zipped_data = list(zip(ex_t_values, ex_mesh_faces))
            zipped_data.sort(key=lambda x: x[0])
            sorted_keys, sorted_group = zip(*zipped_data)  if zipped_data else ([], [])
            sorted_keys_all.append(list(sorted_keys))
            self.sorted_mesh_faces.append(list(sorted_group))

        return sorted_keys_all, self.sorted_mesh_faces
    
    def unroll(self):
        
        self.first_halves = []
        self.second_halves = []
        
        # Se recorre cada branch en self.sorted_mesh_faces
        for branch in self.sorted_mesh_faces:
            half_index = len(list(branch)) // 2  # Si el número es impar, la segunda mitad tendrá 1 elemento más
            self.first_halves.append(branch[:half_index])
            self.second_halves.append(branch[half_index:])

        # primero juntamos las mallas

        # joined_meshes = []

        # for meshes in self.first_halves:
        #     comps.MeshJoin(meshes)
        #     joined_meshes.append(meshes)
        joined_first_meshes = comps.MeshJoin(th.list_to_tree(self.first_halves))
        joined_second_meshes = comps.MeshJoin(th.list_to_tree(self.second_halves))

        # joined_first_meshes[0].Normals.ComputeNormals()


        
        return joined_first_meshes, joined_second_meshes
        

        
        

        



           
            


        return lengths
    

    
def shortestPath(G, source, target):

    sp = nx.shortest_path(G, source, target, weight = "weight")
    
    pts = [G.nodes[i]["pos"] for i in sp]
    faceInd = [i for i in sp]

    return pts, faceInd, sp       
          
    
    

G, dv,de = DualGraphFromMesh(m)

SP = shortestPath(G, s, t)
pts = SP[0]
faceInd = SP[1]
# ts = th.list_to_tree(torus_stripes(m,s,G))

# como saco la class TorusStripes de la lista?
torus = TorusStripes(m,G)
mesh_faces = th.list_to_tree(torus.mesh_faces())
unordered_stripes = th.list_to_tree(torus.torus_stripes())
sorted_faces = th.list_to_tree(torus.sorting_mesh_faces())
sorted_stripes = th.list_to_tree(torus.sorted_stripes()[0])
joined_first_meshes = th.list_to_tree(torus.unroll()[0])
joined_second_meshes = th.list_to_tree(torus.unroll()[1])



# pruebas


# sorted_faces = torus.sorting_mesh_faces()


# m = th.list_to_tree(torus_stripes(m,s,G))

a= dv
b = de
c = faceInd
d = th.list_to_tree(torus.sorted_stripes()[1])


#plot
# path= r"C:\Users\david\Desktop\Session02\session02\images\MDPA_plot5.png"
# PlotGraph(G, path)