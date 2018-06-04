import Voronoi_boundaries
import census_block
import closest
import embedded_graph
import relevant_districts
import census_block_dependents
import areas_of_intersection
import initial_population_assignment
import join
import sys

def gen(shapefilename, assignment_filename, C_3D):
    G = embedded_graph.EGraph()
    bbox = Voronoi_boundaries.find_bbox(C_3D)
    cells = Voronoi_boundaries.power_cells(C_3D, bbox)
    for cell in cells:
        G.process_cell(cell, True) #get rid of extraneous points
    G.find_outer()
    centers_2D = [(x,y) for x,y,z in C_3D]
    def merge(x,y):
        relevant_district_items = y[1]
        district2pop = x[1]
        for item in relevant_district_items:
            item.population = district2pop[item.ID] if item.ID in district2pop else 0
        return y
    closest_it = closest.gen(census_block.gen(shapefilename), C_3D)
    relevant_it = relevant_districts.gen(closest_it, G)
    areas_it = areas_of_intersection.gen(relevant_it, cells)
    dependents_it = census_block_dependents.gen(areas_it, centers_2D)
    it = join.gen(merge, initial_population_assignment.gen(assignment_filename), lambda x:x[0], dependents_it, lambda x:x[0].ID)
    #for x in join.gen(merge, initial_population_assignment.gen(assignment_filename), lambda x:x[0],
    #                      census_block_dependents.gen(areas_of_intersection.gen((relevant_districts.gen(closest.gen(census_block.gen(shapefilename), C_3D), G)), cells), centers_2D), lambda x:x[0].ID):
    for x in it:
        yield x


args = sys.argv[1:]
shapefilename = args.pop(0)
assignment_filename = args.pop(0)
output_filename = args.pop(0)
assignment_file = open(assignment_filename)
k, n = [int(x) for x in assignment_file.readline().split()]
C_3D = [tuple(float(x) for x in assignment_file.readline().split()) for _ in range(k)]
fout = open(output_filename, 'w')
for census_block, relevant_district_items in gen(shapefilename, assignment_filename, C_3D):
    fout.write(str(census_block.ID)+" ")
    for item in relevant_district_items:   #district, area, dependent in zip(relevant_districts, areas, dependents):
        for value in [item.ID, item.population, item.area, item.dependee]:
            fout.write(str(value)+" ")
    fout.write("\n")
    fout.flush() #for debugging
fout.close()

#/Users/klein/drive/District_data/RhodeIsland_census_block_data/tabblock2010_44_pophu /Users/klein/drive/District_data/RI_new_assignment.txt foo.txt
