import Rhino.Geometry as rg #type:ignore
import math
import ghpythonlib.treehelpers as th #type:ignore

from typing import cast, Any #type:ignore


# DECLARE INPUT VARIABLES OF PYTHON COMPONENT
x_points = cast(int, x_points)  # type: ignore
y_points = cast(int, y_points)  # type: ignore

#START CONDING HERE 

# assignment.py to grasshopper
# use Qodo to make the assignment again
# text file to be used as a pseudocode

#1.- create first series of points -
#start by initializing an empty list and fill it with points 
#by creating points with a for loop. The number of points should come 
#from a grasshopper slider called x_points (remember to set the type)
#Increment the X coordinate of the point at each iteration so to create
#a series of points along the X axis line
#store that point to the list
#output this list to grasshopper to verify the result should look like gh component (1.)

pointList1 = []

#your code here
for i in range(x_points):
    point = rg.Point3d(i, 0, 0)
    pointList1.append(point)

a = pointList1

#2. - create second series of points -
#create a second list of points  by copying the code above, but this time
#assign the Y coordinate of each point to a value that comes from an 
#external input which can be a slider in grasshopper called y_points
#output that list as well, the result should look like component (2.) 

pointList2 = []

#your code here

for i in range(y_points):
    point = rg.Point3d(i, 10, 0)
    pointList2.append(point)

b = pointList2


#3. - create lines from two serie of points - 
#initialize another empty list to store some lines
#make another for loop that iterates through each point in any of the list BY INDEX
#within this loop, make a line that draws from points in both lists with the same index
#and append that line to the line list. output the result
#hint: you only need one for loop for this

lineList = []

#your code here
for i in range(len(pointList1)):
    line = rg.Line(pointList1[i], pointList2[i])
    lineList.append(line)

c = lineList

#4.- divide curve -
#initialize another empty list to store some curves
#interate through every line in the line list with a for loop 
#inside the scope of this for loop, create an empty list to store the division points
#inside the for loop, convert each line to a nurbs curve, like shown in class
#divide the new curve into 10 points by applying DivideByCount() method (see rhinocommo) and store the result
#this returns a list of parameters in the line which correspond to each parameter
#you need to iterate through the list of params with another for loop and get the point per each param 
#using Line.PointAt(), and there the points in the list of divison points

allDivPts = [] #this will be a list of lists
curves = []
for line in lineList:
    linePts =[] #create an empty list to fill each iteration
    #your code here
    curve = line.ToNurbsCurve()
    # curves.append(line)

    params = curve.DivideByCount(10, True)
    # allDivPts.append(list(params))
    for param in params:
        point = line.PointAt(param/10)
        linePts.append(point)
    allDivPts.append(linePts) 

d = th.list_to_tree(allDivPts) 

# #6.- make a curve from a list of points
# #again, initialize a en empty list which will contain curves
# #interate through the list of list of points with a for loop
# #create a curve with rg.Curve.CreateInterpolatedCurve() as in 6. (see rhinocommon)
# #append that curve to the list of curves and output it to gh

# make a curve from list of points
curveList = []

#your code goes here
for linePts in allDivPts:
    curve = rg.Curve.CreateInterpolatedCurve(linePts, 3)
    curveList.append(curve)

e= curveList

# # 7.- create a loft surface from curves
# #use rg.Brep.CreateFromLoft() (see rc) to create a surface from loft
# #store it in a variable and output it to gh

# #this will be a list of surfaces

#your code here
for curve in curveList:
    surface = rg.Brep.CreateFromLoft(curveList, rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)

f = surface

# # 8.- create a mesh from Brep
# #The last step is to create a mesh from a Brep using rg.Mesh.CreateFromBrep(), store it and output it to gh
# #keep in mind that CreateFromBrep needs one Brep and CreateFromLoft() returns a list (even if only of one element)
# #so you need to access the first element of the list to get the Brep
# #your code here

mesh = rg.Mesh()
array = mesh.CreateFromBrep(surface[0])
g = array[0]
    



    
    
