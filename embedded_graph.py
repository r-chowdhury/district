'''Construct the dual of the Voronoi diagram (which is the Delaunay triangulation) as a planar graph.
   Input: the list of shapely.geometry.polygon.Polygons, one for each center.
'''

from util import swap, vec, dotproduct, norm
from collections import defaultdict
from math import atan2
from shapely.geometry import Point
from segment_definition import Segment
import array
import numpy

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

#def round_float(x, epsilon):
#    return int(x/epsilon)*epsilon

#def round_pt(pt, epsilon):
#    return (round_float(pt[0], epsilon), round_float(pt[1], epsilon))

#def round_segment(seg, epsilon):
#    return round_pt(seg[0], epsilon), round_pt(seg[1], epsilon)

class PreUsedSegment(Exception):
    def __init__(self, id):
        self.id = id

class SegmentMapper:
    def __init__(self, cancel = False):
        self.num_edges = 0
        self.id2segment = []
        self.id2matched = array.array('B')
        self.segment2id = {}
        self.cancel = cancel
    
    def add_segment(self, segment):
        '''segment is a pair of points, where each point is a pair
           This procedure assigns a dart id for each segment it is given.
           The ids follow the LSB convention: for two segments that are the
           reverse of each other, the corresponding dart ids differ only in their LSBs.
           They have the same edge ids
           The procedure returns the dart id, and stores the dart id-to-segment association in id2segment.
           It also stores the the association from (a possibly rounded version of) the segment to the id in segment2id
        '''
        seg = Segment(segment)
        if seg.swap() in self.segment2id:
            new_id = self.segment2id[seg.swap()] + 1
            self.id2matched[new_id >> 1] = 1
            if self.cancel:
                del self.segment2id[seg.swap()]
                self.id2segment[new_id - 1] = 0
        else:
            new_id = 2*self.num_edges
            self.segment2id[seg] = new_id
            self.num_edges += 1
            self.id2segment.append(seg)
            self.id2matched.append(0)
        return new_id

    def get_id(self, segment):
        seg = Segment(segment)
        return self.segment2id[seg] if seg in self.segment2id else self.segment2id[seg.swap()]+1

    def get_segment(self, ID):
        return self.id2segment[ID >> 1].pt_pair() if ID % 2 == 0 else self.id2segment[(ID-1) >> 1].swap().pt_pair()
    
    def get_missing_segments(self):
        '''Includes the reverse of each segment whose reverse has not been added'''
        return [self.id2segment[i].swap().pt_pair() for i in range(len(self.id2segment)) if not self.id2matched[i]]

class EGraph:
    def __init__(self, m, n, epsilon=0):
        '''if geometric object provided, neighbors are restricted to those along segments
        that intersect the geometric object'''
        self.number_of_vertices = 0
        self.number_of_darts = 0
        self.segmentmapper = SegmentMapper()
        Segment.eps = epsilon #A hack to get segments to match when approximately the same
        #(This is a hack because this applies to all Segments.)
        self.vertices = [array.array('L') for _ in range(n)] 
        self.next = numpy.full(2*m, -1, dtype=numpy.int64)
        self.head = numpy.full(2*m, -1, dtype=numpy.int64)
        self.outer2inner = {}  #[array.array('L') for _ in range(n)] #mapping vertex representing an outer boundary to vertices representing inner boundaries
        self.inner2outer = {}
                
    def rev(self, dart_id): return dart_id ^ 1
    
    def edge(self, dart_id): return dart_id >> 1
    
    def is_dart_present(self, dart_id): return self.head[dart_id] >= 0
    
    def add_region(self, region, remove_redundant = False):
        '''Region is a polygon with an outer boundary and possibly inner boundaries.
        To each boundary corresponds a vertex, with its own incoming darts.
        Darts incoming to a vertex correspond to segments that go around the boundary clockwise for outer boundary,
        counterclockwise for inner boundaries.
        '''
        outer_vertex = self.num_vertices() # vertex corresponding to outer boundary
        self._process_boundary(region.exterior, remove_redundant)
        inner_vertices = []
        for interior_boundary in region.interiors:
            inner_vertices.append(self.num_vertices()) # vertex corresponding to an inner boundary
            self._process_boundary(interior_boundary, remove_redundant)
        self.outer2inner[outer_vertex] = inner_vertices #link outer vertex to inner vertices
        for v in inner_vertices:
            self.inner2outer[v] = outer_vertex
    
    def _new_vertex(self):
        assert self.number_of_vertices < len(self.vertices)
        self.number_of_vertices += 1 #
        
    def _process_boundary(self, linear_ring, remove_redundant):
        self._new_vertex()
        pts = linear_ring.coords[:-1] #omit last pt, which equals first
        if remove_redundant: _remove_redundant(pts) #first get rid of redundant pts
        first_id = None
        for i in range(len(pts)):
            new_id = self._new_segment_helper(pts[i], pts[(i+1)%len(pts)]) #adds dart to vertices table
            if first_id == None:
                first_id = new_id
            else:
                self.next[prev_id] = new_id
            prev_id = new_id
        if first_id != None: #Could be that no points are included
            self.next[new_id] = first_id
    
    def _new_dart_helper(self, dart_id):
            vertex_id = self.number_of_vertices - 1
            self.head[dart_id] = vertex_id #record head of new dart
            self.vertices[vertex_id].append(dart_id) #add incoming dart to vertices table
            
    def _new_segment_helper(self, pt0, pt1):
            "adds dart to tables for new vertex (via _new_dart_helper) and returns id of new dart"
            segment = pt0, pt1
            new_dart_id = self.segmentmapper.add_segment(segment)
            self._new_dart_helper(new_dart_id)
            return new_dart_id

    def find_outer(self):
        '''After cells have been processed, those segments not appearing twice
        form boundaries of other regions.
        '''
        def head(segment): return segment[1]
        def tail(segment): return segment[0]
        #Among the reverses of segments that do appear, which ones do not appear?
        outer_segments = self.segmentmapper.get_missing_segments()
        incident = defaultdict(list) #Will map each point to incident segments, or rather to pairs (segment, bool)
        #where bool indicates incoming (True) or outgoing (False)
        #Populate incident table 
        for segment in outer_segments:
            incident[tail(segment)].append((head(segment),False)) #outgoing
            incident[head(segment)].append((tail(segment), True)) #incoming
        #sort neighbors of each vertex according to angle
        def pt(pt_plus): return pt_plus[0]
        def incoming(pt_plus): return pt_plus[1]
        def angle_finder(start):
            return lambda end_plus: atan2(pt(end_plus)[1]-start[1], pt(end_plus)[0]-start[0])
        #Create and populate analogue of next table for the segments
        #(Not using true next table yet because it is helpful to known vertex id at same time)
        segment_next = {}
        for pt0,pts_plus in incident.items():
            pts_plus.sort(key=angle_finder(pt0))
        #Create vertices for the new polygons
        #Keep track of which darts have been assigned to vertices
        used= set()
        for initial_segment in outer_segments:
            if initial_segment not in used:
                #Create new vertex
                self._new_vertex()
                #Traverse cycle containing initial_segment
                segment = initial_segment
                prev_dart_id = None
                while segment != initial_segment or prev_dart_id == None:
                    used.add(segment) #record having traversed this segment
                    dart_id = self._new_segment_helper(tail(segment), head(segment))
                    if prev_dart_id != None:
                        self.next[prev_dart_id] = dart_id
                    incidence_list = incident[head(segment)] #incidence list for head of current segment
                    i = incidence_list.index((tail(segment), True)) #position of current segment
                    new_segment_head, incoming = incidence_list[(i+1) % len(incidence_list)]
                    segment = head(segment), new_segment_head
                    assert not incoming
                    prev_dart_id = dart_id
                self.next[prev_dart_id] = self.segmentmapper.get_id(segment) #complete the cycle

    def region_data(self, vertex_id):
        '''Given the id of the vertex corresponding to the outer boundary of a region, return the boundaries.
           (Maybe should just return a polygon?  That would require importing Polygon.)'''
        outer_boundary = [self.segmentmapper.get_segment(ID)[0] for ID in self.vertices[vertex_id]]
        inner_boundaries = [[self.segmentmapper.get_segment(ID)[0] for ID in self.vertices[inner_vertex_id]] for inner_vertex_id in self.outer2inner.get(vertex_id, [])]
        return outer_boundary, inner_boundaries
        
    def next(self, id): return self.next[id]

    def incoming(self, vertex_id): return self.vertices[vertex_id]

    def id2segment(self, id): return self.segmentmapper.get_segment(id)

    def num_vertices(self): return self.number_of_vertices

    def endpoints(self, dart_id):
        return [self.head[d] for d in [dart_id, self.rev(dart_id)]]

    def neighbors(self, v):
            adjoining = [self.head[self.rev(d)] for d in self.vertices[v] if self.is_dart_present(self.rev(d))]
            return adjoining + \
                  (self.outer2inner[v] if v in self.outer2inner else []) + \
                  ([self.inner2outer[v]] if v in self.inner2outer else [])

    def _visit(self, root, i, include_fn, v2component_number):
        "returns number of vertices"
        count = 0
        stack = [root]
        while stack != []:
            v = stack.pop()
            if v not in v2component_number and include_fn(v):
                count += 1
                v2component_number[v] = i
                stack.extend(self.neighbors(v))
        return count
        
    def connected_components(self, include_fn):
        v2component_number = {}
        sizes = []
        component_reps = []
        for vertex in range(self.num_vertices()):
            if vertex not in v2component_number and include_fn(vertex):
                sizes.append(self._visit(vertex, len(component_reps), include_fn, v2component_number))
                component_reps.append(vertex)
        return component_reps, v2component_number, sizes


'''
import embedded_graph
from Voronoi_boundaries import *
C_3D, A, assign_pairs, box = Parse("test_assignment.txt")
cells = power_cells(C_3D, box)

G = embedded_graph.EGraph()
for cell in cells: G.process_cell(cell)
G.find_outer()
'''    

            



'''
class PrimalEGraph(EGraph):
    def __init__(self):
        EGraph.__init__(self)
        self.primal_vertices = {}
'''
