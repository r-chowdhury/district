'''Construct the dual of the Voronoi diagram (which is the Delaunay triangulation) as a planar graph.
   Input: the list of shapely.geometry.polygon.Polygons, one for each center.
'''

from math import sqrt

def swap(pair): return pair[1],pair[0]

def vec(tail, head): return head[0]-tail[0], head[1]-tail[1]

def dotproduct(u,v): return u[0]*v[0]+u[1]*v[1]

def normsq(u): return dotproduct(u,u)

def norm(u): return sqrt(normsq(u))

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

class SegmentMapper:
    def __init__(self):
        self.num_edges = 0
        self.id2segment = {}
        self.segment2id = {}

    def add_segment(self, segment):
        '''segment is a pair of points, where each point is a pair
           This procedure assigns a dart id for each segment it is given.
           The ids follow the LSB convention: for two segments that are the
           reverse of each other, the corresponding dart ids differ only in their LSBs.
           They have the same edge ids.
        '''
        if segment in self.segment2id or swap(segment) in self.segment2id:
            self.segment2id[segment] = self.segment2id[swap(segment)] + 1
        else: 
            self.segment2id[segment] = 2*self.num_edges
            self.num_edges += 1
        self.id2segment[self.segment2id[segment]] = segment

    def get_id(self, segment):
        return self.segment2id[segment]

    def get_segment(self, id):
        return self.id2segment[id]
    
    def get_segments(self): return self.segment2id

class EGraph:
    # Is self.vertices needed?
    def __init__(self):
        self.segmentmapper = SegmentMapper()
        self.vertices = []
        self.next = {}
        self.head = {}
                
    def rev(self, dart_id): return dart_id ^ 1
    
    def edge(self, dart_id): return dart_id >> 1
    
    def process_cell(self, cell):
        '''cell is a polygon
        '''
        self.vertices.append([])
        pts = list(cell.exterior.coords)[:-1] #omit last pt, which equals first
        _remove_redundant(pts) #first get rid of redundant pts
        for i in range(len(pts)):
            new_id = self.__new_segment_helper(pts[i], pts[(i+1)%len(pts)])
            if i==0:
                first_id = new_id
            else:
                self.next[prev_id] = new_id
            prev_id = new_id
        self.next[new_id] = first_id
    
    def __new_segment_helper(self, pt0, pt1):
            segment = pt0, pt1
            self.segmentmapper.add_segment(segment)
            vertex_id = len(self.vertices)-1 #last entry in vertices table
            new_id = self.segmentmapper.segment2id[segment]
            self.head[new_id] = vertex_id
            self.vertices[vertex_id].append(new_id)
            return new_id

    def find_outer(self):
        '''After cells have been processed, those segments not appearing twice
        form the boundary of the infinite region.'''
        #Among the reverses of segments that do appear, which ones do not appear?
        outer_segments = [swap(segment) for segment in self.segmentmapper.get_segments() if swap(segment) not in self.segmentmapper.get_segments()]
        #Among those, map first points to second points
        start2end = {pt0:pt1 for (pt0, pt1) in outer_segments}
        #Now form the cycle.
        initial_point = outer_segments[0][0]
        pt0 = initial_point
        self.vertices.append([])
        while True:
            pt1 = start2end[pt0]
            new_id = self.__new_segment_helper(pt0, pt1)
            if pt1 == initial_point:
                break
            pt0 = pt1

    def next(self, id): return self.next[id]

    def incoming(self, vertex_id): return self.vertices[vertex_id]

    def id2segment(self, id): return self.segentmapper.get_segment(id)

    def num_vertices(self): return len(self.vertices)

    def num_darts(self): return len(self.next)
            

#    def dual(self):
#        G = Egraph()
#        for dart in range(self.num_darts()):
#            G.next[dart] =




'''
import build_dp_graph
from Voronoi_boundaries import *
C_3D, A, assign_pairs, box = Parse("test_assignment.txt")
cellss = power_cells(C_3D, box)

G = build_dp_graph.EGraph()
for cell in cells: G.process_cell(cell)
G.find_outer()
'''    
