import sys
from embedded_graph import EGraph
import census_block_file
import closest_kd
import relevant_districts
import initial_population_assignment
import district_graph
import Voronoi_boundaries
from util import num_polygon_segments
'''
    The assignment of blocks to districts is derived as follows.
    If a block's assignment is specified in the output from the ILP solver,
    that assignment is used.  If a block is not assigned there but is assigned
    by do_redistrict, that assignment is used.  Finally, if it is not mentioned in
    either of these places (which means it has zero population and intersects only one 
    power cell), it is assigned to the district of the power cell containing it.
'''

def connectivity(state_abbreviation, state_boundary_shapefilename, assignment_filename, block_filename, ILP_assignment_filename, log_filename):
    assignment_file = open(assignment_filename)
    k, n = [int(x) for x in assignment_file.readline().split()]
    C_3D = [tuple(float(x) for x in assignment_file.readline().split()) for _ in range(k)]
    block_assignment = {int(s[0]):int(s[3]) for s in [line.split() for line in assignment_file]}
    ILP_assignment = {int(s[0]):int(s[1]) for s in [line.split() for line in open(ILP_assignment_filename)]}
    block_assignment.update(ILP_assignment)
    population = k * [0]
    bbox = district_graph.find_bbox(state_abbreviation, state_boundary_shapefilename, C_3D)
    cells = Voronoi_boundaries.power_cells(C_3D, bbox)
    G = district_graph.get(C_3D, cells, bbox)
    L = list(census_block_file.read(block_filename))
    #First, compute population per district
    for block in L:
        if block.population > 0:
            population[block_assignment[block.ID]] += block.population
    log_file = open(log_filename,'w')
    log_file.write("populations: ")
    for pop in population: log_file.write(str(pop) + " ")
    log_file.write("\n")
    log_file.write("Population difference: " + str(max(population) - min(population)) + "\n")
    #Now prepare to check connectivity
    block_ID2block = {block.ID:block for block in L}
    district2block_IDs = [[] for _ in range(k)]
    #Record assignment of blocks whose assignment is explicitly stated
    for block_ID, district_ID in block_assignment.items():
        district2block_IDs[district_ID].append(block_ID)
    #generate assignment of other blocks (each other block is simply assigned to the district whose cell contains it)
    L = list(closest_kd.gen(L, C_3D))
    for block, closest_center_ID in L:
        if block.ID not in block_assignment:
            district2block_IDs[closest_center_ID].append(block.ID)
    #Find for each block which districts it intersects
    M = [(B, i) for B, i in L if B.ID in block_assignment]
    L1 = list(relevant_districts.gen(M, G)) #Could speed this up by running it only on those blocks explicitly assigned to districts
    block_ID2relevant_districts = {b.ID:set(relevant_district_info.keys()) for b, relevant_district_info in L1}
    block_ID2relevant_districts.update({b.ID:{i} for (B, i) in L if B.ID not in block_assignment})
    #Check connectivity of each district
    failure_flag = False
    for i in range(len(cells)):
        log_file.write("district"+str(i)+"\n")
        vertex2block_ID = {}
        n = int(1.1*len(district2block_IDs[i]) + sum(len(block_ID2block[block_ID].polygon.interiors) for block_ID in district2block_IDs[i])) #estimate number of vertices
        m = int(.6*sum(num_polygon_segments(block_ID2block[block_ID].polygon) for block_ID in district2block_IDs[i])) #estimate number of edges
        G = EGraph(m, n, 1e-12) #allow for some rounding error in matching line segments
        for block_ID in district2block_IDs[i]:
            for district_ID in block_ID2relevant_districts[block_ID]:
                geom = block_ID2block[block_ID].polygon.intersection(cells[district_ID])
                if geom.geom_type == 'LineString':
                    print("verify ", block_ID)
                    print(list(block_ID2block[block_ID].polygon.exterior.coords))
                    print("LineString")
                    print(list(geom.coords))
                    continue
                if geom.geom_type in ['Polygon', 'MultiPolygon']:
                    polygons = [geom] if geom.geom_type == 'Polygon' else geom #allows one to deal uniformly with a single polygon or many
                    for polygon in polygons:
                        vertex2block_ID[G.num_vertices()] = block_ID
                        v = G.num_vertices()
                        G.add_region(polygon)
        #test connectivity
        component_reps, v2component_number, sizes = G.connected_components(lambda x: True)
        if len(sizes) > 1:
                failure_flag = True
        if len(sizes) > 1 and max(sizes[1:]) > 1:
                log_file.write("sizes of components: ")
                for size in sizes: log_file.write(str(size)+" ")
                log_file.write("\n")
        for v in component_reps[1:]:
                log_file.write("vertex " + str(v) + " corresponds to block " +  str(vertex2block_ID[v]) + "\n")
        log_file.flush()
    if failure_flag:
        sys.exit(-1)

        
if __name__ == "__main__":
    args = sys.argv[1:]
    state_abbreviation = args.pop(0)
    state_boundary_shapefilename = args.pop(0)
    blockfilename = args.pop(0)
    assignment_filename = args.pop(0)
    block_assignment_filename = args.pop(0)
    log_filename = args.pop(0)
    connectivity(state_abbreviation, state_boundary_shapefilename, assignment_filename, blockfilename, block_assignment_filename, log_filename)

#python3 verify.py RI shapestate_data/cb_2017_us_state_500k RI_blocks makefile_outputs/do_redistrict/RI makefile_outputs/split_pulp/RI verify/RI.log
        
