'''Construct the dual of the Voronoi diagram (which is the Delaunay triangulation) as a planar graph.
   Input: the list of shapely.geometry.polygon.Polygons, one for each center.
'''

def swap(pair): return pair[1],pair[0]

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
        if swap(segment) in self.segment2id:
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
    def process_cell(self, cell):
        '''cell is a polygon
        '''
        self.vertices.append([])
        pts = list(cell.exterior.coords)
        pt0 = pts[0]
        print("cell ", pts) #debugging
        first = True
        for pt1 in pts[1:]:
            print(pt0, pt1) #debugging
            new_id = self.new_segment_helper(pt0, pt1)
            pt0 = pt1
            if first:
                first_id = new_id
                first = False
            else: #not first
                self.next[prev_id] = new_id
            prev_id = new_id
        self.next[prev_id] = first_id
    
    def new_segment_helper(self, pt0, pt1):
            segment = pt0, pt1
            self.segmentmapper.add_segment(segment)
            new_id = self.segmentmapper.segment2id[segment]
            vertex_id = -1 # access last entry in vertex table
            self.vertices[vertex_id].append(new_id)
            return new_id

    def find_outer(self):
        '''After cells have been processed, those segments not appearing twice
        form the boundary of the infinite region.
        vertex id of infinite region is last vertex id'''
        #Among the reverses of segments that do appear, which ones do not appear?
        outer_segments = [swap(segment) for segment in self.segmentmapper.get_segments() if swap(segment) not in self.segmentmapper.get_segments()]
        #Among those, map first points to second points
        start2end = {pt0:pt1 for (pt0, pt1) in outer_segments}
        #Now form the cycle.
        initial_point = outer_segments[0][0]
        pt0 = initial_point
        vertex_number = self.num_vertices()
        self.vertices.append([])
        while True:
            pt1 = start2end[pt0]
            new_id = self.new_segment_helper(pt0, pt1)
            if pt1 == initial_point:
                break

    def next(self, id): return self.next[id]

    def id2segment(self, id): return self.segentmapper.get_segment(id)

    def num_vertices(self): return len(self.vertices)

    def num_darts(self): return len(self.next)
            
#convex_hulls = [sg.MultiPoint(region).convex_hull for region in proj_regions]
#G = build_dp_graph.EGraph()
#for poly in convex_hulls: G.process_cell(poly)
    
