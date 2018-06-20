"""
Goal: for each census block and each district to which the census block could be assigned,
find the neighboring census block that is closer to the center.

Maybe an improvement would be to write to temporary file the blocks, organized by relevant district,
and then read them in one by one so that the program doesn't use so much memory.
"""
from embedded_graph import EGraph

# from shapely.geometry import LineString, Point
from collections import deque
import time
#from plotting import plot_polygons #for debugging

# import deeper


def get(census_block_plus_collection, cells):
    debugflag = True
    time_start = time.clock()
    block_id2block_plus = {}
    boundary_block_IDs = set()
    relevant_blocks = [
        [] for _ in range(len(cells))
    ]  # boundary vertices intersecting district i
    decision_blocks = []
    for block, relevant_district_items in census_block_plus_collection:
        if block.ID % 10000 == 0: print("block_bfs.py phase 1", block.ID)
        #Build set of IDs of blocks that are boundary blocks
        if len(relevant_district_items)> 1:
            boundary_block_IDs.add(block.ID)
            #Build list of blocks that must be decided upon
            if block.population > 0:
                decision_blocks.append((block, relevant_district_items))
        #Keep track of which districts the blocks are relevant to
        for item in relevant_district_items:
            relevant_blocks[item.ID].append(block)
            item.dependee = block.ID # in case the vertex is not reached by BFS, set its dependee field to itself to indicate no true dependee
    for i in range(len(cells)):
        #Build graph of blocks relevant to power cell i
        G = EGraph()
        internal_vertices = set()
        vertex2block_plus = {}  # maps a vertex to corresponding block and associated items
        for block in relevant_blocks[i]:
            if block.population > 0 and block.ID in boundary_block_IDs:
                vertex2block_plus[G.num_vertices()] = block, relevant_district_items
            if block.ID not in boundary_block_IDs:
                internal_vertices.add(G.num_vertices())
            if block.ID in boundary_block_IDs and block.population == 0:
                geometry = block.polygon.intersection(cells[i])
                if geometry.geom_type == 'Polygon':
                    G.add_region(geometry)
                else:
                    if geometry.geom_type == 'MultiPolygon':
                        for polygon in geometry:
                            G.add_region(polygon)
                    else:
                        print("block_bfs2 ", geometry_geom_type, " ID ", block.ID)
            else:
                G.add_region(block.polygon)
        #Find largest connected component of internal vertices
        def internal(v):
            return v in internal_vertices
        print("block_bfs2")
        component_reps, v2component_number, sizes = G.connected_components(internal)
        big_component_number = max(range(len(sizes)), key = lambda j:sizes[j])
        #BFS to find parents/dependees
        #Initialize core
        waiting = deque(v for v in range(G.num_vertices()) if v in v2component_number and v2component_number[v] == big_component_number)
        visited = set(waiting)
        counter = 0
        while len(waiting) > 0:
            if counter % 10000 == 0: print("block_bfs.py phase 2, counter ", counter)
            counter = counter + 1
            v = waiting.pop()
            for w in G.neighbors(v):
                if w not in visited:
                    visited.add(w)
                    waiting.appendleft(w)
                    if w in vertex2block_plus and v in vertex2block_plus:
                        for item in vertex2block_plus[w][1]:
                            if item.ID == i:
                                item.dependee = vertex2block_plus[v][0].ID
                                break
    return decision_blocks

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
