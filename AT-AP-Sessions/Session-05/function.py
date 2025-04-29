

''' MUST READ

# inputs must be named (m, s, p) in order to work with the component.

# m: mesh
# s: paths (tree of paths)
# p: points (tree of points)

# Also, the s and p inputs must be trees of points Change to TREE ACCESS!
# m is left as item acceSs!'''



#r: networkx
#r: matplotlib

# from ast import pattern
from os import path, remove
import re
from typing import cast, Any
from unittest.mock import seal
import networkx as nx # type: ignore
import matplotlib.pyplot as plt # type: ignore
import Rhino.Geometry as rg
import numpy as np
from numpy import true_divide
from System.Collections.Generic import List
import ghpythonlib.treehelpers as th # type: ignore
import ghpythonlib.components as comps # type: ignore
import graph_helpers as graph 
# from Grasshopper.Kernel.Data import DataTree, GH_Path



m = cast(rg.Mesh, m)  # type: ignore
p = cast(rg.Point3d, p)

class PathStripper:

    def __init__(self, mesh, paths, points):

        '''Initializes the PathStripper class with a mesh, paths, and points.'''

        self.mesh = mesh
        self.paths_tree   = paths
        self.indexes = []
        self.Polylines = []
        self.points = points
        self.cull_pattern = []

    def compute_indexes(self):             

        '''Computes the indexes of the paths in the mesh and a Culling pattern.'''
        
        self.indexes      = []
        self.cull_pattern = []

        for path in self.paths_tree.Paths:
            branch = self.paths_tree.Branch(path)
            if len(branch) >= 8:
                self.indexes.append(branch)
                self.cull_pattern.append(True)
            else:
                self.cull_pattern.append(False)

        return self.indexes



    def get_filtered_lists(self):
            
            '''Filters the paths based on the culling pattern.'''

            filtered = []
            for keep, path in zip(self.cull_pattern, self.points.Paths):
                if not keep:
                    continue
                branch = self.points.Branch(path)
                if branch:
                    filtered.append(branch)

            return filtered


    def compute_polylines(self):
            
            '''Computes the polylines from the filtered paths.'''
        
            self.polylines = []
            for raw_branch in self.get_filtered_lists():
                pts = [pt for pt in raw_branch if isinstance(pt, rg.Point3d)]
                if pts:
                    self.polylines.append(rg.Polyline(pts))
            return self.polylines
    
    def compute_distances(self):

        '''Computes many things, but we keep the "Checked_distances" of the polylines and their endpoints.'''
        '''Checked_distances are the distances of the polylines minus the distances of their endpoints.'''

        self.distances = []
        self.endpoint_distances = []
        self.checked_distances = []


        for polyline in self.polylines:
            length = polyline.Length
            self.distances.append(length)

        for polyline in self.polylines:
            start, end = comps.EndPoints(polyline)
            line = rg.Line(start, end)
            distance = line.Length
            self.endpoint_distances.append(distance)
        
        for i in range(len(self.distances)):
            self.checked_distances.append(self.distances[i] - self.endpoint_distances[i])
            
        return self.checked_distances
    
    def compute_sorting(self):

        '''Sorts the ordred indexes based on the checked distances.'''

        paired = list(zip(self.checked_distances, self.indexes))
        paired_sorted = sorted(paired, key=lambda x: x[0])

        sorted_distances, sorted_polylines = zip(*paired_sorted) if paired_sorted else ([], [])

        self.checked_distances = list(sorted_distances)
        self.ordered_indexes   = list(sorted_polylines)

        return self.distances
    
    def unpack_first_branch(self):

        '''Anf finally, unpacks the first branch of the ordered indexes.'''

        self.list_lengths   = [len(branch) for branch in self.ordered_indexes]
        self.flattened_indexes = [item for branch in self.ordered_indexes for item in branch]

        first_len = self.list_lengths[0]
        first_branch = self.flattened_indexes[:first_len]

        return first_branch
    

    
                        ###############   
                        ### OUTPUTS ###
                        ###############   


a                        = PathStripper(m, s, p)
compute_indexes          = a.compute_indexes()
get_filtered_lists       = a.get_filtered_lists()
compute_polylines        = a.compute_polylines()
compute_distances        = a.compute_distances()
compute_sorting          = a.compute_sorting()
unpack_branches_to_lists = a.unpack_first_branch()
