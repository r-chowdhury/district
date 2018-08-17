from embedded_graph import EGraph
from relevant_districts import Relevant_District_Item
from census_block import Intersection_Block
from collections import deque
from util import num_polygon_segments

'''Idea: mix find intersections with building bfs
   Also save blocks to a file
'''

def get(census_block_plus_district_items_collection, cells, starting_number):
    block_ID_counter = starting_number # counter is used for assigning IDs to new artificial blocks
    block_ID2block_plus = {}
    #boundary_block_IDs = set()
    district2relevant_block_IDs = [[] for _ in range(len(cells))]
    decided_block_IDs = set() # IDs of blocks that do not need to be represented in ILP because they are already decided
    intersected_block_IDs = set() #IDs of blocks that do not need to be represented in ILP because they are broken up into artificial blocks
    for block, district_items in census_block_plus_district_items_collection:
        block_ID2block_plus[block.ID] = (block, district_items)
        for district in district_items: # keys
            district2relevant_block_IDs[district].append(block.ID)
    for i in range(len(cells)):
        #Build graph of blocks relevant to power cell i
        vertex2block_ID = {} #could use a list instead of a dictionary
        block_ID2vertices = {} #each value is a tuple of vertices
        boundary_vertices = set()
        n = int(1.2*len(district2relevant_block_IDs[i])) #estimate number of vertices
        m = int(.6*sum(num_polygon_segments(block_ID2block_plus[block_ID][0].polygon) for block_ID in district2relevant_block_IDs[i])) #estimate number of edges
        G = EGraph(m, n, 1e-12)
        for block_ID in district2relevant_block_IDs[i]:
            block_plus = block_ID2block_plus[block_ID]
            block = block_plus[0]
            is_multidistrict = len(block_plus[1]) > 1
            current_vertices = []
            if is_multidistrict:
                geom = block.polygon.intersection(cells[i])
                polygons = [geom] if geom.geom_type == 'Polygon' else geom
            else:
                polygons = [block.polygon]
            divide_up_block = is_multidistrict and block.population == 0
            for polygon in polygons:
                    assert polygon.geom_type == 'Polygon'
                    v = G.num_vertices() #Next vertex to be created
                    current_vertices.append(v)
                    if is_multidistrict and block.population > 0:
                            boundary_vertices.add(v)
                    G.add_region(polygon)
                    current_block_ID = block_ID
                    if divide_up_block:
                            #create new artificial block whose polygon is intersection with district
                            intersected_block_IDs.add(block_ID)
                            current_block_ID = block_ID_counter
                            block_ID_counter += 1
                            new_block = Intersection_Block(current_block_ID, polygon, block_ID)
                            new_district_items = {i:Relevant_District_Item()} #completely new item; this won't have info such as area from original block
                            block_ID2block_plus[current_block_ID] = (new_block, new_district_items)
                            block_ID2vertices[current_block_ID] = (v,)
                    vertex2block_ID[v] = current_block_ID
            if not divide_up_block:
                block_ID2vertices[current_block_ID] = tuple(current_vertices)
        #Find largest connected component of internal vertices
        def external(v):
            return v in boundary_vertices or v in G.inner2outer and G.inner2outer[v] in boundary_vertices
        def internal(v):
            return not external(v)
        component_reps, v2component_number, sizes = G.connected_components(internal)
        big_component_number = max(range(len(sizes)), key = lambda j:sizes[j])
        #BFS to find parents/dependees
        #Initialize core
        core = [v for v in range(G.num_vertices()) if v in v2component_number and v2component_number[v] == big_component_number] #could iterate over keys of v2component_number
        #set dependee to self for each block corresponding to a vertex in core  THIS SHOULD EVENTUALLY NOT BE NECESSARY---USE INITIAL DEFALT VALUE (CURRENTLY -1)
        #for v in core:
        #    block_ID = vertex2block_ID[v] #are there some vertices in core that are not represented in vertex2block_ID?
        #    block_ID2block_plus[block_ID][1][i].dependee = block_ID #indicates no dependency for district i
        waiting = deque(core)
        visited = set(core)
        decided_block_IDs.update([vertex2block_ID[v] for v in core if v in vertex2block_ID]) # Don't need to consider vertices corresponding to inner boundaries---they don't correspond to blocks
        vertex2candidate_districts = [set() for _ in range(G.num_vertices())] #could use a dictionary
        def get_neighbors(v):
            L = [] #should be a set
            for w in G.neighbors(v):
                if w in vertex2block_ID: #False if w is a vertex representing an interior boundary
                    ID = vertex2block_ID[w]
                    L.extend(block_ID2vertices[ID])
                else:
                    L.append(w)
            return L
        while len(waiting) > 0:
            v = waiting.pop()
            v0 = v #find the vertex corresponding to the outer boundary of the polygon corresponding to v
            while v0 not in vertex2block_ID:
                v0 = v0 - 1
            parent_block_ID = vertex2block_ID[v0]
            for w in get_neighbors(v):
                if w not in visited:
                    visited.add(w)
                    waiting.appendleft(w)
                    if w in vertex2block_ID: # if w corresponds to a block (as opposed to corresponding to an inner boundary)
                        block_ID = vertex2block_ID[w]
                        relevant_district_items = block_ID2block_plus[block_ID][1]
                        # districts overlapping the block
                        native_districts = {district for district in relevant_district_items} #keys
                        # native districts together with foreign districts
                        vertex2candidate_districts[w] = native_districts | vertex2candidate_districts[v0]
                        #only update relevant_district_items once per block_ID for this district
                        if w == min(block_ID2vertices[block_ID]):
                            relevant_district_items[i].dependee = parent_block_ID
                            for parent_candidate_district in vertex2candidate_districts[v0] - native_districts: #foreign only
                                relevant_district_items[parent_candidate_district] = Relevant_District_Item(dependee=parent_block_ID)
    return [x for ID, x in block_ID2block_plus.items() if ID not in intersected_block_IDs], decided_block_IDs
                            

