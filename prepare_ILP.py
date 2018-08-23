import census_block_file
import closest_kd
import relevant_districts
#import areas_of_intersection
import initial_population_assignment
import district_graph
import block_bfs
import Voronoi_boundaries
#import census_block_district_intersection
import initial_discrepancy
import time
import sys

def test(state_abbreviation, state_boundary_shapefilename, census_shapefilename, assignment_filename, block_output_file):
    assignment_file = open(assignment_filename)
    k, n = [int(x) for x in assignment_file.readline().split()]
    C_3D = [tuple(float(x) for x in assignment_file.readline().split()) for _ in range(k)]
    bbox = district_graph.find_bbox(state_abbreviation, state_boundary_shapefilename, C_3D)
    cells = Voronoi_boundaries.power_cells(C_3D, bbox)
    G = district_graph.get(C_3D, cells, bbox)
    def merge(x,y):
        relevant_district_items = y[1]
        district2pop = x[1]
        for item in relevant_district_items:
            item.population = district2pop[item.ID] if item.ID in district2pop else 0
        return y
    start_time = time.clock()
    L = list(census_block_file.read(census_shapefilename))
    print("time 1 ", time.clock() - start_time)
    start_time = time.clock()
    L = list(closest_kd.gen(L, C_3D))
    print("time 2 ", time.clock() - start_time)
    start_time = time.clock()
    L = list(relevant_districts.gen(L, G))
    #L = list(census_block_district_intersection.gen(L, cells, len(L)))
    print("time 3 ", time.clock() - start_time)
    start_time = time.clock()
    #L = list(areas_of_intersection.gen(L, cells))
    L, decided_block_IDs = block_bfs.get(L, cells, len(L))
    print("time 5 ", time.clock() - start_time)
    #Write blocks to block_output_file
    for block, _ in L:
        census_block_file.write_census_block(block_output_file, block.ID, block.block_type, block.population, block.polygon)
    block_output_file.close()
    d = {block.ID:(block, rel) for block,rel in L if block.ID not in decided_block_IDs}
    power_diagram_result = {id:pop_assignment for id, pop_assignment in initial_population_assignment.gen(assignment_filename)}
    #Here, item.population is the population of the block assigned to the district by the balanced solution
    #If the block is not represented in power_diagram_result, the block's population is zero.
    for block, rel in L:
            for district, info in rel.items():
                info.population = power_diagram_result[block.ID].get(district, 0) if block.ID in power_diagram_result else 0
            yield block, rel


if __name__ == '__main__':
    args = sys.argv[1:]
    state_abbreviation = args.pop(0)
    state_boundary_shapefilename = args.pop(0)
    shapefilename = args.pop(0)
    assignment_filename = args.pop(0)
    output_filename = args.pop(0)
    processed_block_filename = args.pop(0)
    fout = open(output_filename, 'w')
    block_output_file = open(processed_block_filename, 'wb')
    for district_discrepancy in initial_discrepancy.find(assignment_filename):
        fout.write(str(district_discrepancy)+" ")
    fout.write("\n")
    for census_block, relevant_district_items in test(state_abbreviation, state_boundary_shapefilename, shapefilename, assignment_filename, block_output_file):
        fout.write(str(census_block.ID)+" ")
        for district, info in relevant_district_items.items():
            for value in [district, info.population, info.area, info.dependee if info.dependee != -1 else census_block.ID]:
                fout.write(str(value)+" ")
        fout.write("\n")
    fout.close()
