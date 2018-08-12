import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.spatial as sp
import shapely.geometry as sg
from matplotlib import colors as mcolors
from util import vec, dotproduct, norm

def Parse(filename):
    f = open(filename, "r")
    lines = f.readlines()
    s = lines[0].split()
    nb_centers = int(s[0])
    nb_clients = int(s[1])
    
    C = []
    for i in range(1, nb_centers+1):
        s = lines[i].split()
        x = float(s[0])
        y = float(s[1])
        z = float(s[2])
        C.append([x,y,z])
        
    assign_pairs = {}
    A = []
    j = 0
    for i in range(nb_centers+1, nb_centers+nb_clients+1):
        s = lines[i].split()
        ids = int(s.pop(0))
        x = float(s.pop(0))
        y = float(s.pop(0))
        A.append([x,y])
        assign_pairs[j] = int(s.pop(0))
        j+=1
    f.close()
    return C,A,assign_pairs

def find_bbox(pts):
    #supposed to handle a mixture of 2d and 3d points
    max_pt = [max(pt[i] for pt in pts if len(pt) > i) for i in range(3)]
    min_pt = [min(pt[i] for pt in pts if len(pt) > i) for i in range(3)]
    return min_pt, max_pt

def find_extent(bbox):
    minpt, maxpt = bbox
    return [maxpt[i] - minpt[i] for i in range(3)]

def unbounded(input_region): return any(x==-1 for x in input_region)

def find_proj(bounded_regions):
    proj_regions = []
    # print(bounded_regions)
    for i in range(len(bounded_regions)):
        region = bounded_regions[i]
        proj_regions.append([])
        for p1 in region:
            if p1[2] < 0: continue
            for p2 in region:
                if p2[2] > 0: continue
                v = [p2[0]-p1[0],
                     p2[1]-p1[1],
                     p2[2]-p1[2]]
                t = -p1[2]/v[2]
                proj_point = [p1[0] + t*v[0],
                              p1[1] + t*v[1]]
                proj_regions[i].append(proj_point)
    return proj_regions

def region_contains(bounded_region, pt):
    hull = sp.ConvexHull(bounded_region+[np.array(pt)])
    return set(bounded_region) == {tuple(hull.points[i]) for i in hull.vertices}

def find_region_containing(bounded_regions, pt):
    '''Given a list of bounded regions (each specified by a list of points), and given a point,
       return the first bounded region that contains the point.  (Assumes there is at least one.)'''
    regions_containing = [bounded_region for bounded_region in bounded_regions if region_contains(bounded_region, pt)]
    assert len(regions_containing) == 1
    return regions_containing[0]

from util import norm

def _remove_redundant(pts):
    "Mutates a list of points to get rid of those points that are not needed to define polygon"
    i = 0
    while i < len(pts): #list pts changes during loop
        #test if point i+1 is redundant
        vec1 = vec(pts[i], pts[(i+1)%len(pts)])
        vec2 = vec(pts[(i+1)%len(pts)], pts[(i+2)%len(pts)])
        if dotproduct(vec1, vec2) >= .999999*norm(vec1)*norm(vec2):
            del pts[(i+1)%len(pts)]
        else:
            i = i+1

def power_cells(C_3D, bbox):
    minpt, maxpt = bbox
    extent = find_extent([minpt,maxpt])
    smallpt, bigpt = [minpt[i]-extent[i] for i in range(3)], [maxpt[i]+extent[i] for i in range(3)]
    boundary = np.array([smallpt, [bigpt[0],smallpt[1],smallpt[2]],
                     [smallpt[0],bigpt[1],smallpt[2]],
                     [smallpt[0],smallpt[1],bigpt[2]],
                     [bigpt[0],bigpt[1],smallpt[2]],
                     [smallpt[0],bigpt[1],bigpt[2]],
                     [bigpt[0],smallpt[1],bigpt[2]],
                     bigpt])
    diagram = sp.Voronoi(np.concatenate((C_3D,boundary)))
    #A 'bounded region' is a list of tuples
    bounded_regions = [[tuple(diagram.vertices[j]) for j in region]
                       for region in diagram.regions
                       if region != [] and not unbounded(region)]
    ordered_bounded_regions = [find_region_containing(bounded_regions, pt) for pt in C_3D]
    proj_regions = find_proj(ordered_bounded_regions)
    polygons = [sg.MultiPoint(region).convex_hull for region in proj_regions] #if region != []]
    exteriors = [list(gon.exterior.coords) for gon in polygons]
    for L in exteriors:
        _remove_redundant(L)
    return [sg.Polygon(L) for L in exteriors]

def power_cells_fromfile(filename):
    C_3D, A, assign_pairs = Parse(filename)
    bbox = find_bbox(C_3D+A)
    return power_cells(C_3D, bbox)

    
if __name__ == '__main__':
    power_cells = power_cells_fromfile(sys.argv[1])
    def getCoords(polygon):
        return list(polygon.exterior.coords)
    coords = map(getCoords, power_cells)
    print(list(coords))
    if len(sys.argv) < 2:
        print("Use: ", sys.argv[0], "[file name]")
        exit(-1)
    #print(power_cells_fromfile(sys.argv[1]))
     # Parse_and_plot_boundary(sys.argv[2])
    #plot_helper(C_3D, A, assign_pairs, bbox, sys.argv[2])
    
