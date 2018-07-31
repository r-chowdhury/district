"""
For each district, build a graph of the blocks that overlap that district.  Find the connected components,
 and find the connected component with the greatest number of vertices.
 This component is the *core* of the district.  Compute a breadth-first-search tree with core as root.
 For each block belonging to the core of a district, the block can be assigned only to that district.
 For a block not belonging to the core, the set of candidate districts consists of the set of district it overlaps,
 together with the set of candidate districts of ancestors.  For each candidate district, compute the block's 
 dependee as follows:
  (1) if the block overlaps the candidate district then the block's dependee for that district is the BFS parent in the BFS from that district;
  (2) if a proper ancestor in the BFS tree for another district intersects the candidate district then the dependee is the parent in that BFS tree.

The data structures used:
 * block_id2block_plus, which maps a block's ID to a pair consisting of the census block object and a list of assignment element objects
 * relevant_blocks, which maps a district ID to the list of block objects (maybe it should be the IDs) that intersect that district.
 * block_id2relevant_districts, which maps the ID of a block to the districts overlapping that block.
 * boundary_block_IDS, which includes the ID of every block that intersects multiple districts.
 * decided_IDs, which includes the IDs of blocks belonging to cores of districts.

For each district, a graph G is built of the relevant blocks.
 * vertex2block_ID maps each vertex of this graph to the corresponding block ID.  Note that
   some vertices of the graph represent the interior boundaries of polygons of blocks; these do not
   correspond to blocks so do not appear in vertex2block_ID.


"""
from embedded_graph import EGraph
from relevant_districts import Relevant_District_Item

# from shapely.geometry import LineString, Point
from collections import deque
import time
#from plotting import plot_polygons #for debugging

# import deeper


def get(census_block_plus_collection, cells):
    block_id2block_plus = {}
    boundary_block_IDs = set()
    relevant_blocks = [
        [] for _ in range(len(cells))
    ]  # boundary vertices intersecting district i
    decided_IDs = set()
    for block, relevant_district_items in census_block_plus_collection:
        if block.ID % 10000 == 1: print("block_bfs.py phase 1", block.ID)
        block_id2block_plus[block.ID] = block, relevant_district_items
        #Build set of IDs of blocks that are boundary blocks
        if len(relevant_district_items)> 1:
            boundary_block_IDs.add(block.ID)
        #Keep track of which districts the blocks are relevant to
        for item in relevant_district_items:
            relevant_blocks[item.ID].append(block)
            item.dependee = block.ID # in case the vertex is not assigned parent by BFS, set its dependee field to itself to indicate no true dependee
    for i in range(len(cells)):
        #Build graph of blocks relevant to power cell i
        G = EGraph()
        boundary_vertices = set()
        vertex2block_ID = {}  # maps a vertex to corresponding block ID
        for block in relevant_blocks[i]:
            vertex2block_ID[G.num_vertices()] = block.ID
            if block.ID in boundary_block_IDs:
                boundary_vertices.add(G.num_vertices())
            #if block.ID in boundary_block_IDs and block.population == 0:
            #    geometry = block.polygon.intersection(cells[i])
            #    if geometry.geom_type == 'Polygon':
            #        G.add_region(geometry)
            #    else:
            #        if geometry.geom_type == 'MultiPolygon':
            #            for polygon in geometry:
            #                G.add_region(polygon)
            #        else:
            #            print("block_bfs2 ", geometry_geom_type, " ID ", block.ID)
            #else:
            G.add_region(block.polygon) #will produce multiple vertices if polygon has internal boundaries
            g = G.num_vertices() #for debugging
            pass #for debugging
        #Find largest connected component of internal vertices
        def internal(v):
            return v not in boundary_vertices
        print("block_bfs phase 2, district", i)
        component_reps, v2component_number, sizes = G.connected_components(internal)
        big_component_number = max(range(len(sizes)), key = lambda j:sizes[j])
        #BFS to find parents/dependees
        #Initialize core
        core = [v for v in range(G.num_vertices()) if v in v2component_number and v2component_number[v] == big_component_number]
        waiting = deque(core)
        visited = set(core)
        decided_IDs.update([vertex2block_ID[v] for v in core if v in vertex2block_ID]) # Don't need to consider vertices corresponding to inner boundaries---they don't correspond to blocks
        counter = 0
        vertex2candidate_districts = [set() for _ in range(G.num_vertices())]
        while len(waiting) > 0:
            if counter % 10000 == 0: print("block_bfs.py phase 2, counter ", counter)
            counter = counter + 1
            v = waiting.pop()
            v0 = v #find the vertex corresponding to the outer boundary of the polygon corresponding to v
            while v0 not in vertex2block_ID:
                v0 = v0 - 1
            parent_block_ID = vertex2block_ID[v0]
            for w in G.neighbors(v):
                if w not in visited:
                    visited.add(w)
                    waiting.appendleft(w)
                    if w in vertex2block_ID: # if w corresponds to a block (as opposed to corresponding to an inner boundary)
                        #Add dependee for current district
                        for item in block_id2block_plus[vertex2block_ID[w]][1]: 
                            if item.ID == i:
                                item.dependee = parent_block_ID
                                break
                        #Add items with dependee for foreign districts that are relevant to parent
                        native_districts = {item.ID for item in block_id2block_plus[vertex2block_ID[w]][1]} # districts overlapping the block
                        vertex2candidate_districts[w] = native_districts | vertex2candidate_districts[v0] # native districts together with foreign districts
                        for parent_candidate_district in vertex2candidate_districts[v0] - native_districts: #foreign only
                            assert i in native_districts
                            # Create a new relevant district item for each foreign district
                            item = Relevant_District_Item(parent_candidate_district)
                            item.area = 0 # zero area of intersection with the foreign district
                            item.dependee = parent_block_ID
                            block_id2block_plus[vertex2block_ID[w]][1].append(item)
    return [x for ID, x in block_id2block_plus.items() if ID not in decided_IDs]

"""
import census_block
import closest
import relevant_districts
import district_graph

assignment_filename = "/Users/klein/drive/District_data/RI_new_assignment.txt"
G, C_3D = district_graph.get(assignment_filename)
shapefilename = "/Users/klein/drive/District_data/RhodeIsland_census_block_data/tabblock2010_44_pophu"
closest_it = closest.gen(census_block.gen(shapefilename), C_3D)
relevant_it = relevant_districts.gen(closest_it, G)
L = get(relevant_it, len(C_3D))
print("here")
"""
