import census_block
import closest
import relevant_districts
import areas_of_intersection
import initial_population_assignment
import district_graph
import block_bfs
import join
import sys

def gen(shapefilename, assignment_filename):
    G, cells, C_3D = district_graph.get(assignment_filename)
    def merge(x,y):
        relevant_district_items = y[1]
        district2pop = x[1]
        for item in relevant_district_items:
            item.population = district2pop[item.ID] if item.ID in district2pop else 0
        return y
    closest_it = closest.gen(census_block.gen(shapefilename), C_3D)
    relevant_it = relevant_districts.gen(closest_it, G)
    areas_it = areas_of_intersection.gen(relevant_it, cells)
    census_block_plus_collection = block_bfs.get(areas_it, len(cells))
    # It might be a performance problem that the next statement materializes the whole dict
    d = {block.ID:(block, rel) for block,rel in census_block_plus_collection}
    for id, pop_assignment in initial_population_assignment.gen(assignment_filename):
        if id in d:
            for item in d[id][1]:
                item.population = pop_assignment[item.ID] if item.ID in pop_assignment else 0
            yield d[id]
            
    ####it = join.gen(merge, initial_population_assignment.gen(assignment_filename), lambda x:x[0], iter(census_block_plus_collection), lambda x:x[0].ID)
    #for x in join.gen(merge, initial_population_assignment.gen(assignment_filename), lambda x:x[0],
    #                      census_block_dependents.gen(areas_of_intersection.gen((relevant_districts.gen(closest.gen(census_block.gen(shapefilename), C_3D), G)), cells), centers_2D), lambda x:x[0].ID):
#    for x in it:
#        yield x


args = sys.argv[1:]
shapefilename = args.pop(0)
assignment_filename = args.pop(0)
output_filename = args.pop(0)
fout = open(output_filename, 'w')
counter = 0
for census_block, relevant_district_items in gen(shapefilename, assignment_filename):
    if counter % 10000 == 0: print("counter", counter)
    counter = counter + 1
    fout.write(str(census_block.ID)+" ")
    for item in relevant_district_items:   #district, area, dependent in zip(relevant_districts, areas, dependents):
        for value in [item.ID, item.population, item.area, item.dependee]:
            fout.write(str(value)+" ")
    fout.write("\n")
    fout.flush() #for debugging
fout.close()

#/Users/klein/drive/District_data/RhodeIsland_census_block_data/tabblock2010_44_pophu /Users/klein/drive/District_data/RI_new_assignment.txt foo.txt
