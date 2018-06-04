'''
Read the stream of (census_block, relevant districts)
Keep a set of those census blocks with multiple relevant districts
Meanwhile, build the graph of census blocks.
For each census block x with multiple relevant districts,
  for each relevant district y
     compute the segment linking the centroid of x to the center corresponding to y
     and find the boundary segment of the block through which that segment goes,
     and use the graph to find the corresponding neighboring block
'''
from embedded_graph import EGraph
from shapely.geometry import LineString, Point
from util import find_intersecting

def generator(census_block_plus_relevant_districts_plus_something_collection, centers):
    boundary_elements = []
#    block_id2relevant_districts_and_centroid = {} # Will only store those where len(relevant_districts) > 1
    block_id2vertex = {}
    vertex2block_id = {}
    G = EGraph()
    for census_block, relevant_districts, something in census_block_plus_relevant_districts_plus_something_collection:
        block_id2vertex[census_block.ID] = G.num_vertices() #next vertex id
        vertex2block_id[G.num_vertices] = census_block.ID #could be a list because vertex IDs are consecutive integers
        G.process_cell(census_block.polygon) #eliminate redundant vertices?  Maybe not.
        if len(relevant_districts) > 1:
            boundary_elements.append((census_block, relevant_districts, something))
    G.find_outer()
    for census_block, relevant_districts, something in boundary_elements:
        dependents = []
        for relevant_district in relevant_districts:
            centroid_to_center_segment = LineString([census_block.centroid, Point(centers[relevant_district])])
            block_side_segment = find_intersecting(census_block.polygon.exterior, centroid_to_center_segment)
            if block_side_segment == None:
                dependent = census_block.ID
            else:
                d = G.rev(G.segmentmapper.segment2id[block_side_segment])
                dependent = G.head[d] if d in G.head else census_block.ID #same ID if no dependent
            dependents.append(dependent if dependent < G.num_vertices() else census_block.ID)
        yield census_block, relevant_districts, something, dependents

        
