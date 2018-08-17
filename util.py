from math import sqrt
from shapely.geometry import LineString

def swap(pair): return pair[1],pair[0]

def vec(tail, head): return head[0]-tail[0], head[1]-tail[1]

def dotproduct(u,v): return u[0]*v[0]+u[1]*v[1]

def normsq(u): return dotproduct(u,u)

def norm(u): return sqrt(normsq(u))

def pt2string(u): return str(u[0])+" " + str(u[1])+"\n"

def write_segment(f, segment): f.write(pt2string(segment[0])+pt2string(segment[1])+"\n")

def write_polygon(f, polygon):
    pts = polygon.exterior.coords
    for i in range(len(pts)):
        write_segment(f, (pts[i], pts[(i+1)%len(pts)]))

def find_intersecting(linear_ring, line_string):
    '''find where in the linear ring the line-string intersects.
    '''
    coords =  linear_ring.coords
    for i in range(len(coords)-1):
        if line_string.intersects(LineString([coords[i],coords[i+1]])):
            return coords[i],coords[i+1]
    #don't return anything if nothing intersects

    
def polygon_points(polygon):
    return frozenset(polygon.exterior.coords).union(*(i.coords for i in polygon.interiors))

def num_polygon_segments(polygon):
    return len(polygon.exterior.coords)-1 + sum(len(interior.coords) - 1 for interior in polygon.interiors)
