'''
Read the stream of (census_block, relevant district_items)
Keep a set of those census blocks with multiple relevant districts
Meanwhile, build the graph of census blocks.
For each census block x with multiple relevant districts,
  for each relevant district y
     compute the segment linking the centroid of x to the center corresponding to y
     and find the boundary segment of the block through which that segment goes,
     and use the graph to find the corresponding neighboring block
     This is stored in the corresponding relevant_district_item.  This is mutative but 
     could be made nonmutative by creating new relevant_district_items.
'''
from embedded_graph import EGraph
from shapely.geometry import LineString, Point
from util import find_intersecting

def gen(census_block_plus_collection, centers):
    boundary_elements = []
    block_id2vertex = {}
    vertex2block_id = {}
    G = EGraph()
    for census_block, relevant_district_items in census_block_plus_collection:
        block_id2vertex[census_block.ID] = G.num_vertices() #next vertex id
        vertex2block_id[G.num_vertices] = census_block.ID #could be a list because vertex IDs are consecutive integers
        G.process_cell(census_block.polygon) #eliminate redundant vertices?  Maybe not.
        if len(relevant_district_items) > 1:
            boundary_elements.append((census_block, relevant_district_items))
    # Do not find outer since there are many missing cells
    for census_block, relevant_district_items in boundary_elements:
        for relevant_district_item in relevant_district_items:
            centroid_to_center_segment = LineString([census_block.centroid, Point(centers[relevant_district_item.ID])])
            block_side_segment = find_intersecting(census_block.polygon.exterior, centroid_to_center_segment)
            if block_side_segment == None:
                relevant_district_item.dependee = census_block.ID
            else:
                d = G.rev(G.segmentmapper.segment2id[block_side_segment])
                relevant_district_item.dependee = G.head[d] if d in G.head else census_block.ID #same ID if no dependent
        yield census_block, relevant_district_items

        
