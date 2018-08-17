import census_block_file
import closest_kd
import relevant_districts
import areas_of_intersection
import district_graph
import Voronoi_boundaries
import census_block_district_intersection_test
import pickle
import sys

def original_gen(state_abbreviation, state_boundary_shapefilename, census_shapefilename, assignment_filename):
    assignment_file = open(assignment_filename)
    k, n = [int(x) for x in assignment_file.readline().split()]
    C_3D = [tuple(float(x) for x in assignment_file.readline().split()) for _ in range(k)]
    bbox = district_graph.find_bbox(state_abbreviation, state_boundary_shapefilename, C_3D)
    cells = Voronoi_boundaries.power_cells(C_3D, bbox)
    G = district_graph.get(C_3D, cells, bbox)
    L = list(census_block_file.read(census_shapefilename))
    L = list(closest_kd.gen(L, C_3D))
    L = list(relevant_districts.gen(L, G))
    L = list(census_block_district_intersection_test.gen(L, cells, len(L)))
    for x in L: yield x

def gen(filename):
    fin = open(filename, 'b')
    

if __name__ == '__main__':
    args = sys.argv[1:]
    state_abbreviation = args.pop(0)
    state_boundary_shapefilename = args.pop(0)
    shapefilename = args.pop(0)
    assignment_filename = args.pop(0)
    #output_filename = args.pop(0)
    #fout = open(output_filename, 'wb')
    for census_block, relevant_district_items in original_gen(state_abbreviation, state_boundary_shapefilename, shapefilename, assignment_filename):
        if census_block.ID % 10000 == 0: print(census_block.ID)
        #census_block.write(fout)
        #pickle.dump(relevant_district_items)
    #fout.close()
