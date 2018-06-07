'''
Goal: for each census block and each district to which the census block could be assigned,
find the neighboring census block that is closer to the center.

Maybe an improvement would be to write to temporary file the blocks, organized by relevant district,
and then read them in one by one so that the program doesn't use so much memory.
'''
from embedded_graph import EGraph
from shapely.geometry import LineString, Point
from collections import deque
import pickle
import time
import deeper

def get(census_block_plus_collection, k):
    debugflag = True
    time_start = time.clock()
    G = EGraph()
    vertex2block_id = {}
    relevant_vertices = [set() for _ in range(k)] # boundary vertices intersecting district i
    boundary_vertices = set()
    vertex2block_plus = {} #maps a vertex to corresponding block and associated items
    #create graph G of blocks,  assign them to relevant centers, identify boundary vertices, keep track of blocks of boundary vertices
    counter = 0
    for block, relevant_district_items in census_block_plus_collection:
        if counter % 10000 == 0: print("block_bfs.py phase 1, counter", counter)
        counter = counter + 1
        v = G.num_vertices()
        vertex2block_id[v] = block.ID
        G.process_cell(block.polygon) #new vertex ID is v  --- eliminate redundant vertices?  Maybe not.
        if len(relevant_district_items) > 1: 
            for item in relevant_district_items:
                relevant_vertices[item.ID].add(v)
            boundary_vertices.add(v)
            vertex2block_plus[v] = block, relevant_district_items
    time_start = time.clock()
    #BFS to find parents/dependees for boundary blocks
    for i in range(k):
        waiting = deque(v for v in relevant_vertices[i] if v not in boundary_vertices)
        visited = set(waiting)
        counter = 0
        while len(waiting) > 0:
            if counter % 10000 == 0: print("block_bfs.py phase 2, counter ", counter)
            counter = counter + 1
            v = waiting.pop()
            for incoming_dart in G.incoming(v):
                outgoing_dart = G.rev(incoming_dart)
                if outgoing_dart in G.head:
                    w = G.head[outgoing_dart]
                    if w not in visited and w in relevant_vertices[i]:
                        visited.add(w)
                        waiting.appendleft(w)x
                        for item in vertex2block_plus[w][1]:
                            if item.ID == i:
                                item.dependee = vertex2block_id[v]
                                break
        #Check if, for each district i, the relevant vertices were reached by BFS
        for v in relevant_vertices[i]:
            for item in vertex2block_plus[v][1]:
                if item.ID == i and v not in visited:
                    item.dependee = vertex2block_plus[v][0].ID # the block has no dependee, so assign its own ID
    #Now output the results
    return vertex2block_plus.values() #indexed by boundary_vertices


'''
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
'''
