'''For each census block, find the districts it intersects --- at least min(2, number of intersecting districts).
(Current implementation might miss a third intersecting district.)

   input: sequence of pairs (census_block instance, ID of a district containing centroid)
   output: sequence of pairs (census_block instance, list of IDs of districts the census block intersects)
'''
from shapely.geometry import LineString
from census_block import block_types
from collections import deque

class Relevant_District_Item:
    def __init__(self, dependee = -1):
        self.x = dependee
        i = 1
    
    @property
    def area(self): return 0 #currently not computing or using area
    
    @property
    def dependee(self):
        return self.x

    @dependee.setter
    def dependee(self, value):
        i = 1
        self.x = value

def gen(census_block_plus_district_ID_collection, district_graph):
    for census_block, district_ID in census_block_plus_district_ID_collection:
        # district_ID is ID of corresponding vertex in district_graph

        # below misses the case when block contains a district
        # that doesn't contain the block centroid -neal

        relevant_districts = {district_ID}
        if census_block.block_type != block_types['intersection']:
            waiting = deque({district_ID})
            while len(waiting) > 0:
                v = waiting.pop()
                neighboring_darts = district_graph.vertices[v]
                for d in neighboring_darts:
                    segment = district_graph.id2segment(d)
                    if census_block.polygon.intersects(LineString(segment)):
                        neighbor = district_graph.head[district_graph.rev(d)]
                        if neighbor < district_graph.num_vertices()-1:  # if corresponds to a finite cell
                            if neighbor not in relevant_districts:
                                relevant_districts.add(neighbor)
                                waiting.appendleft(neighbor)
        yield census_block, {i:Relevant_District_Item() for i in relevant_districts}


'''
from embedded_graph import EGraph

def find(iterator_maker):
    G = EGraph()
    block_id2vertex_id = {}
    block_id2
    counter = 0
    for census_block, district_ID in iterator_maker:
        G.process_cell(census_block.polygon)
        block_id2vertex_id[counter] = census_block.ID
        
    G.find_outer()
'''    
