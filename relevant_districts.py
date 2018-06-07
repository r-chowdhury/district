'''For each census block, find the districts it intersects --- at least min(2, number of intersecting districts).
(Current implementation might miss a third intersecting district.)

   input: sequence of pairs (census_block instance, ID of a district containing centroid)
   output: sequence of pairs (census_block instance, list of IDs of districts the census block intersects)
'''
# from embedded_graph import EGraph
from shapely.geometry import LineString  #, shape?


class Relevant_District_Item:
    def __init__(self, ID):
        self.ID = ID


def gen(census_block_plus_district_ID_collection, district_graph):
    for census_block, district_ID in census_block_plus_district_ID_collection:
        # print("relevant districts") #for debugging
        # district_ID is ID of corresponding vertex in district_graph

        # below misses the case when block contains a district
        # that doesn't contain the block centroid -neal

        relevant_districts = {district_ID}
        neighboring_darts = district_graph.vertices[district_ID]
        for d in neighboring_darts:
            segment = district_graph.segmentmapper.id2segment[d]
            if census_block.polygon.intersects(LineString(segment)):
                neighbor = district_graph.head[district_graph.rev(d)]
                if neighbor < district_graph.num_vertices()-1:  # if correspondings to a finite cell
                    relevant_districts.add(neighbor)
        yield census_block, [Relevant_District_Item(i) for i in relevant_districts]


'''
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
