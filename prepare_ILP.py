import Voronoi_boundaries
import census_block
import closest
import embedded_graph
import relevant_districts
import census_block_dependents
import areas_of_intersection
import sys

def gen(shapefilename, C_3D):
    G = embedded_graph.EGraph()
    bbox = Voronoi_boundaries.find_bbox(C_3D)
    cells = Voronoi_boundaries.power_cells(C_3D, bbox)
    for cell in cells:
        G.process_cell(cell, True) #get rid of extraneous points
    G.find_outer()
    centers_2D = [(x,y) for x,y,z in C_3D]
    for x in census_block_dependents.generator(areas_of_intersection.generator((relevant_districts.generator(closest.generator(census_block.generator(shapefilename), C_3D), G)), cells), centers_2D):
        yield x


args = sys.argv[1:]
shapefilename = args.pop(0)
assignment_filename = args.pop(0)
output_filename = args.pop(0)
assignment_file = open(assignment_filename)
k, n = [int(x) for x in assignment_file.readline().split()]
C_3D = [tuple(float(x) for x in assignment_file.readline().split()) for _ in range(k)]
fout = open(output_filename, 'w')
for census_block, relevant_districts, areas, dependents in gen(shapefilename,C_3D):
    fout.write(str(census_block.ID)+" ")
    for district, area, dependent in zip(relevant_districts, areas, dependents):
        for item in [district, area, dependent]:
            fout.write(str(item)+" ")
        fout.write("\n")
fout.close()
