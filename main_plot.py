import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.spatial as sp
import shapely.geometry as sg
from shapely.geometry.polygon import Polygon
from matplotlib import colors as mcolors
import Voronoi_boundaries as vb

colors = [
'red',                #ff0000 = 255   0   0
'web-green',          #00c000 =   0 192   0
'web-blue',         #0080ff =   0 128 255
'dark-magenta',       #c000ff = 192   0 255
'dark-cyan',         #00eeee =   0 238 238
'dark-orange',        #c04000 = 192  64   0
'dark-yellow',        #c8c800 = 200 200   0
'royalblue',          #4169e1 =  65 105 225
'goldenrod',          #ffc020 = 255 192  32
'dark-spring-green',  #008040 =   0 128  64
'purple',             #c080ff = 192 128 255
'steelblue',          #306080 =  48  96 128
'dark-red',           #8b0000 = 139   0   0
'dark-chartreuse',    #408000 =  64 128   0
'orchid',             #ff80ff = 255 128 255
'aquamarine',         #7fffd4 = 127 255 212
'brown',              #a52a2a = 165  42  42
'yellow',          #ffff00 = 255 255   0
'turquoise'
'light-red',        #f03232 = 240  50  50
'light-green',        #90ee90 = 144 238 144
'light-blue',         #add8e6 = 173 216 230
'light-magenta',      #f055f0 = 240'85 240
'light-cyan',         #e0ffff = 224 255 255
'light-goldenrod',    #eedd82 = 238 221 130
'light-pink',         #ffb6c1 = 255 182 193
'light-turquoise',    #afeeee = 175 238 238
'gold',               #ffd700 = 255 215   0
'green',              #00ff00 =   0 255   0
'dark-green',         #006400 =   0 100   0
'spring-green',       #00ff7f =   0 255 127
'forest-green',     #228b22 =  34 139  34
'sea-green',          #2e8b57 =  46 139  87
'blue',               #0000ff =   0   0 255
'dark-blue',          #00008b =   0   0 139
'midnight-blue',      #191970 =  25  25 112
'navy',               #000080 =   0   0 128
'medium-blue',        #0000cd =   0   0 205
'skyblue',            #87ceeb = 135 206 235
'cyan',               #00ffff =   0 255 255
'magenta',            #ff00ff = 255   0 255
'dark-turquoise',     #00ced1 =   0 206 209
'dark-pink',          #ff1493 = 255  20 147
'coral',              #ff7f50 = 255 127  80
'light-coral',        #f08080 = 240 128 128
'orange-red',         #ff4500 = 255  69   0
'salmon',             #fa8072 = 250 128 114
'dark-salmon',        #e9967a = 233 150 122
'khaki',              #f0e68c = 240 230 140
'dark-khaki',         #bdb76b = 189 183 107
'dark-goldenrod',     #b8860b = 184 134  11
'beige',              #f5f5dc = 245 245 220
'olive',              #a08020 = 160 128  32
'orange',             #ffa500 = 255 165   0
'violet',             #ee82ee = 238 130 238
'dark-violet',        #9400d3 = 148   0 211
'plum',               #dda0dd = 221 160 221
'dark-plum',          #905040 = 144  80  64
'dark-olivegreen',    #556b2f =  85 107  47
'orangered4',         #801400 = 128  20   0
'brown4',             #801414 = 128  20  20
'sienna4',            #804014 = 128  64  20
'orchid4',            #804080 = 128  64 128
'mediumpurple3'      #8060c0 = 128  96 192
    ]


def Parse_census_boundary(filename):
    if(filename == ""): return []
    f = open(filename, "r")
    lines = f.readlines()
    census_boundary = []
    for l in lines:
        points = []
        s = l.split()
        for i in range(int(len(s)/2)):
            x = float(s[2*i])
            y = float(s[2*i+1])
            points.append([x,y])
        # print(points)
        census_boundary.append(Polygon(points))
        # print(type(census_boundary[-1]))
    f.close()
    return census_boundary

def Parse_census_assign(filename):
    if(filename == ""): return []
    f = open(filename, "r")
    lines = f.readlines()
    census_assign = {}
    i = 0
    for l in lines:
        s = l.split()
        # census_assign.append(int(s[1]))
        if(int(s[0]) == 0):
            print("AHAAHAA")
            exit()
        census_assign[int(s[0])] = int(s[1])
        
        # print("Census "+s[0]+" assigned to "+s[1])
    f.close()
    return census_assign


def PlotAllVoronoi(C, A, assignment, bounded_regions, bbox, output):
    f = open(output, "w")
    f.write(str(len(C))+" "+str(len(A))+"\n")
    for i in range(len(C)):
        f.write(str(C[i][0])+" "+str(C[i][1])+" "+str(colors[i])+"\n")
    for j in range(len(A)):
        f.write(str(A[j][0])+" "+str(A[j][1])+" "+str(colors[assignment[j]])+"\n")

    for r in bounded_regions:
        x,y = r.exterior.xy
        for i in range(len(x)):
            f.write(str(x[i])+","+str(y[i])+" ")
        f.write("\n") 
    f.close()

def plot_helperVoronoi(C_3D, A, assign_pairs, bbox, outputfile):
    C = [[p[0],p[1]] for p in C_3D]
    regions = vb.power_cells(C_3D, bbox)
    PlotAllVoronoi(C, A, assign_pairs, regions, bbox, outputfile)

def plot_helperVoronoi_fromfile(input_filename, outputfile):
    C_3D, A, assign_pairs, box = vb.Parse(input_filename)
    C = [[p[0],p[1]] for p in C_3D]
    regions = vb.power_cells(C_3D, bbox)
    PlotAllVoronoi(C, A, assign_pairs, regions, bbox, outputfile)






#######################################################
#######################################################
#######################################################
####### End of functions for Voronoi diagrams   #######
####### Begining of functions for GNUplot diagrams ####
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################


def ParseGNUplot(filename):
    f = open(filename, "r")
    lines = f.readlines()
    s = lines[0].split()
    nb_centers = int(s[0])
    nb_clients = int(s[1])
    x_min, y_min = (float("inf"),float("inf"))
    x_max, y_max = (-float("inf"),-float("inf"))
    
    C = []
    for i in range(1, nb_centers+1):
        s = lines[i].split()
        x = float(s[0])
        y = float(s[1])
        color = s[2]
        C.append([x,y,color])
        x_max = max(x_max, x)
        y_max = max(y_max, y)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        

    assign_pairs = {}
    A = []
    for i in range(nb_centers+1, nb_centers+nb_clients+1):
        s = lines[i].split()
        x = float(s[0])
        y = float(s[1])
        color = s[2]
        A.append([x,y,color])
        x_max = max(x_max, x)
        y_max = max(y_max, y)
        x_min = min(x_min, x)
        y_min = min(y_min, y)

    polygons = []
    for i in range(nb_centers+nb_clients+1, len(lines)):
        points_unsplit = lines[i].split()
        points = [[float(points_unsplit[j].split(",")[0]),
                       float(points_unsplit[j].split(",")[1])]
                    for j in range(len(points_unsplit))]
        polygons.append(Polygon(points))
        # print(polygons[-1].exterior.xy)
    f.close()
    return C,A,polygons,[[x_min,y_min],[x_max,y_max]]

    
def Parse_boundary(filename):
    f = open(filename, "r")
    lines = f.readlines()
    boundaries = []
    i = 0
    points = []
    for l in lines:
        if l == "\n" :
            boundaries.append(Polygon(points))
            points = []
            continue
        s = l.split()
        x = float(s[0])
        y = float(s[1])
        points.append([x,y])
    boundaries.append(Polygon(points))
    f.close()
    return boundaries
    
def Parse(filename):
    f = open(filename, "r")
    lines = f.readlines()
    s = lines[0].split()
    nb_centers = int(s[0])
    nb_clients = int(s[1])
    x_min, y_min = (float("inf"),float("inf"))
    x_max, y_max = (-float("inf"),-float("inf"))
    
        
    C = []
    for i in range(1, nb_centers+1):
        s = lines[i].split()
        x = float(s[0])
        y = float(s[1])
        color = s[2]
        C.append([x,y,color])
        x_max = max(x_max, x)
        y_max = max(y_max, y)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        

    assign_pairs = {}
    A = []
    for i in range(nb_centers+1, nb_centers+nb_clients+1):
        s = lines[i].split()
        x = float(s[0])
        y = float(s[1])
        color = s[2]
        A.append([x,y,color])
        x_max = max(x_max, x)
        y_max = max(y_max, y)
        x_min = min(x_min, x)
        y_min = min(y_min, y)

    polygons = []
    for i in range(nb_centers+nb_clients+1, len(lines)):
        points_unsplit = lines[i].split()
        points = [[float(points_unsplit[j].split(",")[0]),
                       float(points_unsplit[j].split(",")[1])]
                    for j in range(len(points_unsplit))]
        polygons.append(Polygon(points))
        # print(polygons[-1].exterior.xy)
    f.close()
    return C,A,polygons,[[x_min,y_min],[x_max,y_max]]


def GNUplot_boundary(p,f):
    f.write("set object polygon from ")
    # print("________")
    # print(p.exterior.xy)
    # print("________")
    # print(p, p.is_empty)
    # print("________")
    x,y = p.exterior.xy
    for i in range(len(x)):
        f.write(str(x[i])+","+str(y[i]))
        if i != len(x)-1:
            f.write(" to ")
    f.write(" fc rgb 'black' lc rgb 'black' lw 2\n")


def GNUplot_nonclipped(p,f):
    f.write("set object polygon from ")
    x,y = p.exterior.xy
    for i in range(len(x)):
        f.write(str(x[i])+","+str(y[i]))
        if i != len(x)-1:
            f.write(" to ")
    f.write(" fc rgb 'light-grey' lw 1.5\n")
    

    
def GNUplot_polygon(p,f,color):
    f.write("set object polygon from ")
    x,y = p.exterior.xy
    for i in range(len(x)):
        f.write(str(x[i])+","+str(y[i]))
        if i != len(x)-1:
            f.write(" to ")
    f.write(" fc rgb '"+color+"' fs solid lw 1.5\n")

    f.write("set object polygon from ")
    x,y = p.exterior.xy
    for i in range(len(x)):
        f.write(str(x[i])+","+str(y[i]))
        if i != len(x)-1:
            f.write(" to ")
    f.write(" fc rgb 'black' lw 1.5\n")

def GNUplot_boundary_census(p,f,color):
    f.write("set object polygon from ")
    x,y = p.exterior.xy
    for i in range(len(x)):
        f.write(str(x[i])+","+str(y[i]))
        if i != len(x)-1:
            f.write(" to ")
    f.write(" fc rgb '"+color+"' fs solid lw 0.2\n")

    f.write("set object polygon from ")
    x,y = p.exterior.xy
    for i in range(len(x)):
        f.write(str(x[i])+","+str(y[i]))
        if i != len(x)-1:
            f.write(" to ")
    f.write(" fc rgb 'black' lw 0.2\n")

    
def GNUplot_point(p,f):
    col = p[2]
    if p[2] in colors:
            col = colors[p[2]]
    f.write('set object circle at '+str(p[0])+","+str(p[1])+' radius char 0.2 fillcolor rgb "'+col+'"\n')

def GNUplot(C, A, boundary, polygons, clipped,
            bbox, outputfilename,
            boundary_census=[], boundary_census_assign=[]):
    f = open(outputfilename, "w")
    for i in range(len(clipped)):
        GNUplot_nonclipped(clipped[i],f)
    for i in range(len(polygons)):
        # col = C[i][2]
        col = polygons[i][1]
        pol = polygons[i][0]
        if type(pol) == sg.multipolygon.MultiPolygon:
            for p in pol:
                GNUplot_polygon(p, f, col)
            continue
        # print("color", colors[i])
        GNUplot_polygon(pol, f, col)
    for i in range(len(boundary)):
        if(boundary[i].is_empty): continue
        GNUplot_boundary(boundary[i],f)
    if boundary_census_assign != [] and boundary_census != []:
        for i in boundary_census_assign:
            if(boundary_census[i].is_empty): continue
            GNUplot_boundary_census(boundary_census[i], f,
                                    colors[boundary_census_assign[i]])
    offset_x = 0.1*(bbox[1][0]-bbox[0][0])
    offset_y = 0.1*(bbox[1][1]-bbox[0][1])
    f.write("set xrange ["+str(bbox[0][0]-offset_x)+":"+str(bbox[1][0]+offset_x)+"]\n")
    f.write("set yrange ["+str(bbox[0][1]-offset_y)+":"+str(bbox[1][1]+offset_y)+"]\n")
    f.write("set key off\n")
    f.write("set terminal pdf enhanced\n")
    f.write("set output '"+outputfilename+".pdf'\n")
    f.write("set size square\n")
    f.write("plot x lc rgb 'white'\n")
    # f.write("pause -1\n")
    f.close()

def get_approx_boundary(A):
    Ap = [[p[0],p[1]] for p in A]
    return sg.MultiPoint(Ap).convex_hull

def clip(polygons, boundary):
    clipped = polygons
    new_clipped = []
    for b in boundary:
        for i in range(len(polygons)):
            p = polygons[i]
            color = colors[i]
            if b.contains(p):
                # print("here with", i)
                new_clipped.append((p,color))
            elif p.intersects(b) :
                # print("There with", i)
                new_clipped.append((p.intersection(b), color))
    # for p in new_clipped:
    #     print(p)
    return new_clipped

def plot_helperGNUplot_fromfile(input_filename, boundary_filename,
                                boundary_census_filename,
                                census_assign_filename,
                                output_filename):
    C_3D, A, polygons, bbox = ParseGNUplot(input_filename)

    boundary = Parse_boundary(boundary_filename)
    clipped_polygons = clip(polygons, boundary)
    
    boundary_census = Parse_census_boundary(boundary_census_filename)
    boundary_census_assign = Parse_census_assign(census_assign_filename)
    GNUplot(C_3D, A, boundary, clipped_polygons, polygons,
            bbox, output_filename, 
            boundary_census,
            boundary_census_assign) #
            

def plot_helperGNUplot(C_3D, A, polygons, bbox, boundary_filename,
                       boundary_census_filename,
                       census_assign_filename,
                       output_filename):
    boundary = Parse_boundary(boundary_filename)

    clipped_polygons = clip(polygons, boundary)

    boundary_census = Parse_census_boundary(boundary_census_filename)
    boundary_census_assign = Parse_census_assign(census_assign_filename)

    GNUplot(C_3D, A, boundary, clipped_polygons, polygons,
            bbox, output_filename,
            boundary_census,
            boundary_census_assign) #
            
    
