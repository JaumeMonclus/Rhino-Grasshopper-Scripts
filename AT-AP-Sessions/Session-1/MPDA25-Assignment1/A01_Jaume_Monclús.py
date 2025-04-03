import Rhino.Geometry as rg
import ghpythonlib.treehelpers as th
import math
import Rhino

### Lists to Return ###

a_point_list = []
b_point_list = []
lines = []
divided_points = []
moved_divided_points = []
z_values = []
vectors = []
sinusoidal_points = []
interpolated_curves = []
interpolated_curves_v = []
uv_params = []
evaluated_points = []
mesh_faces = []

# Initial Points

for p in range(x):

    a = rg.Point3d(p, 0, 0)
    a_point_list.append(a)

    b = rg.Point3d(p, y, 0)
    b_point_list.append(b)

# Creation of the lines

for i in range(len(a_point_list)):

    line = rg.LineCurve(a_point_list[i], b_point_list[i])
    lines.append(line)

# Ara el que fem és dividir les corves

for j in range(len(lines)):

    params = lines[j].DivideByCount(10, True)
    
    point1 = [lines[j].PointAt(t) for t in params]
    divided_points.append(point1)

# Extraction of the vector and translation

for rows in divided_points: 

    # The first line covers the amplitude of the vector
    vector_sine = [math.sin(rg.Vector3d(single_point.X, single_point.Y, single_point.Z).Length) for single_point in rows]

    # The second line assigns said amplitude to the z comp of a new vector
    moving_vector = [rg.Vector3d(0, 0, m) for m in vector_sine]

    vectors.append(moving_vector)

# Creation of the Points   

num_u = len(divided_points) 
num_v = max(len(row) for row in divided_points)  

for u_coor in range(num_u):

    for v_coor in range(num_v):

        # Iterating through a nested loop to assign to each point its respective vector
        divided_points[u_coor][v_coor] += vectors[u_coor][v_coor]

    # We extract ourselves of the first loop to iterate through the rows in order to interpolate and create a NURBS from interpolation.
    interpolated_curve = rg.Curve.CreateInterpolatedCurve(divided_points[u_coor], 3)
    interpolated_curves.append(interpolated_curve)

sinusoidal_points.extend(divided_points)

# Finally we create a loft from the list of curves 

loft = rg.Brep.CreateFromLoft(interpolated_curves, rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Uniform, False)

# Mesh from Loft ( resulting Mesh will be one Row and Column Larger than the grasshopper definition, Solution Covered After! )

mesh_from_brep = rg.Mesh()

# Es necessari entrar els punts a la malla abans de passar els seus index

for rows in divided_points:
    for pt in rows:
        mesh_from_brep.Vertices.Add(pt)

# Declare each face index

for u in range(num_u - 1):

    for v in range(num_v - 1):
        
        idx0 = u * num_v + v
        idx1 = u * num_v + v + 1
        idx2 = (u + 1) * num_v + v + 1  
        idx3 = (u + 1) * num_v + v

        f = rg.MeshFace(idx0, idx1, idx2, idx3)
        mesh_from_brep.Faces.AddFace(f)


#-----------------------------------------------------------------------------------------------#
# Alternative, Create a Surface from points so we can regulate the amount of U & V Subdivisions
#-----------------------------------------------------------------------------------------------#


#Flattening the point structure

points_flat = []

for f_row in divided_points:
    for f_pt in f_row:
        points_flat.append(f_pt)

nrbs_srf = rg.NurbsSurface.CreateThroughPoints(points_flat, num_u, num_v, 3, 3, False, False)

#Extracting the domain of the surface 

U_dom = nrbs_srf.Domain(0)
V_dom = nrbs_srf.Domain(1)

# Creating 2 lists of values for U & V 

values_u = [U_dom.T0 + (idu * U_dom.Length)/(Uu-1)  for idu in range(Uu)]
values_v = [V_dom.T0 + (idv *V_dom.Length)/(Vv-1) for idv in range (Vv)]

# rebuilding the initial Point structure so that we have rows and columns

for paramu in values_u:
    row_params = []
    for paramv in values_v:
        row_params.append([paramu, paramv])
    uv_params.append(row_params)

# Evaluating the surface at each [u,v] so we can extract a point in the same data structure

for row in uv_params:
    row_points = []

    for i_uv_params in row:
        evaluated_point = nrbs_srf.PointAt(i_uv_params[0],i_uv_params[1])

        row_points.append(evaluated_point)

    evaluated_points.append(row_points)

# Final Step, creating a quad mesh

mesh_from_nurbs_surface = rg.Mesh()

# Es necessari entrar els punts a la malla abans de passar els seus index

for rows in evaluated_points:
    for pt in rows:
        mesh_from_nurbs_surface.Vertices.Add(pt)

# Declare each face index

for u in range(Uu - 1):

    for v in range(Vv - 1):
        
        idx0 = u * Vv + v
        idx1 = u * Vv + v + 1
        idx2 = (u + 1) * Vv + v + 1  
        idx3 = (u + 1) * Vv + v

        f = rg.MeshFace(idx0, idx1, idx2, idx3)
        mesh_from_nurbs_surface.Faces.AddFace(f)

### OUTPUTS ###

# Initial Points

Ipa = a_point_list
Ipb = b_point_list

# Lines

L = lines

# Divided Points

Dvp = th.list_to_tree(divided_points)

# Vectors

Mv = th.list_to_tree(vectors)

# Sinusoidal Points

Sp = th.list_to_tree(sinusoidal_points)

# Interpolated Curves

Crvs = interpolated_curves

# Resulting Loft

Lft = loft

Nrbs_srf = nrbs_srf

# Resulting Mesh from brep

Mfb = mesh_from_brep

# Resulting Mesh from surface

Mfs = mesh_from_nurbs_surface


a = th.list_to_tree(evaluated_points)




# OTHER

# b = th.list_to_tree(sinusoidal_moved_divided_points)
# a = th.list_to_tree(interpolated_curves)

# for crv in range(len(interpolated_curves)):
#     loft = rg.Brep.CreateFromLoft(list(interpolated_curves), rg.LoftType.Normal, False)
#     a = th.list_to_tree(divided_points)
